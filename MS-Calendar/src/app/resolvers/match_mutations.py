import strawberry
from typing import Optional
from datetime import datetime
from sqlalchemy import select

from app.graphql_types import (
    Match as MatchType,
    CreateMatchInput,
    UpdateMatchInput,
    UpdateScoreInput,
    MatchStatus
)
from app.models import Match
from app.database import get_db_session


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
            
            # Recharger avec les relations
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
            
            # Mettre à jour les champs fournis
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
