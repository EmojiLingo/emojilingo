# WorldEmojiDay 2024 - Parole di Dante
import os
import json
import roman
from sortedcontainers import SortedSet
from unidecode import unidecode
from Levenshtein import ratio
import re
from .utils import download_table, ensure_strings_dict

'''
SPREADSHEET
https://docs.google.com/spreadsheets/d/13vkH3a-C0OpVTm9r5daFg_y0MN8lPASwGICaa72zaGg/edit?SPREADSHEET_GID=262347955#SPREADSHEET_GID=262347955

'', , , , 'Ref IT', 'Ref EN', 'Source IT', 'Source EN']

table.keys(): [
    'id', # 0-based index
    'Day', # {0: 1.01, 1: 2.01, ..., 363: 30.12, 364: 31.12}
    'IT',  # {0: 'trasumanar', 1: 'color che son sospesi', ..., 364: 'stelle'}
    'EN',  # same above
    'Emojilingo', # {0: '🪐', 1: "👥↪️'🕸", 2: '🧍🔆', ..., '👨\u200d👩\u200d👦', 364: '✨'}
    'Emojiligo\nChat-GPT\n(Manuale)',                           # same above
    'Emojiligo\nChat-GPT\n3.5-turbo-0125\n(Italian)',           # same above
    'Spiegazione\nChat-GPT\n3.5-turbo-0125\n(Italian)',         # same above
    'Emojilingo\nChat-GPT\n4-0613\n(Italian)',                  # same above
    'Spiegazione\nChat-GPT\n4-0613\n(Italian)',                 # same above
    'Emojiligo\nChat-GPT\n3.5-turbo-0125\n(English)',           # same above
    'Spiegazione\nChat-GPT\n3.5-turbo-0125\n(English)',         # same above
    'Emojilingo\nChat-GPT\n4-0613\n(English)',                  # same above
    'Spiegazione\nChat-GPT\n4-0613\n(English)'                  # same above
    'Ref IT', # {0: 'Paradiso, I, 70', 1: 'Inferno, II, 52', ...,  364: 'Inferno XXXIV, 139'}
    'Ref EN', # same above
    'Source IT', # {0: "Trasumanar significar ...', 364: '...'}
    'Source EN'  # same above
]
'''

DC_JSON = os.path.join('../_sources/dc_Hollander.json')
SPREADSHEET_KEY = '13vkH3a-C0OpVTm9r5daFg_y0MN8lPASwGICaa72zaGg'
SPREADSHEET_GID = 262347955
GPT_EMOJILINGO_COLUMN_HEADER = 'Emojiligo\nChat-GPT\n3.5-turbo-0125\n(Italian)'
GPT_EXPLANATION_COLUMN_HEADER = 'Spiegazione\nChat-GPT\n3.5-turbo-0125\n(Italian)'

def fuzzy_enhence(term, terzina):
    num_chars_term = len(term)
    num_chars_terzina = len(terzina)

    # normalize: remove accents and lowercase it
    norm_term = unidecode(term).lower()
    norm_terzina = unidecode(terzina).lower()

    # divide in tokens including punct and spaces
    terzina_tokens = re.findall( r"[\w]+|[\W]", terzina)
    norm_terzina_tokens = re.findall( r"[\w]+|[\W]", norm_terzina)
    assert len(terzina_tokens) == len(norm_terzina_tokens)
    num_tokens = len(terzina_tokens)
    # print(tokens)

    # make sure same num of chars after normalization
    assert len(norm_term) == num_chars_term
    assert len(norm_terzina) == num_chars_terzina

    # sorted candidates by best match
    # * -score
    # * span
    # * result
    candidates = SortedSet()
    counter = 0
    for span_start_token in range(num_tokens):
        for span_end_token in range(span_start_token+1, num_tokens+1):
            counter += 1
            norm_span_tokens = norm_terzina_tokens[span_start_token:span_end_token]
            span_tokens = terzina_tokens[span_start_token:span_end_token]
            norm_span_chars = ''.join(norm_span_tokens)
            span_chars = ''.join(span_tokens)
            # Using fuzz library to span ratio
            score = ratio(norm_term, norm_span_chars)
            before = ''.join(terzina_tokens[:span_start_token])
            after = ''.join(terzina_tokens[span_end_token:])
            result =  f'{before}<em>{span_chars}</em>{after}'
            # sorted in tuple
            # - by score from big to small (in absolute terms)
            # - and then by span alphabetical order)

            candidates.add((-score, span_chars, result))
            if counter > 100:
                candidates.pop() # remove last one

    best_cand_score, best_cand_span, best_cand_result = candidates[0]
    best_cand_score = -best_cand_score # transfor to pos

    return best_cand_score, best_cand_span, best_cand_result

def get_terzina(dc_json, lang, book_en, canto_num,  line, term, debug=True):
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

    ]
    if islast:
        # get previous terzina
        result = [
            canto_lang[str(start_line_terzina-3)],
            canto_lang[str(start_line_terzina-2)],
            canto_lang[str(start_line_terzina-1)],
            canto_lang[str(start_line_terzina)]
        ]
    else:
        result = [
            canto_lang[str(start_line_terzina)],
            canto_lang[str(start_line_terzina+1)],
            canto_lang[str(start_line_terzina+2)]
        ]


    result = '<br>'.join(result)
    score, matched_span, emph_terzina = fuzzy_enhence(term, result)
    if debug:
        if score < 0.65:
            print(
                f'{score}: term="{term}" match="{matched_span}" book={book_en} canto={canto_num}  line={line}')
            print('Terzina:', emph_terzina)
            print('--------------\n')

    return emph_terzina

def main(lang):

    assert lang in ['IT','EN']

    with open(DC_JSON) as fin:
        dc_json = json.load(fin)

    languages = {
        'IT': 'Italiano',
        'EN': 'English'
    }
    # date_header = {
    #     'IT': 'Data', # (giorno.mese)
    #     'EN': 'Date' # (day.month)
    # }

    intro = {
        'IT': "<p>Emojilingo partecipa alla Giornata Mondiale degli Emoji 2024 con Parole di Dante, un glossario della Divina Commedia di Dante Alighieri tradotto in emoji con corrispondenze in italiano e in inglese, e con un esperimento di AI di traduzione dalla lingua alla emoji-lingua.</p><p>Per più informazioni sul progetto <a href=\"../parole_di_dante\">clicca qua</a>.</p>",
        'EN': "<p>Emojilingo celebrates World Emoji Day 2024 with Parole di Dante (Dante’s words), a glossary of Dante Alighieri's Divine Comedy translated into emoji with corresponding translations from Italian to English and vice versa, and with an AI experiment of translation from language to the emoji-language.</p><p>For more info about the project <a href=\"../parole_di_dante\">click here</a>.</p>"
    }

    table = download_table(SPREADSHEET_KEY, SPREADSHEET_GID)
    # print(json.dumps(table, indent=3))

    dates = list(ensure_strings_dict(table['Day']).values())
    table_emojilingo = ensure_strings_dict(table['Emojilingo'])
    # table_chatgpt_manuale = ensure_strings_dict(table['Chat-GPT\n(Manuale)'])
    table_chatgpt_api = ensure_strings_dict(table[GPT_EMOJILINGO_COLUMN_HEADER])
    # table_chatgpt_spiegazione = ensure_strings_dict(table[GPT_EXPLANATION_COLUMN_HEADER])

    table_lang = ensure_strings_dict(table[lang])
    emojilingo = list(table_emojilingo.values())
    chatgpt = list(table_chatgpt_api.values())
    txt_lang = list(table_lang.values())
    ref_lang= list(table[f'Ref {lang}'].values())
    ref_EN= list(table[f'Ref EN'].values())
    source_lang = list(table[f'Source {lang}'].values())

    # page html output
    md_output = []

    md_output.extend([
        '<div class="wed-announcement">',
        intro[lang],
        '</div>'
    ])

    # start div with table
    md_output.extend([
        '<div class="tableFixHeadScrollBody">',
            '<table>'
                '<colgroup>',
                    '<col width="5%">',
                    '<col width="40%">',
                    '<col width="25%">',
                    '<col width="35%">',
                '</colgroup>'
    ])

    # header
    md_output.extend([
        '<thead>',
            '<tr class="table-header">',
                # f'<th>{date_header[lang]}</th>',
                '<th></th>', # dt-control
                f'<th>{languages[lang]}</th>',
                f'<th>Emojilingo</th>',
                f'<th>Chat-GPT</th>',
            '</tr>',
            # search input
            '<tr>',
                '<th colspan="100%">',
                    ' <input type="text" id="searchInput" onkeyup="searchFunction()" placeholder="Search...">'
                '</th>'
            '</tr>',
        '</thead>',
    ])

    # start of tbody
    md_output.extend([
        '<tbody>'
    ])

    date_txt_el_ref_source = [
        (d, t, e, gpt, r_en, r_lang, s) for d, t, e, gpt, r_en, r_lang, s in
        zip(dates, txt_lang, emojilingo, chatgpt, ref_EN, ref_lang, source_lang)
    ]
    date_txt_el_ref_source_alpha = sorted(
        # sorted alpha by term (parenthesis at the end)
        date_txt_el_ref_source, key=lambda x: (not x[1][0].isalnum(), x[1].lower())
    )

    # debug: take first 10
    # date_txt_el_ref_source_alpha = date_txt_el_ref_source_alpha[:10]

    for d, term, el, gpt, ref_en, ref_lang, source in date_txt_el_ref_source_alpha:
        ref_book_EN, ref_canto_roman, ref_line_num = ref_en.split(',')
        ref_book_EN = ref_book_EN.strip()
        ref_canto_num = roman.fromRoman(ref_canto_roman.strip())
        ref_line_num = int(ref_line_num)
        el = el.replace('\n','').replace("'","^") # "＇"

        terzina_lang = get_terzina(
            dc_json, lang, ref_book_EN, ref_canto_num, ref_line_num, term
        )

        md_output.extend([
            '<tr class="notfirst">',
                # '<td>' + d + '</td>', # date (better not)
                '<td class="dt-control"></td>',
                '<td> <span>' + term + '</span> </td>',
                '<td> <span class=emojitext>' + el + '</span> </td>',
                '<td> <span class=emojitext>' +gpt + '</span> </td>',
            '</tr>',
            '<tr style="display:none" class="extra-info">',
                '<td></td>', # dt-control
                '<td colspan=3>',
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

    # end of tbody
    md_output.extend([
        '</tbody>'
    ])

    # end of table
    md_output.extend([
            '</table>',
        '</div>',
    ])


    with open(f'../_i18n/{lang.lower()}/worldemojiday.html', 'w') as f:
        f.write('\n'.join(md_output))


if __name__ == "__main__":
    for lang in ['IT','EN']:
        print('##########')
        print('####', lang)
        print('##########\n')
        main(lang)