# backend/app.py

from flask import Flask, request, jsonify
from clip_module import get_clip_similarity
from summary_module import generate_summary
from utils import save_image_temp

app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # 설명 받기
        description = request.form.get('description')
        image_file = request.files['image']

        # 이미지 임시 저장
        image_path = save_image_temp(image_file)

        # CLIP 유사도 분석
        similarity_score = get_clip_similarity(image_path, description)

        # GPT 요약 및 평가
        summary_text = generate_summary(description, similarity_score)

        return jsonify({
            'similarity': round(similarity_score, 3),
            'summary': summary_text
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
