from opencc import OpenCC

import os
import requests
import chardet
import json


def delete_existing_file(path):
    if os.path.exists(path):
        print(f"Deleting pre-existing file {path}...........")
        os.remove(path)


def clear_directory(directory):
    for root, dirs, files in os.walk(directory, topdown=False):
        # Delete all files
        for file in files:
            file_path = os.path.join(root, file)
            os.remove(file_path)

        # Delete all empty subdirectories
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            os.rmdir(dir_path)


def write_append(text, filename):
    """Append decoded text to file."""
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "a", encoding="utf-8") as output_file:
            output_file.write(text)
    except Exception as e:
        print(f"[!] Failed to write file: {e}")


def write_overwrite(text, filename):
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w", encoding="utf-8") as output_file:
            output_file.write(text)
    except Exception as e:
        print(f"[!] Failed to write file: {e}")


def clean_txt(raw_txt, cleaned_txt, MATCH_STRINGS):
    print("\n[Cleaning Output]")
    # Step 1: Open and read the lines from the input file
    with open(raw_txt, "r") as file:
        lines = file.readlines()

    # Step 2: Filter the lines that do not contain any of the match_strings
    filtered_lines = [
        line for line in lines if not any(match in line for match in MATCH_STRINGS)
    ]

    # Step 3: Write the filtered lines to the output file
    with open(cleaned_txt, "w") as file:
        file.writelines(filtered_lines)

    check_sim_or_tra(cleaned_txt)

    print(f"[Done] Cleaned text saved to: {cleaned_txt}")


def detect_encoding(content):
    result = chardet.detect(content)
    return result["encoding"]


def getdataOnepage(url):
    r = requests.get(url)
    html = r.text.split("\n")


def get_links(url, curr, total):
    list = [url]
    if curr == 1:
        root = url.split(".html")[0]
        end = ".html"
        for i in range(2, total + 1):
            list.append(root + "_" + str(i) + end)
    print(list)
    return list


def read_txt(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
            return text
    except Exception as e:
        print(f"[Error] Failed to read file: {e}")
        return None


def check_sim_or_tra(path, threshold=0.8):
    """
    Heuristically detect whether text is Simplified or Traditional.
    Returns 'simplified', 'traditional', or 'undetermined'.
    """
    text = read_txt(path)
    # --- Take first 40 chars ---
    sample40 = text.strip()[:40]

    # Initialize both converters
    cc_t2s = OpenCC("t2s")
    cc_s2t = OpenCC("s2t")

    if not sample40:
        return "undetermined"

    # Convert both ways
    to_simplified = cc_t2s.convert(sample40)
    to_traditional = cc_s2t.convert(sample40)

    # Compare character overlap
    same_as_simplified = sum(1 for a, b in zip(sample40, to_simplified) if a == b)
    same_as_traditional = sum(1 for a, b in zip(sample40, to_traditional) if a == b)
    total = len(sample40)

    ratio_simplified = same_as_simplified / total
    ratio_traditional = same_as_traditional / total

    if ratio_simplified > ratio_traditional and ratio_simplified > threshold:
        print(
            "text is simplified, do nothing\n",
            f"ratio_simplified: {ratio_simplified}\n",
            f"ratio_traditional: {ratio_traditional}\n",
        )
        print("do nothing, already simplified")
    elif ratio_traditional > ratio_simplified and ratio_traditional > threshold:
        print(
            "text is traditional, converting ...\n",
            f"ratio_simplified: {ratio_simplified}\n",
            f"ratio_traditional: {ratio_traditional}\n",
        )
        simplified_text = cc_t2s.convert(text)
        write_overwrite(simplified_text, path)
        print("converted to simplified")
    else:
        print("undetermined whether text is simplified or traditional")

def read_json(path, key):
    try:
        with open(path, "r", encoding="utf-8") as f:
            dict = json.load(f)[key]
            return dict
    except Exception as e:
        print(f"[Error] Failed to read file: {e}")
        return None