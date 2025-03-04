from ulid import ULID
from study.domain.study import StudySession, StudyData, Subject
from study.domain.repository.study_repo import IStudy
from datetime import datetime
from typing import Optional
from dependency_injector.wiring import inject

class StudyService:
    @inject
    def __init__(self, study_repo: IStudy):
        self.study_repo = study_repo
        self.ulid = ULID()

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
            items_per_page = items_per_page,
        )
    
    # 사용자의 특정 세션의 세부데이터를 가져온다.
    def get_datas(self, user_id: str, session_id: str) -> list[StudyData]:
        return self.study_repo.find_datas_by_session_id(user_id = user_id, session_id = session_id)    
        
    
    # 학습 세션 생성
    def create_session(
        self,
        user_id: str,
        subject: str,
        start_time: str,
    )-> StudySession:
        now = datetime.now()
        subject = self.study_repo.find_by_subject_name(user_id = user_id, subject_name = subject)

        session = StudySession(
            id = self.ulid.generate(),
            user_id = user_id,
            subject_id = subject.id,
            subject = subject.subject_name,
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
        end_time: str,
        avg_focus: Optional[float] = None,
    ):
        session = self.study_repo.find_session_by_id(user_id = user_id, session_id = id)

        session.updated_at = datetime.now()
        session.avg_focus = avg_focus
        session.end_time = end_time

        self.study_repo.update_session(user_id = user_id, session = session)

        return session

    # ppg 데이터 생성
    def create_data(
        self,
        user_id: str,
        session_id: str,
        datas: list[dict]
    ) -> list[StudyData]:

        session = self.study_repo.find_session_by_id(user_id = user_id, session_id = session_id)
        
        now = datetime.now()
        study_datas = []
        for data in datas:
            study_data = StudyData(
                id = self.ulid.generate(),
                session_id = session_id,
                ppg_value = data.ppg_value,
                focus_score = data.focus_score,
                time = data.time,
                created_at = now
            )
            study_datas.append(study_data)

        return self.study_repo.save_data(user_id = user_id, datas = study_datas)

    # 특정 세션 삭제
    def delete_session(self, user_id: str, session_id: str):
        return self.study_repo.delete_session(user_id = user_id, session_id = session_id)

    # 전체 과목 조회
    def get_subjects(self, user_id: str):
        return self.study_repo.get_subjects(user_id = user_id)

    # 과목 추가
    def create_subject(self, user_id: str, subject_name: str) -> Subject:
        now = datetime.now()

        subject = Subject(
            id = self.ulid.generate(),
            user_id = user_id,
            subject_name = subject_name,
            created_at = now
        )

        return self.study_repo.save_subject(user_id = user_id, subject = subject)
    
    # 과목명 수정
    def update_subject(self, user_id: str, target_name: str, new_name: str) -> Subject:
        subject = self.study_repo.find_by_subject_name(user_id = user_id, subject_name = target_name)

        subject.subject_name = new_name
        
        return self.study_repo.update_subject(user_id = user_id, subject = subject)
    
    # 과목 삭제
    def delete_subject(self, user_id: str, subject_name:str):
        subject = self.study_repo.find_by_subject_name(user_id = user_id, subject_name = subject_name)

        return self.study_repo.delete_subject(user_id = user_id, subject = subject)

    

        