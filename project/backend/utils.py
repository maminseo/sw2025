# backend/utils.py

import os
import uuid
import json
import datetime
from PIL import Image
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

TEMP_DIR = os.path.join(os.path.dirname(__file__), "temp_images")
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "collected.json")

def save_image_temp(image_file):
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

    filename = f"{uuid.uuid4().hex}.jpg"
    filepath = os.path.join(TEMP_DIR, filename)
    image_file.save(filepath)
    return filepath

def load_collected_data():
    if not os.path.exists(DB_PATH):
        return []
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_collected_data(entry):
    data = load_collected_data()
    data.append(entry)
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def check_duplicate(new_vector, old_vectors, threshold=0.85):
    if not old_vectors:
        return False
    similarities = cosine_similarity([new_vector], old_vectors)
    return np.max(similarities) > threshold

def make_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")