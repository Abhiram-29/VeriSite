import re
import numpy as np
import unicodedata
from urllib.parse import urlparse


def has_misleading_chars(url):
  for char in url:
    if not (char.isascii() or char.isspace()):
      category = unicodedata.category(char)
      if category.startswith("L") and not unicodedata.combining(char):
        return True
  return  False

def preprocess_url(url):
    url = re.sub(r'https?://', '', url)
    parts = url.split('/', 1)
    domain = parts[0]
    path = parts[1] if len(parts) > 1 else ""
    text_rep = f"{domain} {path.replace('/', ' ')}"

    return text_rep

def extract_url_features(url,bert_output):
    url = url.strip().lower()
    protocol = 1 if urlparse(url).scheme == 'https' else 0
    url = re.sub(r"https?://","",url)
    parts = url.split("/",1)
    domain = parts[0]
    path = parts[1] if len(parts)>1 else ""
    features = {
        "domain_length" : len(domain),
        "subdomains" : domain.count('.'),
        'num_dots': url.count('.'),
         'num_equals': url.count('='),
         'protocol': protocol,
        "missing_chars": has_misleading_chars(url),
        'bert_output': bert_output
    }

    return np.array(list(features.values()))