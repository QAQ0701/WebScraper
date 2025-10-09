from selenium.webdriver.common.by import By

from helper.utils import delete_existing_file
from jjwxc_helper.CONSTANTS_JJ import FONT_PATH, NETLOG_PATH, GLYPH_DIR, MAP_PATH
from jjwxc_helper.PUAglyph_to_image import render_given_pua_glyphs
from jjwxc_helper.glyphTOunicode import generate_map

import requests
import hashlib
import os
import json
import re
import time

# ======================================
#            VARIABLES
# ======================================
changed_font = True


# ======================================
#            HELPER FUNCTIONS
# ======================================
def get_font_url(driver):
    """
    Detect dynamically injected .woff2 font from network logs, download it,
    and save to FONT_PATH. Returns FONT_PATH if successful, else None.
    """
    logs = driver.get_log("performance")
    delete_existing_file(NETLOG_PATH)
    with open(NETLOG_PATH, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2)

    woff2_urls = []
    print(type(logs))

    for entry in logs:
        entry_json = json.loads(entry["message"])
        inner = entry_json["message"]
        params = inner.get("params", {})

        if (
            inner.get("method") == "Network.requestWillBeSent"
            and params.get("type") == "Font"
        ):
            font_url = params["request"]["url"]
            woff2_urls.append(font_url)

    # remove duplicates, preserve order
    woff2_urls = list(dict.fromkeys(woff2_urls))

    if not woff2_urls:
        print("[Font] No .woff2 font found in network logs.")
        return None
    if woff2_urls:
        # print("Found .woff2 URLs:", woff2_urls)
        font_url = woff2_urls[-1]  # usually the last one is the current font
        print("[Font] Found .woff2 via network:", font_url)
        return font_url


def download_font(font_url):
    # Ensure folder exists
    os.makedirs(os.path.dirname(FONT_PATH), exist_ok=True)

    try:
        r = requests.get(font_url, timeout=10)
        r.raise_for_status()
        with open(FONT_PATH, "wb") as f:
            f.write(r.content)
        print(f"[Font] Downloaded font → {FONT_PATH}")
        return FONT_PATH
    except Exception as e:
        print(f"[!] Failed to download font: {e}")
        # fallback if cached font exists
        if os.path.exists(FONT_PATH):
            print("[Font] Using cached font.")
            return FONT_PATH
        return None


def load_pua_map(json_path: str):
    """Load PUA → Unicode mapping from JSON file."""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Flatten the structure: {'': '样', '': '去', ...}
    mapping = {k: v["char"] for k, v in data.items() if "char" in v}
    return mapping


def decode_font(text: str, mapping: dict):
    """Decode PUA text using a precomputed mapping dict."""
    return "".join(mapping.get(ch, ch) for ch in text)


def compare_hash(url):
    """Check if the MD5 hash of the font file contents (and its binary) match."""
    last_font_hash = None
    # Check if file exists
    if os.path.exists(FONT_PATH):
        with open(FONT_PATH, "rb") as f:
            font_data_old = f.read()
            last_font_hash = hashlib.md5(font_data_old).hexdigest()
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            current_hash, font_data = hashlib.md5(r.content).hexdigest(), r.content

            if current_hash != last_font_hash:
                print(f"Deleting pre-existing font file ...")
                os.remove(FONT_PATH)
                print(f"[Font] Font changed. Downloading new font → {FONT_PATH}")
                os.makedirs(os.path.dirname(FONT_PATH), exist_ok=True)
                with open(FONT_PATH, "wb") as f:
                    f.write(font_data)
                global changed_font
                print(f"changed_font: {changed_font}, setting to True")
                changed_font = True
            else:
                print(f"changed_font: {changed_font}, setting to False")
                changed_font = False
                print("[Font] Font unchanged — reusing cached version.")
    except Exception as e:
        print(f"[!] Font hash check failed for {url}: {e}")
        return


# def validate_font():
#     """Return True/False if the MD5 hash of the font file contents (and its binary) match."""
#     """True if the font has changed, False otherwise."""
#     last_font_hash = None
#     new_font_hash = None
#     # Check if file exists
#     if os.path.exists(FONT_PATH):
#         with open(FONT_PATH, "rb") as f:
#             font_data_old = f.read()
#             last_font_hash = hashlib.md5(font_data_old).hexdigest()

#     if os.path.exists("scraper/cookies/jjwxcfont_7ui0o.woff2"):
#         with open("scraper/cookies/jjwxcfont_7ui0o.woff2", "rb") as f:
#             font_data_new = f.read()
#             new_font_hash = hashlib.md5(font_data_new).hexdigest()

#     if last_font_hash != new_font_hash:
#         print(True)
#     else:
#         print(False)


def extract_pua_chars(text: str):
    """Return a set of all PUA characters present in the given text."""
    # Match characters in Unicode Private Use Areas
    return set(re.findall(r"[\uE000-\uF8FF]", text))


def ensure_latest_font(driver):
    """
    Detect whether the font changed since last chapter.
    Return (font_path, new_font_hash, changed_flag)
    """
    font_url = get_font_url(driver)
    if font_url == None:
        print("[Font] Skipping font check.")
        return
    if not font_url:
        if not os.path.exists(FONT_PATH):
            raise FileNotFoundError(f"No cached font and no font found on page.")
        else:
            print("[Font] Using cached font.")
    else:
        if not os.path.exists(FONT_PATH):
            # if no previously cached font exists, download
            download_font(font_url)
        else:  # compare new url with cached font
            compare_hash(font_url)
    pseudo_mapping = get_pseudo_mapping(driver)
    print("Detected pseudo-content mapping:", pseudo_mapping)
    # Inject pseudo-content dynamically
    for selector, content in pseudo_mapping.items():
        script = f"""
        document.querySelectorAll('{selector}').forEach(el => {{
            el.textContent = '{content}' + el.textContent;
        }});
        """
        driver.execute_script(script)

def get_pseudo_mapping(driver):
    script = """
    let mapping = {};

    for (const sheet of document.styleSheets) {
        // Skip stylesheets we can't access (cross-origin)
        if (sheet.href && sheet.href.startsWith('http') && !sheet.href.includes(location.host)) continue;

        try {
            if (!sheet.cssRules) continue;
            for (const rule of sheet.cssRules) {
                if (!rule.selectorText) continue;

                // Only target rules that include ::before
                if (rule.selectorText.includes("::before")) {
                    const selectors = rule.selectorText.split(",");
                    const content = rule.style.getPropertyValue("content");
                    if (!content) continue;

                    const clean = content.replace(/^["']|["']$/g, ""); // strip quotes
                    // Handle multiple selectors like ".c_evt, .c_ngt::before"
                    for (let sel of selectors) {
                        sel = sel.replace("::before", "").trim();
                        mapping[sel] = clean;
                    }
                }
            }
        } catch (e) {
            continue;
        }
    }

    return mapping;
    """
    return driver.execute_script(script)


def is_content_loaded(driver):
    try:
        element = driver.find_element(By.CLASS_NAME, "novelbody")
        return "vip内容加载中..." not in element.text and element.text.strip() != ""
    except:
        return False


def decode_VIP(txt):
    if not os.path.exists(FONT_PATH):
        return txt  # fallback to raw text

    try:
        print(f"[Decoding VIP] Changed font?: {changed_font}")
        if changed_font:
            puas = extract_pua_chars(txt)
            # PUA to Image
            render_given_pua_glyphs(puas, FONT_PATH, GLYPH_DIR, 64)
            # #Image to UNICODE MAP
            print("\n[Generating Map]")
            generate_map(MAP_PATH)
            time.sleep(0.5)
        # --- Decode Font ---
        PUA_MAPPING = load_pua_map(MAP_PATH)
        return decode_font(txt, PUA_MAPPING)
    except Exception as e:
        print(f"[Error decoding VIP text]: {e}")
        return txt  # fallback to raw text
