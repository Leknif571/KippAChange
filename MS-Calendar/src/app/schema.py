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


@strawberry.type
class Mutation:
    """Root Mutation"""

    @strawberry.field
    def ping(self) -> str:
        return "pong"


schema = strawberry.Schema(query=Query, mutation=Mutation)