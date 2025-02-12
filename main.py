from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from user.interface.controllers.user_controller import router as user_routers
from note.interface.controllers.note_controller import router as note_routers
from middlewares import create_middlewares
from fastapi import FastAPI
from containers import Container
import uvicorn

app = FastAPI()
app.container = Container()
app.include_router(user_routers)
# app.include_router(note_routers)

create_middlewares(app)

# 422 에러를 400에러로 변환
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    return JSONResponse(
        status_code=400,
        content=exc.errors(),
    )

# @app.get("/")
# def hello():
#     return {"Hello": "FastAPI"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
