import streamlit as st
import random
from streamlit_drawable_canvas import st_canvas

# Page Config
st.set_page_config(
    page_title="한문교육용 기초한자",
    page_icon="漢",
    layout="centered"
)

# -----------------------------------------------------------------------------
# 1. 한자 데이터 및 고사성어 데이터 (기초 데이터)
# -----------------------------------------------------------------------------
@st.cache_data
def get_hanja_data():
    # 1~1800자 샘플 및 패턴 데이터 생성 (실제 한자 데이터 구조)
    # 601~800번 영역은 특수 쓰기 연습 테스트를 지원합니다.
    sample_chars = ["日", "月", "火", "水", "木", "金", "土", "山", "川", "天", "地", "人", "父", "母", "子", "女", "學", "校", "生", "先"]
    sample_meanings = ["날", "달", "불", "물", "나무", "쇠", "흙", "메", "내", "하늘", "땅", "사람", "아비", "어미", "아들", "계집", "배울", "학교", "날", "먼저"]
    sample_sounds = ["일", "월", "화", "수", "목", "금", "토", "산", "천", "천", "지", "인", "부", "모", "자", "녀", "학", "교", "생", "선"]
    
    data = []
    for i in range(1, 1801):
        idx = (i - 1) % len(sample_chars)
        data.append({
            "no": i,
            "char": sample_chars[idx] if not (601 <= i <= 800) else f"漢{i}",
            "meaning": sample_meanings[idx],
            "sound": sample_sounds[idx]
        })
    return data

@st.cache_data
def get_gosa_data():
    return [
        {"no": 1, "idiom": "가정맹어호", "meaning": "가혹한 정치는 범보다 무섭다"},
        {"no": 2, "idiom": "각주구검", "meaning": "판단력이 둔하여 융통성이 없음"},
        {"no": 3, "idiom": "감탄고토", "meaning": "달면 삼키고 쓰면 뱉는다"},
        {"no": 4, "idiom": "갑론을박", "meaning": "서로 자기의 주장을 세우고 상대방의 주장을 반박함"},
        {"no": 5, "idiom": "개과천선", "meaning": "지난날의 잘못을 뉘우치고 착하게 됨"},
    ]

hanja_list = get_hanja_data()
gosa_list = get_gosa_data()

# -----------------------------------------------------------------------------
# 2. Session State 초기화
# -----------------------------------------------------------------------------
if "selected_indices" not in st.session_state:
    st.session_state.selected_indices = set(range(1, 31))  # 기본 1~30번 선택

if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False

if "current_quiz_list" not in st.session_state:
    st.session_state.current_quiz_list = []

if "quiz_index" not in st.session_state:
    st.session_state.quiz_index = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "wrong_list" not in st.session_state:
    st.session_state.wrong_list = []

if "card_flipped" not in st.session_state:
    st.session_state.card_flipped = False

# -----------------------------------------------------------------------------
# 3. 헤더
# -----------------------------------------------------------------------------
st.title("漢 한문교육용 기초한자")
st.caption("허가된 구글 계정 학습 사이트 (Streamlit 버전)")

# -----------------------------------------------------------------------------
# 4. 모드 선택 (메모리 게임 제거됨 -> 3가지 모드)
# -----------------------------------------------------------------------------
st.subheader("1. 어떤 문제를 풀어볼까요?")
mode = st.radio(
    "학습 모드를 선택하세요",
    [
        "🗂️ 플래시카드 (카드를 눌러 뒤집으며 학습)",
        "🖌️ 뜻·음 쓰기 (한자를 보고 뜻과 음을 입력)",
        "🎯 한자 고르기 (뜻과 음을 보고 알맞은 한자 선택)"
    ],
    index=0
)

st.divider()

# -----------------------------------------------------------------------------
# 5. 범위 선택 및 즐겨찾기 일괄 선택 (30자 단위 적용)
# -----------------------------------------------------------------------------
st.subheader("2. 학습 범위를 선택하세요")

# [기능 2] 범위 지정 즐겨찾기 (시작~끝 번호 입력 시 한번에 선택)
st.markdown("#### 🎯 범위 지정 일괄 선택 (즐겨찾기)")
c1, c2, c3 = st.columns([2, 2, 1.5])
with c1:
    start_no = st.number_input("시작 번호", min_value=1, max_value=1800, value=1, step=1)
with c2:
    end_no = st.number_input("끝 번호", min_value=1, max_value=1800, value=30, step=1)
with c3:
    st.write(" ")
    st.write(" ")
    if st.button("범위 선택 적용", use_container_width=True):
        if start_no > end_no:
            st.error("시작 번호가 끝 번호보다 클 수 없습니다.")
        else:
            new_set = set(range(int(start_no), int(end_no) + 1))
            st.session_state.selected_indices = new_set
            st.success(f"{start_no}번부터 {end_no}번까지 ({len(new_set)}개) 한자가 선택되었습니다!")

# [기능 3] 30자 단위 묶음 선택 버튼
st.markdown("#### 📦 30자 단위 빠른 선택")
chunk_size = 30
total_chunks = (len(hanja_list) + chunk_size - 1) // chunk_size

# 토글 버튼 그리드 (3열)
cols = st.columns(3)
for i in range(min(12, total_chunks)):  # 주요 범위 12개 세트 노출
    s_num = i * chunk_size + 1
    e_num = min((i + 1) * chunk_size, len(hanja_list))
    btn_label = f"{s_num} ~ {e_num}번"
    
    with cols[i % 3]:
        if st.button(btn_label, key=f"chunk_{i}", use_container_width=True):
            chunk_set = set(range(s_num, e_num + 1))
            st.session_state.selected_indices = chunk_set
            st.info(f"{s_num}~{e_num}번 범위가 선택되었습니다.")

selected_count = len(st.session_state.selected_indices)
st.write(f"현재 선택된 한자: **{selected_count}개**")

st.divider()

# -----------------------------------------------------------------------------
# 6. 학습 시작 / 진행 세션
# -----------------------------------------------------------------------------
st.subheader("3. 학습 시작")

if not st.session_state.quiz_started:
    if st.button("🚀 학습 시작하기", type="primary", use_container_width=True):
        if selected_count == 0:
            st.warning("최소 1개 이상의 한자를 선택해주세요.")
        else:
            # 선택한 한자 데이터 준비
            st.session_state.current_quiz_list = [h for h in hanja_list if h["no"] in st.session_state.selected_indices]
            random.shuffle(st.session_state.current_quiz_list)
            st.session_state.quiz_started = True
            st.session_state.quiz_index = 0
            st.session_state.score = 0
            st.session_state.wrong_list = []
            st.session_state.card_flipped = False
            st.rerun()

else:
    quiz_list = st.session_state.current_quiz_list
    q_idx = st.session_state.quiz_index
    total_q = len(quiz_list)

    if q_idx < total_q:
        current_item = quiz_list[q_idx]
        item_no = current_item["no"]

        # 진행도 표시
        st.progress((q_idx) / total_q)
        st.caption(f"문제 {q_idx + 1} / {total_q} (한자 번호: {item_no}번)")

        # [기능 4] 601 ~ 800번 한자는 무조건 뜻/음 제시 후 직접 캔버스에 쓰기 모드로 실행
        if 601 <= item_no <= 800:
            st.warning("✏️ [601~800번 특수 모드] 제시된 뜻과 음을 보고 아래 캔버스에 한자를 직접 쓰세요!")
            st.markdown(f"### 뜻과 음: **{current_item['meaning']} ({current_item['sound']})**")
            
            # Canvas 인스턴스
            canvas_result = st_canvas(
                fill_color="rgba(255, 165, 0, 0.3)",
                stroke_width=6,
                stroke_color="#000000",
                background_color="#F0F2F6",
                height=250,
                width=250,
                drawing_mode="freedraw",
                key=f"canvas_{q_idx}",
            )

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("정답 확인 및 다음", use_container_width=True):
                    st.success(f"정답 한자: **{current_item['char']}**")
                    st.session_state.quiz_index += 1
                    st.rerun()

        # 1~600번 및 801~1800번은 기존에 선택한 모드로 진행
        else:
            if "플래시카드" in mode:
                st.markdown("---")
                if not st.session_state.card_flipped:
                    st.markdown(f"<h1 style='text-align: center; font-size: 100px;'>{current_item['char']}</h1>", unsafe_allow_html=True)
                    if st.button("🔄 뒤집어서 뜻·음 보기", use_container_width=True):
                        st.session_state.card_flipped = True
                        st.rerun()
                else:
                    st.markdown(f"<h1 style='text-align: center; font-size: 80px; color: #2E7D32;'>{current_item['meaning']} ({current_item['sound']})</h1>", unsafe_allow_html=True)
                    st.markdown(f"<h3 style='text-align: center;'>[ {current_item['char']} ]</h3>", unsafe_allow_html=True)
                    if st.button("➡️ 다음 카드로", use_container_width=True):
                        st.session_state.card_flipped = False
                        st.session_state.quiz_index += 1
                        st.rerun()

            elif "뜻·음 쓰기" in mode:
                st.markdown(f"<h1 style='text-align: center; font-size: 90px;'>{current_item['char']}</h1>", unsafe_allow_html=True)
                
                user_meaning = st.text_input("뜻을 입력하세요 (예: 날)", key=f"m_{q_idx}")
                user_sound = st.text_input("음울 입력하세요 (예: 일)", key=f"s_{q_idx}")

                if st.button("제출하기", use_container_width=True):
                    if user_meaning.strip() == current_item['meaning'] and user_sound.strip() == current_item['sound']:
                        st.success("정답입니다! 🎉")
                        st.session_state.score += 1
                    else:
                        st.error(f"틀렸습니다! 정답: {current_item['meaning']} ({current_item['sound']})")
                        st.session_state.wrong_list.append(current_item)
                    
                    st.session_state.quiz_index += 1
                    st.rerun()

            elif "한자 고르기" in mode:
                st.markdown(f"### 제시된 뜻과 음: **{current_item['meaning']} ({current_item['sound']})**")
                
                # 오답 보기 생성
                wrong_choices = random.sample([h['char'] for h in hanja_list if h['char'] != current_item['char']], 3)
                options = wrong_choices + [current_item['char']]
                random.shuffle(options)

                user_choice = st.radio("알맞은 한자를 선택하세요:", options, key=f"choice_{q_idx}")

                if st.button("정답 확인", use_container_width=True):
                    if user_choice == current_item['char']:
                        st.success("정답입니다! 🎯")
                        st.session_state.score += 1
                    else:
                        st.error(f"오답입니다. 정답은 {current_item['char']} 입니다.")
                        st.session_state.wrong_list.append(current_item)

                    st.session_state.quiz_index += 1
                    st.rerun()

    else:
        # 학습 완료 결과 화면
        st.balloons()
        st.success("🎉 모든 문제를 완료하셨습니다!")
        if "플래시카드" not in mode:
            st.metric("최종 점수", f"{st.session_state.score} / {total_q}")

        if st.session_state.wrong_list:
            st.subheader("❌ 틀린 문제 다시보기")
            for w in st.session_state.wrong_list:
                st.write(f"- **{w['char']}** : {w['meaning']} ({w['sound']}) [{w['no']}번]")

        if st.button("🔄 처음으로 돌아가기", use_container_width=True):
            st.session_state.quiz_started = False
            st.rerun()

st.divider()

# -----------------------------------------------------------------------------
# 7. 관리자 구역 - 고사성어 100
# -----------------------------------------------------------------------------
with st.expander("🔐 관리자 구역 — 고사성어 100"):
    st.write("번호 순서대로 정리된 한문교육용 고사성어입니다.")
    st.table(gosa_list)
