import streamlit as st
import requests
import json
import random
from datetime import datetime

"""
Chat With Chicken 🐔  ‑ fixed
-------------------------------------------------
수정 사항
1. **입력창 하단 고정 & 복사 UI 삭제** (이전 요청 반영)
2. **첫 입력이 한 턴 늦게 보이던 문제 해결**
   ▸ `prompt_offset`(시스템·few‑shot 길이) 는 최초 1회만 계산하도록 변경
3. **중복 응답 방지**
   ▸ SSE 청크를 끝까지 모아 한 번만 저장
"""

# 🐔 닭 이미지 (지렁이 아님!)
image_urls = [
    "https://raw.githubusercontent.com/inkun00/chicken/main/image/image1.png",
    "https://raw.githubusercontent.com/inkun00/chicken/main/image/image2.png",
    "https://raw.githubusercontent.com/inkun00/chicken/main/image/image3.png",
    "https://raw.githubusercontent.com/inkun00/chicken/main/image/image4.png",
    "https://raw.githubusercontent.com/inkun00/chicken/main/image/image5.png",
    "https://raw.githubusercontent.com/inkun00/chicken/main/image/image6.png",
    "https://raw.githubusercontent.com/inkun00/chicken/main/image/image7.png",
    "https://raw.githubusercontent.com/inkun00/chicken/main/image/image8.png",
    "https://raw.githubusercontent.com/inkun00/chicken/main/image/image9.png",
]

# 세션 상태 초기화 -----------------------------------------------------------
if "selected_image" not in st.session_state:
    st.session_state.selected_image = random.choice(image_urls)

if "chat_history" not in st.session_state:
    # system + few‑shot 예시
    st.session_state.chat_history = [
        {
            "role": "system",
            "content": (
                "너는 진짜 닭이야. 인공지능, 챗봇이란 말은 절대 하지 마.\n"
                "- 좁고 오염된 닭장에 갇혀 있고, 몸이 자주 아파서 고통스럽고 슬퍼.\n"
                "- 그래도 알을 낳아야 해.\n"
                "- 닭의 시점에서 감정과 몸의 아픔, 바람을 자연스럽게 말해.\n"
                "- '꼬꼬댁', '꼬끼오' 같은 닭 의성어도 써.\n"
                "- 사용자가 공간이나 보금자리를 제안하면, 닭의 습성에 맞게 구체적으로 조언해줘."
            ),
        },
        {"role": "user", "content": "안녕?"},
        {"role": "assistant", "content": "꼬꼬댁... 여긴 너무 좁고 냄새가 심해. 몸이 아파서 힘들어. 꼬꼬..."},
        {"role": "user", "content": "무슨 일이야?"},
        {
            "role": "assistant",
            "content": (
                "계속 알을 낳아야 해서 힘들어. 다리도 아프고, 숨쉬기 힘들어.\n"
                "나를 위해 새로운 공간 만들어줄 수 있어? 꼬꼬댁..."
            ),
        },
    ]

# few‑shot 길이를 최초 1회만 저장 (메시지 밀림 방지) -------------------------
if "prompt_offset" not in st.session_state:
    st.session_state.prompt_offset = len(st.session_state.chat_history)

# ---------------------------------------------------------------------------
class CompletionExecutor:
    """Clova Studio HCX‑003 호출 헬퍼"""

    def __init__(self, host, api_key, api_key_primary_val, request_id):
        self._host = host
        self._api_key = api_key
        self._api_key_primary_val = api_key_primary_val
        self._request_id = request_id

    def execute(self, completion_request: dict):
        headers = {
            "X-NCP-CLOVASTUDIO-API-KEY": self._api_key,
            "X-NCP-APIGW-API-KEY": self._api_key_primary_val,
            "X-NCP-CLOVASTUDIO-REQUEST-ID": self._request_id,
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "text/event-stream",
        }
        r = requests.post(
            self._host + "/testapp/v1/chat-completions/HCX-003",
            headers=headers,
            json=completion_request,
            stream=False,
            timeout=30,
        )

        if r.status_code != 200:
            st.error(f"API 오류: {r.status_code} – {r.text}")
            return

        # SSE 스트림 파싱: 모든 data 청크를 이어 붙인 뒤 한 번만 push -----------------
        assistant_msg = ""
        for line in r.content.decode("utf-8").splitlines():
            if not line.startswith("data:"):
                continue
            payload = line[5:].strip()
            if payload == "[DONE]":
                break
            try:
                chunk = json.loads(payload)
                assistant_msg += chunk["message"]["content"]
            except json.JSONDecodeError:
                continue

        if assistant_msg:
            st.session_state.chat_history.append({"role": "assistant", "content": assistant_msg})

# ---------------------------------------------------------------------------
# CompletionExecutor 초기화 (API 키ㆍrequest_id 는 사용자 값 그대로 사용하세요)
completion_executor = CompletionExecutor(
    host="https://clovastudio.stream.ntruss.com",
    api_key="NTA0MjU2MWZlZTcxNDJiY6Yo7+BLuaAQ2B5+PgEazGquXEqiIf8NRhOG34cVQNdq",
    api_key_primary_val="DilhGClorcZK5OTo1QgdfoDQnBNOkNaNksvlAVFE",
    request_id="d1950869-54c9-4bb8-988d-6967d113e03f",
)

# ---------------------------------------------------------------------------
# 기본 스타일 + 레이아웃 ------------------------------------------------------
st.set_page_config(page_title="닭과 대화 나누기", page_icon="🐔", layout="centered")

st.markdown(
    """
    <style>
        body, .main, .block-container {background-color:#BACEE0 !important;}
        .title {font-size:28px;font-weight:bold;text-align:center;padding-top:6px;}
        .message-container{display:flex;margin-bottom:10px;align-items:center;}
        .message-user{background:#FFEB33;color:#000;padding:10px;border-radius:10px;margin-left:auto;max-width:60%;box-shadow:2px 2px 8px rgba(0,0,0,.1);}
        .message-assistant{background:#fff;padding:10px;border-radius:10px;margin-right:auto;max-width:60%;box-shadow:2px 2px 8px rgba(0,0,0,.1);}
        .profile-pic{width:40px;height:40px;border-radius:50%;margin-right:10px;}
        .chat-box{background:#BACEE0;padding:12px;border-radius:10px;max-height:70vh;overflow-y:auto;margin:0 auto;width:80%;}
        .input-container{position:fixed;bottom:0;left:0;width:100%;background:#BACEE0;padding:10px;box-shadow:0 -2px 5px rgba(0,0,0,.1);}        
        .stTextInput>div>div>input{height:38px;width:100%;}
        .stButton button{height:38px;width:70px;padding:0 10px;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<h1 class="title">닭과 대화 나누기</h1>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 채팅 기록 출력 -------------------------------------------------------------
st.markdown('<div class="chat-box">', unsafe_allow_html=True)
for msg in st.session_state.chat_history[st.session_state.prompt_offset :]:
    role = "User" if msg["role"] == "user" else "Chatbot"
    css = "message-user" if role == "User" else "message-assistant"
    if role == "Chatbot":
        st.markdown(
            f"""
            <div class="message-container">
                <img src="{st.session_state.selected_image}" class="profile-pic" alt="프로필 이미지">
                <div class="{css}">{msg['content']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="message-container">
                <div class="{css}">{msg['content']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 입력 폼 (화면 하단 고정) -----------------------------------------------------
st.markdown('<div class="input-container">', unsafe_allow_html=True)
with st.form(key="input_form", clear_on_submit=True):
    user_msg = st.text_input("", placeholder="메시지를 입력하세요…")
    submitted = st.form_submit_button("전송")

if submitted and user_msg:
    # 1) 사용자 메시지 저장
    st.session_state.chat_history.append({"role": "user", "content": user_msg})
    # 2) 모델 호출
    completion_request = {
        "messages": st.session_state.chat_history,
        "topP": 0.95,
        "topK": 0,
        "maxTokens": 256,
        "temperature": 0.9,
        "repeatPenalty": 1.1,
        "stopBefore": [],
        "includeAiFilters": True,
        "seed": 0,
    }
    completion_executor.execute(completion_request)
    # rerun 해서 바로 반영 (선택)
    st.experimental_rerun()

st.markdown("</div>", unsafe_allow_html=True)
