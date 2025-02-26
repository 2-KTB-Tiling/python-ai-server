from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field
from typing import Optional, List, Dict

from til_generator import generate_til  # 기존 LLM 호출 함수

app = FastAPI()

# 1. 요청 데이터 모델 정의 (명세서에 맞춤)
class ConvertRequest(BaseModel):
    content: str = Field(..., title="TIL 내용", description="사용자가 학습한 TIL 내용")
    image: Optional[str] = Field(None, title="이미지", description="64인코딩된 이미지 (선택 사항)")

class EnhanceRequest(BaseModel):
    content: str = Field(..., title="TIL 내용", description="사용자가 학습한 TIL 내용")
    language: str = Field(..., title="언어", description="ko 또는 en")
    include_images: bool = Field(..., title="이미지 포함 여부", description="이미지 추천 여부")

# 2. LLM을 이용한 Markdown 변환 API (TIL 변환)
@app.post("/api/v1/convert")
def convert_til(request: ConvertRequest, authorization: str = Header(...)):
    """ 사용자가 작성한 TIL을 Markdown으로 변환하는 API """
    try:
        # 🔹 인증 헤더 검증
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=400, detail={"message": "invalid_request", "data": None})

        # 🔹 LLM을 이용하여 Markdown 변환
        markdown_text = generate_til(request.content)
        response_data = {
            "message": "convert_success",
            "data": {"markdown": markdown_text}
        }
        return response_data

    except Exception as e:
        return HTTPException(status_code=500, detail={"message": "llm_server_error", "data": None})


# # 3. 키워드 추출 및 이미지 삽입 API (현재 동작 x)
# @app.post("/api/v1/enhance")
# def enhance_til(request: EnhanceRequest, authorization: str = Header(...)):
#     """ TIL 내용을 분석하여 키워드 추출 및 적절한 이미지 삽입 요청 """
#     try:
#         # 인증 헤더 검증
#         if not authorization.startswith("Bearer "):
#             raise HTTPException(status_code=400, detail={"message": "invalid_request", "data": None})

#         # 키워드 추출 (예제 데이터)
#         keywords = ["Nest.js", "백엔드", "TypeScript"] if "Nest.js" in request.content else ["키워드 없음"]

#         # 이미지 추천 (예제 데이터)
#         suggested_images = [{"keyword": "Nest.js", "url": "https://example.com/nestjs.jpg"}] if request.include_images else []

#         response_data = {
#             "message": "enhance_success",
#             "data": {
#                 "keywords": keywords,
#                 "suggested_images": suggested_images
#             }
#         }
#         return response_data

#     except Exception as e:
#         return HTTPException(status_code=500, detail={"message": "llm_server_error", "data": None})
