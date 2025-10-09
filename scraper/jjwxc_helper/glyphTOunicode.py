from paddleocr import PaddleOCR
from PIL import Image, ImageOps, ImageFilter

from .CONSTANTS_JJ import GLYPH_DIR, VIP, DEBUG_IMG_DIR

import json
import os
import io
import numpy as np
import re
import logging


# ======================================
#            CONFIG
# ======================================
logger = logging.getLogger(__name__)  # child logger
logger.info("This is a message from glyphTOunicode.py")

# ======================================
#            VARIABLES
# ======================================
OCR = (
    PaddleOCR(
        lang="ch",
        det_model_dir=None,
        use_angle_cls=False,
    )
    if VIP
    else None
)

# ======================================
#            CONSTANTS
# ======================================
# Paths
# PATH = "scraper/jjwxc_helper/debug/issue_glyphs"  # debug
OUTPUT_JSON_DEFAULT = "scraper/jjwxc_helper/data"
TEMP_PATH = "scraper/jjwxc_helper/data/modImg.png"

# Load full character dict from config.json
with open(
    "/Users/o_o/.paddlex/official_models/PP-OCRv5_server_rec/config.json",
    "r",
    encoding="utf-8",
) as f:
    cfg = json.load(f)

# char_list = cfg["PostProcess"]["character_dict"]

# # Filter only Chinese characters
# ch_only = [ch for ch in char_list if re.match(r"^[\u4e00-\u9fff]$", ch)]


def delete_existing_file(path):
    if os.path.exists(path):
        logging.info(f"Deleting pre-existing file {path}...........")
        os.remove(path)


def to_rgb(arr):
    """Convert a grayscale 2D array to H x W x 3 RGB array."""
    if len(arr.shape) == 2:  # grayscale
        arr = np.stack([arr] * 3, axis=-1)  # duplicate channels
    return arr


def preprocess_image(arr):
    """Optional preprocessing to improve recognition: add padding and resize to 128x128"""
    img = Image.fromarray(arr)
    img = img.convert("L")  # grayscale
    img = img.filter(ImageFilter.MaxFilter(3))
    img = ImageOps.expand(img, border=10, fill=255)  # add padding
    img = img.resize((150, 150), Image.LANCZOS)

    arr = np.array(img)
    arr = to_rgb(arr)
    return arr

    # output = TEMP_PATH
    # img.save(output)
    # return output


def thicken_image(input, iterations=2):
    # Open and convert to grayscale
    img = Image.open(input).convert("L")
    img = ImageOps.invert(img)  # text black on white

    # Convert to binary
    img_bin = img.point(lambda x: 0 if x < 128 else 255, "1")

    # Convert to numpy for dilation
    arr = np.array(img_bin, dtype=np.uint8)
    for _ in range(iterations):
        # Dilate: expand black pixels
        arr = np.minimum(
            255,
            arr
            + np.roll(arr, 1, axis=0)
            + np.roll(arr, -1, axis=0)
            + np.roll(arr, 1, axis=1)
            + np.roll(arr, -1, axis=1),
        )

    # Convert back to image
    img_thick = Image.fromarray(arr).convert("L")
    img_thick = ImageOps.invert(img_thick)  # invert back if needed
    threshold = 250
    arr = np.array(img_thick)
    arr = np.where(arr < threshold, 0, 255).astype(np.uint8)  # black or white
    arr = to_rgb(arr)
    return arr

    # img_bw = Image.fromarray(arr)
    # output = TEMP_PATH
    # img_bw.save(output)
    # return output


def generate_map(output_path=OUTPUT_JSON_DEFAULT):
    # # Initialize PaddleOCR in recognition-only mode
    # ocr = PaddleOCR(
    #     lang="ch",
    #     det_model_dir=None,
    #     use_angle_cls=False,
    # )
    results = {}
    failed = []
    delete_existing_file(output_path)
    img_files = [f for f in os.listdir(GLYPH_DIR) if f.endswith(".png")]

    logging.info(f"Found {len(img_files)} images. Starting OCR...")

    for i, img_file in enumerate(img_files, 1):
        path = os.path.join(GLYPH_DIR, img_file)
        logging.info(f"[{i}/{len(img_files)}] Processing {img_file}...")

        # First attempt
        ocr_result = OCR.predict(path)

        char = None
        score = 0.0

        if ocr_result and ocr_result[0].get("rec_texts"):
            char = ocr_result[0]["rec_texts"][0]
            score = float(ocr_result[0]["rec_scores"][0])

        if char == "EE":
            char = "出"
        if char == "出":
            score = 0.88

        # Retry if OCR failed or confidence is below 0.9
        if score < 0.9:
            logging.debug(
                f"  → Low confidence ({score:.4f}) or no detection, retrying with thickening..."
            )
            arr = thicken_image(path, iterations=3)
            ocr_result_retry = OCR.predict(arr)
            if ocr_result_retry and ocr_result_retry[0].get("rec_texts"):
                char = ocr_result_retry[0]["rec_texts"][0]
                score = float(ocr_result_retry[0]["rec_scores"][0])
                if char == "其":
                    logging.debug(f"  → Found '其', setting score to 0.86...")
                    score = 0.86
            if score < 0.85:
                logging.debug(
                    f"  → Still low confidence ({score:.4f}), trying preprocessing"
                )
                ocr_result_retry = OCR.predict(preprocess_image(arr))
                if ocr_result_retry and ocr_result_retry[0].get("rec_texts"):
                    char = ocr_result_retry[0]["rec_texts"][0]
                    score = float(ocr_result_retry[0]["rec_scores"][0])
                if score < 0.8:
                    logging.debug(
                        f"  → Still low confidence ({score:.4f}), trying slimming"
                    )
                    ocr_result_retry = OCR.predict(
                        preprocess_image(thicken_image(path, iterations=2))
                    )
                    if ocr_result_retry and ocr_result_retry[0].get("rec_texts"):
                        char = ocr_result_retry[0]["rec_texts"][0]
                        score = float(ocr_result_retry[0]["rec_scores"][0])
                    if score < 0.83:
                        logging.error(
                            f"  → Failed to recognize ({score:.4f}), skipping..."
                        )
                        failed.append(f"{char}{img_file}")

        # Split filename and extension
        name, ext = os.path.splitext(img_file)
        score_trunc = int(score * 100)
        old_path = f"{GLYPH_DIR}/{img_file}"
        codepoint = img_file[2:6]
        if char == "X":
            char = "又"
        if char == "茸":
            char = "真"
        if char == "田":
            char = "由"
        if char == "+":
            char = "十"
        if char == "□" or char == "口":
            char = "口"
        if char == "24":
            char = "好"
        if char == "K":
            char = "下"

        if score < 0.8:
            if char == "我":
                char = "等"
            if char == "E":
                char = "而"
            if char == "2":
                char = "气"
            if char == "四":
                char = "自"
            if char == "→":
                char = "个"
            if char == "章":
                char = "真"
            if char == "茸":
                char = "真"
            if char == "几":
                char = "己"
            new_dir = f"{DEBUG_IMG_DIR}/{name}_{char}_{score_trunc}{ext}"
            # Make sure target directory exists
            os.makedirs(DEBUG_IMG_DIR, exist_ok=True)
            # Move/rename file
            os.rename(old_path, new_dir)
            logging.info(f"Moved {old_path} -> {new_dir}")

        # Add character at the end (e.g., "_A")
        new_name = f"{GLYPH_DIR}/{name}_{char}_{score_trunc}{ext}"
        # Rename the file
        os.rename(old_path, new_name)

        if char:
            logging.info(f"  → Recognized as: {char} (confidence: {score:.4f})")
        else:
            logging.warning(
                f"  → Failed to recognize ({new_name}, confidence: {score:.4f})"
            )

    logging.warning(f"\nFailed to recognize {len(failed)} images:")
    for f in failed:
        logging.warning(f"  {f}")
        results[chr(int(codepoint, 16))] = {"char": char, "confidence": score}
    # Save results
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    logging.info(f"OCR done! Results saved to: {output_path}")


# generate_map("scraper/cookies/map.json") # debug
