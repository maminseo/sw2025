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
이 정보를 반드시 간결하게 요약하고, 신뢰도를 '낮음/중간/높음' 중 하나로 판단해주세요.
추가 설명이나 사족 없이, 아래 형식 그대로만 출력하세요.

출력 형식:

[요약]
(1~2문장 요약)

[신뢰도]
낮음 / 중간 / 높음
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

다음 중 가장 적절한 사건 유형을 선택하세요:
[화재 / 교통사고 / 폭력 / 자연재해 / 인명 사고 / 기타]

[화재] 불이 발생한 사건 (예: 건물 화재, 차량 화재 등)
[교통사고] 차량 충돌이나 도로에서의 사고
[폭력] 사람 간의 물리적 충돌, 공격, 위협 등 (예: 싸움, 칼부림, 폭행 등)
[자연재해] 기후나 자연 현상으로 인한 사건 (예: 홍수, 지진, 태풍 등)
[인명 사고] 사람의 부상, 사망, 실종, 추락 등 인적 피해 중심 사건 (예: 익사, 실종, 추락 등)
[기타] 위 항목에 해당하지 않는 기타 사건

출력 형식: 카테고리: (선택한 항목)
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "너는 뉴스 제보 내용을 분석하여 사건 유형을 분류하는 전문가야."},
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
            {"role": "system", "content": "너는 뉴스 제보의 중요도를 평가하는 전문가야."},
            {"role": "user", "content": prompt}
        ]
    )

    return response['choices'][0]['message']['content']