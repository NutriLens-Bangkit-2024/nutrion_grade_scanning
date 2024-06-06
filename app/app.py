from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from werkzeug.utils import secure_filename
from model.model import read_img, find_value
import os

app = FastAPI()

ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'heic']


class ImageUpload(BaseModel):
    filename: str
    content_type: str
    file: bytes

    @classmethod
    async def from_upload_file(cls, file: UploadFile):
        content = await file.read()
        return cls(
            filename=file.filename,
            content_type=file.content_type,
            file=content
        )


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
    image = await ImageUpload.from_upload_file(file)
    if allowed_file(image.filename):
        filename = secure_filename(image.filename)
        image_path = os.path.join('./image_saved/', filename)
        with open(image_path, "wb") as buffer:
            buffer.write(image.file)
        img = read_img(image_path)

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

        os.remove(image_path)

        return PredictionOut(**nutrient_values)
    else:
        raise HTTPException(status_code=400, detail="Invalid file format")
