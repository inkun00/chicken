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
bot_profile_url = st.session_state.selected_image

# 대화 기록 초기화
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [{
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
    }]

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
        resp = r.content.decode('utf-8')
        full = ""
        for line in resp.split("\n"):
            if line.startswith("data:"):
                j = line[5:].strip()
                if j == "[DONE]":
                    break
                try:
                    msg = json.loads(j)
                    full += msg.get("message", {}).get("content", "")
                except:
                    pass
        # 중복 제거
        m = re.match(r'^(?P<p>.+)\1$', full, flags=re.DOTALL)
        if m:
            full = m.group("p")
        if full:
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": full.strip()
            })

# CompletionExecutor 초기화 (요청하신 request_id 적용)
completion_executor = CompletionExecutor(
    host='https://clovastudio.stream.ntruss.com',
    api_key='NTA0MjU2MWZlZTcxNDJiY6Yo7+BLuaAQ2B5+PgEazGquXEqiIf8NRhOG34cVQNdq',
    api_key_primary_val='DilhGClorcZK5OTo1QgdfoDQnBNOkNaNksvlAVFE',
    request_id='d1950869-54c9-4bb8-988d-6967d113e03f'
)

# 타이틀 스타일
st.markdown("""
<style>
.title { text-align:center; font-size:28px; font-weight:bold; padding-top:10px; }
</style>
""", unsafe_allow_html=True)
st.markdown('<h1 class="title">닭과 대화 나누기</h1>', unsafe_allow_html=True)

def render_chat():
    # 메시지별 HTML 생성
    msgs_html = ""
    for msg in st.session_state.chat_history[1:]:
        if msg["role"] == "assistant":
            msgs_html += f'''
<div class="message-container" style="display:flex; align-items:center; margin-bottom:10px;">
  <img src="{bot_profile_url}" style="width:40px; height:40px; border-radius:50%; margin-right:10px;" />
  <div style="background:#FFF; padding:10px; border-radius:10px; max-width:60%; box-shadow:2px 2px 10px rgba(0,0,0,0.1);">
    {msg["content"]}
  </div>
</div>'''
        else:
            msgs_html += f'''
<div class="message-container" style="display:flex; justify-content:flex-end; margin-bottom:10px;">
  <div style="background:#FFEB33; padding:10px; border-radius:10px; max-width:60%; box-shadow:2px 2px 10px rgba(0,0,0,0.1);">
    {msg["content"]}
  </div>
</div>'''

    # iframe 형태로 전체 렌더 및 자동 스크롤 스크립트 삽입
    html = f"""
<html>
  <body style="margin:0; padding:0; background:#BACEE0;">
    <div id="chat-box" style="
      box-sizing:border-box;
      padding:20px;
      width:100%; height:400px;
      overflow-y:auto;
      background:#BACEE0;
    ">
      {msgs_html}
    </div>
    <script>
      // 메시지 렌더 후 바로 스크롤을 맨 아래로
      var box = document.getElementById('chat-box');
      box.scrollTop = box.scrollHeight;
    </script>
  </body>
</html>
"""
    components.html(html, height=430, scrolling=False)

# 최초 렌더
render_chat()

# 입력 폼
with st.form("input_form", clear_on_submit=True):
    user_msg = st.text_input("메시지를 입력하세요:")
    send = st.form_submit_button("전송")

# 전송 처리
if send and user_msg:
    st.session_state.chat_history.append({"role":"user","content":user_msg})
    req = {
        'messages': st.session_state.chat_history,
        'topP': 0.95, 'topK': 0,
        'maxTokens': 256, 'temperature': 0.9,
        'repeatPenalty': 1.1,
        'stopBefore': [], 'includeAiFilters': True
    }
    completion_executor.execute(req)
    render_chat()
