# backend/summary_module.py

import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_summary(description, similarity_score):
    prompt = f"""
다음은 뉴스 제보 내용입니다.

설명:
\"{description}\"

이 제보는 이미지와 설명 간 유사도가 {similarity_score}입니다.
이 정보를 요약하고, 신뢰도를 '낮음/중간/높음' 중 하나로 판단해주세요.
출력 형식은 아래와 같게 해주세요.

[요약]
내용 요약 1~2문장

[신뢰도]
낮음 / 중간 / 높음 중 하나
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "너는 뉴스 제보를 정리하고 신뢰도를 분석하는 요약 전문가야."},
            {"role": "user", "content": prompt}
        ]
    )

    return response['choices'][0]['message']['content']

def classify_category(description):
    prompt = f"""
설명: "{description}"

이 사건의 유형을 하나 선택하세요:
[화재 / 교통사고 / 폭력 / 자연재해 / 기타]

형식: 카테고리: (선택한 항목)
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "너는 뉴스 제보 내용을 보고 카테고리를 분류하는 전문가야."},
            {"role": "user", "content": prompt}
        ]
    )

    return response['choices'][0]['message']['content']

def rate_importance(description):
    prompt = f"""
설명: "{description}"

이 제보의 중요도를 1~5점 척도로 판단해주세요.
1: 사소함 / 5: 매우 중대한 사건

형식: 중요도: (1~5)
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "너는 제보의 중요도를 평가하는 전문가야."},
            {"role": "user", "content": prompt}
        ]
    )

    return response['choices'][0]['message']['content']