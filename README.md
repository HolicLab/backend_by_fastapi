### 회원가입, 로그인
**POST** /users : 유저 생성
**GET** /users : 유저 목록 조회
**DELETE** /users : 유저 삭제(회원 탈퇴) 
**POST** /users/login : 로그인
**PUT** /users/{user_id} : 유저 정보 업데이트
**GET** /users/me : 로그인한 사용자 정보
### 학습 데이터
**POST** /study/session/start : 학습 세션 생성
**POST** /study/session/end : 학습 세션 종료
**POST** /study/data : 집중도 데이터 저장
**GET** /study/session : 전체 세션 조회
**GET** /study/data/{session_id} : 특정 세션의 전체 데이터 조회
**DELETE** /study/session/{session_id} : 학습 세션 삭제


### 데이터 모델
#### User
| Column     | Type        | Description | Constraint |
| ---------- | ----------- | ----------- | ---------- |
| id         | ULID(36)    | 사용자 ID      | PK         |
| name       | VARCHAR(32) | 이름          |            |
| email      | VARCHAR(64) | 이메일, 아이디    | Unique     |
| password   | VARCHAR(64) | 비밀번호        |            |
| created_at | TIMESTAMP   | 생성시간        |            |
| updated_at | TIMESTAMP   | 수정시간        |            |

#### StudySession

| Column     | Type        | Description | Constraint          |
| ---------- | ----------- | ----------- | ------------------- |
| id         | ULID(36)    | 세션 고유 ID    | PK                  |
| user_id    | ULID(36)    | 사용자 ID      | on_delete = CASCADE |
| subject    | VARCHAR(10) | 과목명         |                     |
| avg_focus  | Float       | 평균 집중도      |                     |
| start_time | VARCHAR(30) | 학습 시작 시간    |                     |
| end_time   | VARCHAR(30) | 학습 종료 시간    |                     |
| created_at | TIMESTAMP   | 생성시간        |                     |
| updated_at | TIMESTAMP   | 수정시간        |                     |

#### StudyData

| Column      | Type        | Description   | Constraint          |
| ----------- | ----------- | ------------- | ------------------- |
| id          | ULID(36)    | 데이터 고유 ID     | PK                  |
| user_id     | ULID(36)    | 사용자 ID        | on_delete = CASCADE |
| session_id  | ULID(36)    | 데이터가 속한 세션 ID | on_delete = CASCADE |
| ppg_value   | FLOAT       | ppg값          |                     |
| focus_score | FLOAT       | 집중도           |                     |
| time        | VARCHAR(30) | 집중도 측정 시간     |                     |
| created_at  | TIMESTAMP   | 생성시간          |                     |
