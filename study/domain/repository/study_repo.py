from abc import ABCMeta, abstractmethod
from study.domain.study import StudySession, StudyData, Subject

class IStudy(metaclass=ABCMeta):
    @abstractmethod
    def get_sessions(self, user_id: str, page: int, items_per_page:int) -> tuple[int, list[StudySession]]:
        raise NotImplementedError

    @abstractmethod
    def find_datas_by_session_id(self, user_id: str, session_id: str) -> list[StudyData]:
        raise NotImplementedError

    @abstractmethod
    def find_session_by_id(self, user_id: str, session_id: str) -> StudySession:
        raise NotImplementedError

    @abstractmethod
    def save_session(self, user_id:str, session: StudySession) -> StudySession:
        raise NotImplementedError

    @abstractmethod
    def update_session(self, user_id:str, session: StudySession) -> StudySession:
        raise NotImplementedError
    
    @abstractmethod
    def save_data(self, user_id:str, datas: list[StudyData]) -> list[StudyData]:
        raise NotImplementedError

    # 학습 세션 삭제
    @abstractmethod
    def delete_session(self, user_id:str, session_id: str):
        raise NotImplementedError
    
    # 과목 조회
    @abstractmethod
    def get_subjects(self, user_id:str) -> list[Subject]:
        raise NotImplementedError
    
    # 과목 추가
    @abstractmethod
    def save_subject(self, user_id:str, subject: Subject) -> Subject:
        raise NotImplementedError

    # 과목 수정
    @abstractmethod
    def update_subject(self, user_id:str, subject: Subject) -> Subject:
        raise NotImplementedError

    # 과목 삭제
    @abstractmethod
    def delete_subject(self, user_id:str, subject: Subject):
        raise NotImplementedError
    
    # 과목명으로 과목 조회
    @abstractmethod
    def find_by_subject_name(self, user_id:str, subject_name:str) -> Subject:
        raise NotImplementedError
