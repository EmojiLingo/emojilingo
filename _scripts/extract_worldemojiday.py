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
    date_header = {
        'IT': 'Data', # (giorno.mese)
        'EN': 'Date' # (day.month)
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

    dates = list(ensure_strings_dict(table['Day']).values())
    table_emojilingo = ensure_strings_dict(table['EmojiLingo'])
    table_lang = ensure_strings_dict(table[lang])
    emojilingo = list(table_emojilingo.values())
    txt_lang = list(table_lang.values())
    ref_lang = list(table[f'Ref {lang}'].values())
    source_lang = list(table[f'Source {lang}'].values())

    md_output = ['<table>']
    md_output.extend([
        '<tr class="table-header">',
            # f'<th>{date_header[lang]}</th>',
            '<th></th>',
            f'<th>{languages[lang]}</th>',
            f'<th>EmojiLingo</th>',
        '</tr>'
    ])
    md_output.append(
        '<tr> <th colspan="100%"> <input type="text" id="searchInput" onkeyup="searchFunction()" placeholder="Search..."> </th> </tr>'
    )

    date_txt_el_ref_source = [
        (d,t,e,r,s) for d,t,e,r,s in
        zip(dates, txt_lang, emojilingo, ref_lang, source_lang)
    ]
    date_txt_el_ref_source_alpha = sorted(
        # sorted alpha by txt (parenthesis at the end)
        date_txt_el_ref_source, key=lambda x: (not x[1][0].isalnum(), x[1].lower())
    )
    for d,txt,el,ref,source in date_txt_el_ref_source_alpha:
        # print(txt,el)
        el = el.replace('\n','').replace("'","^") # "＇"
        md_output.extend([
            '<tr class="notfirst">',
                # '<td>' + d + '</td>',
                '<td class="dt-control"></td>',
                '<td> <span>' + txt + '</span> </td>',
                '<td> <span class=emojitext>' + el + '</span> </td>',
            '</tr>',
            '<tr style="display:none" class="extra-info">',
                '<td></td>',
                '<td colspan=2>',
                    # 'Extra Information:<br>',
                    f'<strong>Ref</strong>: {ref}<br>',
                    f'<strong>Source</strong>: {source}<br>',
                '</td>',
            '</tr>'
        ])

    with open(f'_i18n/{lang.lower()}/worldemojiday.html', 'w') as f:
        f.write('\n'.join(md_output))



if __name__ == "__main__":
    main('IT')
    main('EN')
