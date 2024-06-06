import pytesseract
import re
from PIL import Image

# r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# '/app/.apt/usr/bin/tesseract'
def read_img(img):
    pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
    image = Image.open(img)
    image = image.convert('L')
    threshold = 128
    image = image.point(lambda p: p > threshold and 255)
    text = pytesseract.image_to_string(image).lower()
    return text


def find_value(text, *keywords):
    lines = text.split('\n')
    for line in lines:
        for keyword in keywords:
            if keyword in line.lower():
                match = re.search(r'[\d,]+\.?\d*', line)
                if match:
                    return float(match.group().replace(',', '.'))
    return 0