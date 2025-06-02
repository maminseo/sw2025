# backend/app.py
# pip install -r requirements.txt
# pip install git+https://github.com/openai/CLIP.git

from flask import Flask, request, jsonify
from clip_module import get_clip_similarity, get_clip_vector
from summary_module import generate_summary, classify_category, rate_importance
from utils import (
    save_image_temp, save_collected_data, load_collected_data,
    make_timestamp, check_duplicate, init_db
)
init_db()

import numpy as np

app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        description = request.form.get('description', '')
        image_file = request.files.get('image', None)

        # 설명 없이 들어오면 에러
        if not description:
            return jsonify({'error': '설명이 필요합니다.'}), 400

        # 1. 이미지 저장 (있다면)
        image_path = None
        if image_file:
            image_path = save_image_temp(image_file)
        
        # 2. CLIP 유사도/벡터
        similarity_score = None
        image_vector = None
        if image_path:
            similarity_score = get_clip_similarity(image_path, description)
            image_vector = get_clip_vector(image_path)
        else:
            similarity_score = "이미지 없음"

        # 3. GPT 요약
        summary = generate_summary(description, similarity_score)

        # 4. GPT 카테고리 분류
        category = classify_category(description)

        # 5. GPT 중요도 점수 (1~5)
        importance = rate_importance(description)

        # 6. 유사 제보 검사
        all_data = load_collected_data()
        existing_vectors = [d["image_vector"] for d in all_data if d.get("image_vector")]

        is_duplicate = False
        if image_vector is not None:
            is_duplicate = check_duplicate(image_vector, existing_vectors)

        # 7. DB 저장
        result_entry = {
            "timestamp": make_timestamp(),
            "description": description,
            "image_path": image_path,
            "similarity": float(similarity_score) if isinstance(similarity_score, np.generic) else similarity_score,
            "summary": summary,
            "category": category,
            "importance": int(importance) if isinstance(importance, np.generic) else importance,
            "duplicate": is_duplicate,
            "image_vector": image_vector.tolist() if image_vector is not None else None
        }
        save_collected_data(result_entry)

        # 8. 결과 전송
        return jsonify({
            "summary": summary,
            "similarity": similarity_score,
            "category": category,
            "importance": importance,
            "duplicate": is_duplicate
        })

    except Exception as e:
        print("💥 [ERROR] 예외 발생:", e)
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)