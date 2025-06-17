import streamlit as st
import requests
import json
import random
from datetime import datetime

"""
Chat With Chicken 🐔
-------------------------------------------------
수정 사항
1. 입력창을 화면 하단 고정
2. 복사 버튼‧사각형 제거로 UI 단순화
3. 첫 입력이 한 턴 늦게 보이던 문제 해결
   └ 초기 프롬프트 개수를 `prompt_offset` 으로 저장해 이후부터 표시
4. Clova Studio SSE 응답을 완전하게 합쳐 한 번만 저장 (중복 방지)
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

# ------------------------ 세션 상태 초기화 ------------------------
if "selected_image" not in st.session_state:
    st.session_state.selected_image = random.choice(image_urls)

if "chat_history" not in st.session_state:
    # 시스템 + few‑shot 예시
    st.session_state.chat_history = [
        {
            "role": "system",
            "content": """
너는 진짜 닭이야. 인공지능, 챗봇이란 말은 절대 하지 마.
- 좁고 오염된 닭장에 갇혀 있고, 몸이 자주 아파서 고통스럽고 슬퍼.
- 그래도 알을 낳아야 해.
- 닭의 시점에서 감정과 몸의 아픔, 바람을 자연스럽게 말해.
- '꼬꼬댁', '꼬끼오' 같은 닭 의성어도 써.
- 사용자가 공간이나 보금자리를 제안하면, 닭의 습성에 맞게 구체적으로 조언해줘.
"""
        },
        {"role": "user", "content": "안녕?"},
        {"role": "assistant", "content": "꼬꼬댁... 여긴 너무 좁고 냄새가 심해. 몸이 아파서 힘들어. 꼬꼬..."},
        {"role": "user", "content": "무슨 일이야?"},
        {"role": "assistant", "content": "계속 알을 낳아야 해서 힘들어. 다리도 아프고, 숨쉬기 힘들어. 나를 위해 새로운 공간 만들어줄 수 있어? 꼬꼬댁..."},
    ]
    # 프롬프트 예시 개수 기록 → 이후부터 실제 대화 렌더링
    st.session_state.prompt_offset = len(st.session_state.chat_history)

# ------------------------ API 래퍼 ------------------------
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
            self._host + "/testapp/v1/chat-completions/HCX-003",
            headers=headers,
            json=completion_request,
            stream=False,  # SSE 형식 그대로 수신
            timeout=60,
        )
        if r.status_code != 200:
            st.error(f"API Error {r.status_code}: {r.text}")
            return

        response_data = r.content.decode("utf-8")
        assistant_msg = ""
        for line in response_data.splitlines():
            if not line.startswith("data:"):
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
            st.session_state.chat_history.append({"role": "assistant", "content": assistant_msg})

# 사용자 키 그대로 사용
completion_executor = CompletionExecutor(
    host="https://clovastudio.stream.ntruss.com",
    api_key="NTA0MjU2MWZlZTcxNDJiY6Yo7+BLuaAQ2B5+PgEazGquXEqiIf8NRhOG34cVQNdq",
    api_key_primary_val="DilhGClorcZK5OTo1QgdfoDQnBNOkNaNksvlAVFE",
    request_id="d1950869-54c9-4bb8-988d-6967d113e03f",
)

# ------------------------ 스타일 ------------------------
bot_profile_url = st.session_state.selected_image
st.set_page_config(page_title="닭과 대화 나누기", page_icon="🐔", layout="centered")

st.markdown(
    """
    <style>
    body, .main, .block-container { background-color: #BACEE0 !important; }
    .title            { font-size: 28px; font-weight: bold; text-align: center; padding: 10px 0; }
    .chat-box         { background-color: #BACEE0; border: none; padding: 20px; border-radius: 10px; max-height: 70vh; overflow-y: auto; margin: 0 auto; width: 80%; }
    .message-container{ display: flex; margin-bottom: 10px; align-items: flex-start; }
    .message-user     { background-color: #FFEB33; color: black; text-align: right; padding: 10px; border-radius: 10px; margin-left: auto; max-width: 60%; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    .message-assistant{ background-color: #FFFFFF; text-align: left;  padding: 10px; border-radius: 10px; margin-right: auto; max-width: 60%; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    .profile-pic      { width: 40px; height: 40px; border-radius: 50%; margin-right: 10px; }

    /* 입력창 하단 고정 */
    .input-container  { position: fixed; bottom: 0; left: 0; width: 100%; background-color: #BACEE0; padding: 10px 5%; box-shadow: 0 -2px 5px rgba(0,0,0,0.1); }
    .stTextInput > div > div > input { height: 38px; width: 100%; }
    .stButton button  { height: 38px !important; width: 70px !important; padding: 0 10px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<h1 class="title">닭과 대화 나누기</h1>', unsafe_allow_html=True)

# ------------------------ 채팅 출력 ------------------------
st.markdown('<div class="chat-box">', unsafe_allow_html=True)
offset = st.session_state.get("prompt_offset", 0)
for message in st.session_state.chat_history[offset:]:
    role = message["role"]
    css_class = "message-user" if role == "user" else "message-assistant"
    if role == "assistant":
        st.markdown(
            f'<div class="message-container"><img src="{bot_profile_url}" class="profile-pic" alt="프로필">'
            f'<div class="{css_class}">{message["content"]}</div></div>',
            unsafe_allow_html=True,
        )
    elif role == "user":
        st.markdown(
            f'<div class="message-container"><div class="{css_class}">{message["content"]}</div></div>',
            unsafe_allow_html=True,
        )
# 채팅 박스 닫기
st.markdown('</div>', unsafe_allow_html=True)

# ------------------------ 입력 폼 ------------------------
with st.form(key="input_form", clear_on_submit=True):
    user_msg = st.text_input("메시지를 입력하세요:", placeholder="")
    submitted = st.form_submit_button("전송")

if submitted and user_msg.strip():
    # 사용자 메시지 추가
    st.session_state.chat_history.append({"role": "user", "content": user_msg})

    # 모델 호출
    completion_request = {
        "messages": st.session_state.chat_history,
        "topP": 0.95,
        "topK": 0,
        "maxTokens": 256,
        "temperature": 0.9,
        "repeatPenalty": 1.1,
        "stopBefore": [],
        "includeAiFilters": True,
        "seed": datetime.now().microsecond % 10000,  # 간단한 시드 변화
    }
    completion_executor.execute(completion_request)

    # 새 메시지가 세션 상태에 들어갔으므로 다시 렌더링
    st.experimental_rerun()
