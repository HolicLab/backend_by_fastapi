from dataclasses import dataclass
from datetime import datetime

@dataclass
class StudySession:
    id: str
    user_id: str
    subject_id: str | None
    subject: str | None
    avg_focus: float | None
    ai_avg_focus: float | None
    start_time: str
    end_time: str | None
    created_at: datetime
    updated_at: datetime

@dataclass
class StudyData:
    id: str
    session_id: str
    ppg_value: float
    focus_score: float
    time: datetime
    created_at: datetime

@dataclass
class Subject:
    id: str
    user_id: str
    subject_name: str
    created_at: datetime