from fastapi import FastAPI
from pydantic import BaseModel
import hashlib
import json
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS (VERY IMPORTANT)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PredictionInput(BaseModel):
    crop: str
    state: str
    temperature: float
    rainfall: float


def generate_hash(data: dict) -> str:
    json_string = json.dumps(data, sort_keys=True)
    return hashlib.sha256(json_string.encode()).hexdigest()


@app.post("/predict")
def predict(data: PredictionInput):

    # Dummy model (replace later)
    predicted_price = 3000 + data.temperature * 5 - data.rainfall * 2

    prediction_output = {
        "crop": data.crop,
        "state": data.state,
        "price": predicted_price
    }

    hash_value = generate_hash(prediction_output)

    return {
        "prediction": prediction_output,
        "hash": hash_value
    }
