"""
inference.py
------------
Loads the fine-tuned MuRIL model and runs headline prediction.
No IndicNLP dependency — uses unicodedata (Python stdlib) instead.
Model weights are auto-downloaded from Hugging Face Hub on first run.
"""

import os
import re
import unicodedata
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForMultipleChoice

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR       = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH     = os.path.join(BASE_DIR, "models", "muril_model")
TOKENIZER_PATH = os.path.join(BASE_DIR, "models", "tokenizer")

# ── Hugging Face Hub repo that stores the model weights ────────────────────────
# Set this to YOUR HF username/repo, e.g. "vedhvishnu/muril-hindi-headline"
HF_MODEL_REPO  = "Vedhvishnu/muril-hindi-headline"

# ── Config (must match training) ───────────────────────────────────────────────
MAX_LENGTH = 256
DEVICE     = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ── Lazy-loaded singletons ─────────────────────────────────────────────────────
_model     = None
_tokenizer = None


def _download_from_hub() -> None:
    """
    Download model + tokenizer from Hugging Face Hub into the local models/ dir.
    Called automatically the first time load_model() is invoked and the weights
    are not already on disk (e.g. on a fresh HF Spaces container).
    """
    from huggingface_hub import snapshot_download

    models_dir = os.path.join(BASE_DIR, "models")
    os.makedirs(models_dir, exist_ok=True)

    print(f"⏳ Downloading model weights from HF Hub ({HF_MODEL_REPO}) ...")
    snapshot_download(
        repo_id=HF_MODEL_REPO,
        local_dir=models_dir,
        local_dir_use_symlinks=False,   # write real files, not symlinks
        ignore_patterns=["*.msgpack", "flax_model*", "tf_model*"],  # skip non-PyTorch weights
    )
    print("✅ Download complete.")


def load_model():
    """Load model and tokenizer once; reuse on subsequent calls."""
    global _model, _tokenizer
    if _model is not None:
        return _model, _tokenizer

    # Auto-download weights from HF Hub if not present locally
    if not os.path.isdir(MODEL_PATH) or not os.path.isdir(TOKENIZER_PATH):
        if HF_MODEL_REPO == "YOUR_HF_USERNAME/muril-hindi-headline":
            raise RuntimeError(
                "Model weights not found locally and HF_MODEL_REPO is not set.\n"
                "Edit inference.py and replace YOUR_HF_USERNAME with your "
                "Hugging Face username."
            )
        _download_from_hub()

    print(f"Loading tokenizer from {TOKENIZER_PATH} ...")
    _tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_PATH)

    print(f"Loading MuRIL model from {MODEL_PATH} ...")
    _model = AutoModelForMultipleChoice.from_pretrained(MODEL_PATH)
    _model.to(DEVICE)
    _model.eval()
    print(f"✅ Model ready on {DEVICE}")

    return _model, _tokenizer


# ── Preprocessing (mirrors training, IndicNLP-free) ────────────────────────────
def preprocess_hindi(text: str) -> str:
    """
    Clean a Hindi text string.
    Matches the training preprocess_hindi() exactly, minus IndicNLP:
      - unicodedata NFC  ≈  IndicNormalizerFactory for common cases
      - Devanagari-only regex handles the rest
    """
    if not isinstance(text, str):
        return ""
    text = unicodedata.normalize("NFC", text)           # Unicode normalization
    text = re.sub(r"http\S+|www\.\S+", " ", text)       # Remove URLs
    text = re.sub(r"<[^>]+>", " ", text)                # Remove HTML tags
    # Keep only Devanagari Unicode block + digits + spaces
    text = re.sub(r"[^\u0900-\u097F\u0966-\u096F0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ── Inference ──────────────────────────────────────────────────────────────────
def predict_headline(article: str, options: list) -> dict:
    """
    Predict the correct headline for a Hindi news article.

    Args:
        article : Raw Hindi article text (preprocessing handled internally).
        options : Exactly 4 candidate headline strings.

    Returns:
        {
          'predicted_index'    : int (0-3),
          'predicted_headline' : str,
          'confidence_scores'  : {'option_0': float%, ..., 'option_3': float%},
          'all_options'        : list[str]
        }
    """
    if len(options) != 4:
        raise ValueError("Exactly 4 candidate options are required.")

    model, tokenizer = load_model()

    # ── Preprocess article ────────────────────────────────────────────────────
    art_clean = preprocess_hindi(article)

    # Smart truncation: keep first 100 + last 100 tokens if article is long
    tokens = art_clean.split()
    if len(tokens) > 200:
        art_clean = " ".join(tokens[:100] + tokens[-100:])

    # ── Tokenize 4 (article, option) pairs ───────────────────────────────────
    encodings = [
        tokenizer(
            art_clean,
            preprocess_hindi(opt),
            max_length=MAX_LENGTH,
            padding="max_length",
            truncation="only_first",   # truncate article, never the headline
            return_tensors="pt",
        )
        for opt in options
    ]

    # Shape: [1, 4, MAX_LENGTH]
    input_ids      = torch.stack([e["input_ids"].squeeze(0)      for e in encodings]).unsqueeze(0).to(DEVICE)
    attention_mask = torch.stack([e["attention_mask"].squeeze(0) for e in encodings]).unsqueeze(0).to(DEVICE)

    # ── Forward pass ──────────────────────────────────────────────────────────
    with torch.no_grad():
        logits = model(
            input_ids=input_ids,
            attention_mask=attention_mask
        ).logits.squeeze(0).cpu().numpy()   # shape: [4]

    # Numerically-stable softmax
    exp_l = np.exp(logits - logits.max())
    probs = exp_l / exp_l.sum()
    pred  = int(np.argmax(probs))

    return {
        "predicted_index"    : pred,
        "predicted_headline" : options[pred],
        "confidence_scores"  : {
            f"option_{i}": round(float(probs[i]) * 100, 2) for i in range(4)
        },
        "all_options": options,
    }
