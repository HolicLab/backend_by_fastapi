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
    subject: str
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
    session = study_session.create_session(
        user_id = current_user.id,
        subject= body.subject,
        start_time = body.start_time,
    )

    response = asdict(session)

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
    user_id: str
    session_id: str
    ppg_value: float
    focus_score: float
    time: str
    created_at: datetime

# 데이터 생성 요청에 대한 파이단틱 모델
class CreateDataResponse(BaseModel):
    session_id: str = Field(min_length = 1, max_length = 36)
    ppg_value: float
    focus_score: float
    time: str = Field(min_length = 1, max_length = 36)

# POST /study/data (집중도 데이터 저장)
@router.post("/data", status_code = 201, response_model = DataResponse)
@inject
def create_data(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    body : CreateDataResponse,
    study_service: StudyService = Depends(Provide[Container.study_service])
):
    data = study_service.create_data(
        user_id = current_user.id,
        session_id = body.session_id,
        ppg_value = body.ppg_value,
        focus_score = body.focus_score,
        time = body.time
    )

    response = asdict(data)

    return response

# 세션 get 요청 응답 파이단틱 모델
class GetSessionResponse(BaseModel):
    total_count: int
    items_per_page: int
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