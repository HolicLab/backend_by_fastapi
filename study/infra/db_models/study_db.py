from database import Base
from datetime import datetime
from sqlalchemy import String, DateTime, Column, ForeignKey, Float
from sqlalchemy.orm import relationship

class StudySession(Base):
    __tablename__ = "StudySession"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    subject_id = Column(String(36), ForeignKey("Subject.id", ondelete="SET NULL"))
    subject = Column(String(10), nullable=True)
    avg_focus = Column(Float(asdecimal=True))
    start_time = Column(String(30))
    end_time = Column(String(30))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, onupdate=datetime.utcnow)

    # all, delete-orphan옵션에 의해 StudySession 객체가 삭제될때 연관된 StudyData 객체들도 자동으로 삭제
    study_data = relationship("StudyData", back_populates="study_session", cascade="all, delete-orphan")
    subject_obj = relationship("Subject", back_populates="study_session")

class StudyData(Base):
    __tablename__ = "StudyData"

    id = Column(String(36), primary_key=True)
    session_id = Column(String(36), ForeignKey("StudySession.id", ondelete="CASCADE"), nullable=False)
    ppg_value = Column(Float(asdecimal=True))
    focus_score = Column(Float(asdecimal=True))
    time = Column(String(30))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    study_session = relationship("StudySession", back_populates="study_data")

class Subject(Base):
    __tablename__ = "Subject"
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    subject_name = Column(String(10), unique=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    study_session = relationship("StudySession", back_populates="subject_obj")