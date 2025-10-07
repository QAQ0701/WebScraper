from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

from helper.utils import clear_directory
from .CONSTANTS_JJ import GLYPH_DIR, FONT_PATH

import os
import re

WOFF2_PATH = FONT_PATH
OUTPUT_DIR = GLYPH_DIR


def extract_pua_chars(text: str):
    """Return a set of all PUA characters present in the given text."""
    # Match characters in Unicode Private Use Areas
    return set(re.findall(r"[\uE000-\uF8FF]", text))


def render_pua_glyphs(font_path, output_dir="glyphs", size=64):
    """
    Render all PUA glyphs (U+E000–U+F8FF) in a JJWXC font to individual PNG files.

    font_path: path to .woff2 or .ttf font file
    output_dir: folder to save images
    size: font render size in pixels
    """
    os.makedirs(output_dir, exist_ok=True)
    font = TTFont(font_path)
    cmap = font["cmap"].getBestCmap()
    img_font = ImageFont.truetype(font_path, size)

    count = 0
    for codepoint in sorted(cmap.keys()):
        if 0xE000 <= codepoint <= 0xF8FF:  # Only Private Use Area
            ch = chr(codepoint)
            img = Image.new("L", (size + 16, size + 16), 255)
            draw = ImageDraw.Draw(img)
            draw.text((8, 0), ch, font=img_font, fill=0)
            filename = f"{output_dir}/U+{codepoint:04X}.png"
            img.save(filename)
            count += 1
    print(f"Rendered {count} PUA glyphs to '{output_dir}'.")


def render_given_pua_glyphs(given, font_path, output_dir="glyphs", size=64):
    """
    Render only the specified PUA glyphs (U+E000–U+F8FF) from a JJWXC font file.

    Parameters
    ----------
    given : iterable
        Iterable of PUA characters (e.g., {'\ue613', '\ue881', ...})
    font_path : str
        Path to .woff2 or .ttf font file.
    output_dir : str
        Directory to save rendered PNGs.
    size : int
        Font render size in pixels.

    Each glyph is saved as 'U+XXXX.png' under output_dir.
    """
    clear_directory(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    # Load font using both TTFont (to check cmap) and Pillow (to render)
    ttfont = TTFont(font_path)
    cmap = ttfont["cmap"].getBestCmap()
    img_font = ImageFont.truetype(font_path, size)

    rendered_count = 0

    for ch in given:
        codepoint = ord(ch)
        if not (0xE000 <= codepoint <= 0xF8FF):
            print(f"[Skip] {ch} (U+{codepoint:04X}) not in PUA range.")
            continue
        if codepoint not in cmap:
            print(f"[⚠️ Missing] Font does not contain glyph for U+{codepoint:04X}")
            continue

        img = Image.new("L", (size + 16, size + 16), 255)
        draw = ImageDraw.Draw(img)

        # Centering the glyph roughly
        try:
            bbox = img_font.getbbox(ch)
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        except AttributeError:
            w, h = draw.textsize(ch, font=img_font)

        x = (img.width - w) / 2
        y = (img.height - h) / 2
        draw.text((x, y), ch, font=img_font, fill=0)

        filename = f"{output_dir}/U+{codepoint:04X}.png"
        img.save(filename)
        # print(f"[Saved] {filename}")
        rendered_count += 1
    print(
        f"\n✅ Rendered {rendered_count}/{len(given)} given PUA glyphs to '{output_dir}'."
    )


# #Example usage:
# render_pua_glyphs(
#     WOFF2_PATH,
#     OUTPUT_DIR,
#     size=64,
# )


# text = "‌她，‌了, 站起‌‌，, ‌,寓‌‌, ‌悄‌，没‌‌。"
# glyphs = extract_pua_chars(text)

# render_given_pua_glyphs(
#     glyphs,
#     WOFF2_PATH,
#     OUTPUT_DIR,
#     size=64,
# )
