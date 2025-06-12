#backend파일에 __init__.py파일 빈파일로 생성
import streamlit as st
import requests
import base64
import os
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))#__init__.py필요
sys.path.append(project_root)
from backend.utils import load_collected_data
data = load_collected_data()

st.set_page_config(page_title="관리자 페이지", layout="centered")

# 배경 이미지 base64 인코딩 (없으면 None)
encoded = None
try:
    with open("./static/newspaper.jpg", "rb") as f:
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


        .stTextInput > div > input,
        .stTextArea > div > textarea {{
            background-color: rgba(255, 255, 255, 0.9);
            color: white !important;
            border-radius: 8px;
        }}
        div[data-testid="stNotification"] div[role="status"] {{
            color: white !important;
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
if not st.session_state.get("logged_in"):
    st.markdown("<span style='color:white;'>로그인이 필요합니다.</span>", unsafe_allow_html=True)
else:
    st.markdown("## 📰 뉴스 데이터베이스")
    st.markdown("<span style='color: white;'>______________________________________________________________________________________</span>", unsafe_allow_html=True)
   
    data = load_collected_data() 

    if len(data) == 0:
        st.warning("저장된 제보가 없습니다.")
    else:
        total = len(data)
        for i, result_entry in enumerate(data[::-1]):
            display_index = total - i
            st.markdown("<span style='color: white;'>______________________________________________________________________________________</span>", unsafe_allow_html=True)

            st.markdown(f"### 📄 제보 {display_index}")
            for key, value in result_entry.items():
                if(key=="id"): continue
                if(key=="image_path" and value==None):
                    continue
                elif(key=="image_path"):
                    try:
                        st.image(value, width=300)
                    except:
                        st.warning("이미지를 불러올 수 없습니다.")
                elif(key=="similarity" and value==None):
                    continue
                elif(key=="image_vector"):
                    continue
                elif(key=="image_vector"):
                    st.write(f"**{key}**: [벡터 생략, 길이 {len(value)}]")
                elif(key=="duplicate"):
                    if(value): st.write("중복없음")
                    else: st.write("중복")
                elif(key=="timestamp" or key=="similarity"):
                    st.write(f"{key}: {value}")
                else:
                    st.write(f"{value}")
            st.markdown("<span style='color: white;'>______________________________________________________________________________________</span>", unsafe_allow_html=True)
