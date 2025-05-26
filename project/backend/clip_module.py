# backend/clip_module.py

import torch
import clip
from PIL import Image

# CLIP 모델과 전처리기 로드 (한 번만 로딩)
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

def get_clip_similarity(image_path, text):
    """
    이미지 경로와 설명 텍스트를 받아 CLIP 유사도 계산
    """
    # 이미지와 텍스트 전처리
    image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)
    text = clip.tokenize([text]).to(device)

    # 피처 추출
    with torch.no_grad():
        image_features = model.encode_image(image)
        text_features = model.encode_text(text)

        # 유사도 계산 (cosine similarity)
        similarity = torch.nn.functional.cosine_similarity(image_features, text_features)
        return similarity.item()
