import strawberry
from datetime import datetime
from typing import Optional
from enum import Enum


@strawberry.enum
class MatchStatus(Enum):
    SCHEDULED = "SCHEDULED"
    LIVE = "LIVE"
    FINISHED = "FINISHED"
    POSTPONED = "POSTPONED"
    CANCELLED = "CANCELLED"


@strawberry.type
class Sport:
    id: int
    name: str
    code: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


@strawberry.type
class Team:
    id: int
    name: str
    short_name: Optional[str] = None
    code: str
    logo_url: Optional[str] = None
    country: Optional[str] = None
    sport_id: int
    created_at: datetime
    updated_at: datetime


@strawberry.type
class Competition:
    id: int
    name: str
    code: str
    country: Optional[str] = None
    season: Optional[str] = None
    sport_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    sport: Optional[Sport] = None


@strawberry.type
class Match:
    id: int
    competition_id: int
    home_team_id: int
    away_team_id: int
    match_date: datetime
    status: MatchStatus
    home_score: Optional[int] = 0
    away_score: Optional[int] = 0
    venue: Optional[str] = None
    referee: Optional[str] = None
    round: Optional[str] = None
    home_odds: Optional[float] = None
    draw_odds: Optional[float] = None
    away_odds: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    
    # Relations
    competition: Optional[Competition] = None
    home_team: Optional[Team] = None
    away_team: Optional[Team] = None


# Input types pour les mutations
@strawberry.input
class CreateMatchInput:
    competition_id: int
    home_team_id: int
    away_team_id: int
    match_date: datetime
    venue: Optional[str] = None
    referee: Optional[str] = None
    round: Optional[str] = None


@strawberry.input
class UpdateMatchInput:
    match_id: int
    match_date: Optional[datetime] = None
    status: Optional[MatchStatus] = None
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    venue: Optional[str] = None
    referee: Optional[str] = None
    round: Optional[str] = None
    home_odds: Optional[float] = None
    draw_odds: Optional[float] = None
    away_odds: Optional[float] = None


@strawberry.input
class UpdateScoreInput:
    match_id: int
    home_score: int
    away_score: int
    status: Optional[MatchStatus] = None
