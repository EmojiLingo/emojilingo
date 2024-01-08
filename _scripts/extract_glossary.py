import requests
import pandas as pd
from io import BytesIO
import json
import re

def download_table():
    spreadsheet_key = '1p6Uo9XzwKDO1R2eteoTKb6wOv6Bvgop5r0uz0f1tHXA'
    url = f'https://docs.google.com/spreadsheets/d/{spreadsheet_key}/export?gid=0&format=csv'
    r = requests.get(url, allow_redirects=True)
    data = r.content    
    df = pd.read_csv(BytesIO(data))
    table = df.to_dict()
    return table

def main(lang):
    assert lang in ['IT','EN']
    table = download_table()
    # print(json.dumps(table, indent=3))
    table_emojilingo = table['EMOJILINGO']
    table_lang = table[lang]
    strings_emojilingo = table_emojilingo.values()
    strings_lang = table_lang.values()
    
    md_output = []
    md_output.append(f'| {lang} | EmojiLingo |')
    md_output.append('| ------- | ---------- |')
    pairs = [(l,e) for l,e in zip(strings_lang, strings_emojilingo)]
    pairs = sorted(pairs, key=lambda x: x[0])
    for en,el in pairs:
        en = en.replace('\n','')
        el = re.sub(' +\(\d+\)', '', el)
        el = el.replace('\n','').replace("'","^") # "＇"
        md_output.append(
            '| ' + en + ' | <span class="emojitext">' + el + '</span> |'
        )
    
    with open(f'_i18n/{lang}/glossary.md', 'w') as f:
        f.write('\n'.join(md_output))



if __name__ == "__main__":
    main('IT')
    main('EN')
