from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from dependency_injector.wiring import inject, Provide
from datetime import datetime
from typing import Annotated
from dataclasses import asdict

from common.auth import CurrentUser, get_current_user
from containers import Container
from study.application.study_service import StudyService


router = APIRouter(prefix="/study")

# 세션 파이단틱 응답 모델
class SessionResponse(BaseModel):
    id: str
    user_id: str
    subject_id: str | None
    subject: str | None
    avg_focus: float | None
    start_time: str
    end_time: str | None
    created_at: datetime
    updated_at: datetime

# 세션 생성 요청 대한 파이단틱 모델
class CreateSessionResponse(BaseModel):
    subject: str = Field(min_length=1, max_length=10)
    start_time: str = Field(min_length=1, max_length=30)

# POST /study/session/start (학습 세션 생성)
@router.post("/session/start", status_code = 201, response_model = SessionResponse)
@inject
def create_session(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    body: CreateSessionResponse,
    study_service: StudyService = Depends(Provide[Container.study_service])
):
    # if study_service is None:
    #     raise ValueError("study_service가 None입니다. 의존성 주입 확인 필요")
    
    # print("study_service가 정상적으로 주입되었습니다.")  # 여기서도 출력되는지 확인

    session = study_service.create_session(
        user_id = current_user.id,
        subject= body.subject,
        start_time = body.start_time,
    )

    response = asdict(session)
    return response

# 세션 종료 요청에 대한 파이단틱 모델
class CompleteSessionResponse(BaseModel):
    id: str = Field(min_length=1, max_length=36),
    avg_focus : float | None = None
    end_time: str = Field(min_length=1, max_length=30)

# POST /study/session/end (학습 세션 종료)
@router.post("/session/end", status_code = 201, response_model = SessionResponse)
@inject
def complete_session(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    body: CompleteSessionResponse,
    study_service: StudyService = Depends(Provide[Container.study_service])
):
    session = study_service.complete_session(
        id = body.id,
        user_id = current_user.id,
        end_time = body.end_time,
        avg_focus = body.avg_focus,
    )
    response = asdict(session)
    return session

# 데이터 파이단틱 응답 모델
class DataResponse(BaseModel):
    id: str
    session_id: str
    ppg_value: float
    focus_score: float
    time: str
    created_at: datetime

# 개별 데이터 항목에 대한 내부 모델 (단일 데이터)
class SingleData(BaseModel):
    ppg_value: float
    focus_score: float
    time: str = Field(min_length = 1, max_length = 36)

# 데이터 생성 요청에 대한 파이단틱 모델 (리스트 허용)
class CreateDataResponse(BaseModel):
    session_id: str = Field(min_length = 1, max_length = 36)
    datas: list[SingleData] = Field(..., min_items=1)

# POST /study/data (집중도 데이터 저장)
@router.post("/data", status_code = 201, response_model = list[DataResponse])
@inject
def create_data(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    body : CreateDataResponse,
    study_service: StudyService = Depends(Provide[Container.study_service])
):
    created_datas = study_service.create_data(
        session_id = body.session_id,
        user_id = current_user.id,
        datas = body.datas
    )

    return created_datas

# 세션 get 요청 응답 파이단틱 모델
class GetSessionResponse(BaseModel):
    total_count: int
    page: int
    sessions: list[SessionResponse]

# GET /study/session : 전체 세션 조회
@router.get("/session", response_model = GetSessionResponse)
@inject
def get_sessions(
    page: int = 1,
    items_per_page: int = 10,
    current_user: CurrentUser = Depends(get_current_user),
    study_service: StudyService = Depends(Provide[Container.study_service])
):
    total_count, sessions = study_service.get_sessions(
        user_id = current_user.id,
        page = page,
        items_per_page = items_per_page,
    )

    res_sessions = []
    for session in sessions:
        session_dict = asdict(session)
        res_sessions.append(session_dict)
    
    return {
        "total_count" : total_count,
        "page" : page,
        "sessions" : res_sessions,
    }

# 데이터 get 요청 응답 파이단틱 모델
class GetDataResponse(BaseModel):
    datas: list[DataResponse]

# GET /study/data/{session_id} : 특정 세션의 전체 데이터 조회
@router.get("/data/{session_id}", response_model=GetDataResponse)
@inject
def get_datas(
    session_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    study_service: StudyService = Depends(Provide[Container.study_service])
):
    datas = study_service.get_datas(
        user_id = current_user.id,
        session_id = session_id,
    )

    if datas is None:
        return {"datas": []}

    res_data = []
    for data in datas:
        data_dict = asdict(data)
        res_data.append(data_dict)
    
    return {
        "datas": res_data
    }

# DELETE /study/session/{session_id} : 특정 학습 세션 삭제
@router.delete("/session/{session_id}", status_code=204)
@inject
def delete_session(
    session_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    study_service: StudyService = Depends(Provide[Container.study_service])
):
    study_service.delete_session(
        user_id = current_user.id,
        session_id = session_id
    )

# 과목 파이단틱 응답 모델
class SubjectResponse(BaseModel):
    id: str
    user_id: str
    subject_name: str
    created_at: datetime

# 과목 생성 요청 파이단틱 모델
class CreateSubjectResponse(BaseModel):
    subject_name: str

# POST /study/subject (과목 생성)
@router.post("/subject", status_code = 201, response_model = SubjectResponse)
@inject
def create_subject(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    body: CreateSubjectResponse,
    study_service: StudyService = Depends(Provide[Container.study_service])
):
    subject = study_service.create_subject(
        user_id = current_user.id,
        subject_name = body.subject_name
    )

    response = asdict(subject)
    return response

# 과목 get 요청 응답 파이단틱
class GetSubjectResponse(BaseModel):
    subjects: list[SubjectResponse]

# get /study/subject (과목 조회)
@router.get("/subject", response_model = GetSubjectResponse)
@inject
def get_subjects(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    study_service: StudyService = Depends(Provide[Container.study_service])
):
    subjects = study_service.get_subjects(
        user_id = current_user.id
    )

    if subjects is None:
        return {"subjects": []}
    
    res_subject = []
    for subject in subjects:
        subject_dict = asdict(subject)
        res_subject.append(subject_dict)
    
    return {
        "subjects" : res_subject
    }
# 과목명 변경 파이단틱 모델
class UpdateSubjectName(BaseModel):
    id: str
    user_id: str
    subject_name: str
    created_at: datetime

# PUT /study/subject/{target_name}/{new_name} : 과목명 변경
@router.put("/subject/{target_name}/{new_name}", response_model=UpdateSubjectName)
@inject
def update_subject(
    target_name: str,
    new_name: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    study_service: StudyService = Depends(Provide[Container.study_service])
):
    subject = study_service.update_subject(
        user_id = current_user.id,
        target_name = target_name,
        new_name = new_name
    )

    response = asdict(subject)
    return response

# DELETE /subject/{subject_name} : 특정 과목 삭제
@router.delete("/subject/{subject_name}", status_code=204)
@inject
def delete_subject(
    subject_name: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    study_service: StudyService = Depends(Provide[Container.study_service])
):
    study_service.delete_subject(
        user_id = current_user.id,
        subject_name = subject_name
    )
