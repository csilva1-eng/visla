from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    instagram_id = Column(String(50), unique=True, nullable=False)
    instagram_username = Column(String(100))
    google_refresh_token = Column(String)
    google_email = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    last_active = Column(DateTime)