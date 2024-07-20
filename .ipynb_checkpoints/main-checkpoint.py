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
import threading

app = FastAPI()

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
        return None, None

def get_page_rank(domain):
    url = 'https://openpagerank.com/api/v1.0/getPageRank'
    query = {'domains[]': [domain]}
    headers = {'API-OPR': 'YOUR_API_KEY_HERE'}
    response = requests.get(url, headers=headers, params=query)
    return response.json()['response'][0]['rank']

@app.post("/extract")
def extract_data(data: URLData):
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
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
