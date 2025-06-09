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
    텍스트가 77 토큰을 초과하면 자동으로 자르되, 예외 발생을 사전에 방지함
    """
    while True:
        try:
            text_tensor = clip.tokenize([text]).to(device)
            break
        except RuntimeError:
            text = text[:-1]  # 한 글자씩 줄여서 재시도
            if len(text) == 0:
                raise ValueError("입력된 텍스트가 너무 짧습니다.")

    image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)

    with torch.no_grad():
        image_features = model.encode_image(image)
        text_features = model.encode_text(text_tensor)

        # 🔁 정규화 추가
        image_features /= image_features.norm(dim=-1, keepdim=True)
        text_features /= text_features.norm(dim=-1, keepdim=True)

        similarity = torch.nn.functional.cosine_similarity(image_features, text_features)
        return similarity.squeeze().item()

def get_clip_vector(image_path):
    """
    이미지 경로를 받아 CLIP 512차원 벡터를 추출 (numpy array로 반환)
    """
    image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)
    with torch.no_grad():
        image_features = model.encode_image(image)

        # 🔁 정규화 추가
        image_features /= image_features.norm(dim=-1, keepdim=True)

        return image_features[0].cpu().numpy()
