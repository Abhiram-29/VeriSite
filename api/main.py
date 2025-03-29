import numpy as np
from fastapi import FastAPI, Request
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from peft import LoraConfig, get_peft_model,PeftModel
from utils import preprocess_url, has_misleading_chars,extract_url_features
from xgboost import XGBClassifier
import pickle
from pydantic import BaseModel

class predictParams(BaseModel):
    url : str

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_path = "deberta_v3-1"
base_model = AutoModelForSequenceClassification.from_pretrained("microsoft/deberta-v3-base")
deberta_model = PeftModel.from_pretrained(base_model, model_path, is_trainable=False)
tokenizer = AutoTokenizer.from_pretrained(model_path)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
deberta_model.to(device)
deberta_model.eval()
filename = 'xgboost_model.pkl'
xgb_model = pickle.load(open(filename, 'rb'))

app = FastAPI()

@app.post("/predict")
def predict(
    request : Request,
    params : predictParams
):
    url = params.url
    text_rep = preprocess_url(url)
    with torch.no_grad():
        inputs = tokenizer([text_rep], return_tensors="pt", padding=True, truncation=True, max_length=512).to(device)
        outputs = deberta_model(**inputs)
        logits = outputs.logits
        bert_prediction = torch.argmax(logits, dim=-1).tolist()

    url_features = extract_url_features(url,bert_prediction[0])
    final_prediction = xgb_model.predict([url_features])
    final_pred_label = int(final_prediction[0]) 
    print(final_prediction)
    return {"prediction":final_pred_label}

