import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field
from typing import Optional
from app.til_generator import generate_til  # LLM 호출 함수
import asyncio

# `.env` 파일 로드
load_dotenv()

# 환경 변수 가져오기
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# 요청 데이터 모델 정의
class ConvertRequest(BaseModel):
    content: str = Field(..., title="TIL 내용", description="사용자가 학습한 TIL 내용")
    image: Optional[str] = Field(None, title="이미지", description="64인코딩된 이미지 (선택 사항)")

# LLM을 이용한 Markdown 변환 API
@app.post("/api/v1/summation")
async def convert_til(request: ConvertRequest, authorization: str = Header(...)):
    """ 사용자가 작성한 TIL을 Markdown으로 변환하는 API """
    try:
        # 인증 헤더 검증
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=400, detail={"message": "invalid_request", "data": None})

        # 환경 변수 확인
        if not OPENAI_API_KEY:
            raise HTTPException(status_code=500, detail={"message": "missing_openai_key", "data": None})

        # LLM을 이용하여 Markdown 변환
        markdown_text = await generate_til(request.content)

        return {"message": "convert_success", "data": {"markdown": markdown_text}}

    except HTTPException as e:
        raise e  

    except Exception as e:
        print(f"[ERROR] {e}")
        raise HTTPException(status_code=500, detail={"message": "llm_server_error", "data": None})