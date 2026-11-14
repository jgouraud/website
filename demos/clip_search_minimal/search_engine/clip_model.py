"""Cached CLIP query encoder, with explicit startup loading and warmup."""
from __future__ import annotations

from functools import lru_cache
import os
from threading import Lock

import numpy as np
from PIL import Image, ImageOps

from search_engine.model_artifacts import verified_checkpoint_path
from search_engine.validation import read_reference_image, validate_description

_INFERENCE_LOCK = Lock()
_PRELOAD_LOCK = Lock()


@lru_cache(maxsize=1)
def _load_model():
    import clip
    import torch

    torch.set_num_threads(max(1, int(os.environ.get('CLIP_SEARCH_THREADS', min(4, os.cpu_count() or 1)))))
    checkpoint = verified_checkpoint_path()
    model, preprocess = clip.load(str(checkpoint), device='cpu')
    model.eval()
    return torch, model, preprocess


@lru_cache(maxsize=1)
def _tokenizer():
    from clip.simple_tokenizer import SimpleTokenizer
    return SimpleTokenizer()


@lru_cache(maxsize=1)
def _warm_model() -> None:
    _load_model()
    _tokenizer()
    embed_texts(['a mechanical part'])
    embed_images([Image.new('RGB', (224, 224), 'white')])


def preload_model() -> None:
    """Load model/tokenizer once and warm both encoders before enabling search."""
    with _PRELOAD_LOCK:
        _warm_model()


def embed_texts(texts: list[str]) -> np.ndarray:
    """Embed every token, averaging normalized chunks for CLIP's 77-token limit."""
    if len(texts) > 16:
        raise ValueError('Embed at most 16 descriptions per batch.')
    texts = [validate_description(text) for text in texts]
    torch, model, _ = _load_model()
    tokenizer = _tokenizer()
    token_rows, owners = [], []
    for owner, text in enumerate(texts):
        tokens = tokenizer.encode(text)
        for offset in range(0, max(1, len(tokens)), 75):
            chunk = [tokenizer.encoder['<|startoftext|>'], *tokens[offset:offset + 75], tokenizer.encoder['<|endoftext|>']]
            row = torch.zeros(77, dtype=torch.long)
            row[:len(chunk)] = torch.tensor(chunk)
            token_rows.append(row)
            owners.append(owner)
    if not texts:
        return np.empty((0, 512), dtype=np.float32)
    encoded = []
    with _INFERENCE_LOCK, torch.inference_mode():
        for offset in range(0, len(token_rows), 16):
            batch = model.encode_text(torch.stack(token_rows[offset:offset + 16])).float()
            encoded.extend((batch / batch.norm(dim=-1, keepdim=True)).cpu().numpy())
    result = np.zeros((len(texts), 512), dtype=np.float32)
    np.add.at(result, owners, np.asarray(encoded))
    return result / np.linalg.norm(result, axis=1, keepdims=True)


def embed_images(images: list[Image.Image]) -> np.ndarray:
    """Encode catalog and uploaded images with exactly the same preprocessing."""
    torch, model, preprocess = _load_model()
    if not images:
        return np.empty((0, 512), np.float32)
    colors = [preprocess(_pad_to_square(source)) for source in images]
    with _INFERENCE_LOCK, torch.inference_mode():
        color_vectors = model.encode_image(torch.stack(colors)).float()
        color_vectors /= color_vectors.norm(dim=-1, keepdim=True)
    return color_vectors.cpu().numpy()


def _pad_to_square(image: Image.Image) -> Image.Image:
    # Match the original query's 224px square normalization, without requiring
    # the former object detection / image update pipeline.
    image = ImageOps.exif_transpose(image).convert('RGB')
    width, height = image.size
    size = max(width, height)
    background = Image.new('RGB', (size, size), 'white')
    background.paste(image, ((size - width) // 2, (size - height) // 2))
    return background.resize((224, 224), Image.Resampling.LANCZOS)


def embed_query(text: str, image_bytes: bytes | None) -> tuple[np.ndarray | None, np.ndarray | None]:
    """Encode user text and the uploaded image for comparison with catalog images."""
    text_vector = embed_texts([text.strip()])[0] if text.strip() else None
    image_vector = None
    if image_bytes is not None:
        with read_reference_image(image_bytes) as source:
            image_vector = embed_images([source])[0]
    return text_vector, image_vector
