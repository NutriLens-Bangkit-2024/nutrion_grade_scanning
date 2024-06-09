import cv2
import numpy as np
from paddleocr import PPStructure
from bs4 import BeautifulSoup
import re
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

app = FastAPI()

class PredictionOut(BaseModel):
    takaran_saji: int
    energi: float
    protein: float
    lemak: float
    karbohidrat: float
    serat: float
    natrium: float

class NutritionLabelExtractor:
    ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'heic']

    def __init__(self):
        self.table_engine = PPStructure(layout=False, show_log=True, ocr=True)
        self.nutrients = {
            'takaran_saji': {'serving size', 'takaran saji', 'serving', 'saji', 'saiz hidangan', 'jumlah per kemasan',
                             'amount per pack'},
            'energi': ['energi total', 'total energi', 'energy total', 'total energy', 'calories', 'energi', 'energy'],
            'protein': ['protein'],
            'lemak': ['lemak total', 'total lemak', 'total fat', 'lemak'],
            'karbohidrat': ['karbohidrat', 'karbohidrat total', 'total carbohydrate'],
            'serat': ['serat', 'serat pangan', 'dietary fiber'],
            'natrium': ['natrium', 'garam', 'salt', 'sodium']
        }

    def allowed_file(self, filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS

    def read_img(self, img_data):
        img_array = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        result = self.table_engine(img)
        # convert html to text using BeautifulSoup
        soup = BeautifulSoup(result[0]['res']['html'], 'html.parser')
        td_elements = soup.find_all('td')
        extracted_text = [td.get_text(strip=True) for td in td_elements]
        text = "\n".join(extracted_text).lower()
        return text

    def cleaning_text(self, text):
        # create a new line whenever there is '%'
        text = re.sub(r'%', '%\n', text)
        # replace '9' with 'g' if it is followed by a space or end of line
        text = re.sub(r'(?<=\d)9(?=\s|$)', 'g', text)
        return text

    def find_value(self, img_text, *keywords):
        clean_text = self.cleaning_text(img_text)
        lines = clean_text.split('\n')
        for i, line in enumerate(lines):
            for keyword in keywords:
                if keyword in line.lower():
                    pattern = rf"({keyword}.*?)(\d+(?:\.\d+)?)"
                    match = re.search(pattern, clean_text, re.DOTALL)
                    if match:
                        return float(match.group(2))
        return float(0)

nutrition_label_extractor = NutritionLabelExtractor()

@app.get("/")
def home():
    return {"health_check": "OK"}
@app.post("/predict", response_model=PredictionOut)
async def prediction(file: UploadFile = File(...)):
    if nutrition_label_extractor.allowed_file(file.filename):
        contents = await file.read()
        img_text = nutrition_label_extractor.read_img(contents)

        nutrient_values = {}
        for nutrient, variations in nutrition_label_extractor.nutrients.items():
            value = nutrition_label_extractor.find_value(img_text, *variations)
            nutrient_values[nutrient] = value

        return PredictionOut(**nutrient_values)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type.")


