from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class Team(BaseModel):
    __tablename__ = "teams"

    name = Column(String(200), nullable=False)
    short_name = Column(String(50))
    code = Column(String(20), unique=True, nullable=False)
    logo_url = Column(String(500))
    country = Column(String(100))
    sport_id = Column(Integer, ForeignKey("sports.id"), nullable=False)

    # Relations
    sport = relationship("Sport")
