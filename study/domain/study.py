from dataclasses import dataclass
from datetime import datetime

@dataclass
class StudySession:
    id: str
    user_id: str
    subject: str
    avg_focus: float
    start_time: datetime
    end_time: datetime
    created_at: datetime

@dataclass
class StudyData:
    id: str
    user_id: str
    session_id: str
    ppg_value: float
    focus_score: float
    time: datetime
    created_at: datetime