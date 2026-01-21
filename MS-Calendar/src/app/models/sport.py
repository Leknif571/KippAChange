from sqlalchemy import Column, String, Boolean
from .base import BaseModel


class Sport(BaseModel):
    __tablename__ = "sports"

    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(20), unique=True, nullable=False) 
    description = Column(String(500))
    is_active = Column(Boolean, default=True)
