# WorldEmojiDay 2024 - Parole di Dante
import os
import requests
import pandas as pd
from io import BytesIO
import json
import roman
from sortedcontainers import SortedSet
from Levenshtein import ratio

from collections import OrderedDict

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

dirname = os.path.dirname(__file__)
dc_json_file = os.path.join(dirname, '../_sources/dc_Hollander.json')
with open(dc_json_file) as fin:
    dc_json = json.load(fin)

def fuzzy_enhence(term, terzina):
    num_chars_terzina = len(terzina)
    # sorted candidates by best match
    # * -score
    # * span
    # * result
    candidates = SortedSet()
    counter = 0
    for span_start in range(num_chars_terzina):
        for span_end in range(span_start+1, num_chars_terzina):
            counter += 1
            span = terzina[span_start:span_end]
            # Using fuzz library to span ratio
            score = ratio(term, span)
            before = terzina[:span_start]
            after = terzina[span_end:]
            result =  f'{before}<em>{span}</em>{after}'
            # sorted in tuple
            # - by score from big to small (in absolute terms)
            # - and then by span alphabetical order)
            candidates.add((-score, span, result))
            if counter > 100:
                candidates.pop() # remove last one
    return candidates[0][-1] # get last element in tuple (result)

def get_terzina(lang, book_en, canto_num,  line, txt):
    line_pos_terzina = line % 3 # position of line in terzina

    match line_pos_terzina:
        case 1: # 1 -> beginning
            start_line_terzina = line
        case 2: # 2 -> middle
            start_line_terzina = line - 1
        case 0: # 0 -> last one
            start_line_terzina = line - 2

    canto_lang = dc_json[book_en][str(canto_num)][lang]
    islast = len(canto_lang) == start_line_terzina
    result = [
        canto_lang[str(start_line_terzina)]
    ]
    if not islast:
        result.extend([
            canto_lang[str(start_line_terzina+1)],
            canto_lang[str(start_line_terzina+2)]
        ])

    result = '<br>'.join(result)
    result = fuzzy_enhence(txt, result)
    # search txt_lang in result and Emphasized text (with <em>)
    # for i, line in enumerate(result):
    #     if txt in line:
    #         result[i] = line.replace(txt, f'<em> {txt} </em>')

    return result

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
    ref_lang= list(table[f'Ref {lang}'].values())
    ref_EN= list(table[f'Ref EN'].values())
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
        (d,t,e,r_en,r_lang,s) for d,t,e,r_en,r_lang,s in
        zip(dates, txt_lang, emojilingo, ref_EN, ref_lang, source_lang)
    ]
    date_txt_el_ref_source_alpha = sorted(
        # sorted alpha by txt (parenthesis at the end)
        date_txt_el_ref_source, key=lambda x: (not x[1][0].isalnum(), x[1].lower())
    )
    for d,txt,el,ref_en,ref_lang,source in date_txt_el_ref_source_alpha:
        # print(txt,el)
        ref_book_EN, ref_canto_roman, ref_line_num = ref_en.split(',')
        ref_book_EN = ref_book_EN.strip()
        ref_canto_num = roman.fromRoman(ref_canto_roman.strip())
        ref_line_num = int(ref_line_num)
        el = el.replace('\n','').replace("'","^") # "＇"

        terzina_lang = get_terzina(
            lang, ref_book_EN, ref_canto_num, ref_line_num, txt
        )

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
                    f'<strong>{ref_lang}</strong><br>',
                    # f'<strong>Source</strong>:<br>',
                    '<blockquote>' +
                        # ''.join(f'{verso}<br> ' for verso in terzina_lang) +
                        terzina_lang +
                    '</blockquote>',
                '</td>',
            '</tr>'
        ])

    with open(f'_i18n/{lang.lower()}/worldemojiday.html', 'w') as f:
        f.write('\n'.join(md_output))



if __name__ == "__main__":
    main('IT')
    main('EN')
    # print(fuzzy_enhence(
    #     "abbaglio",
    #     "tal mi fec'ïo a quell' ultimo foco\nmentre che detto fu: \"Perché t'abbagli\nper veder cosa che qui non ha loco?",
    # ))
