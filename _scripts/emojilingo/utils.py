import requests
import pandas as pd
from io import BytesIO

def download_table(key, gid):
    url = f'https://docs.google.com/spreadsheets/d/{key}/export?SPREADSHEET_GID={gid}&format=csv'
    r = requests.get(url, allow_redirects=True)
    data = r.content
    df = pd.read_csv(BytesIO(data))
    table = df.to_dict()
    return table

def ensure_strings_list(l):
    return [str(l) if type(l) is not str else e for e in l]

def ensure_strings_dict(d):
    new_dict = {
        k: str(v) if type(v) is not str else v
        for k,v in d.items()
    }
    return new_dict
