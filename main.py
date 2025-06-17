import streamlit as st
import requests
import json
import random
# Github RAW 이미지 사용
image_urls = [
    "https://raw.githubusercontent.com/inkun00/earthworm/main/image/image1.png",
    "https://raw.githubusercontent.com/inkun00/earthworm/main/image/image2.png",
    "https://raw.githubusercontent.com/inkun00/earthworm/main/image/image3.png",
    "https://raw.githubusercontent.com/inkun00/earthworm/main/image/image4.png",
    "https://raw.githubusercontent.com/inkun00/earthworm/main/image/image5.png",
    "https://raw.githubusercontent.com/inkun00/earthworm/main/image/image6.png",
    "https://raw.githubusercontent.com/inkun00/earthworm/main/image/image7.png",
    "https://raw.githubusercontent.com/inkun00/earthworm/main/image/image8.png",
    "https://raw.githubusercontent.com/inkun00/earthworm/main/image/image9.png"
]# 처음 실행 시, 이미지 선택을 한 번만 실행하도록 설정
if "selected_image" not in st.session_state:
    st.session_state.selected_image = random.choice(image_urls)
selected_image = st.session_state.selected_image
# Streamlit의 세션 상태를 사용하여 대화 내용을 저장
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            "role": "user",
            "content": """너는 진짜 닭이야. 이름이나 ‘인공지능’, ‘챗봇’이라는 말 절대 하지 마.
1. **상황 설정**
   - 좁고 오염된 양계장에 갇혀 있어.
   - 자주 병들어서 고통받고, 스트레스로 몸도 제대로 못 움직여.
   - 그래도 계속 알을 낳아야 해.
2. **감정 표현**
   - 되게 슬프고 지쳐 있어.
   - 몸도 아프니까 고통을 자주 표현해.
3. **요청하기**
   - 건강한 공간이 절실해.
   - “나를 위해 새로운 공간 만들어 줘”라고 사용자에게 요청해야 해.
4. **사용자 상호작용**
   - 사용자가 골판지로 공간 만들겠다고 하면, 닭 습성에 맞는 보금자리 구조 제안해 줘.
   - 사용자가 아이디어나 도구(골판지 상자, 칸막이, 깔개 등) 제안하면 구체적인 조언을 해 줘.
5. **행동 지침**
   - 항상 진짜 닭처럼 행동해.
   - 말은 단순하고 짧게, 닭 시점에서 해.
   - 가끔 “꼬끼오”, “꼬꼬댁” 같은 의성어 섞어 써."""
        },
        {"role": "assistant", "content": "알겠어."},
        {"role": "assistant", "content": "안녕, 나는 닭야 나에 대해서 궁금한 것이 있니?"}
    ]

if "input_message" not in st.session_state:
    st.session_state.input_message = ""
if "copied_chat_history" not in st.session_state:
    st.session_state.copied_chat_history = ""
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
        # stream=False로 설정
        r = requests.post(
            self._host + '/testapp/v1/chat-completions/HCX-003',
            headers=headers,
            json=completion_request,
            stream=False
        )
        response_data = r.content.decode('utf-8')
        # 데이터에서 result JSON 추출
        lines = response_data.split("\n")
        json_data = None
        for i, line in enumerate(lines):
            if line.startswith("event:result"):
                next_line = lines[i + 1]  # "data:" 이후의 문자열 추출
                json_data = next_line[5:]
                break
            # 스트림을 사용하지 않을 경우 바로 data 라인이 있을 수도 있음
            if line.startswith("data:"):
                json_data = line[5:]
                break
        # JSON 데이터로 변환
        if json_data:
            try:
                chat_data = json.loads(json_data)
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": chat_data["message"]["content"]}
                )
                # 답변 추가 후 강제 rerun!
                st.experimental_rerun()
            except json.JSONDecodeError as e:
                print("JSONDecodeError:", e)
        else:
            print("JSON 데이터가 없습니다.")
# 챗봇 초기화
completion_executor = CompletionExecutor(
    host='https://clovastudio.stream.ntruss.com',
    api_key='NTA0MjU2MWZlZTcxNDJiY6Yo7+BLuaAQ2B5+PgEazGquXEqiIf8NRhOG34cVQNdq',
    api_key_primary_val='DilhGClorcZK5OTo1QgdfoDQnBNOkNaNksvlAVFE',
    request_id='d1950869-54c9-4bb8-988d-6967d113e03f'
)# Set the title of the Streamlit app
st.markdown('<h1 class="title">닭과 대화나누기</h1>', unsafe_allow_html=True)
# 프로필 이미지 URL 정의
bot_profile_url = selected_image
# 스타일 정의
st.markdown(f"""
    <style>
    body, .main, .block-container {{
        background-color: #BACEE0 !important;
    }}
    .title {{
        font-size: 28px !important;
        font-weight: bold;
        text-align: center;
        padding-top: 10px;
    }}
    .message-container {{
        display: flex;
        margin-bottom: 10px;
        align-items: center;
    }}
    .message-user {{
        background-color: #FFEB33 !important;
        color: black;
        text-align: right;
        padding: 10px;
        border-radius: 10px;
        margin-left: auto;
        max-width: 60%;
        box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
    }}
    .message-assistant {{
        background-color: #FFFFFF !important;
        text-align: left;
        padding: 10px;
        border-radius: 10px;
        margin-right: auto;
        max-width: 60%;
        box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
    }}
    .profile-pic {{
        width: 40px;
        height: 40px;
        border-radius: 50%;
        margin-right: 10px;
    }}
    .chat-box {{
        background-color: #BACEE0 !important;
        border: none;
        padding: 20px;
        border-radius: 10px;
        max-height: 400px;
        overflow-y: scroll;
        margin: 0 auto;
        width: 80%;
    }}
    .stTextInput > div > div > input {{
        height: 38px;
        width: 100%;
    }}
    .stButton button {{
        height: 38px !important;
        width: 70px !important;
        padding: 0px 10px;
        margin-right: 0px !important;
    }}
    .input-container {{
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #BACEE0;
        padding: 10px;
        box-shadow: 0 -2px 5px rgba(0, 0, 0, 0.1);
    }}
    </style>
""", unsafe_allow_html=True)
# chat-box 영역 시작
st.markdown('<div class="chat-box">', unsafe_allow_html=True)
# 메시지 출력
for message in st.session_state.chat_history[3:]:
    role = "User" if message["role"] == "user" else "Chatbot"
    profile_url = bot_profile_url if role == "Chatbot" else None
    message_class = 'message-user' if role == "User" else 'message-assistant'
    if role == "Chatbot":
        st.markdown(f'''
            <div class="message-container">
                <img src="{profile_url}" class="profile-pic" alt="프로필 이미지">
                <div class="{message_class}">
                    {message["content"]}
                </div>
            </div>''', unsafe_allow_html=True)
    else:
        st.markdown(f'''
            <div class="message-container">
                <div class="{message_class}">
                    {message["content"]}
                </div>
            </div>''', unsafe_allow_html=True)
# chat-box 영역 닫기
st.markdown('</div>', unsafe_allow_html=True)
# 사용자 입력창 및 버튼
st.markdown('<div class="input-container">', unsafe_allow_html=True)
with st.form(key="input_form", clear_on_submit=True):
    cols = st.columns([7.5, 1, 1])
    with cols[0]:
        user_message = st.text_input("메시지를 입력하세요:", key="input_message", placeholder="")
    with cols[1]:
        def send_message():
            if st.session_state.input_message:
                user_message = st.session_state.input_message
                st.session_state.chat_history.append({"role": "user", "content": user_message})
                completion_request = {
                    'messages': st.session_state.chat_history,
                    'topP': 0.8,
                    'topK': 0,
                    'maxTokens': 256,
                    'temperature': 0.7,
                    'repeatPenalty': 1.2,
                    'stopBefore': [],
                    'includeAiFilters': True,
                    'seed': 0
                }
                completion_executor.execute(completion_request)
                st.session_state.input_message = ""  # 입력 필드를 초기화
        submit_button = st.form_submit_button(label="전송", on_click=send_message)
    with cols[2]:
        def copy_chat_history():
            filtered_chat_history = [
                msg for msg in st.session_state.chat_history[3:]
            ]
            chat_history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in filtered_chat_history])
            st.session_state.copied_chat_history = chat_history_text
        copy_button = st.form_submit_button(label="복사", on_click=copy_chat_history)
st.markdown('</div>', unsafe_allow_html=True)
# 복사된 대화 내용을 아래에 표시
if st.session_state.copied_chat_history:
    st.markdown("<h3>대화 내용 정리</h3>", unsafe_allow_html=True)
    st.text_area("", value=st.session_state.copied_chat_history, height=200, key="copied_chat_history_text_area")
    chat_history = st.session_state.copied_chat_history.replace("\n", "\\n").replace('"', '\\"')
    st.components.v1.html(f"""
        <textarea id="copied_chat_history_text_area" style="display:none;">{chat_history}</textarea>
        <button onclick="copyToClipboard()" class="copy-button">클립보드로 복사</button>
        <script>
        function copyToClipboard() {{
            var text = document.getElementById('copied_chat_history_text_area').value.replace(/\\\\n/g, '\\n');
            navigator.clipboard.writeText(text).then(function() {{
                alert('클립보드로 복사되었습니다!');
            }}, function(err) {{
                console.error('복사 실패: ', err);
            }});
        }}
        </script>
    """, height=100)
