import streamlit as st
import requests
import json
import random

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
    "https://raw.githubusercontent.com/inkun00/chicken/main/image/image9.png"
]
if "selected_image" not in st.session_state:
    st.session_state.selected_image = random.choice(image_urls)
selected_image = st.session_state.selected_image

# 대화 기록 초기화
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        # system 프롬프트: 역할과 맥락만
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
        # 🟢 Few-shot 예시
        {"role": "user", "content": "안녕?"},
        {"role": "assistant", "content": "꼬꼬댁... 여긴 너무 좁고 냄새가 심해. 몸이 아파서 힘들어. 꼬꼬..."},
        {"role": "user", "content": "무슨 일이야?"},
        {"role": "assistant", "content": "계속 알을 낳아야 해서 힘들어. 다리도 아프고, 숨쉬기 힘들어. 나를 위해 새로운 공간 만들어줄 수 있어? 꼬꼬댁..."}
    ]

class CompletionExecutor:
    def __init__(self, host, api_key, api_key_primary_val, request_id):
        self._host = host
        self._api_key = api_key
        self._api_key_primary_val = api_key_primary_val
        self._request_id = request_id

    def execute(self, completion_request):
        headers = {
            'X-NCP-CLOVASTUDIO-API-KEY': self._api_key,
            'X-NCP-APIGW-API-KEY': self._api_key_primary_val,
            'X-NCP-CLOVASTUDIO-REQUEST-ID': self._request_id,
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'text/event-stream'
        }
        # stream=False로 해도 전체 SSE 로그가 r.content에 담겨 옵니다.
        r = requests.post(
            self._host + '/testapp/v1/chat-completions/HCX-003',
            headers=headers,
            json=completion_request,
            stream=False
        )
        full_data = r.content.decode('utf-8')
        assembled = ""
        for line in full_data.split("\n"):
            if not line.startswith("data:"):
                continue
            data = line[5:].strip()
            if data == "[DONE]":
                continue
            try:
                msg = json.loads(data)
                # 각 청크의 'content'를 순서대로 이어붙임
                assembled += msg["message"]["content"]
            except Exception as e:
                st.error(f"API 응답 파싱 오류: {e}")
        # 한번만 이력에 추가
        if assembled:
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": assembled
            })

# CompletionExecutor 초기화 (본인 키로 교체)
completion_executor = CompletionExecutor(
    host='https://clovastudio.stream.ntruss.com',
    api_key='YOUR_API_KEY',
    api_key_primary_val='YOUR_SECONDARY_KEY',
    request_id='YOUR_REQUEST_ID'
)

# Streamlit UI 스타일 & 타이틀
st.markdown(
    '<h1 class="title">닭과 대화 나누기</h1>',
    unsafe_allow_html=True
)
bot_profile_url = selected_image
st.markdown(f"""
    <style>
    body, .main, .block-container {{ background-color: #BACEE0 !important; }}
    .title {{ font-size: 28px !important; font-weight: bold; text-align: center; padding-top: 10px; }}
    .message-container {{ display: flex; margin-bottom: 10px; align-items: center; }}
    .message-user {{ background-color: #FFEB33; color: black; text-align: right; padding: 10px; border-radius: 10px; margin-left: auto; max-width: 60%; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }}
    .message-assistant {{ background-color: #FFFFFF; text-align: left; padding: 10px; border-radius: 10px; margin-right: auto; max-width: 60%; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }}
    .profile-pic {{ width: 40px; height: 40px; border-radius: 50%; margin-right: 10px; }}
    .chat-box {{ background-color: #BACEE0; border: none; padding: 20px; border-radius: 10px; max-height: 400px; overflow-y: scroll; margin: 0 auto; width: 80%; }}
    .stTextInput > div > div > input {{ height: 38px; width: 100%; }}
    .stButton button {{ height: 38px !important; width: 70px !important; padding: 0 10px; margin-right: 0 !important; }}
    .input-container {{ position: fixed; bottom: 0; left: 0; width: 100%; background-color: #BACEE0; padding: 10px; box-shadow: 0 -2px 5px rgba(0,0,0,0.1); }}
    </style>
""", unsafe_allow_html=True)

# 사용자 입력 폼
with st.form(key="input_form", clear_on_submit=True):
    user_msg = st.text_input("메시지를 입력하세요:", placeholder="")
    submit_button = st.form_submit_button(label="전송")

if submit_button and user_msg:
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_msg
    })
    completion_request = {
        'messages': st.session_state.chat_history,
        'topP': 0.95,
        'topK': 0,
        'maxTokens': 256,
        'temperature': 0.9,
        'repeatPenalty': 1.1,
        'stopBefore': [],
        'includeAiFilters': True,
        'seed': 0
    }
    completion_executor.execute(completion_request)

# 대화 출력
st.markdown('<div class="chat-box">', unsafe_allow_html=True)
for message in st.session_state.chat_history[5:]:
    if message["role"] == "assistant":
        st.markdown(f'''
            <div class="message-container">
                <img src="{bot_profile_url}" class="profile-pic" alt="프로필 이미지">
                <div class="message-assistant">{message["content"]}</div>
            </div>''', unsafe_allow_html=True)
    else:
        st.markdown(f'''
            <div class="message-container">
                <div class="message-user">{message["content"]}</div>
            </div>''', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# 대화 복사 기능 (생략 가능)
