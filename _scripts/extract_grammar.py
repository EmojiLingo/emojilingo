import requests
import pandas as pd
from io import BytesIO
import json

def download_table(lang):
    assert lang in ['en', 'it']
    gid = {
        'it': 0,
        'en': 972602287
    }
    spreadsheet_key = '1ilz9_I86xrEdwWleMwAu3CBGp2PEjH2yVyzAhqItUJA'
    url = f'https://docs.google.com/spreadsheets/d/{spreadsheet_key}/export?gid={gid[lang]}&format=csv'
    r = requests.get(url, allow_redirects=True)
    data = r.content    
    df = pd.read_csv(BytesIO(data))
    table = df.to_dict()
    return table

def main(lang):
    table = download_table(lang)
    
    # print(json.dumps(table, indent=3))
    rules = table['Rules'].values()
    explanations = table['Explanations'].values()
    
    md_output = []
    for r,e in zip(rules, explanations):
        r = str(r).replace('<','\<').replace('>','\>')
        e = str(e).replace('<','\<').replace('>','\>')
        if r!='nan':
            md_output.append('# ' + str(r))
        if e!='nan':
            md_output.append('- ' + str(e))
        else:
            md_output.append('')

    with open(f'_i18n/{lang}/grammar.md', 'w') as f:
        f.write('\n'.join(md_output))


if __name__ == "__main__":
    main(lang='it')
    main(lang='en')
