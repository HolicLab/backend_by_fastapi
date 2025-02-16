from database import Base
from datetime import datetime
from sqlalchemy import String, DateTime, Column, ForeignKey, Float
from sqlalchemy.orm import relationship

class StudySession(Base):
    __tablename__ = "StudySession"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    subject = Column(String(10))
    avg_focus = Column(Float(asdecimal=True))
    start_time = Column(String(30))
    end_time = Column(String(30))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, onupdate=datetime.utcnow)

    study_data = relationship("StudyData", back_populates="study_session")

class StudyData(Base):
    __tablename__ = "StudyData"

    id = Column(String(36), primary_key=True)
    session_id = Column(String(36), ForeignKey("StudySession.id"), nullable=False)
    ppg_value = Column(Float(asdecimal=True))
    focus_score = Column(Float(asdecimal=True))
    time = Column(String(30))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    study_session = relationship("StudySession", back_populates="study_data")