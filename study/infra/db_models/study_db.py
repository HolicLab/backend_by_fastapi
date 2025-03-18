from database import Base
from datetime import datetime
from sqlalchemy import String, DateTime, Column, ForeignKey, Float, TIMESTAMP
from sqlalchemy.orm import relationship
# from user.infra.db_models.user import User
import pytz

# 한국 시간대 객체 생성 (pytz 사용)
korea_timezone = pytz.timezone('Asia/Seoul')

def get_korea_now():
    return datetime.now(korea_timezone)

class StudySession(Base):
    __tablename__ = "StudySession"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("User.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(String(36), ForeignKey("Subject.id", ondelete="SET NULL"), nullable=True)
    subject = Column(String(10), nullable=True)
    avg_focus = Column(Float(asdecimal=True))
    start_time = Column(String(30))
    end_time = Column(String(30))
    created_at = Column(DateTime(6), nullable=False, default=get_korea_now)
    updated_at = Column(DateTime(6), nullable=False, onupdate=get_korea_now)

    # all, delete-orphan옵션에 의해 StudySession 객체가 삭제될때 연관된 StudyData 객체들도 자동으로 삭제
    study_data = relationship("StudyData", back_populates="study_session", cascade="all, delete-orphan")
    subject_obj = relationship("Subject", back_populates="study_sessions")
    user = relationship("User", back_populates="study_sessions")

class StudyData(Base):
    __tablename__ = "StudyData"

    id = Column(String(36), primary_key=True)
    session_id = Column(String(36), ForeignKey("StudySession.id", ondelete="CASCADE"), nullable=False)
    ppg_value = Column(Float(asdecimal=True))
    focus_score = Column(Float(asdecimal=True))
    time = Column(TIMESTAMP(6))
    created_at = Column(TIMESTAMP(6), nullable=False, default=get_korea_now)

    study_session = relationship("StudySession", back_populates="study_data")

class Subject(Base):
    __tablename__ = "Subject"
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("User.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_name = Column(String(10), unique=True)
    created_at = Column(DateTime(6), nullable=False, default=get_korea_now)

    study_sessions = relationship("StudySession", back_populates="subject_obj")
    user = relationship("User", back_populates="subjects")