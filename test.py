import torch
from transformers import AutoModelForMultipleChoice

print("Loading model...")
model = AutoModelForMultipleChoice.from_pretrained("models/muril_model")
print("Model loaded!")
