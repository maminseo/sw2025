from flask import Flask, request, jsonify
from clip_module import get_clip_similarity, get_clip_vector
from summary_module import generate_summary, classify_category, rate_importance
from utils import (
    save_image_temp, save_collected_data, load_collected_data,
    make_timestamp, check_duplicate, init_db, count_similar_reports
)
import numpy as np

# 앱 초기화 및 DB 준비
app = Flask(__name__)
init_db()

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        description = request.form.get('description', '')
        image_file = request.files.get('image', None)

        if not description:
            return jsonify({'error': '설명이 필요합니다.'}), 400

        # 이미지 저장
        image_path = save_image_temp(image_file) if image_file else None

        # GPT 요약 먼저 실행
        summary = generate_summary(description, similarity_score=None)
        clip_description = summary  # 요약문을 CLIP에 사용할 텍스트

        # CLIP 유사도 및 벡터 계산
        similarity_score = None
        image_vector = None
        if image_path:
            similarity_score = get_clip_similarity(image_path, clip_description)
            image_vector = get_clip_vector(image_path)

        # 카테고리/중요도 (원본 설명 기반)
        category = classify_category(description)
        importance = rate_importance(description)

        # 유사 제보 중복 검사
        all_data = load_collected_data()
        existing_vectors = [d["image_vector"] for d in all_data if d.get("image_vector")]

        is_duplicate = False
        reliable = False
        similar_count = 0

        if image_vector is not None:
            is_duplicate = check_duplicate(image_vector, existing_vectors)
            similar_count = count_similar_reports(image_vector, existing_vectors)
            reliable = similar_count >= 5


        # similarity % 환산 (숫자일 경우만)
        if isinstance(similarity_score, (int, float)):
            similarity_percent = round(similarity_score * 100, 1)
        else:
            similarity_percent = "이미지 없음"

        # DB 저장
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

        # 응답 반환
        return jsonify({
            "summary": summary,
            "similarity": similarity_percent,  # 이미지 없을 땐 "이미지 없음"
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
