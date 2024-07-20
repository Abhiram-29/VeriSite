from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from urllib.parse import urlparse
import re
import requests
import unicodedata
import socket
from datetime import datetime, timezone
import ssl
from OpenSSL import crypto
import whois
from fastapi.middleware.cors import CORSMiddleware 
import logging
import joblib
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import OrdinalEncoder
from sklearn.pipeline import Pipeline
import dill


app = FastAPI()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# Define custom transformers
class FillMissingValues(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.sslMean = 95.42572488662911
        self.domainAgeMean = 4768.3417287504235

    def fit(self, X, y=None):
        self.sslMean = X['sslAge'].mean() if 'sslAge' in X else self.sslMean
        self.domainAgeMean = X['domainAge'].mean() if 'domainAge' in X else self.domainAgeMean
        return self

    def transform(self, X):
        X = X.copy()
        X['PageRank'].fillna(10000000, inplace=True)
        X['registrar'].fillna("", inplace=True)
        X['sslAge'].fillna(self.sslMean, inplace=True)
        X['domainAge'].fillna(self.domainAgeMean, inplace=True)
        X['domain'].fillna("", inplace=True)
        return X

class ExtractDomain(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()
        X['domain'] = X['domain'].apply(lambda url: url.split('.')[-1] if len(url.split('.')) > 2 else 'None')
        return X

class OrdinalEncoderWrapper(BaseEstimator, TransformerMixin):
    def __init__(self, encoded_columns):
        self.encoded_columns = encoded_columns
        self.encoder = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)

    def fit(self, X, y=None):
        self.encoder.fit(X[self.encoded_columns])
        return self

    def transform(self, X):
        X = X.copy()
        X[self.encoded_columns] = self.encoder.transform(X[self.encoded_columns])
        return X

# Load the trained model
model_path = 'Model.pkl'
def load_model(filename):
    with open(filename, 'rb') as file:
        return dill.load(file)
try:
    model = load_model(model_path)
    logger.info(f"Model loaded from {model_path}")
except Exception as e:
    logger.error(f"Error loading model: {e}")

class URLData(BaseModel):
    url: str

def calculate_url_depth(url):
    return urlparse(url).path.count('/') - 1 if urlparse(url).path != '/' else 0

def get_protocol(url):
    return urlparse(url).scheme

def get_domain(url):
    return urlparse(url).netloc

def get_ssl_age(domain):
    try:
        context = ssl.create_default_context()
        conn = context.wrap_socket(
            socket.socket(socket.AF_INET),
            server_hostname=domain,
        )
        conn.settimeout(10)
        conn.connect((domain, 443))

        cert = conn.getpeercert(True)
        pem_cert = ssl.DER_cert_to_PEM_cert(cert)
        conn.close()

        x509 = crypto.load_certificate(crypto.FILETYPE_PEM, pem_cert)
        timestamp = x509.get_notBefore().decode('utf-8')
        issue_date = datetime.strptime(timestamp, '%Y%m%d%H%M%S%z').replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        age = now - issue_date
        return age.days
    except Exception as e:
        logger.error(f"Error getting SSL age for domain {domain}: {e}")
        return None

def get_domain_info(domain):
    try:
        info = whois.whois(domain)
        created_date = info.creation_date
        if isinstance(created_date, list):
            created_date = created_date[0]
        domain_age = (datetime.now() - created_date).days if created_date else None
        registrar = info.registrar
        return domain_age, registrar
    except Exception as e:
        logger.error(f"Error getting domain info for {domain}: {e}")
        return None, None

def get_page_rank(domain):
    try:
        url = 'https://openpagerank.com/api/v1.0/getPageRank'
        query = {'domains[]': [domain]}
        headers = {'API-OPR': 'YOUR_API_KEY_HERE'}
        response = requests.get(url, headers=headers, params=query)
        response.raise_for_status()  # Check for HTTP errors
        data = response.json()
        if 'response' in data and data['response']:
            return data['response'][0]['rank']
        else:
            logger.error(f"Unexpected response structure: {data}")
            return None
    except Exception as e:
        logger.error(f"Error getting page rank for domain {domain}: {e}")
        return None

@app.post("/extract")
def extract_data(data: URLData):
    logger.info(f"Received data: {data}")
    url = data.url
    try:
        url_length = len(url)
        url_depth = calculate_url_depth(url)
        protocol = get_protocol(url)
        domain = get_domain(url)
        ssl_age = get_ssl_age(domain)
        domain_age, registrar = get_domain_info(domain)
        page_rank = get_page_rank(domain)

        result = {
            "urlLength": url_length,
            "urlDepth": url_depth,
            "protocol": protocol,
            "domain": domain,
            "domainAge": domain_age,
            "registrar": registrar,
            "sslAge": ssl_age,
            "pageRank": page_rank,
        }
        logger.info(f"Processed data: {result}")
        return result
    except Exception as e:
        logger.error(f"Error processing data: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/predict")
def predict_score(data: URLData):
    logger.info(f"Received data for prediction: {data}")
    url = data.url
    try:
        url_length = len(url)
        url_depth = calculate_url_depth(url)
        protocol = get_protocol(url)
        domain = get_domain(url)
        ssl_age = get_ssl_age(domain)
        domain_age, registrar = get_domain_info(domain)
        page_rank = get_page_rank(domain)

        # Prepare features for prediction
        features = np.array([[
            url_length,
            url_depth,
            protocol,
            domain,
            domain_age,
            registrar,
            ssl_age,
            page_rank
        ]])

        # Predict score using the loaded model
        prediction = model.predict(features)
        score = prediction[0]

        result = {
            "predictedScore": score
        }
        logger.info(f"Prediction result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error making prediction: {e}")
        raise HTTPException(status_code=400, detail=str(e))
