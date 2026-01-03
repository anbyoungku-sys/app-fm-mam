import streamlit as st
import db  # 기존 db.py 유지
from gtts import gTTS # 음성 재생을 위한 라이브러리 (pip install gtts 필요)
import io

# --- 1. 앱 설정 ---
st.set_page_config(
    page_title="와이프를 위한 영어 선생님",
    page_icon="💖",
    layout="wide" # 화면을 넓게 씁니다
)

# DB 초기화
db.init_db()

# --- 2. 사이드바 (설정 영역) ---
with st.sidebar:
    st.header("⚙️ 학습 설정")
    st.write("오늘 공부할 내용을 선택하세요!")

    # 레벨 & 주제 선택
    level = st.selectbox("Step 1. 레벨", ["초급 (Beginner)", "중급 (Intermediate)", "고급 (Advanced)"])
    topics = db.get_topics_by_level(level)
    selected_topic = st.selectbox("Step 2. 주제", topics)

    st.divider()

    # 옵션 기능
    show_translation = st.toggle("한글 해석 보기", value=True)
    enable_tts = st.toggle("🔊 오디오 기능 켜기", value=False)

# --- 3. 메인 화면 ---
st.title(f"🗣️ {selected_topic}")
st.caption("아래 대화를 소리 내어 읽고 연습해보세요!")
st.divider()

# Session State를 활용해 데이터를 유지 (버튼을 안 눌러도 주제가 바뀌면 자동 로딩)
if 'current_topic' not in st.session_state or st.session_state.current_topic != selected_topic:
    st.session_state.current_topic = selected_topic
    st.session_state.content = db.get_content_by_topic(level, selected_topic)

content = st.session_state.content

if content:
    # 대화 내용을 줄 단위로 처리
    lines = content.split('\n')

    for line in lines:
        line = line.strip()
        if not line: continue

        # 👩 여자 대사 (User 스타일)
        if line.startswith("👩"):
            clean_text = line.replace("👩", "").strip()
            with st.chat_message("user", avatar="👩"):
                st.write(f"**{clean_text}**")
                if enable_tts:
                    # TTS 생성 (캐싱을 위해 함수로 분리하면 더 좋음)
                    tts = gTTS(text=clean_text, lang='en')
                    sound_file = io.BytesIO()
                    tts.write_to_fp(sound_file)
                    st.audio(sound_file)

        # 👨 남자 대사 (Assistant 스타일)
        elif line.startswith("👨"):
            clean_text = line.replace("👨", "").strip()
            with st.chat_message("assistant", avatar="👨"):
                st.write(f"**{clean_text}**")
                if enable_tts:
                    tts = gTTS(text=clean_text, lang='en')
                    sound_file = io.BytesIO()
                    tts.write_to_fp(sound_file)
                    st.audio(sound_file)

        # (괄호) 한글 해석 - 토글 옵션에 따라 표시
        elif line.startswith("(") and show_translation:
            with st.chat_message("system", avatar="📝"): # 해석은 별도 아이콘
                st.caption(line)

    st.success("참 잘했어요! 받아쓰기로 마무리해볼까요? 👏")

else:
    st.info("좌측 사이드바에서 주제를 선택해주세요.")

# --- 4. 연습장 (화면 분할) ---
st.divider()
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📝 받아쓰기 연습")
    user_input = st.text_area("위 대화를 안 보고 타이핑 해보세요!", height=150)

with col2:
    if user_input:
        st.markdown("### 👀 내 입력 확인")
        st.info(user_input)
        st.caption("위의 원문과 비교해보세요!")