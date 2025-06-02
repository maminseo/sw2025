# backend/utils.py

import os
import uuid
import json
import datetime
import sqlite3
from PIL import Image
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# 경로 설정
TEMP_DIR = os.path.join(os.path.dirname(__file__), "temp_images")
DB_FILE = os.path.join(os.path.dirname(__file__), "data", "collected.db")

# 이미지 임시 저장
def save_image_temp(image_file):
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

    filename = f"{uuid.uuid4().hex}.jpg"
    filepath = os.path.join(TEMP_DIR, filename)
    image_file.save(filepath)
    return filepath

# DB 초기화 (최초 1회만 실행됨)
def init_db():
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        description TEXT,
        image_path TEXT,
        similarity REAL,
        summary TEXT,
        category TEXT,
        importance TEXT,
        duplicate INTEGER,
        image_vector TEXT
    )
    ''')
    conn.commit()
    conn.close()

# 데이터 저장 (DB insert)
def save_collected_data(entry):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO submissions (
            timestamp, description, image_path, similarity, summary,
            category, importance, duplicate, image_vector
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        entry['timestamp'],
        entry['description'],
        entry['image_path'],
        float(entry['similarity']) if isinstance(entry['similarity'], (int, float)) else None,
        entry['summary'],
        entry['category'],
        entry['importance'],
        int(entry['duplicate']),
        json.dumps(entry['image_vector']) if entry['image_vector'] else None
    ))
    conn.commit()
    conn.close()

# 전체 데이터 로드 (DB select)
def load_collected_data():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute('SELECT * FROM submissions')
    rows = cur.fetchall()
    columns = [col[0] for col in cur.description]
    conn.close()

    data = []
    for row in rows:
        row_dict = dict(zip(columns, row))
        if row_dict.get("image_vector"):
            row_dict["image_vector"] = json.loads(row_dict["image_vector"])
        data.append(row_dict)
    return data

# 이미지 벡터 유사도 중복 감지
def check_duplicate(new_vector, old_vectors, threshold=0.85):
    old_vectors = [np.array(v) for v in old_vectors if v is not None]
    if not old_vectors:
        return False

    old_vectors = np.vstack(old_vectors)
    similarities = cosine_similarity([new_vector], old_vectors)

    return np.max(similarities) > threshold

# 현재 시간 타임스탬프 반환
def make_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
