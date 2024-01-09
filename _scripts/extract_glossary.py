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
    languages = {
        'IT': 'Italiano',
        'EN': 'English'    
    }
    table = download_table()
    # print(json.dumps(table, indent=3))
    table_emojilingo = table['EMOJILINGO']
    table_lang = table[lang]
    strings_emojilingo = table_emojilingo.values()
    strings_lang = table_lang.values()
    
    md_output = ['<table>']    
    md_output.append(f'<tr>  <th>{languages[lang]}</th>  <th>EmojiLingo</th> </tr>')        
    md_output.append(
        '<tr> <th colspan="2"> <input type="text" id="searchInput" onkeyup="searchFunction()" placeholder="Search..."> </th> </tr>'
    )
    strings_emojilingo = [re.sub(' +\(\d+\)', '', el) for el in strings_emojilingo]
    pairs = list(set([(l,e) for l,e in zip(strings_lang, strings_emojilingo)]))
    pairs = sorted(pairs, key=lambda x: x[0].lower())
    for en,el in pairs:
        el = el.replace('\n','').replace("'","^") # "＇"
        md_output.append(
            '<tr><td>' + en + '</td> <td><span class="emojitext">' + el + '</span></td></tr>'
        )
    
    with open(f'_i18n/{lang}/glossary.html', 'w') as f:
        f.write('\n'.join(md_output))



if __name__ == "__main__":
    main('IT')
    main('EN')
