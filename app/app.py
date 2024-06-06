from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from werkzeug.utils import secure_filename
from model.model import read_img, find_value
import os

app = FastAPI()

ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'heic']

class PredictionOut(BaseModel):
    energi: float
    protein: float
    lemak: float
    karbohidrat: float
    serat: float
    natrium: float


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.get("/")
def home():
    return {"health_check": "OK"}


@app.post("/predict", response_model=PredictionOut)
async def prediction(file: UploadFile = File(...)):
    if allowed_file(file.filename):
        contents = await file.read()
        img = read_img(contents)

        nutrients = {
            'energi': ['energi total', 'total energi', 'energy total', 'total energy', 'calories', 'energi', 'energy'],
            'protein': ['protein'],
            'lemak': ['lemak', 'lemak total', 'total lemak', 'total fat'],
            'karbohidrat': ['karbohidrat', 'karbohidrat total', 'total carbohydrate'],
            'serat': ['serat', 'serat pangan', 'dietary fiber'],
            'natrium': ['natrium', 'garam', 'salt', 'sodium']
        }

        nutrient_values = {}
        for nutrient, variations in nutrients.items():
            value = find_value(img, *variations)
            nutrient_values[nutrient] = value

        return PredictionOut(**nutrient_values)
    else:
        raise HTTPException(status_code=400, detail="Invalid file format")