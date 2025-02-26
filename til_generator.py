import os
from dotenv import load_dotenv

from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# .env 파일 로드
load_dotenv()

# OpenAI API 키 가져오기
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# LLM 설정 (GPT-4 사용)
llm = ChatOpenAI(model_name="gpt-4-turbo", openai_api_key=OPENAI_API_KEY)

# 프롬프트 템플릿 설정
prompt_template = PromptTemplate(
    input_variables=["user_notes"],  # 변경된 변수명
    template="사용자가 작성한 노트 '{user_notes}'을(를) 기반으로 TIL을 작성해줘."
)

# LangChain Chain 생성
til_chain = LLMChain(llm=llm, prompt=prompt_template)

# 함수: TIL 생성 요청
def generate_til(user_notes: str) -> str:
    response = til_chain.run(user_notes=user_notes)
    return response
