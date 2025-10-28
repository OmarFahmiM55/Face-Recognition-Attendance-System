from sqlalchemy import Integer, String, Boolean, Column, DateTime
from database import Base
from datetime import datetime

class FaceEncoding(Base):
    __tablename__ = "Face_encoding"
    id = Column(Integer, primary_key=True, autoincrement=True) 
    user_id = Column(String(100), unique=True)  
    encoding = Column(String(10000))
    detected_at = Column(DateTime, nullable=True)
    fingerprint_enabled = Column(Integer, default=0) 
    status = Column(String(100), nullable=True)

