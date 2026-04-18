---
title: Hindi Headline Oracle
emoji: 📰
colorFrom: yellow
colorTo: gray
sdk: gradio
sdk_version: 5.7.1
app_file: app.py
pinned: false
python_version: "3.12"
---

# 📰 Hindi Headline Oracle — शीर्षक भविष्यवक्ता

> **MuRIL-based 4-way multiple-choice classifier for Hindi news headlines**  
> 86% accuracy · IndicGLUE WSTP dataset · Interactive Gradio UI

---

## What It Does

Given a Hindi news article and **4 candidate headlines**, the model predicts which headline correctly belongs to the article. This is the Wikipedia Section Title Prediction (WSTP) task from the IndicGLUE benchmark.

| Model      | Val Accuracy | Test Accuracy |
|------------|-------------|---------------|
| TF-IDF Cosine | 52.88% | 51.79% |
| Word2Vec + XGBoost | ~72% | ~71% |
| **MuRIL (fine-tuned)** | **86.73%** | **86.11%** |

---

## Project Structure

```
HEADLINES_PRED/
├── app.py               ← Gradio UI (entry point)
├── inference.py         ← Model loading + prediction logic
├── upload_model.py      ← One-time script: upload weights to HF Hub
├── requirements.txt
├── .gitignore
├── README.md
└── models/              ← NOT in git — auto-downloaded from HF Hub at runtime
    ├── muril_model/     ← Fine-tuned MuRIL weights
    └── tokenizer/       ← MuRIL tokenizer files
```

---

## Local Setup & Run

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/HEADLINES_PRED.git
cd HEADLINES_PRED
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set your HF Hub model repo
In `inference.py`, set:
```python
HF_MODEL_REPO = "your-hf-username/muril-hindi-headline"
```
The app will auto-download model weights on first run.

### 4. Launch
```bash
python app.py
```
Opens at `http://localhost:7860`

---

## How Inference Works

```
User Input (raw Hindi text)
        ↓
preprocess_hindi()         ← unicodedata NFC + Devanagari regex
        ↓
MuRIL Tokenizer            ← [CLS] article [SEP] option_i [SEP]  × 4
        ↓
AutoModelForMultipleChoice ← fine-tuned on IndicGLUE WSTP Hindi
        ↓
Softmax over 4 logits      ← confidence scores
        ↓
Predicted headline + confidence bars
```

---

## Model Details

| Setting | Value |
|---------|-------|
| Base model | `google/muril-base-cased` |
| Task | `AutoModelForMultipleChoice` |
| Max length | 256 tokens |
| Batch size | 8 (effective 32 with grad accum) |
| Learning rate | 2e-5 |
| Epochs | 5 (early stopping patience 2) |
| Dataset | `ai4bharat/indic_glue` — `wstp.hi` |
| Train size | 44,069 samples |
| Val / Test | 5,509 each |

---

## Dataset

[IndicGLUE](https://huggingface.co/datasets/ai4bharat/indic_glue) — Wikipedia Section Title Prediction (`wstp.hi`)

Each sample has:
- `sectionText` → Hindi Wikipedia article body
- `titleA / titleB / titleC / titleD` → 4 candidate section titles
- `correctTitle` → the ground-truth title (label 0–3)

---

*Built with MuRIL · IndicGLUE · Gradio · PyTorch · HuggingFace Transformers*
