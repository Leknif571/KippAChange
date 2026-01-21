from sqlalchemy import Column, String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel


class Competition(BaseModel):
    __tablename__ = "competitions"

    name = Column(String(200), nullable=False)
    code = Column(String(50), unique=True, nullable=False)  
    country = Column(String(100))
    season = Column(String(20)) 
    sport_id = Column(Integer, ForeignKey("sports.id"), nullable=False)
    is_active = Column(Boolean, default=True)


    sport = relationship("Sport", back_populates="competitions")
    matches = relationship("Match", back_populates="competition")


from .sport import Sport
Sport.competitions = relationship("Competition", back_populates="sport")
