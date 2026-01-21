from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Float, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .base import BaseModel


class MatchStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    LIVE = "LIVE"
    FINISHED = "FINISHED"
    FINISHED = "FINISHED"
    POSTPONED = "POSTPONED"
    CANCELLED = "CANCELLED"

class MatchResult(str, enum.Enum):
    HOME_WIN = "HOME_WIN"
    AWAY_WIN = "AWAY_WIN"
    DRAW = "DRAW"
    NO_RESULT = "NO_RESULT"


class Match(BaseModel):
    __tablename__ = "matches"

    competition_id = Column(Integer, ForeignKey("competitions.id"), nullable=False)
    home_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    away_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    
    match_date = Column(DateTime, nullable=False, index=True)
    
    status = Column(SQLEnum(MatchStatus), default=MatchStatus.SCHEDULED, nullable=False)

    result = Column(SQLEnum(MatchResult), default=MatchResult.NO_RESULT, nullable=False)
    
    home_score = Column(Integer, default=0)
    away_score = Column(Integer, default=0)
    
    venue = Column(String(200))  
    referee = Column(String(100))
    round = Column(String(50))  
    
    # Cotes moyennes (optionnel pour référence)
    home_odds = Column(Float)
    draw_odds = Column(Float)
    away_odds = Column(Float)

    # Le match est pariable uniquement si les cotes sont définies
    is_bettable = Column(Boolean, default=False)

    competition = relationship("Competition", back_populates="matches")
    home_team = relationship("Team", foreign_keys=[home_team_id])
    away_team = relationship("Team", foreign_keys=[away_team_id])
