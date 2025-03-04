from fastapi import HTTPException
from sqlalchemy.orm import joinedload

from database import SessionLocal
from study.domain.study import StudySession, StudyData, Subject
from study.domain.repository.study_repo import IStudy
from study.infra.db_models.study_db import StudySession as Session_db
from study.infra.db_models.study_db import StudyData as Data_db
from study.infra.db_models.study_db import Subject as SubjectDB
from utils.db_utils import row_to_dict
from dataclasses import asdict

class StudyRepository(IStudy):
    # db에서 학습 세션을 조회
    def get_sessions(self, user_id: str, page: int, items_per_page:int) -> tuple[int, list[StudySession]]:
        with SessionLocal() as db:
            query = (
                db.query(Session_db)
                .filter(Session_db.user_id == user_id)
            )
            total_count = query.count()
            sessions = (
                query.offset((page - 1) * items_per_page).limit(items_per_page).all()
            )
        session_vos = [StudySession(**row_to_dict(session)) for session in sessions]

        return total_count, session_vos

    # StudyData db에서 세션 id에 해당하는 집중도 데이터 조회
    def find_datas_by_session_id(self, user_id: str, session_id: str) -> list[StudyData]:
        with SessionLocal() as db:
            datas = (
                db.query(Data_db)
                .join(Session_db)
                .filter(Session_db.user_id == user_id, Data_db.session_id == session_id)
                .all()
            )

            if not datas:
                return None
        
        return [StudyData(**row_to_dict(data)) for data in datas]

    # db에서 학습 세션을 조회 
    def find_session_by_id(self, user_id: str, session_id: str) -> StudySession:
        with SessionLocal() as db:
            session = (
                db.query(Session_db).filter(Session_db.user_id == user_id, Session_db.id == session_id)
                .first()
            )
            if not session:
                raise HTTPException(status_code = 422)
        
        return StudySession(**row_to_dict(session))

    # 학습 세션을 db에 생성한다.(학습 시작)
    def save_session(self, user_id:str, session: StudySession) -> StudySession:
        with SessionLocal() as db:
            new_session = Session_db(
                id = session.id,
                user_id = user_id,
                subject_id = session.subject_id,
                subject = session.subject,
                avg_focus = session.avg_focus,
                start_time = session.start_time,
                end_time = session.end_time,
                created_at = session.created_at,
                updated_at = session.updated_at,
            )
            db.add(new_session)
            db.commit()
            db.refresh(new_session)
        return StudySession(**row_to_dict(new_session))
    
    # 학습 세션을 수정 (학습 종료)
    def update_session(self, user_id:str, session: StudySession) -> StudySession:
        with SessionLocal() as db:
            new_session = (
                db.query(Session_db)
                .filter(Session_db.user_id == user_id, Session_db.id == session.id).first()
            )
            if not new_session:
                raise HTTPException(status_code = 422)
            
            new_session.updated_at = session.updated_at
            new_session.avg_focus = session.avg_focus
            new_session.end_time = session.end_time

            db.add(new_session)
            db.commit()

            return StudySession(**row_to_dict(new_session))
            
    # StudyData 집중도 데이터 생성 (bulk insert)
    def save_data(self, user_id:str, datas: list[StudyData]) -> list[StudyData]:
        with SessionLocal() as db:
            new_datas = [
                {   # 직접 딕셔너리로 매핑
                    "id": data.id,
                    "session_id": data.session_id,
                    "ppg_value": data.ppg_value,
                    "focus_score": data.focus_score,
                    "time": data.time,
                    "created_at": data.created_at
                }
                for data in datas
            ]
            db.bulk_insert_mappings(Data_db, new_datas)  # 수정된 new_datas 사용
            db.commit()
            return datas

    # 학습 세션 삭제
    def delete_session(self, user_id:str, session_id: str):
        with SessionLocal() as db:
            session = db.query(Session_db).filter(Session_db.user_id == user_id, Session_db.id == session_id).first()

            if not session:
                raise HTTPException(status_code = 422)

            db.delete(session)
            db.commit()
    
     # 과목 조회
    def get_subjects(self, user_id:str) -> list[Subject]:
        with SessionLocal() as db:
            subjects = (
                db.query(SubjectDB)
                .filter(SubjectDB.user_id == user_id)
                .all()
            )

            if not subjects:
                return None
            
        return [Subject(**row_to_dict(subject)) for subject in subjects]

        
    # 과목 추가
    def save_subject(self, user_id:str, subject: Subject) -> Subject:
        with SessionLocal() as db:
            new_subject = SubjectDB(
                id = subject.id,
                user_id = subject.user_id,
                subject_name = subject.subject_name,
                created_at = subject.created_at
            )
            db.add(new_subject)
            db.commit()
            db.refresh(new_subject)
        return Subject(**row_to_dict(new_subject))

    # 과목 수정
    def update_subject(self, user_id:str, subject: Subject) -> Subject:
        with SessionLocal() as db:
            new_subject = (
                db.query(SubjectDB)
                .filter(SubjectDB.user_id == user_id, SubjectDB.id == subject.id)
                .first()
            )

            if not new_subject:
                raise HTTPException(status_code = 422)
            
            new_subject.subject_name = subject.subject_name
            db.add(new_subject)
            db.commit()

            return Subject(**row_to_dict(new_subject))

    # 과목 삭제
    def delete_subject(self, user_id:str, subject: Subject):
        with SessionLocal() as db:
            subject = (
                db.query(SubjectDB)
                .filter(SubjectDB.user_id == user_id, SubjectDB.id == subject.id)
                .first()
            )

            if not subject:
                return HTTPException(status_code = 422)

            db.delete(subject)
            db.commit()

    # 과목명으로 과목 조회
    def find_by_subject_name(self, user_id:str, subject_name:str) -> Subject:
        with SessionLocal() as db:
            subject = (
                db.query(SubjectDB)
                .filter(SubjectDB.user_id == user_id, SubjectDB.subject_name == subject_name)
                .first()
            )

            if not subject:
                raise HTTPException(status_code = 422)
        
        return Subject(**row_to_dict(subject))