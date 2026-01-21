import strawberry
from enum import Enum


@strawberry.enum
class MatchResult(Enum):
    HOME_WON = "HOME_WON"
    AWAY_WON = "AWAY_WON"
    DRAW = "DRAW"
    NO_RESULT = "NO_RESULT"


@strawberry.input
class FinishMatchInput:
    match_id: int
    home_score: int
    away_score: int


@strawberry.type
class FinishMatchPayload:
    match_id: int
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    result: MatchResult
    message: str