import re
import sys


def extract_pua_chars(text: str):
    """Return a set of all PUA characters present in the given text."""
    # Match characters in Unicode Private Use Areas
    return set(re.findall(r'[\uE000-\uF8FF]', text))

text = "‌‌。"
print(extract_pua_chars(text))