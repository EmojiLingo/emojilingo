# WorldEmojiDay 2024 - Parole di Dante

import requests
import pandas as pd
from io import BytesIO
import json
import re
import math

def download_table():
    spreadsheet_key = '13vkH3a-C0OpVTm9r5daFg_y0MN8lPASwGICaa72zaGg'
    gid = 262347955
    url = f'https://docs.google.com/spreadsheets/d/{spreadsheet_key}/export?gid={gid}&format=csv'
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

def main(lang):
    assert lang in ['IT','EN']
    languages = {
        'IT': 'Italiano',
        'EN': 'English'
    }
    table = download_table()
    # print(json.dumps(table, indent=3))

    '''
    table keys: [
        'Day', # {0: 1.01, 1: 2.01, ..., 363: 30.12, 364: 31.12}
        'IT',  # {0: 'trasumanar', 1: 'color che son sospesi', ..., 364: 'stelle'}
        'EN',  # same above
        'EmojiLingo', # {0: '🪐', 1: "👥↪️'🕸", 2: '🧍🔆', ..., '👨\u200d👩\u200d👦', 364: '✨'}
        'Chat-GPT',          # same above
        'Ref IT', # {0: 'Paradiso, I, 70', 1: 'Inferno, II, 52', ...,  364: 'Inferno XXXIV, 139'}
        'Ref EN', # same above
        'Source IT', # {0: "Trasumanar significar ...', 364: '...'}
        'Source EN'  # same above
    ]
    '''

    table_emojilingo = ensure_strings_dict(table['EmojiLingo'])
    table_lang = ensure_strings_dict(table[lang])
    strings_emojilingo = table_emojilingo.values()
    strings_lang = table_lang.values()

    md_output = ['<table>']
    md_output.append(f'<tr>  <th>{languages[lang]}</th>  <th>EmojiLingo</th> </tr>')
    md_output.append(
        '<tr> <th colspan="2"> <input type="text" id="searchInput" onkeyup="searchFunction()" placeholder="Search..."> </th> </tr>'
    )

    # for i, el in enumerate(strings_emojilingo):
    #     if type(el) is float and math.isnan(el):
    #         strings_emojilingo = ''
    #     else:
    #         strings_emojilingo = re.sub(' +\(\d+\)', '', el)

    pairs = list(set([(l,e) for l,e in zip(strings_lang, strings_emojilingo)]))
    pairs_alpha = sorted(pairs, key=lambda x: x[0].lower())
    for txt,el in pairs_alpha:
        # print(txt,el)
        el = el.replace('\n','').replace("'","^") # "＇"
        md_output.append(
            '<tr><td>' + txt + '</td> <td><span class="emojitext">' + el + '</span></td></tr>'
        )

    with open(f'_i18n/{lang.lower()}/worldemojiday.html', 'w') as f:
        f.write('\n'.join(md_output))



if __name__ == "__main__":
    main('IT')
    main('EN')
