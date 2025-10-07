import requests
import chardet

def detect_encoding(content):
    result = chardet.detect(content)
    return result["encoding"]


url = ""  # Replace with the URL of the website you want to read

# Make an HTTP request to the website
response = requests.get(url)

if response.status_code == 200:
    # Detect the encoding of the content
    detected_encoding = detect_encoding(response.content)
    print(detect_encoding)

    # Decode the content using the detected encoding
    decoded_content = response.content.decode(detected_encoding)

    # Now 'decoded_content' contains the content of the website using the detected encoding
    print(decoded_content)
else:
    print(f"Failed to retrieve the web page. Status code: {response.status_code}")
