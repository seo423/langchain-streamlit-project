from attr import dataclass
import streamlit as st
from langchain_core.messages.chat import ChatMessage
from langchain_teddynote import logging
from langchain_teddynote.messages import random_uuid
from modules.agent import create_agent_executor
from dotenv import load_dotenv
from modules.handler import stream_handler, format_search_result
from modules.tools import WebSearchTool

# API KEY 정보로드
load_dotenv()

# 프로젝트 이름
logging.langsmith("Perplexity")

st.title("Perplexity 💬")
st.markdown(
    "A Perplexity clone (https://www.perplexity.ai/) with web search capabilities powered by an LLM. It supports multi-turn conversations."
)

# 대화기록을 저장하기 위한 용도로 생성
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# ReAct Agent 초기화
if "react_agent" not in st.session_state:
    st.session_state["react_agent"] = None

# include_domains 초기화
if "include_domains" not in st.session_state:
    st.session_state["include_domains"] = []

# 사이드바 생성
with st.sidebar:
    # 초기화 버튼 생성
    clear_btn = st.button("Clear Conversation")

    # 모델 선택 메뉴
    selected_model = st.selectbox("Select an LLM", ["gpt-4o", "gpt-4o-mini"], index=0)

    # 검색 결과 개수 설정
    search_result_count = st.slider("Adjust the number of search results", min_value=1, max_value=10, value=3)

    # include_domains 설정
    st.subheader("Search Domain Settings")
    search_topic = st.selectbox("Search Topic", ["general", "news"], index=0)
    new_domain = st.text_input("Enter a Domain to Add")
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("Add Domain", key="add_domain"):
            if new_domain and new_domain not in st.session_state["include_domains"]:
                st.session_state["include_domains"].append(new_domain)

    # 현재 등록된 도메인 목록 표시
    st.write("Registered Domains:")
    for idx, domain in enumerate(st.session_state["include_domains"]):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.text(domain)
        with col2:
            if st.button("Delete", key=f"del_{idx}"):
                st.session_state["include_domains"].pop(idx)
                st.rerun()

    # 설정 버튼
    apply_btn = st.button("Apply Settings", type="primary")


@dataclass
class ChatMessageWithType:
    chat_message: ChatMessage
    msg_type: str
    tool_name: str


# 이전 대화를 출력
def print_messages():
    for message in st.session_state["messages"]:
        if message.msg_type == "text":
            st.chat_message(message.chat_message.role).write(  # 각 사용자와 agent의 대화가 출력됨
                message.chat_message.content
            )
        elif message.msg_type == "tool_result": # 도구 호출 결과를 보여줌. 즉, 검색 결과
            with st.expander(f"✅ {message.tool_name}"):
                st.markdown(message.chat_message.content)


# 새로운 메시지를 추가
def add_message(role, message, msg_type="text", tool_name=""):
    if msg_type == "text":
        st.session_state["messages"].append(
            ChatMessageWithType(
                chat_message=ChatMessage(role=role, content=message),
                msg_type="text",
                tool_name=tool_name,
            )
        )
    elif msg_type == "tool_result":
        st.session_state["messages"].append(
            ChatMessageWithType(
                chat_message=ChatMessage(
                    role="assistant", content=format_search_result(message)
                ),
                msg_type="tool_result",
                tool_name=tool_name,
            )
        )


# 초기화 버튼이 눌리면...
if clear_btn:
    st.session_state["messages"] = []
    st.session_state["thread_id"] = random_uuid()
# 이전 대화 기록 출력
print_messages()

# 사용자의 입력
user_input = st.chat_input("Ask me anything!")

# 경고 메시지를 띄우기 위한 빈 영역
warning_msg = st.empty()

# 설정 버튼이 눌리면...
if apply_btn:
    tool = WebSearchTool().create()
    tool.max_results = search_result_count
    tool.include_domains = st.session_state["include_domains"]
    tool.topic = search_topic
    st.session_state["react_agent"] = create_agent_executor(
        model_name=selected_model,
        tools=[tool],
    )
    st.session_state["thread_id"] = random_uuid()

# 만약에 사용자 입력이 들어오면...
if user_input:
    agent = st.session_state["react_agent"]
    # Config 설정

    if agent is not None:
        config = {"configurable": {"thread_id": st.session_state["thread_id"]}}
        # 사용자의 입력
        st.chat_message("user").write(user_input)

        with st.chat_message("assistant"):
            # 빈 공간(컨테이너)을 만들어서, 여기에 토큰을 스트리밍 출력한다.
            container = st.empty()

            ai_answer = ""

            # 최종답변과 검색한 결과를 보여주는 container반환, 도구 호출하면서 전달된 인자값, Agent답변
            #             Agent
            #               ↓
            #       web_search Tool 호출
            #               ↓
            #             검색 결과
            #               ↓
            #          Agent가 답변 생성
            container_messages, tool_args, agent_answer = stream_handler(container, agent,
                {
                    "messages": [
                        ("human", user_input),
                    ]
                },
                config,
            )

            # 대화기록을 저장한다.
            add_message("user", user_input)
            for tool_arg in tool_args:
                add_message(
                    "assistant",
                    tool_arg["tool_result"],
                    "tool_result",
                    tool_arg["tool_name"],
                )
            add_message("assistant", agent_answer)
    else:
        warning_msg.warning("Please complete the settings in the sidebar.")
