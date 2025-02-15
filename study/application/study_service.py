from ulid import ULID
from study.domain.study import StudySession, StudyData
from study.domain.repository.study_repo import IStudy
from datetime import datetime

class StudyService:
    def __init__(self, study_repo: IStudy):
        self.study_repo = study_repo
        self.ulid = ULID

    # 사용자의 학습 세션들을 가져온다(페이지네이션 처리됨)
    def get_sessions(
        self, 
        user_id: str, 
        page: int, 
        items_per_page: int
    ) -> tuple[int, list[StudySession]]:
        return self.study_repo.get_sessions(
            user_id = user_id, 
            page = page, 
            items_per_page = items_per_page
        )
    
    # 사용자의 특정 세션의 세부데이터를 가져온다.
    def get_datas(self, user_id: str, session_id: str) -> List[StudyData]:
        return self.study_repo.find_datas_by_session_id(user_id = user_id, session = session_id)    
        
    
    # 학습 세션 생성
    def create_session(
        self,
        user_id: str,
        subject: str,
        start_time: datetime,
    )-> StudySession:
        now = datetime.now()

        session = StudySession(
            id = self.ulid.generate(),
            user_id = user_id,
            subject = subject,
            avg_focus = None,
            start_time = start_time,
            end_time = None,
            created_at = now,
            updated_at = now,
        )

        self.study_repo.save_session(user_id = user_id, session = session)
        
        return session
    
    # 학습 세션 종료
    def complete_session(
        self,
        id: str,
        user_id: str,
        avg_focus: float | None = None,
        end_time: str
    ):
        session = self.study_repo.find_session_by_id(user_id = user_id, session_id = id)

        session.updated_at = datetime.now()
        session.avg_focus = avg_focus
        session.end_time = end_time

        self.user_repo.update_session(user_id = user_id, session = session)

        return session

    # ppg 데이터 생성
    def create_data(
        self,
        user_id: str,
        session_id: str,
        ppg_value: float,
        focus_score: float,
        time: str,
    ) -> StudyData:
        now = datetime.now()

        data = StudyData(
            id = self.ulid.generate(),
            user_id = user_id,
            session_id = session_id,
            ppg_value = ppg_value,
            focus_score = focus_score,
            time = time,
            create_at = now
        )

        self.study_repo.save_data(user_id = user_id, data = data)

        return data

    # 특정 세션 삭제
    def delete_session(self, user_id: str, session_id: str):
        return self.study_repo.delete_session(user_id = user_id, session_id = session_id)
