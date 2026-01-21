import strawberry
from typing import Optional
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.graphql_types import (
    Match as MatchType,
    CreateMatchInput,
    UpdateMatchInput,
    UpdateScoreInput,
    MatchStatus,
    MatchResult,
    FinishMatchInput,
    FinishMatchPayload
)
from app.models import Match
from app.database import get_db_session

# Import RabbitMQ
try:
    from app.MBManager import publish_match_finished
    RABBITMQ_ENABLED = True
except Exception:
    RABBITMQ_ENABLED = False


def calculate_match_result(home_score: int, away_score: int) -> MatchResult:
    """Calcule le résultat du match en fonction des scores"""
    if home_score is None or away_score is None:
        return MatchResult.NO_RESULT
    if home_score > away_score:
        return MatchResult.HOME_WON
    elif away_score > home_score:
        return MatchResult.AWAY_WON
    else:
        return MatchResult.DRAW


@strawberry.type
class MatchMutation:
    @strawberry.mutation
    async def create_match(self, input: CreateMatchInput) -> MatchType:
        """Créer un nouveau match"""
        async with get_db_session() as session:
            new_match = Match(
                competition_id=input.competition_id,
                home_team_id=input.home_team_id,
                away_team_id=input.away_team_id,
                match_date=input.match_date,
                venue=input.venue,
                referee=input.referee,
                round=input.round,
                status=MatchStatus.SCHEDULED.value
            )
            session.add(new_match)
            await session.commit()
            await session.refresh(new_match)

            result = await session.execute(
                select(Match).where(Match.id == new_match.id)
            )
            match = result.scalar_one()

            from app.resolvers.match_queries import MatchQuery
            query = MatchQuery()
            return query._convert_to_type(match)

    @strawberry.mutation
    async def update_match(self, input: UpdateMatchInput) -> Optional[MatchType]:
        """Mettre à jour un match"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Match).where(Match.id == input.match_id)
            )
            match = result.scalar_one_or_none()

            if not match:
                return None

            if input.match_date is not None:
                match.match_date = input.match_date
            if input.status is not None:
                match.status = input.status.value
            if input.home_score is not None:
                match.home_score = input.home_score
            if input.away_score is not None:
                match.away_score = input.away_score
            if input.venue is not None:
                match.venue = input.venue
            if input.referee is not None:
                match.referee = input.referee
            if input.round is not None:
                match.round = input.round
            if input.home_odds is not None:
                match.home_odds = input.home_odds
            if input.draw_odds is not None:
                match.draw_odds = input.draw_odds
            if input.away_odds is not None:
                match.away_odds = input.away_odds

            match.updated_at = datetime.utcnow()
            await session.commit()
            await session.refresh(match)

            from app.resolvers.match_queries import MatchQuery
            query = MatchQuery()
            return query._convert_to_type(match)

    @strawberry.mutation
    async def update_score(self, input: UpdateScoreInput) -> Optional[MatchType]:
        """Mettre à jour le score d'un match (pour le live)"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Match).where(Match.id == input.match_id)
            )
            match = result.scalar_one_or_none()

            if not match:
                return None

            match.home_score = input.home_score
            match.away_score = input.away_score

            if input.status is not None:
                match.status = input.status.value

            match.updated_at = datetime.utcnow()
            await session.commit()
            await session.refresh(match)

            from app.resolvers.match_queries import MatchQuery
            query = MatchQuery()
            return query._convert_to_type(match)

    @strawberry.mutation
    async def finish_match(self, input: FinishMatchInput) -> FinishMatchPayload:
        """
        Termine un match avec le score final (appelé par le trader).
        - Met à jour le score et le statut en FINISHED
        - Calcule le résultat (HOME_WON, AWAY_WON, DRAW)
        - Publie le résultat sur RabbitMQ pour MS-Bet
        """
        async with get_db_session() as session:
            # Récupérer le match avec ses relations
            result = await session.execute(
                select(Match)
                .options(
                    selectinload(Match.home_team),
                    selectinload(Match.away_team),
                    selectinload(Match.competition)
                )
                .where(Match.id == input.match_id)
            )
            match = result.scalar_one_or_none()

            if not match:
                raise Exception(f"Match {input.match_id} non trouvé")

            # Vérifier que le match était pariable
            if not match.is_bettable:
                raise Exception(f"Match {input.match_id} n'était pas pariable, impossible de le terminer")

            # Mettre à jour le match
            match.home_score = input.home_score
            match.away_score = input.away_score
            match.status = MatchStatus.FINISHED.value
            match.is_bettable = False  # Plus pariable une fois terminé
            match.updated_at = datetime.utcnow()

            await session.commit()
            await session.refresh(match)

            # Calculer le résultat
            match_result = calculate_match_result(input.home_score, input.away_score)

            # Préparer le payload
            home_team_name = match.home_team.name if match.home_team else "Unknown"
            away_team_name = match.away_team.name if match.away_team else "Unknown"

            # Publier sur RabbitMQ pour MS-Bet
            if RABBITMQ_ENABLED:
                publish_match_finished({
                    "match_id": match.id,
                    "home_team_id": match.home_team_id,
                    "away_team_id": match.away_team_id,
                    "home_team": home_team_name,
                    "away_team": away_team_name,
                    "home_score": input.home_score,
                    "away_score": input.away_score,
                    "result": match_result.value,  # "HOME_WON", "AWAY_WON", "DRAW"
                    "competition_id": match.competition_id,
                    "home_odds": float(match.home_odds) if match.home_odds else None,
                    "draw_odds": float(match.draw_odds) if match.draw_odds else None,
                    "away_odds": float(match.away_odds) if match.away_odds else None,
                })

            return FinishMatchPayload(
                match_id=match.id,
                home_team=home_team_name,
                away_team=away_team_name,
                home_score=input.home_score,
                away_score=input.away_score,
                result=match_result,
                message=f"Match terminé: {home_team_name} {input.home_score} - {input.away_score} {away_team_name}"
            )

    @strawberry.mutation
    async def delete_match(self, match_id: int) -> bool:
        """Supprimer un match"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Match).where(Match.id == match_id)
            )
            match = result.scalar_one_or_none()

            if not match:
                return False

            await session.delete(match)
            await session.commit()
            return True
