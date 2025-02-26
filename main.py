from fastapi import FastAPI
from pydantic import BaseModel
from til_generator import generate_til  # LangChain 함수 가져오기

app = FastAPI()

# 기본 엔드포인트 추가 (API 상태 확인용)
@app.get("/")
def home():
    return {"message": "Welcome to the TIL Generator API"}

# 요청 데이터 모델 정의
class TILRequest(BaseModel):
    user_notes: str  # 입력 데이터 필드

# TIL 자동 생성 API
@app.post("/generate_til")
def generate_til_api(request: TILRequest):
    til_text = generate_til(request.user_notes)
    return {"user_notes": request.user_notes, "til": til_text}
