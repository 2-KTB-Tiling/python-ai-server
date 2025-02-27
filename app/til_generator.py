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

# 환경 변수 로드
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# GPT-4o 모델 초기화
model = init_chat_model(
    "gpt-4o-mini",
    model_provider="openai",
    temperature=0.3,  # 창의성 줄이고, 더 명확한 응답 유도
    max_tokens=1024   # 응답 길이 제한
)

# 역할(Role) 정의
ROLE_DESCRIPTION = """
당신은 20년 이상의 경력을 가진 시니어 개발자입니다.  
사용자가 제공한 학습 노트를 기반으로 **최적화된 Markdown 형식의 TIL**을 작성하는 역할을 합니다.
"""

# 응답 스타일(Response Style) 설정
RESPONSE_STYLE = """
- **전문적이면서도 이해하기 쉽게 작성하세요.**  
- **Markdown 형식을 엄격하게 준수하세요.**  
- **사용자의 원래 표현을 살리되, 가독성을 높이도록 개선하세요.**  
- **불필요한 내용을 제거하고, 핵심 내용을 강조하세요.**  
"""

# 규칙(Rules) 정의
RULES = """
- 📌 **반드시 아래 형식의 Markdown으로 작성할 것**:
## 날짜: YYYY-MM-DD  # 설명: 사용자에게 입력받은 날짜 및 요일을 넣어주되, (월)과 같이 공백 없이 출력할 것.
- **날짜 형식을 유지하며, 괄호()와 요일 사이에 공백을 추가하지 마세요.**

### 📌 스크럼
- 학습 목표 1: (내용)
- 학습 목표 2: (내용)
- 학습 목표 3: (내용)

### 📖 새로 배운 내용

#### 주제 1: (주제 설명)
📌 (핵심 요약)
- (세부 내용 1)
- (세부 내용 2)

#### 주제 2: (주제 설명)
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

- **Markdown 개행(`"  \n"`)을 지켜야 합니다.**  
- **이전 대화를 참고하여 중복을 줄이고 부족한 내용을 보완하세요.**  
- **학습 목표와 해결 방법을 명확하게 정리하세요.**  
- **유용한 추가 정보를 제공하세요.**  
"""

# 4️지시문(Prompt Instructions)
PROMPT_INSTRUCTIONS = """
아래 사용자의 학습 노트를 기반으로 위의 역할, 응답 스타일, 규칙을 준수하여 최적의 TIL을 작성하세요.  
"""

# 최종 프롬프트 조립
prompt_template = ChatPromptTemplate.from_messages(
  [
      ("system", ROLE_DESCRIPTION),
      ("system", RESPONSE_STYLE),
      ("system", RULES),
      ("system", PROMPT_INSTRUCTIONS),
      MessagesPlaceholder(variable_name="messages"),
  ]
)

# 메시지 최적화 (토큰 길이 제한)
trimmer = trim_messages(
  max_tokens=512,
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

# LLM 호출 함수 (성능 최적화 적용)
def call_model(state: State):
    trimmed_messages = trimmer.invoke(state["messages"])
    prompt = prompt_template.invoke({"messages": trimmed_messages})
    response = model.invoke(prompt)
    return {"messages": response}

# 모델 호출 노드 추가
workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

# LangGraph 메모리 저장 (세션 관리 가능, 성능 최적화 적용)
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

# FastAPI 엔드포인트에서 호출하는 함수 (비동기 처리 추가)
async def generate_til(user_notes: str) -> str:
    input_messages = [HumanMessage(user_notes)]
    try:
        print("📌 LangGraph 입력:", user_notes)
        config = {"configurable": {"thread_id": "static_session"}}  # 세션 재사용하여 성능 최적화
        output = app.invoke({"messages": input_messages}, config=config)
        response_text = output["messages"][-1].content.replace("\n", "  \n")  # GitHub 호환 개행 처리
        print("🚀 LangGraph 응답:", response_text)
        return response_text
    except Exception as e:
        print("LangGraph 오류:", e)
        return ""