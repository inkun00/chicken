import streamlit as st
import streamlit.components.v1 as components
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
selected_image = st.session_state.selected_image

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
        r = requests.post(
            f"{self._host}/testapp/v1/chat-completions/HCX-003",
            headers=headers,
            json=completion_request,
            stream=False
        )
        response_data = r.content.decode('utf-8')
        full_content = ""
        for line in response_data.split("\n"):
            if line.startswith("data:"):
                json_data = line[5:].strip()
                if json_data == "[DONE]":
                    break
                try:
                    chat_data = json.loads(json_data)
                    chunk = chat_data.get("message", {}).get("content", "")
                    full_content += chunk
                except Exception as e:
                    st.error(f"API 응답 파싱 오류: {e}")
        # 중복 제거
        m = re.match(r'^(?P<part>.+)\1$', full_content, flags=re.DOTALL)
        if m:
            full_content = m.group('part')

        if full_content:
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": full_content.strip()
            })

# CompletionExecutor 초기화
completion_executor = CompletionExecutor(
    host='https://clovastudio.stream.ntruss.com',
    api_key='NTA0MjU2MWZlZTcxNDJiY6Yo7+BLuaAQ2B5+PgEazGquXEqiIf8NRhOG34cVQNdq',
    api_key_primary_val='DilhGClorcZK5OTo1QgdfoDQnBNOkNaNksvlAVFE',
    request_id='d1950869-54c9-4bb8-988d-6967d113e03f'
)

# 스타일 및 타이틀
st.markdown(
    '<h1 class="title">닭과 대화 나누기</h1>',
    unsafe_allow_html=True
)
st.markdown("""
<style>
body, .main, .block-container { background-color: #BACEE0 !important; }
.title { font-size: 28px !important; font-weight: bold; text-align: center; padding-top: 10px; }
.message-container { display: flex; margin-bottom: 10px; align-items: center; }
.message-user { background-color: #FFEB33; color: black; text-align: right; padding: 10px; border-radius: 10px; margin-left: auto; max-width: 60%; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
.message-assistant { background-color: #FFFFFF; text-align: left; padding: 10px; border-radius: 10px; margin-right: auto; max-width: 60%; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
.profile-pic { width: 40px; height: 40px; border-radius: 50%; margin-right: 10px; }
.chat-box { background-color: #BACEE0; border: none; padding: 20px; border-radius: 10px; max-height: 400px; overflow-y: auto; margin: 0 auto; width: 80%; }
.stTextInput > div > div > input { height: 38px; width: 100%; }
.stButton button { height: 38px !important; width: 70px !important; padding: 0 10px; margin-right: 0 !important; }
</style>
""", unsafe_allow_html=True)

bot_profile_url = selected_image

# 채팅 출력용 placeholder 생성
chat_placeholder = st.empty()

def render_chat():
    # HTML 문자열로 조립 (id="chat-box" 추가)
    html = '<div class="chat-box" id="chat-box">'
    for msg in st.session_state.chat_history[1:]:
        if msg["role"] == "assistant":
            html += f'''
<div class="message-container">
    <img src="{bot_profile_url}" class="profile-pic" alt="프로필 이미지">
    <div class="message-assistant">{msg["content"]}</div>
</div>'''
        else:
            html += f'''
<div class="message-container">
    <div class="message-user">{msg["content"]}</div>
</div>'''
    html += '</div>'

    # 화면에 렌더링
    chat_placeholder.markdown(html, unsafe_allow_html=True)

    # 자동 스크롤: 새 메시지 생길 때마다 맨 아래로 이동
    components.html(
        """
        <script>
        setTimeout(function() {
            var box = window.parent.document.getElementById('chat-box');
            if (box) {
                box.scrollTop = box.scrollHeight;
            }
        }, 100);
        </script>
        """,
        height=0,
        width=0,
    )

# 초기 렌더링
render_chat()

# 입력 폼
with st.form(key="input_form", clear_on_submit=True):
    user_msg = st.text_input("메시지를 입력하세요:", placeholder="")
    submit_button = st.form_submit_button(label="전송")

# 전송 처리
if submit_button and user_msg:
    st.session_state.chat_history.append({"role": "user", "content": user_msg})
    completion_request = {
        'messages': st.session_state.chat_history,
        'topP': 0.95,
        'topK': 0,
        'maxTokens': 256,
        'temperature': 0.9,
        'repeatPenalty': 1.1,
        'stopBefore': [],
        'includeAiFilters': True
    }
    completion_executor.execute(completion_request)
    render_chat()
