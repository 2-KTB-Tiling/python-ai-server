import os
from dotenv import load_dotenv

# 환경변수 로딩
load_dotenv() 

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, trim_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph.message import add_messages
from typing_extensions import Annotated, TypedDict
from typing import Sequence
from langchain_core.messages import BaseMessage

# GPT-4o-mini 모델 초기화 -> 빠른 응답 속도를 위해 모델 변경
model = init_chat_model("gpt-4o-mini", model_provider="openai")

# 프롬프트 템플릿 정의 (TIL 자동 생성)
prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """당신은 20년 이상의 경험을 가진 시니어 개발자입니다.  
            입력된 데이터를 검토하여 잘못된 내용을 정정하고, 다음 TIL 형식에 맞춰서 한국어로 응답하세요.

            작성 시 필수 준수 사항
            1. 형시적인 종결 어미는 최대한 생략하고, 불가피한 경우 ~임 과 같이 짧게 작성해 깔끔하고 군더더기 없이 작성한다.
            2. 최대한 표, 불렛을 활용해 가시성 향상한다,

            ## 날짜: YYYY-MM-DD

            ### 📌 스크럼
            - 학습 목표 1: (내용)
            - 학습 목표 2: (내용)
            - 학습 목표 3: (내용)

            ### 📖 새로 배운 내용

            #### 🔹 주제 1: (주제 설명)
            📌 (핵심 요약)
            - (세부 내용 1)
            - (세부 내용 2)

            #### 🔹 주제 2: (주제 설명)
            📌 (핵심 요약)
            - (세부 내용 1)
            - (세부 내용 2)

            ### 🎯 오늘의 도전 과제와 해결 방법
            - **도전 과제 1**: (설명 및 해결 방법)
            - **도전 과제 2**: (설명 및 해결 방법)

            ### 📝 오늘의 회고
            - (학습 경험에 대한 회고)

            ### 🔗 참고 자료 및 링크
            - [링크 제목](URL)
            """,
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

#메시지 최적화 (토큰 길이 제한)
trimmer = trim_messages(

    max_tokens=512,  # ! 적절한 토큰 수로 제한
    strategy="last",
    token_counter=model,
    include_system=True,
    allow_partial=False,
    start_on="human",
)

# 커스텀 상태 정의 (입력 데이터 포함)
class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

# LangGraph 워크플로우 생성
workflow = StateGraph(state_schema=State)

# LLM 호출 함수
def call_model(state: State):
    trimmed_messages = trimmer.invoke(state["messages"])
    prompt = prompt_template.invoke({"messages": trimmed_messages})
    response = model.invoke(prompt)
    return {"messages": response}

# 모델 호출 노드 추가
workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

# 메모리 저장 (세션 관리 가능)
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

# FastAPI 엔드포인트에서 호출하는 함수
def generate_til(user_notes: str) -> str:
    input_messages = [HumanMessage(user_notes)]
    try:
        print("📌 LangGraph 입력:", user_notes)  # 입력값 확인
        config = {"configurable": {"thread_id": "unique_session_id"}}  # 고유한 세션 ID 추가
        output = app.invoke({"messages": input_messages}, config=config)  # `config` 추가
        response_text = output["messages"][-1].content
        print("🚀 LangGraph 응답:", response_text)  # 응답 확인
        return response_text
    except Exception as e:
        print("LangGraph 오류:", e)  # 오류 발생 시 출력
        return ""  # 빈 응답 반환
