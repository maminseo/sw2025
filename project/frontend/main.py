#main.py
#util에서 저장시 is_duplicate를 bool로 형태 변환
#pip install --upgrade streamlit
import streamlit as st
import requests
import base64

st.set_page_config(page_title="뉴스 제보 분석기", layout="centered")

# 배경 이미지 base64 인코딩 (없으면 None)
encoded = None
try:
    with open("./static/newspaper.jpg", "rb") as f:
        img_bytes = f.read()
        encoded = base64.b64encode(img_bytes).decode()
except FileNotFoundError:
    encoded = None


# 스타일 정의(인코딩 성공)
if encoded:

    st.markdown(
        f"""
        <style>
        .stApp {{
            background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)),
                        url("data:image/jpeg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            color: black;
        }}

        h2, h3 {{
            color: white !important;
        }}

    .stTextInput > div > input,
    .stTextArea > div > textarea {{
        background-color: rgba(255, 255, 255, 0.9);
        color: white !important;
        border-radius: 8px;
    }}

   
        .score-bar {{
            background-color: #ddd;
            border-radius: 10px;
            width: 100%;
            height: 24px;
            margin-top: 10px;
        }}

        .score-fill {{
            height: 100%;
            border-radius: 10px;
            text-align: center;
            line-height: 24px;
            font-weight: bold;
            color: white;
        }}
        button['primary']{{
            background-color:white !improtant;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #222;
            color: white;
        }

        h2, h3, .stTextInput > div > input, .stTextArea > div > textarea {
            color: white !important;
        }

        .stTextInput > div > input,
        .stTextArea > div > textarea {
            background-color: rgba(255, 255, 255, 0.9);
            color: black !important;
            border-radius: 8px;
        }

        .score-bar {
            background-color: #ddd;
            border-radius: 10px;
            width: 100%;
            height: 24px;
            margin-top: 10px;
        }

        .score-fill {
            height: 100%;
            border-radius: 10px;
            text-align: center;
            line-height: 24px;
            font-weight: bold;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True
    )



# 제목 및 설명
st.markdown("## 📰 뉴스 제보 진위 분석기")
st.markdown("<span style='color: white;'>이미지와 설명을 입력하면 요약 및 신뢰도를 분석해줍니다.</span>", unsafe_allow_html=True)
st.markdown("<span style='color: white;'>______________________________________________________________________________________</span>", unsafe_allow_html=True)
#로그인 입력
# :green[🖼️ 이미지 업로드]
# 입력 폼
with st.form("input_form"):
    image = st.file_uploader("", type=["jpg", "png", "jpeg"])
    st.markdown("<p style='color: white; font-weight:bold; margin-top: 1px;'>🖼️ 이미지 업로드</p>", unsafe_allow_html=True)
    description = st.text_area(
        "",
        placeholder="내용을 입력해주세요"
    )
    st.markdown("<p style='color: white; font-weight:bold; margin-top: 1px;'>✏️ 제보 설명 입력</p>", unsafe_allow_html=True)
    st.markdown("")
    submitted = st.form_submit_button("🔍분석 시작!")

st.markdown("<span style='color: white;'>______________________________________________________________________________________</span>", unsafe_allow_html=True)



# 결과 출력
if submitted:
    if not image and not description:
        st.toast("설명을 입력해주세요.")
    else:
        with st.spinner("분석 중입니다..."):
            try:
                if image:
                    files = {"image": image}
                else:
                    files = None

                data = {"description": description}

                response = requests.post(
                    "http://localhost:5000/analyze",
                    files=files,
                    data=data
                )

                if response.status_code == 200:
                    result = response.json()
                    st.success("✅ 분석 완료!")
                    if(result.get('similarity', 0)=="이미지 없음"):
                        simil = 0
                    else:
                        simil = float(result.get('similarity', 0))
                    im = (result.get('importance', 0))#중요도
                    if simil >=85 :
                        color = '#e53935'  # 빨강
                    elif simil < 85  and simil>=50:
                        color = '#fb8c00'  # 주황
                    else:
                        color = '#43a047'  # 초록

                    # 신뢰도 기반 다수 제보 표시
                    if result.get("reliable", False):
                        st.markdown("### ✅ 다수의 제보가 있어 신뢰도가 높습니다.")
                        st.markdown(f"🔁 유사 제보 수: {result.get('similar_count', 0)}건")

                    # 점수 막대
                    st.markdown(f"""
                    <div class="score-bar">
                        <div class="score-fill" style="width:{simil}%; background-color:{color};">
                            {simil:.1f}%
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown(f"{result.get('category', 0)}")
                    st.markdown(f"{im}")
                    st.markdown("### 📝 요약")
                    st.markdown(result.get('summary', '요약 내용이 없습니다.'))
                else:
                    st.toast("❌ 오류 발생: " + response.text)
            except Exception as e:
                st.toast(f"❌ 예외 발생: {str(e)}")
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

logout = False
login = False
pw = ""
col1, col2, col3 = st.columns([6, 3, 3])             
with col3:
    if st.session_state.logged_in:
        with st.form("logout"):
            logout = st.form_submit_button("🔑로그아웃")
    else:
        with st.form("login_form"):
            pw = st.text_input(":green[비밀번호 입력]",type="password", max_chars=4) 
            login = st.form_submit_button("관리자 로그인")

if logout:
    st.toast("로그아웃 되었습니다.")
    st.session_state.logged_in = False
    st.rerun()

if login:
    if pw == "0000":
        st.session_state.logged_in = True
        st.rerun()
        st.toast("로그인 성공! manage페이지를 볼 수 있습니다.")
    else:
        st.error("비밀번호 오류")