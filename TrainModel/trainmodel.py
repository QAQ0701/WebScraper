import os
import shutil
from pathlib import Path

# --- USER CONFIG ---
DATASET_DIR = "dataset_images"  # folder containing your 200 images
LABEL_FILE = "labels.txt"       # file containing mapping: img_name character
OUTPUT_DIR = "paddleocr_dataset"
PRETRAINED_MODEL = "path_to_ppocrv5_rec_pretrained"  # download from PaddleOCR model zoo
TRAIN_CONFIG = "rec_ppocr_custom.yml"
TRAIN_SPLIT_RATIO = 0.8  # 80% train, 20% val
NUM_EPOCHS = 50
LEARNING_RATE = 1e-4

# --- Step 1: Prepare PaddleOCR dataset structure ---
train_dir = Path(OUTPUT_DIR)/"train"
val_dir = Path(OUTPUT_DIR)/"val"
train_dir.mkdir(parents=True, exist_ok=True)
val_dir.mkdir(parents=True, exist_ok=True)

train_label_lines = []
val_label_lines = []

# Read your labels
with open(LABEL_FILE, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Shuffle lines
import random
random.shuffle(lines)

split_idx = int(len(lines) * TRAIN_SPLIT_RATIO)

for i, line in enumerate(lines):
    img_name, char_label = line.strip().split()
    src_path = Path(DATASET_DIR)/img_name
    if i < split_idx:
        dst_path = train_dir/img_name
        train_label_lines.append(f"train/{img_name} {char_label}\n")
    else:
        dst_path = val_dir/img_name
        val_label_lines.append(f"val/{img_name} {char_label}\n")
    shutil.copy(src_path, dst_path)

# Save label files
with open(Path(OUTPUT_DIR)/"train_label.txt", "w", encoding="utf-8") as f:
    f.writelines(train_label_lines)
with open(Path(OUTPUT_DIR)/"val_label.txt", "w", encoding="utf-8") as f:
    f.writelines(val_label_lines)

print("✅ Dataset conversion complete.")

# --- Step 2: Create ppocr_keys_custom.txt ---
chars = set()
for line in lines:
    chars.add(line.strip().split()[1])

with open("ppocr_keys_custom.txt", "w", encoding="utf-8") as f:
    f.writelines([c+"\n" for c in sorted(chars)])

print("✅ Custom character list created.")

# --- Step 3: Create minimal training config ---
train_config_content = f"""
Global:
  algorithm: CRNN
  use_gpu: True
  epoch_num: {NUM_EPOCHS}
  log_smooth_window: 20
  print_batch_step: 1
  save_epoch_step: 5
  eval_batch_step: 0
  train_batch_size_per_card: 8
  eval_batch_size_per_card: 8
  image_shape: [3, 32, 32]
  character_type: "ch"
  character_dict_path: "ppocr_keys_custom.txt"
  max_text_length: 1
  pretrained_model: "{PRETRAINED_MODEL}"
  checkpoints: "output_rec"
  save_inference_dir: "inference"
  save_res_path: "result.json"
  distributed: False
  infer_img: "doc/imgs_words/ch/word_1.jpg"
  use_space_char: False

Optimizer:
  name: Adam
  beta1: 0.9
  beta2: 0.999
  lr: {LEARNING_RATE}

Loss:
  name: CTC

Architecture:
  name: CRNN

Train:
  dataset:
    name: SimpleDataSet
    data_dir: "{OUTPUT_DIR}"
    label_file_list: ["{OUTPUT_DIR}/train_label.txt"]
    transforms:
      - DecodeImage:
          img_mode: "BGR"
          channel_first: False
      - RecAug:
          name: RecAug
    shuffle: True

Eval:
  dataset:
    name: SimpleDataSet
    data_dir: "{OUTPUT_DIR}"
    label_file_list: ["{OUTPUT_DIR}/val_label.txt"]
    transforms:
      - DecodeImage:
          img_mode: "BGR"
          channel_first: False
"""

with open(TRAIN_CONFIG, "w", encoding="utf-8") as f:
    f.write(train_config_content)

print(f"✅ Training config saved to {TRAIN_CONFIG}")

# --- Step 4: Start fine-tuning ---
import subprocess

subprocess.run([
    "python3", "tools/train.py",
    "-c", TRAIN_CONFIG,
    "-o", f"Global.pretrained_model={PRETRAINED_MODEL}"
])
