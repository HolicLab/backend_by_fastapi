from fastapi import HTTPException
from sqlalchemy.future import select
from sqlalchemy.sql import func
from database import AsyncSessionLocal
from study.domain.study import StudySession, StudyData, Subject
from study.domain.repository.study_repo import IStudy
from study.infra.db_models.study_db import StudySession as Session_db
from study.infra.db_models.study_db import StudyData as Data_db
from study.infra.db_models.study_db import Subject as SubjectDB
from utils.db_utils import row_to_dict

class StudyRepository(IStudy):
    # db에서 학습 세션을 조회
    async def get_sessions(self, user_id: str, page: int, items_per_page:int) -> tuple[int, list[StudySession]]:
        async with AsyncSessionLocal() as db:
            total_count_query = select(func.count()).select_from(Session_db).where(Session_db.user_id == user_id)
            total_count_result = await db.execute(total_count_query)
            total_count = total_count_result.scalar()
            
            query = (
                select(Session_db)
                .where(Session_db.user_id == user_id)
                .offset((page - 1) * items_per_page)
                .limit(items_per_page)
            )

            result = await db.execute(query)
            sessions = result.scalars().all()
        
        return total_count, [StudySession(**row_to_dict(session)) for session in sessions]
    
    async def get_session_dates(self, user_id:str) -> tuple[int, list[str]]:
        async with AsyncSessionLocal() as db:
            query = (
                select(func.date(Session_db.created_at))
                .where(Session_db.user_id == user_id)
            )
            
            result = await db.execute(query)
            dates = result.scalars().all()
            
            res_date = []
            for date in dates:
                if str(date) in res_date:
                    continue
                res_date.append(str(date))
        
        return len(res_date), list(res_date)

    async def get_sessions_by_date(self, user_id: str, date: str) -> tuple[int, list[StudySession]]:
        async with AsyncSessionLocal() as db:
            query = (
                select(Session_db)
                .where(
                    Session_db.user_id == user_id,
                    func.date(Session_db.created_at) == date
                )
            )
            
            result = await db.execute(query)
            sessions = result.scalars().all()
        
        return len(sessions), [StudySession(**row_to_dict(session)) for session in sessions]

    # StudyData db에서 세션 id에 해당하는 집중도 데이터 조회
    async def find_datas_by_session_id(self, user_id: str, session_id: str) -> list[StudyData]:
        async with AsyncSessionLocal() as db:
            query = (
                select(Data_db)
                .join(Session_db)
                .where(Session_db.user_id == user_id, Data_db.session_id == session_id)
            )
            result = await db.execute(query)
            datas = result.scalars().all()
            if not datas:
                return []
        
        return [StudyData(**row_to_dict(data)) for data in datas]

    # db에서 학습 세션을 조회 
    async def find_session_by_id(self, user_id: str, session_id: str) -> StudySession:
        async with AsyncSessionLocal() as db:
            query = (
                select(Session_db).where(Session_db.user_id == user_id, Session_db.id == session_id)
            )
            result = await db.execute(query)
            session = result.scalars().first()
            if not session:
                raise HTTPException(status_code = 422)
        
        return StudySession(**row_to_dict(session))

    # 학습 세션을 db에 생성한다.(학습 시작)
    async def save_session(self, user_id:str, session: StudySession) -> StudySession:
        async with AsyncSessionLocal() as db:
            new_session = Session_db(
                id = session.id,
                user_id = user_id,
                subject_id = session.subject_id,
                subject = session.subject,
                avg_focus = session.avg_focus,
                ai_avg_focus = session.ai_avg_focus,
                start_time = session.start_time,
                end_time = session.end_time,
                created_at = session.created_at,
                updated_at = session.updated_at,
            )
            db.add(new_session)
            await db.commit()
            await db.refresh(new_session)
        return StudySession(**row_to_dict(new_session))
    
    # 학습 세션을 수정 (학습 종료)
    async def update_session(self, user_id:str, session: StudySession) -> StudySession:
        async with AsyncSessionLocal() as db:
            query = select(Session_db).where(Session_db.user_id == user_id, Session_db.id == session.id)
            result = await db.execute(query)
            new_session = result.scalars().first()

            if not new_session:
                raise HTTPException(status_code = 422)
            
            new_session.updated_at = session.updated_at
            new_session.avg_focus = session.avg_focus
            new_session.ai_avg_focus = session.ai_avg_focus
            new_session.end_time = session.end_time

            await db.commit()

        return StudySession(**row_to_dict(new_session))
            
    # StudyData 집중도 데이터 생성 (bulk insert)
    async def save_data(self, user_id:str, datas: list[StudyData]) -> list[StudyData]:
        async with AsyncSessionLocal() as db:
            new_datas = [
                Data_db(   
                    id = data.id,
                    session_id = data.session_id,
                    ppg_value = data.ppg_value,
                    focus_score = data.focus_score,
                    time = data.time,
                    created_at = data.created_at
                )
                for data in datas
            ]
            db.add_all(new_datas)
            await db.commit()

        return datas

    # 학습 세션 삭제
    async def delete_session(self, user_id:str, session_id: str):
        async with AsyncSessionLocal() as db:
            query = select(Session_db).where(Session_db.user_id == user_id, Session_db.id == session_id)
            result = await db.execute(query)
            session = result.scalars().first()

            if not session:
                raise HTTPException(status_code = 422)

            await db.delete(session)
            await db.commit()
    
     # 과목 조회
    async def get_subjects(self, user_id:str) -> list[Subject]:
        async with AsyncSessionLocal() as db:
            query = select(SubjectDB).where(SubjectDB.user_id == user_id)
            result = await db.execute(query)
            subjects = result.scalars().all()

            if not subjects:
                return None
            
        return [Subject(**row_to_dict(subject)) for subject in subjects]

        
    # 과목 추가
    async def save_subject(self, user_id:str, subject: Subject) -> Subject:
        async with AsyncSessionLocal() as db:
            new_subject = SubjectDB(
                id = subject.id,
                user_id = subject.user_id,
                subject_name = subject.subject_name,
                created_at = subject.created_at,
            )
            db.add(new_subject)
            await db.commit()
            await db.refresh(new_subject)

        return Subject(**row_to_dict(new_subject))

    # 과목 수정
    async def update_subject(self, user_id:str, subject: Subject) -> Subject:
        async with AsyncSessionLocal() as db:
            query = select(SubjectDB).where(SubjectDB.user_id == user_id, SubjectDB.id == subject.id)
            result = await db.execute(query)
            new_subject = result.scalars().first()

            if not new_subject:
                raise HTTPException(status_code = 422)
            
            new_subject.subject_name = subject.subject_name
            await db.commit()

        return Subject(**row_to_dict(new_subject))

    # 과목 삭제
    async def delete_subject(self, user_id:str, subject: Subject):
        async with AsyncSessionLocal() as db:
            query = select(SubjectDB).where(SubjectDB.user_id == user_id, SubjectDB.id == subject.id)
            result = await db.execute(query)
            subject = result.scalars().first()

            if not subject:
                raise HTTPException(status_code = 422)

            await db.delete(subject)
            await db.commit()

    # 과목명으로 과목 조회
    async def find_by_subject_name(self, user_id:str, subject_name:str) -> Subject:
        async with AsyncSessionLocal() as db:
            query = select(SubjectDB).where(SubjectDB.user_id == user_id, SubjectDB.subject_name == subject_name)
            result = await db.execute(query)
            subject = result.scalars().first()

            if not subject:
                raise HTTPException(status_code = 422)
        
        return Subject(**row_to_dict(subject))
