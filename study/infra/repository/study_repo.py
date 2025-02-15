from study.domain.study import StudySession, StudyData
from study.domain.repository.study_repo import IStudy


class StudyRepository(IStudy):
    def get_sessions(self, user_id: str, page: int, items_per_page:int) -> tuple[int, list[StudySession]]:
        raise NotImplementedError

    def find_datas_by_session_id(self, user_id: str, session_id: str) -> list[StudyData]:
        raise NotImplementedError

    def find_session_by_id(self, user_id: str, session_id: str) -> StudySession:
        raise NotImplementedError

    def save_session(self, user_id:str, session: StudySession) -> StudySession:
        raise NotImplementedError
    
    def update_session(self, user_id:str, session: StudySession) -> StudySession:
        raise NotImplementedError

    def save_data(self, user_id:str, data: StudyData) -> StudyData:
        raise NotImplementedError

    def delete_session(self, user_id:str, session_id: str) -> StudySession:
        raise NotImplementedError

