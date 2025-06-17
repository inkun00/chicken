import streamlit as st
import requests
import json
import random
from datetime import datetime

"""
Chat With Chicken 🐔
-------------------------------------------------
• 입력창 하단 고정, 복사 UI 제거
• 첫 메시지 지연·중복 응답 버그 해결
• `st.experimental_rerun()` → **`st.rerun()`** 로 업데이트 (Streamlit ≥ 1.32)
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

# --- 세션 상태 초기화 ------------------------------------------------------

if "selected_image" not in st.session_state:
    st.session_state.selected_image = random.choice(image_urls)

if "chat_history" not in st.session_state:
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
            "content": "계속 알을 낳아야 해서 힘들어. 다리도 아프고, 숨쉬기 힘들어. 나를 위해 새로운 공간 만들어줄 수 있어? 꼬꼬댁...",
        },
    ]

# 화면에 실제로 보여줄 첫 인덱스 (시스템‧few‑shot 제외)
if "prompt_offset" not in st.session_state:
    st.session_state.prompt_offset = len(st.session_state.chat_history)

# --- API 래퍼 --------------------------------------------------------------

class CompletionExecutor:
    def __init__(self, host, api_key, api_key_primary_val, request_id):
        self._host = host
        self._api_key = api_key
        self._api_key_primary_val = api_key_primary_val
        self._request_id = request_id

    def execute(self, completion_request):
        headers = {
            "X-NCP-CLOVASTUDIO-API-KEY": self._api_key,
            "X-NCP-APIGW-API-KEY": self._api_key_primary_val,
            "X-NCP-CLOVASTUDIO-REQUEST-ID": self._request_id,
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "text/event-stream",
        }

        r = requests.post(
            f"{self._host}/testapp/v1/chat-completions/HCX-003",
            headers=headers,
            json=completion_request,
            stream=True,  # 실시간 청크 수신
            timeout=30,
        )

        if r.status_code != 200:
            st.error(f"API 오류: {r.status_code} - {r.text}")
            return

        assistant_msg = ""
        for line in r.iter_lines(decode_unicode=True):
            if not line or not line.startswith("data:"):
                continue
            json_data = line[5:].strip()
            if json_data == "[DONE]":
                break
            try:
                payload = json.loads(json_data)
                assistant_msg += payload["message"]["content"]
            except Exception as e:
                st.error(f"응답 파싱 오류: {e}")

        if assistant_msg:
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": assistant_msg,
            })
            st.rerun()  # 즉시 UI 업데이트 (Streamlit ≥ 1.32)

# CompletionExecutor 초기화 (아래 키는 예시, 본인 키 사용)
completion_executor = CompletionExecutor(
    host="https://clovastudio.stream.ntruss.com",
    api_key="NTA0MjU2MWZlZTcxNDJiY6Yo7+BLuaAQ2B5+PgEazGquXEqiIf8NRhOG34cVQNdq",
    api_key_primary_val="DilhGClorcZK5OTo1QgdfoDQnBNOkNaNksvlAVFE",
    request_id="d1950869-54c9-4bb8-988d-6967d113e03f",
)

# --- UI 레이아웃 -----------------------------------------------------------

st.set_page_config(page_title="닭과 대화 나누기", page_icon="🐔", layout="centered")

st.markdown(
    """
    <style>
    body, .main, .block-container { background-color: #BACEE0 !important; }
    .title { font-size: 28px; font-weight: bold; text-align: center; padding-top: 10px; }
    .message-container { display: flex; margin-bottom: 10px; align-items: center; }
    .message-user { background-color: #FFEB33; color: black; text-align: right; padding: 10px; border-radius: 10px; margin-left: auto; max-width: 60%; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    .message-assistant { background-color: #FFFFFF; text-align: left; padding: 10px; border-radius: 10px; margin-right: auto; max-width: 60%; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    .profile-pic { width: 40px; height: 40px; border-radius: 50%; margin-right: 10px; }
    .chat-box { background-color: #BACEE0; border: none; padding: 20px; border-radius: 10px; max-height: 500px; overflow-y: scroll; margin: 0 auto; width: 80%; }
    .stTextInput > div > div > input { height: 38px; width: 100%; }
    .stButton button { height: 38px !important; width: 70px !important; padding: 0 10px; margin-right: 0 !important; }
    .input-container { position: fixed; bottom: 0; left: 0; width: 100%; background-color: #BACEE0; padding: 10px 0; box-shadow: 0 -2px 5px rgba(0,0,0,0.1); }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<h1 class="title">닭과 대화 나누기</h1>', unsafe_allow_html=True)

# --- 채팅 출력 -------------------------------------------------------------

st.markdown('<div class="chat-box">', unsafe_allow_html=True)
for message in st.session_state.chat_history[st.session_state.prompt_offset :]:
    role_class = "message-user" if message["role"] == "user" else "message-assistant"
    if message["role"] == "assistant":  # 프로필 사진 포함
        st.markdown(
            f"<div class='message-container'>"
            f"  <img src='{st.session_state.selected_image}' class='profile-pic' alt='프로필 이미지'>"
            f"  <div class='{role_class}'>{message['content']}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
    else:  # 사용자 메시지
        st.markdown(
            f"<div class='message-container'>"
            f"  <div class='{role_class}'>{message['content']}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
st.markdown('</div>', unsafe_allow_html=True)

# --- 입력 폼 (화면 하단 고정) ---------------------------------------------

st.markdown('<div class="input-container">', unsafe_allow_html=True)
with st.form(key="input_form", clear_on_submit=True):
    user_msg = st.text_input("메시지를 입력하세요:", placeholder="")
    if st.form_submit_button(label="전송") and user_msg:
        # 채팅 히스토리에 사용자 메시지 저장
        st.session_state.chat_history.append({"role": "user", "content": user_msg})

        # 모델 요청 파라미터 구성
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

st.markdown('</div>', unsafe_allow_html=True)
