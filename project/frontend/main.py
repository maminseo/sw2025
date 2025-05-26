# frontend/main.py

import streamlit as st
import requests

st.set_page_config(page_title="뉴스 제보 분석기", layout="centered")

st.title("📰 뉴스 제보 진위 분석기 (CLIP + GPT)")

st.markdown("이미지와 설명을 입력하면 CLIP + GPT로 요약 및 신뢰도를 분석해줍니다.")

# 입력 폼
with st.form("input_form"):
    image = st.file_uploader("🖼️ 이미지 업로드", type=["jpg", "png", "jpeg"])
    description = st.text_area("✏️ 제보 설명 입력")
    submitted = st.form_submit_button("분석 시작!")

# 결과 출력
if submitted:
    if not image or not description:
        st.warning("이미지와 설명을 모두 입력해주세요.")
    else:
        with st.spinner("분석 중입니다..."):
            response = requests.post(
                "http://localhost:5000/analyze",  # 백엔드 주소
                files={"image": image},
                data={"description": description}
            )

            if response.status_code == 200:
                result = response.json()
                st.success("✅ 분석 완료!")
                st.markdown(f"**유사도 점수:** {result['similarity']}")
                st.markdown("---")
                st.markdown(result['summary'])
            else:
                st.error("❌ 오류 발생: " + response.text)
