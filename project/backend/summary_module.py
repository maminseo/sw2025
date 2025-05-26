# backend/summary_module.py

import openai

# 👉 여기에 본인 OpenAI API 키를 입력
openai.api_key = "your-openai-api-key"

def generate_summary(description, similarity_score):
    """
    사용자 설명 + CLIP 유사도를 기반으로 GPT에게 요약 요청
    """
    prompt = f"""
다음은 뉴스 제보 내용입니다.

설명:
\"{description}\"

이 제보는 이미지와 설명 간 유사도가 {similarity_score:.2f}입니다.
이 정보를 요약하고, 신뢰도를 '낮음/중간/높음' 중 하나로 판단해주세요.
출력 형식은 아래와 같게 해주세요.

[요약]
내용 요약 1~2문장

[신뢰도]
낮음 / 중간 / 높음 중 하나
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",  # gpt-3.5-turbo도 가능
        messages=[
            {"role": "system", "content": "너는 뉴스 제보를 정리하고 신뢰도를 분석하는 요약 전문가야."},
            {"role": "user", "content": prompt}
        ]
    )

    return response['choices'][0]['message']['content']
