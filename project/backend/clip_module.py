import torch
import clip
from PIL import Image
from konlpy.tag import Okt

device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

def get_clip_similarity(image_path, text):
    while True:
        try:
            text_tensor = clip.tokenize([text]).to(device)
            break
        except RuntimeError:
            text = text[:-1]
            if len(text) == 0:
                raise ValueError("입력된 텍스트가 너무 짧습니다.")

    image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)

    with torch.no_grad():
        image_features = model.encode_image(image)
        text_features = model.encode_text(text_tensor)
        image_features /= image_features.norm(dim=-1, keepdim=True)
        text_features /= text_features.norm(dim=-1, keepdim=True)
        similarity = torch.nn.functional.cosine_similarity(image_features, text_features)
        return similarity.squeeze().item()

def get_clip_vector(image_path):
    image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)
    with torch.no_grad():
        image_features = model.encode_image(image)
        image_features /= image_features.norm(dim=-1, keepdim=True)
        return image_features[0].cpu().numpy()

def extract_keywords(text, top_n=10):
    okt = Okt()
    nouns = okt.nouns(text)
    freq = {}
    for n in nouns:
        freq[n] = freq.get(n, 0) + 1
    sorted_nouns = sorted(freq.items(), key=lambda x: -x[1])
    keywords = [n[0] for n in sorted_nouns[:top_n]]
    return ' '.join(keywords)