# backend/clip_module.py

import torch
import clip
from PIL import Image

# 디바이스 설정 (GPU 사용 가능하면 CUDA, 아니면 CPU)
device = "cuda" if torch.cuda.is_available() else "cpu"

# CLIP 모델과 전처리기 로드
model, preprocess = clip.load("ViT-B/32", device=device)

def get_clip_similarity(image_path, text):
    """
    이미지 경로와 설명 텍스트를 받아 CLIP 유사도 계산 (cosine similarity)
    """
    image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)
    text = clip.tokenize([text]).to(device)

    with torch.no_grad():
        image_features = model.encode_image(image)
        text_features = model.encode_text(text)
        similarity = torch.nn.functional.cosine_similarity(image_features, text_features)
        return similarity.squeeze().item()  # ✅ 텐서 조건 오류 방지

def get_clip_vector(image_path):
    """
    이미지 경로를 받아 CLIP 512차원 벡터를 추출 (numpy array로 반환)
    """
    image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)
    with torch.no_grad():
        image_features = model.encode_image(image)
        return image_features[0].cpu().numpy()
