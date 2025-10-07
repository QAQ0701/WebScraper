from paddleocr import PaddleOCR
from PIL import Image, ImageOps
import numpy as np

PATH = "scraper/jjwxc_glyphs24/U+E155_口_口_口.png"


def preprocess_image(path):
    """Optional preprocessing to improve recognition."""
    img = Image.open(path).convert("L")
    # img = img.filter(ImageFilter.MaxFilter(3))
    img = ImageOps.expand(img, border=10, fill=255)
    img = img.resize((150, 150), Image.LANCZOS)
    temp_path = path.replace(".png", "_preprocessed.png")
    img.save("./output/modImg.png")
    img.save(temp_path)
    return temp_path


def thicken_image(path, output_path=None, iterations=1):
    # Open and convert to grayscale
    img = Image.open(path).convert("L")
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
    img_bw = Image.fromarray(arr)

    if output_path:
        img_bw.save(output_path)
    return output_path


thickened_img = thicken_image(PATH, "./output/thickened.png", iterations=2)


# TEST = preprocess_image(thickened_img)
TEST = thickened_img

ocr = PaddleOCR(
    lang="ch",
    det_model_dir=None,
    use_angle_cls=False,
)
ocr_result = ocr.predict(TEST)
# ocr_result = ocr.predict("./output/thickened.png")
# Extract recognized text and confidence
if ocr_result and ocr_result[0].get("rec_texts"):
    recognized = ocr_result[0]["rec_texts"][0]
    confidence = float(ocr_result[0]["rec_scores"][0])
    print(f"Image: {PATH}")
    print(f"Recognized character: '{recognized}'")
    print(f"Confidence: {confidence:.2%}")
else:
    print(f"Image: {PATH}")
    print("No text detected")

# print(f"OCR result: {ocr_result}")
