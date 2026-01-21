import strawberry
from datetime import datetime
from typing import Optional, Any, List


def _get_score_from_model(model, *names, default: int = 0) -> int:
    for n in names:
        if hasattr(model, n):
            val = getattr(model, n)
            if val is not None:
                try:
                    return int(val)
                except Exception:
                    return default
    return default


@strawberry.type
class TeamType:
    id: int
    name: str


@strawberry.type
class CompetitionType:
    id: int
    name: str


@strawberry.type
class MatchType:
    # on garde la référence au modèle SQLAlchemy en privé
    _model: strawberry.Private[Any]

    @strawberry.field
    def id(self) -> int:
        return getattr(self._model, "id")

    @strawberry.field
    def matchDate(self) -> datetime:
        return getattr(self._model, "match_date")

    @strawberry.field
    def status(self) -> str:
        return getattr(self._model, "status")

    @strawberry.field
    def scoreHome(self) -> int:
        return _get_score_from_model(self._model, "score_home", "home_score")

    @strawberry.field
    def scoreAway(self) -> int:
        return _get_score_from_model(self._model, "score_away", "away_score")

    @strawberry.field
    def venue(self) -> Optional[str]:
        return getattr(self._model, "venue", None)

    @strawberry.field
    def round(self) -> Optional[str]:
        return getattr(self._model, "round", None)

    @strawberry.field
    def homeOdds(self) -> Optional[float]:
        return getattr(self._model, "home_odds", None)

    @strawberry.field
    def drawOdds(self) -> Optional[float]:
        return getattr(self._model, "draw_odds", None)

    @strawberry.field
    def awayOdds(self) -> Optional[float]:
        return getattr(self._model, "away_odds", None)

    @strawberry.field
    def homeTeam(self) -> TeamType:
        ht = getattr(self._model, "home_team", None)
        return TeamType(id=ht.id, name=ht.name) if ht is not None else TeamType(id=0, name="")

    @strawberry.field
    def awayTeam(self) -> TeamType:
        at = getattr(self._model, "away_team", None)
        return TeamType(id=at.id, name=at.name) if at is not None else TeamType(id=0, name="")

    @strawberry.field
    def competition(self) -> Optional[CompetitionType]:
        c = getattr(self._model, "competition", None)
        return CompetitionType(id=c.id, name=c.name) if c is not None else None


# utilitaire pour retourner un MatchType à partir d'un modèle SQLAlchemy
def map_match(model) -> MatchType:
    return MatchType(_model=model)


@strawberry.type
class Query:
    """Root Query"""

    @strawberry.field
    async def getUpcomingMatches(self, daysAhead: int = 7, limit: int = 10) -> List[MatchType]:
        # import local resolver here to avoid import cycles
        from app.resolvers.match_queries import get_upcoming_matches
        models = await get_upcoming_matches(days_ahead=daysAhead, limit=limit)
        return [map_match(m) for m in models]

    @strawberry.field
    async def getLiveMatches(self) -> List[MatchType]:
        from app.resolvers.match_queries import get_live_matches
        models = await get_live_matches()
        return [map_match(m) for m in models]

    @strawberry.field
    async def getBettableMatches(self, limit: int = 50) -> List[MatchType]:
        """Retourne les matchs pariables (cotes définies par un trader)"""
        from app.resolvers.match_queries import get_bettable_matches
        models = await get_bettable_matches(limit=limit)
        return [map_match(m) for m in models]

@strawberry.type
class Mutation:
    """Root Mutation"""

    @strawberry.field
    def ping(self) -> str:
        return "pong"

    @strawberry.mutation
    async def setMatchOdds(
        self,
        matchId: int,
        homeOdds: float,
        drawOdds: float,
        awayOdds: float
    ) -> MatchType:
        """
        Permet à un trader de définir les cotes d'un match.
        Une fois les cotes définies, le match devient pariable.
        """
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        from app.database import get_db_session
        from app.models import Match
        from app.MBManager import publish_match_bettable

        async with get_db_session() as session:
            q = await session.execute(
                select(Match)
                .options(
                    selectinload(Match.home_team),
                    selectinload(Match.away_team),
                    selectinload(Match.competition)
                )
                .where(Match.id == matchId)
            )
            match = q.scalar_one_or_none()

            if not match:
                raise Exception(f"Match {matchId} non trouvé")

            # Mettre à jour les cotes
            match.home_odds = homeOdds
            match.draw_odds = drawOdds
            match.away_odds = awayOdds
            match.is_bettable = True

            await session.commit()
            await session.refresh(match)

            # Publier l'événement sur RabbitMQ pour MS-Bet
            publish_match_bettable({
                "id": match.id,
                "home_team": match.home_team.name,
                "away_team": match.away_team.name,
                "match_date": match.match_date.isoformat(),
                "competition": match.competition.name if match.competition else None,
                "home_odds": match.home_odds,
                "draw_odds": match.draw_odds,
                "away_odds": match.away_odds,
                "venue": match.venue,
                "round": match.round
            })

            return map_match(match)

    @strawberry.mutation
    async def selectMatchForBet(
        self,
        matchId: int,
        userId: str
    ) -> MatchType:
        """
        Sélectionne un match pour parier.
        Publie un message sur RabbitMQ pour notifier MS-Bet et MS-Notifications.
        """
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        from app.database import get_db_session
        from app.models import Match
        from app.MBManager import publish_match_selected_for_bet

        async with get_db_session() as session:
            q = await session.execute(
                select(Match)
                .options(
                    selectinload(Match.home_team),
                    selectinload(Match.away_team),
                    selectinload(Match.competition)
                )
                .where(Match.id == matchId)
            )
            match = q.scalar_one_or_none()

            if not match:
                raise Exception(f"Match {matchId} non trouvé")

            if not match.is_bettable:
                raise Exception(f"Le match {matchId} n'est pas encore pariable (cotes non définies)")

            # Publier l'événement sur RabbitMQ
            publish_match_selected_for_bet({
                "id": match.id,
                "home_team": match.home_team.name,
                "away_team": match.away_team.name,
                "match_date": match.match_date.isoformat(),
                "competition": match.competition.name if match.competition else None,
                "home_odds": match.home_odds,
                "draw_odds": match.draw_odds,
                "away_odds": match.away_odds,
                "venue": match.venue,
                "round": match.round
            }, user_id=userId)

            return map_match(match)


schema = strawberry.Schema(query=Query, mutation=Mutation)