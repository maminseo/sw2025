import streamlit as st
import requests
import base64

st.set_page_config(page_title="뉴스 제보 분석기", layout="centered")

# 배경 이미지 base64 인코딩 (없으면 None)
encoded = None
try:
    with open("static/nwspaper.jpg", "rb") as f:
        img_bytes = f.read()
        encoded = base64.b64encode(img_bytes).decode()
except FileNotFoundError:
    encoded = None

# 스타일 정의
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
            color: white;
        }}

        h2, h3, .stTextInput > div > input, .stTextArea > div > textarea {{
            color: white !important;
        }}

        .stTextInput > div > input,
        .stTextArea > div > textarea {{
            background-color: rgba(255, 255, 255, 0.9);
            color: black !important;
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
st.markdown("이미지와 설명을 입력하면 요약 및 신뢰도를 분석해줍니다.")
st.markdown("<span style='color: white;'>______________________________________________________________________________________</span>", unsafe_allow_html=True)

# 입력 폼
with st.form("input_form"):
    image = st.file_uploader("🖼️ 이미지 업로드", type=["jpg", "png", "jpeg"])
    description = st.text_area(
        "✏️ 제보 설명 입력",
        placeholder="내용을 입력해주세요"
    )
    submitted = st.form_submit_button("분석 시작!")

st.markdown("<span style='color: white;'>______________________________________________________________________________________</span>", unsafe_allow_html=True)

# 결과 출력
if submitted:
    if not image and not description:
        st.warning("이미지와 설명을 모두 입력해주세요.")
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

                    simil = float(result.get('similarity', 0))

                    if simil > 85:
                        color = '#e53935'  # 빨강
                    elif simil > 65:
                        color = '#fb8c00'  # 주황
                    else:
                        color = '#43a047'  # 초록

                    # 점수 막대
                    st.markdown(f"""
                    <div class="score-bar">
                        <div class="score-fill" style="width:{simil}%; background-color:{color};">
                            {simil:.1f}%
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown("### 📝 요약")
                    st.markdown(result.get('summary', '요약 내용이 없습니다.'))
                else:
                    st.error("❌ 오류 발생: " + response.text)
            except Exception as e:
                st.error(f"❌ 예외 발생: {str(e)}")
