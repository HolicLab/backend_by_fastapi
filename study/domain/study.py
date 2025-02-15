from dataclasses import dataclass
from datetime import datetime

@dataclass
class StudySession:
    id: str
    user_id: str
    subject: str
    avg_focus: float | None
    start_time: str
    end_time: str | None
    created_at: datetime
    updated_at: datetime

@dataclass
class StudyData:
    id: str
    user_id: str
    session_id: str
    ppg_value: float
    focus_score: float
    time: str
    created_at: datetime