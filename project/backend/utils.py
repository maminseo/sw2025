# backend/utils.py

import os
import uuid

TEMP_DIR = os.path.join(os.path.dirname(__file__), "temp_images")

def save_image_temp(image_file):
    """
    업로드된 이미지 파일을 서버에 임시 저장하고 경로 반환
    """
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

    # 고유 파일명 생성
    filename = f"{uuid.uuid4().hex}.jpg"
    filepath = os.path.join(TEMP_DIR, filename)

    # 저장
    image_file.save(filepath)
    return filepath
