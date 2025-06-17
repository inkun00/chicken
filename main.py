import streamlit as st
import requests
import json
import random

# ─── 1. 이미지 URL 리스트 ───────────────────────────────────────────────
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

# ─── 2. 세션 상태 초기화 ──────────────────────────────────────────────────
if "selected_image" not in st.session_state:
    st.session_state.selected_image = random.choice(image_urls)

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

if "copied_chat_history" not in st.session_state:
    st.session_state.copied_chat_history = ""

# ─── 3. 페이지 타이틀 & CSS ─────────────────────────────────────────────
st.markdown('<h1 class="title">닭과 대화나누기</h1>', unsafe_allow_html=True)
st.markdown(f"""
<style>
  body, .main, .block-container {{ background-color: #BACEE0 !important; }}
  .title {{ font-size: 28px; font-weight: bold; text-align: center; padding-top: 10px; }}
  .message-container {{ display: flex; margin-bottom: 10px; align-items: center; }}
  .message-user {{ background-color: #FFEB33; color: black; text-align: right;
                   padding: 10px; border-radius: 10px; margin-left: auto; max-width: 60%;
                   box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }}
  .message-assistant {{ background-color: #FFF; text-align: left; padding: 10px;
                       border-radius: 10px; margin-right: auto; max-width: 60%;
                       box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }}
  .profile-pic {{ width: 40px; height: 40px; border-radius: 50%; margin-right: 10px; }}
  .chat-box {{ background-color: #BACEE0; border: none; padding: 20px; border-radius: 10px;
               max-height: 400px; overflow-y: scroll; margin: 0 auto; width: 80%; }}
  .input-container {{ position: fixed; bottom: 0; left: 0; width: 100%; background-color: #BACEE0;
                      padding: 10px; box-shadow: 0 -2px 5px rgba(0,0,0,0.1); }}
  .stTextInput > div > div > input {{ height: 38px; width: 100%; }}
  .stButton button {{ height: 38px !important; width: 70px !important; padding: 0 10px; }}
</style>
""", unsafe_allow_html=True)

bot_profile_url = st.session_state.selected_image

# ─── 4. 대화 기록 출력 ────────────────────────────────────────────────────
st.markdown('<div class="chat-box">', unsafe_allow_html=True)
for msg in st.session_state.chat_history[3:]:
    is_user = (msg["role"] == "user")
    cls = "message-user" if is_user else "message-assistant"
    if is_user:
        st.markdown(f'''
            <div class="message-container">
                <div class="{cls}">{msg["content"]}</div>
            </div>
        ''', unsafe_allow_html=True)
    else:
        st.markdown(f'''
            <div class="message-container">
                <img src="{bot_profile_url}" class="profile-pic" alt="프로필">
                <div class="{cls}">{msg["content"]}</div>
            </div>
        ''', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ─── 5. 입력 폼 ─────────────────────────────────────────────────────────
st.markdown('<div class="input-container">', unsafe_allow_html=True)
with st.form(key="input_form", clear_on_submit=True):
    user_input = st.text_input("메시지를 입력하세요:", key="input_message")
    submit = st.form_submit_button("전송")
st.markdown('</div>', unsafe_allow_html=True)

# ─── 6. 전송 처리 & API 호출 ─────────────────────────────────────────────
if submit and user_input:
    # 1) 세션에 사용자 메시지 추가
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # 2) 봇 API 호출 함수
    def call_bot_api(history):
        host = "https://clovastudio.stream.ntruss.com"
        headers = {
            "X-NCP-CLOVASTUDIO-API-KEY": "YOUR_API_KEY",
            "X-NCP-APIGW-API-KEY": "YOUR_PRIMARY_KEY",
            "X-NCP-CLOVASTUDIO-REQUEST-ID": "d1950869-54c9-4bb8-988d-6967d113e03f",
            "Content-Type": "application/json; charset=utf-8"
        }
        payload = {
            "messages": history,
            "topP": 0.8,
            "topK": 0,
            "maxTokens": 256,
            "temperature": 0.7,
            "repeatPenalty": 1.2,
            "stream": False
        }
        res = requests.post(f"{host}/testapp/v1/chat-completions/HCX-003",
                            headers=headers, json=payload)
        res.raise_for_status()
        return res.json()["message"]["content"]

    # 3) 응답 추가
    try:
        reply = call_bot_api(st.session_state.chat_history)
    except Exception as e:
        reply = f"오류 발생: {e}"
    st.session_state.chat_history.append({"role": "assistant", "content": reply})

# ─── 7. 대화 내용 복사 기능 ───────────────────────────────────────────────
if st.button("대화 내용 복사"):
    hist = "\n".join(f"{m['role']}: {m['content']}"
                     for m in st.session_state.chat_history[3:])
    st.session_state.copied_chat_history = hist

if st.session_state.copied_chat_history:
    st.text_area("복사된 대화", st.session_state.copied_chat_history, height=200)
