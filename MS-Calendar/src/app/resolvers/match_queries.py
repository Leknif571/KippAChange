import strawberry
from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from app.graphql_types import Match as MatchType, MatchStatus
from app.models import Match
from app.database import get_db_session


@strawberry.type
class MatchQuery:
    @strawberry.field
    async def get_match(self, match_id: int) -> Optional[MatchType]:
        """Récupérer un match par son ID"""
        async with get_db_session() as session:
            result = await session.execute(
                select(Match)
                .options(
                    selectinload(Match.competition),
                    selectinload(Match.home_team),
                    selectinload(Match.away_team)
                )
                .where(Match.id == match_id)
            )
            match = result.scalar_one_or_none()
            if match:
                return self._convert_to_type(match)
            return None

    @strawberry.field
    async def get_matches(
        self,
        sport_id: Optional[int] = None,
        competition_id: Optional[int] = None,
        team_id: Optional[int] = None,
        status: Optional[MatchStatus] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[MatchType]:
        """Récupérer une liste de matchs avec filtres"""
        async with get_db_session() as session:
            query = select(Match).options(
                selectinload(Match.competition),
                selectinload(Match.home_team),
                selectinload(Match.away_team)
            )
            
            filters = []
            if competition_id:
                filters.append(Match.competition_id == competition_id)
            if team_id:
                filters.append(
                    or_(Match.home_team_id == team_id, Match.away_team_id == team_id)
                )
            if status:
                filters.append(Match.status == status.value)
            if from_date:
                filters.append(Match.match_date >= from_date)
            if to_date:
                filters.append(Match.match_date <= to_date)
            
            if filters:
                query = query.where(and_(*filters))
            
            query = query.order_by(Match.match_date.asc()).limit(limit).offset(offset)
            
            result = await session.execute(query)
            matches = result.scalars().all()
            return [self._convert_to_type(match) for match in matches]

    @strawberry.field
    async def get_upcoming_matches(
        self,
        competition_id: Optional[int] = None,
        days_ahead: int = 7,
        limit: int = 50
    ) -> List[MatchType]:
        """Récupérer les matchs à venir dans les prochains jours"""
        now = datetime.utcnow()
        from datetime import timedelta
        future_date = now + timedelta(days=days_ahead)
        
        return await self.get_matches(
            competition_id=competition_id,
            status=MatchStatus.SCHEDULED,
            from_date=now,
            to_date=future_date,
            limit=limit
        )

    @strawberry.field
    async def get_live_matches(
        self,
        competition_id: Optional[int] = None
    ) -> List[MatchType]:
        """Récupérer les matchs en cours"""
        return await self.get_matches(
            competition_id=competition_id,
            status=MatchStatus.LIVE
        )

    def _convert_to_type(self, match: Match) -> MatchType:
        """Convertir un modèle SQLAlchemy en type GraphQL"""
        from app.graphql_types import Competition as CompType, Team as TeamType, Sport as SportType
        
        competition_type = None
        if match.competition:
            sport_type = None
            if hasattr(match.competition, 'sport') and match.competition.sport:
                sport_type = SportType(
                    id=match.competition.sport.id,
                    name=match.competition.sport.name,
                    code=match.competition.sport.code,
                    description=match.competition.sport.description,
                    is_active=match.competition.sport.is_active,
                    created_at=match.competition.sport.created_at,
                    updated_at=match.competition.sport.updated_at
                )
            
            competition_type = CompType(
                id=match.competition.id,
                name=match.competition.name,
                code=match.competition.code,
                country=match.competition.country,
                season=match.competition.season,
                sport_id=match.competition.sport_id,
                is_active=match.competition.is_active,
                created_at=match.competition.created_at,
                updated_at=match.competition.updated_at,
                sport=sport_type
            )
        
        home_team_type = None
        if match.home_team:
            home_team_type = TeamType(
                id=match.home_team.id,
                name=match.home_team.name,
                short_name=match.home_team.short_name,
                code=match.home_team.code,
                logo_url=match.home_team.logo_url,
                country=match.home_team.country,
                sport_id=match.home_team.sport_id,
                created_at=match.home_team.created_at,
                updated_at=match.home_team.updated_at
            )
        
        away_team_type = None
        if match.away_team:
            away_team_type = TeamType(
                id=match.away_team.id,
                name=match.away_team.name,
                short_name=match.away_team.short_name,
                code=match.away_team.code,
                logo_url=match.away_team.logo_url,
                country=match.away_team.country,
                sport_id=match.away_team.sport_id,
                created_at=match.away_team.created_at,
                updated_at=match.away_team.updated_at
            )
        
        return MatchType(
            id=match.id,
            competition_id=match.competition_id,
            home_team_id=match.home_team_id,
            away_team_id=match.away_team_id,
            match_date=match.match_date,
            status=MatchStatus(match.status),
            home_score=match.home_score,
            away_score=match.away_score,
            venue=match.venue,
            referee=match.referee,
            round=match.round,
            home_odds=match.home_odds,
            draw_odds=match.draw_odds,
            away_odds=match.away_odds,
            created_at=match.created_at,
            updated_at=match.updated_at,
            competition=competition_type,
            home_team=home_team_type,
            away_team=away_team_type
        )


import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db_session
from app.models import Match
from app.models.match import MatchStatus

async def get_upcoming_matches(days_ahead: int = 7, limit: int = 10):
    now = datetime.utcnow()
    end = now + timedelta(days=days_ahead)
    async with get_db_session() as session:
        q = await session.execute(
            select(Match)
            .options(
                selectinload(Match.home_team),
                selectinload(Match.away_team),
                selectinload(Match.competition)
            )
            .where(Match.match_date >= now, Match.match_date <= end)
            .order_by(Match.match_date)
            .limit(limit)
        )
        return q.scalars().all()

async def get_live_matches():
    async with get_db_session() as session:
        q = await session.execute(
            select(Match)
            .options(
                selectinload(Match.home_team),
                selectinload(Match.away_team),
                selectinload(Match.competition)
            )
            .where(Match.status == MatchStatus.LIVE)
            .order_by(Match.match_date)
        )
        return q.scalars().all()
