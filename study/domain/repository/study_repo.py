from abc import ABCMeta, abstractmethod
from study.domain.study import StudySession, StudyData

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
    def save_data(self, user_id:str, data: StudyData) -> StudyData:
        raise NotImplementedError

    @abstractmethod
    def delete_session(self, user_id:str, session_id: str):
        raise NotImplementedError
    
