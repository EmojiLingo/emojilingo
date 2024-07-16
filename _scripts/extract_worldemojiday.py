# WorldEmojiDay 2024 - Parole di Dante
import os
import requests
import pandas as pd
from io import BytesIO
import json
import roman
from sortedcontainers import SortedSet
from Levenshtein import ratio
import re
from collections import OrderedDict
import textwrap
import time
import random
import openai
from openai import OpenAI

'''
SPREADSHEET
https://docs.google.com/spreadsheets/d/13vkH3a-C0OpVTm9r5daFg_y0MN8lPASwGICaa72zaGg/edit?SPREADSHEET_GID=262347955#SPREADSHEET_GID=262347955

table.keys(): [
    'id', # 0-based index
    'Day', # {0: 1.01, 1: 2.01, ..., 363: 30.12, 364: 31.12}
    'IT',  # {0: 'trasumanar', 1: 'color che son sospesi', ..., 364: 'stelle'}
    'EN',  # same above
    'Emojilingo', # {0: '🪐', 1: "👥↪️'🕸", 2: '🧍🔆', ..., '👨\u200d👩\u200d👦', 364: '✨'}
    'Chat-GPT\n(Manuale)',          # same above
    'Chat-GPT\n(API)',          # same above
    'Chat-GPT\n(Spiegazione',          # same above
    'Ref IT', # {0: 'Paradiso, I, 70', 1: 'Inferno, II, 52', ...,  364: 'Inferno XXXIV, 139'}
    'Ref EN', # same above
    'Source IT', # {0: "Trasumanar significar ...', 364: '...'}
    'Source EN'  # same above
]
'''

CURRENT_DIR = os.path.dirname(__file__)
CHATGPT_JSON = os.path.join(CURRENT_DIR, '../_chatgpt/', 'chatgpt.json')
DC_JSON = os.path.join(CURRENT_DIR, '../_sources/dc_Hollander.json')
SPREADSHEET_KEY = '13vkH3a-C0OpVTm9r5daFg_y0MN8lPASwGICaa72zaGg'
SPREADSHEET_GID = 262347955

def download_table():
    url = f'https://docs.google.com/spreadsheets/d/{SPREADSHEET_KEY}/export?SPREADSHEET_GID={SPREADSHEET_GID}&format=csv'
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

def get_terzina(dc_json, lang, book_en, canto_num,  line, txt):
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
    if islast:
        # get previous terzina
        result.extend([
            canto_lang[str(start_line_terzina-3)],
            canto_lang[str(start_line_terzina-2)],
            canto_lang[str(start_line_terzina-1)]
        ])
    else:
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

def retry_with_exponential_backoff(
    func,
    initial_delay = 2,
    additional_delay = 5,
    max_retries: int = 10,
):
    """Retry a function with exponential backoff."""

    def wrapper(*args, **kwargs):
        num_retries = 0
        delay = initial_delay

        while True:
            try:
                return func(*args, **kwargs)

            except Exception as error:
                print(
                    'Error in request',
                    type(error).__name__,
                    error.args
                )

                num_retries += 1

                if num_retries > max_retries:
                    raise Exception(f"Maximum number of retries ({max_retries}) exceeded.")

                delay += additional_delay

                time.sleep(delay)

            except Exception as e:
                raise e

    return wrapper


def main_ChatGPT(debug=True):
    # https://platform.openai.com/docs/overview
    from dotenv import load_dotenv
    import os

    # chat GPT preps

    load_dotenv()
    client = OpenAI(
        api_key = os.getenv('CHATGPT_API_KEY')
    )

    @retry_with_exponential_backoff
    def send_request_to_chatgpt(messages):
        response = client.chat.completions.create(
            # two messages (prompt and next term)
            messages = messages,

            # max_tokens = 4000,

            # 'gpt-4-turbo' not available wiht this key
            model = "gpt-3.5-turbo",

            #  only the new GPT-4 Turbo models support reproducible outputs
            # seed = 7263081721,
            temperature = 1, # default 1

            # request_timeout = 10
        )
        return response

    def chat_with_gpt(term):

        prompt_with_term = textwrap.dedent(
            f"""\
            Ti darò una parola dalla Divina Commedia di Dante e ti chiedo di inventare una traduzione in emoji.

            Rispondimi con una singola traduzione in 2 righe di testo puro (senza formattazione):
            - traduzione in emoji
            - breve frase di spiegazione della scelta.

            La parola è `{term}`"""
        )

        # single message with prompt and term
        messages = [
            {
                "role": "user",
                "content": prompt_with_term
            }
        ]

        response = send_request_to_chatgpt(messages)
        choice = response.choices[0]

        response_txt = choice.message.content

        if debug:
            print(term)
            print(response_txt)

        response_txt_lines = [
            l.strip()
            for l in response_txt.splitlines()
            if l.strip() != ''
        ]

        if len(response_txt_lines)!=2:
            print(f'Error in num of lines ({len(response_txt_lines)})')
            print(f'Repeating request...\n')
            return chat_with_gpt(term)
        else:
            emojilingo_chatgpt, explanation = response_txt_lines

        if debug:
            print('emojilingo_chatgpt: ', emojilingo_chatgpt)
            print('explanation: ', explanation)

        result_json = {
            'model': response.model,
            'id': response.id,
            'created': response.created,
            # only the new GPT-4 Turbo models support reproducible outputs
            'fingerprint': response.system_fingerprint,                    # finish_reason
                # 'stop' - finished
                # 'length' - max_tokens exceeded
            # 'finish_reason': choice.finish_reason,
            # 'content': json.loads(choice.message.content),

            'response_processed': {
                'term_it': term,
                'emojilingo_chatgpt': emojilingo_chatgpt,
                'explanation': explanation
            }
        }

        return result_json

    # retrieve terms from spreadsheet
    table = download_table()
    termini_it_dict = ensure_strings_dict(table['IT']) # index -> term
    termini_it = list(termini_it_dict.values())

    # test first 10 by uncommenting this line
    # termini_it = termini_it[:10]

    num_termini_it = len(termini_it)

    if os.path.exists(CHATGPT_JSON):
        with open(CHATGPT_JSON) as fin:
            full_result_json = json.load(fin)
            if debug:
                print(f'Found {len(full_result_json)} stored terms')
    else:
        full_result_json = {}


    num_terms_stored = len(full_result_json)

    for index in range(num_terms_stored, num_termini_it):

        term = termini_it[index]

        if debug:
            print(index)

        term_result_json = chat_with_gpt(term)
        full_result_json[term] = term_result_json

        if debug:
            print('\n-----------------------\n')

        # rewrite full json file for every term
        with open(CHATGPT_JSON, 'w') as fout:
            json.dump(
                full_result_json,
                fout,
                indent=3,
                ensure_ascii=False
            )

'''
Create a test.txt file with a field from chatgpt.json
'''
def extract_chatgpt_manual():

    with open(CHATGPT_JSON) as fin:
        full_result_json = json.load(fin)

    with open('test.txt', 'w') as fout:
        emojilingo_chatgpt = [
            value['response_processed']['emojilingo_chatgpt']
            for term, value in full_result_json.items()
        ]
        explanation = [
            value['response_processed']['explanation']
            for term, value in full_result_json.items()
        ]
        fout.write(
            '\n'.join(explanation)
        )


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
        'IT': "<p>Emojilingo partecipa alla Giornata Mondiale degli Emoji 2024 con Parole di Dante, un glossario della Divina Commedia di Dante Alighieri tradotto in emoji con corrispondenze in italiano e in inglese, e con un esperimento di AI di traduzione dalla lingua alla emoji-lingua.</p><p>Per più informazioni <a href=\"../parole_di_dante\">clicca qua</a>.</p>",
        'EN': "<p>Emojilingo celebrates World Emoji Day 2024 with Parole di Dante (Dante’s words), a glossary of Dante Alighieri's Divine Comedy translated into emoji with correspondences in Italian and English, and with an AI experiment of translation from language to the emoji-language.</p><p>For more info <a href=\"../parole_di_dante\">click here</a>.</p>"
    }

    table = download_table()
    # print(json.dumps(table, indent=3))

    dates = list(ensure_strings_dict(table['Day']).values())
    table_emojilingo = ensure_strings_dict(table['Emojilingo'])
    # table_chatgpt_manuale = ensure_strings_dict(table['Chat-GPT\n(Manuale)'])
    table_chatgpt_api = ensure_strings_dict(table['Chat-GPT\n(API)'])
    # table_chatgpt_spiegazione = ensure_strings_dict(table['Chat-GPT\n(Spiegazione'])

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
                    '<col width="35%">',
                    '<col width="28%">',
                    '<col width="32%">',
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
        # sorted alpha by txt (parenthesis at the end)
        date_txt_el_ref_source, key=lambda x: (not x[1][0].isalnum(), x[1].lower())
    )

    # debug: take first 10
    # date_txt_el_ref_source_alpha = date_txt_el_ref_source_alpha[:10]

    for d, txt, el, gpt, ref_en, ref_lang, source in date_txt_el_ref_source_alpha:
        ref_book_EN, ref_canto_roman, ref_line_num = ref_en.split(',')
        ref_book_EN = ref_book_EN.strip()
        ref_canto_num = roman.fromRoman(ref_canto_roman.strip())
        ref_line_num = int(ref_line_num)
        el = el.replace('\n','').replace("'","^") # "＇"

        terzina_lang = get_terzina(
            dc_json, lang, ref_book_EN, ref_canto_num, ref_line_num, txt
        )

        md_output.extend([
            '<tr class="notfirst">',
                # '<td>' + d + '</td>', # date (better not)
                '<td class="dt-control"></td>',
                '<td> <span>' + txt + '</span> </td>',
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


    with open(f'_i18n/{lang.lower()}/worldemojiday.html', 'w') as f:
        f.write('\n'.join(md_output))




if __name__ == "__main__":
    main('IT')
    main('EN')

    # chat_with_gpt('trasumanar')
    # main_ChatGPT()
    # extract_chatgpt_manual() # create a temp.txt file with a field from chatgpt.json
