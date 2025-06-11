from flask import Flask, request, jsonify
from clip_module import get_clip_similarity, get_clip_vector, extract_keywords
from summary_module import generate_summary, classify_category, rate_importance
from utils import (
    save_image_temp, save_collected_data, load_collected_data,
    make_timestamp, check_duplicate, init_db, count_similar_reports
)
import numpy as np

app = Flask(__name__)
init_db()

# 🔥 키워드 리스트
FIRE_KEYWORDS = ["불", "화재", "연기", "화염", "폭발", "소방차", "불길"]
INJURY_KEYWORDS = ["사망", "사고", "실종", "익사", "부상", "추락"]

# ✅ 보정 함수
def adjust_similarity(description, image_path, original_score, category=None):
    has_fire_kw = any(k in description for k in FIRE_KEYWORDS)
    has_injury_kw = any(k in description for k in INJURY_KEYWORDS)
    is_fire_image = "fire" in image_path.lower() or "화재" in image_path.lower()

    adjusted = original_score

    if is_fire_image and not has_fire_kw:
        adjusted *= 0.1
    elif has_fire_kw and is_fire_image:
        adjusted *= 1.3
    elif has_fire_kw and category and "화재" in category:
        adjusted *= 1.1
    elif has_injury_kw and is_fire_image:
        adjusted *= 0.2

    return min(max(adjusted, 0), 1.0)


@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        description = request.form.get('description', '')
        image_file = request.files.get('image', None)

        if not description:
            return jsonify({'error': '설명이 필요합니다.'}), 400

        image_path = save_image_temp(image_file) if image_file else None

        # 1️⃣ GPT 요약 및 키워드 추출
        summary = generate_summary(description, similarity_score=None)
        keywords = extract_keywords(description)
        clip_description = summary + " " + keywords
        clip_description = clip_description[:300]

        # 2️⃣ CLIP 유사도 계산
        similarity_score = None
        image_vector = None
        if image_path:
            similarity_score = get_clip_similarity(image_path, clip_description)
            image_vector = get_clip_vector(image_path)

        # 3️⃣ GPT 기반 카테고리 분류 및 중요도 평가
        category = classify_category(description)
        importance = rate_importance(description)

        # 4️⃣ 유사도 보정
        if similarity_score is not None:
            similarity_score = adjust_similarity(description, image_path, similarity_score, category=category)

        # 5️⃣ 중복 검사 및 신뢰도 판단
        all_data = load_collected_data()
        existing_vectors = [d["image_vector"] for d in all_data if d.get("image_vector")]

        is_duplicate = False
        reliable = False
        similar_count = 0

        if image_vector is not None:
            is_duplicate = check_duplicate(image_vector, existing_vectors)
            similar_count = count_similar_reports(image_vector, existing_vectors)
            reliable = similar_count >= 5

        if isinstance(similarity_score, (int, float)):
            similarity_percent = round(similarity_score * 100, 1)
        else:
            similarity_percent = "이미지 없음"

        result_entry = {
            "timestamp": make_timestamp(),
            "description": description,
            "image_path": image_path,
            "similarity": float(similarity_score) if isinstance(similarity_score, (int, float)) else None,
            "summary": summary,
            "category": category,
            "importance": int(importance) if isinstance(importance, np.generic) else importance,
            "duplicate": bool(is_duplicate),
            "image_vector": image_vector.tolist() if image_vector is not None else None
        }
        save_collected_data(result_entry)

        return jsonify({
            "summary": summary,
            "similarity": similarity_percent,
            "category": category,
            "importance": importance,
            "duplicate": bool(is_duplicate),
            "reliable": reliable,
            "similar_count": similar_count
        })

    except Exception as e:
        print("💥 [ERROR] 예외 발생:", e)
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)