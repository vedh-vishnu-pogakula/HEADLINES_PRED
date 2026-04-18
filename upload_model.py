"""
upload_model.py
---------------
ONE-TIME SCRIPT: Uploads your local model weights to Hugging Face Hub.
Run this ONCE from your local machine before deploying to HF Spaces.

Usage:
    pip install huggingface_hub
    python upload_model.py
"""

import os
from huggingface_hub import HfApi, login

# ── CONFIG — edit these two lines ────────────────────────────────────────────
HF_USERNAME  = "YOUR_HF_USERNAME"          # your Hugging Face username
REPO_NAME    = "muril-hindi-headline"      # name for the new model repo
# ──────────────────────────────────────────────────────────────────────────────

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR   = os.path.join(BASE_DIR, "models")
REPO_ID      = f"{HF_USERNAME}/{REPO_NAME}"


def main():
    print("🔐 Logging in to Hugging Face Hub ...")
    login()   # opens browser or prompts for token

    api = HfApi()

    # Create the repo if it doesn't exist
    print(f"\n📦 Creating repo '{REPO_ID}' (if it doesn't exist) ...")
    api.create_repo(repo_id=REPO_ID, repo_type="model", exist_ok=True, private=False)
    print(f"✅ Repo ready: https://huggingface.co/{REPO_ID}")

    # Upload the entire models/ folder preserving subdirectory structure
    print(f"\n⏳ Uploading models/ folder (~912 MB, may take several minutes) ...")
    api.upload_folder(
        folder_path=MODELS_DIR,
        repo_id=REPO_ID,
        repo_type="model",
        commit_message="Add fine-tuned MuRIL weights and tokenizer",
    )

    print(f"\n🎉 Done! Model uploaded to: https://huggingface.co/{REPO_ID}")
    print(f"\nNext: Set HF_MODEL_REPO = \"{REPO_ID}\" in inference.py")


if __name__ == "__main__":
    main()
