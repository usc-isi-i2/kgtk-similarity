import os
import requests
import json
import pandas as pd


def call_semantic_similarity(input_file, url):
    file_name = os.path.basename(input_file)

    files = {
        'file': (file_name, open(input_file, mode='rb'), 'application/octet-stream')
    }
    resp = requests.post(url, files=files, params={'similarity_types': 'all'})
    
    s = resp.json()
    if isinstance(s, str):
        s = json.loads(s)
    
    return pd.DataFrame(s)

url = 'https://kgtk.isi.edu/similarity_api'
df = call_semantic_similarity('test_file.tsv', url)
df.to_csv('test_file_similarity.tsv', index=False, sep='\t')
