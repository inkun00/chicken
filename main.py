import streamlit as st
import requests
import json
import random
import re

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
bot_profile_url = st.session_state.selected_image

# 대화 기록 초기화
if "chat_history" not in st.session_state:
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
- 모든 응답은 최대 3문장 이내로 작성할 것.
"""
        }
    ]

class CompletionExecutor:
    def __init__(self, host, api_key, api_key_primary_val, request_id):
        self.host = host
        self.api_key = api_key
        self.api_key_primary_val = api_key_primary_val
        self.request_id = request_id

    def execute(self, completion_request):
        headers = {
            'X-NCP-CLOVASTUDIO-API-KEY': self.api_key,
            'X-NCP-APIGW-API-KEY': self.api_key_primary_val,
            'X-NCP-CLOVASTUDIO-REQUEST-ID': self.request_id,
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'text/event-stream'
        }
        r = requests.post(
            f"https://clovastudio.stream.ntruss.com/testapp/v1/chat-completions/HCX-003",
            headers=headers,
            json=completion_request,
            stream=False
        )
        data = r.content.decode('utf-8')
        full = ""
        for line in data.splitlines():
            if line.startswith("data:"):
                payload = line[5:].strip()
                if payload == "[DONE]":
                    break
                try:
                    msg = json.loads(payload).get("message", {}).get("content", "")
                    full += msg
                except:
                    pass
        # 중복 두 번 반복 제거
        m = re.match(r'^(?P<t>.+)\1$', full, flags=re.DOTALL)
        if m:
            full = m.group("t")
        if full:
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": full.strip()
            })

# Executor 초기화 (키·ID는 원본 그대로)
executor = CompletionExecutor(
    host='https://clovastudio.stream.ntruss.com',
    api_key='NTA0MjU2MWZlZTcxNDJiY6Yo7+BLuaAQ2B5+PgEazGquXEqiIf8NRhOG34cVQNdq',
    api_key_primary_val='DilhGClorcZK5OTo1QgdfoDQnBNOkNaNksvlAVFE',
    request_id='d1950869-54c9-4bb8-988d-6967d113e03f'
)

# 전역 CSS 및 레이아웃
st.markdown(f"""
<style>
  body, .main, .block-container {{
    background-color: #BACEE0 !important;
    padding: 0;
    margin: 0;
    height: 100vh;
  }}
  .chat-container {{
    display: flex;
    flex-direction: column;
    height: 100%;
  }}
  .header {{ text-align: center; padding: 10px; font-size: 28px; font-weight: bold; }}
  .chat-box {{
    flex: 1;
    overflow-y: auto;
    padding: 20px;
  }}
  .message-container {{ display: flex; margin-bottom: 10px; align-items: center; }}
  .message-user {{
    background-color: #FFEB33;
    color: black;
    text-align: right;
    padding: 10px;
    border-radius: 10px;
    margin-left: auto;
    max-width: 60%;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
  }}
  .message-assistant {{
    background-color: #FFFFFF;
    text-align: left;
    padding: 10px;
    border-radius: 10px;
    margin-right: auto;
    max-width: 60%;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
  }}
  .profile-pic {{
    width: 40px; height: 40px; border-radius: 50%; margin-right: 10px;
  }}
  .input-area {{ padding: 10px; background-color: #BACEE0; }}
  .stTextInput > div > div > input {{ height: 38px; width: 100%; }}
  .stButton button {{ height: 38px !important; width: 70px !important; }}
</style>
""", unsafe_allow_html=True)

# 레이아웃 시작
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# 헤더
st.markdown('<div class="header">닭과 대화 나누기</div>', unsafe_allow_html=True)

# 대화창
st.markdown('<div class="chat-box">', unsafe_allow_html=True)
for msg in st.session_state.chat_history[1:]:
    if msg["role"] == "assistant":
        st.markdown(f'''
          <div class="message-container">
            <img src="{bot_profile_url}" class="profile-pic" alt="닭">
            <div class="message-assistant">{msg["content"]}</div>
          </div>
        ''', unsafe_allow_html=True)
    else:
        st.markdown(f'''
          <div class="message-container">
            <div class="message-user">{msg["content"]}</div>
          </div>
        ''', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# 입력창
st.markdown('<div class="input-area">', unsafe_allow_html=True)
with st.form(key="input_form", clear_on_submit=True):
    user_input = st.text_input("", placeholder="메시지를 입력하세요...")
    submit = st.form_submit_button("전송")
    if submit and user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        executor.execute({
            "messages": st.session_state.chat_history,
            "topP": 0.95,
            "topK": 0,
            "maxTokens": 256,
            "temperature": 0.9,
            "repeatPenalty": 1.1,
            "stopBefore": [],
            "includeAiFilters": True
        })
st.markdown('</div>', unsafe_allow_html=True)

# 레이아웃 닫기
st.markdown('</div>', unsafe_allow_html=True)
