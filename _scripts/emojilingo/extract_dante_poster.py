# Emojilingo 2024 - Parole di Dante
import os
import json
import roman
from sortedcontainers import SortedSet
from unidecode import unidecode
from Levenshtein import ratio
import re
import textwrap
import emoji
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
    'Ref IT',  # {0: 'Paradiso, I, 70', 1: 'Inferno, II, 52', ...,  364: 'Inferno XXXIV, 139'}
    'Ref EN',  # same above
    'Emojitaliano', # {0: '🪐', 1: "👥↪️'🕸", 2: '🧍🔆', ..., '👨\u200d👩\u200d👦', 364: '✨'} (Manually translated by Francesca)
    'Emojilingo\nChat-GPT\n(Manuale \nIncompleto)',
    'Emojilingo\nChat-GPT\n(Manuale)',                           # same above
    'Emojilingo\nChat-GPT\n3.5-turbo-0125\n(Italian)',           # same above
    'Spiegazione\nChat-GPT\n3.5-turbo-0125\n(Italian)',         # same above
    'Emojilingo\nChat-GPT\n4-0613\n(Italian)',                  # same above
    'Spiegazione\nChat-GPT\n4-0613\n(Italian)',                 # same above
    'Emojilingo\nChat-GPT\n3.5-turbo-0125\n(English)',           # same above
    'Spiegazione\nChat-GPT\n3.5-turbo-0125\n(English)',         # same above
    'Emojilingo\nChat-GPT\n4-0613\n(English)',                  # same above
    'Spiegazione\nChat-GPT\n4-0613\n(English)',                  # same above

    # EVALUATION
    'Eval GPT-4-0613\nItalian\nWinner, Model',
    'Eval GPT-4-0613\nItalian\nWinner, Emoji',

    'Source IT', # {0: "Trasumanar significar ...', 364: '...'}
    'Source EN'  # same above
]





'''

DIVINA_COMMEDIA_JSON = os.path.join('../_sources/dc_Hollander.json')
SPREADSHEET_KEY = '13vkH3a-C0OpVTm9r5daFg_y0MN8lPASwGICaa72zaGg'
SPREADSHEET_GID = 262347955
EMOJILINGO_GPT_COLUMN_HEADER = 'Eval GPT-4-0613\nItalian\nWinner, Emoji'

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
            result =  f'{before}\\textit{{{span_chars}}}{after}'
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


    result = ' \\newline\n'.join(result)
    score, matched_span, emph_terzina = fuzzy_enhence(term, result)
    if debug:
        if score < 0.65:
            print(
                f'{score}: term="{term}" match="{matched_span}" book={book_en} canto={canto_num}  line={line}')
            print('Terzina:', emph_terzina)
            print('--------------\n')

    return emph_terzina

SUB_EMOJI = {
    'italy': 'flag-italy',
    'a-button-(blood-type)': 'a-button-blood-type',
    'enraged-face': 'red-question-mark', #TODO: fix me
    'face-with-crossed-out-eyes': 'red-question-mark' #TODO: fix me
}

def get_emoji_tex(em_str):
    # Emojitaliano (\emoji{cut-of-meat}\emoji{wolf}})
    tex = ''
    for e in emoji.analyze(em_str):
        e_tex = e.value.data['en'].lower() # 👍 -> :thumbs_up:
        e_tex = e_tex[1:-1] # remove : beginning and end (thumbs_up)
        e_tex = e_tex.replace('_','-') # thumbs_up -> thumbs-up
        e_tex = e_tex.replace('’', '') # man’s-shoe -> mans-shoe
        if e_tex in SUB_EMOJI:
            e_tex = SUB_EMOJI[e_tex]
        tex += f'\emoji{{{e_tex}}}'
    return tex

def date_sorter(dm):
    # TODO: fix me
    result =  [int(x) for x in dm.split('.')]
    result.reverse()
    result = tuple(result)
    return result

def main(lang, months, col_num):

    assert lang in ['IT','EN']

    # open divina commedia
    with open(DIVINA_COMMEDIA_JSON) as fin:
        dc_json = json.load(fin)

    languages = {
        'IT': 'Italiano',
        'EN': 'English'
    }

    table = download_table(SPREADSHEET_KEY, SPREADSHEET_GID)

    dates = list(ensure_strings_dict(table['Day']).values())

    table_emojitaliano = ensure_strings_dict(table['Emojitaliano']) # manually translated (by Francesca)
    table_emojilingo_chatgpt = ensure_strings_dict(table[EMOJILINGO_GPT_COLUMN_HEADER])

    table_lang = ensure_strings_dict(table[lang])
    emojitaliano = list(table_emojitaliano.values())
    emojilingo = list(table_emojilingo_chatgpt.values())
    txt_lang = list(table_lang.values())
    ref_lang= list(table[f'Ref {lang}'].values())
    ref_EN= list(table[f'Ref EN'].values())
    source_lang = list(table[f'Source {lang}'].values())

    # table tex output
    tex_output = []

    tex_output.append(
        textwrap.dedent(
            '''
            \\begin{tabular}{
                m{2cm} % term
                p{2cm} % date
                m{5cm} % verse
                % m{5cm} % crusca explanation
                m{2cm} % emojitaliano
                m{2cm} % emojilingo
                % m{3cm} % chat-gpt 3.5
                % m{3cm} % chat-gpt 4
                % m{5cm} % chat-gpt explanation
            }
            % HEADER
                \multicolumn{1}{c}{\\textbf{Term}}
            &   \multicolumn{1}{c}{\\textbf{Date}}
            &   \multicolumn{1}{c}{\\textbf{Verse}}
            %&  \multicolumn{1}{c}{\\textbf{AC Explanation}}
            &   \multicolumn{1}{c}{\\textbf{Emojitaliano}}
            &   \multicolumn{1}{c}{\\textbf{Emojilingo}}
            %&  \multicolumn{1}{c}{\\textbf{GPT-3.5 (IT)}}
            %&  \multicolumn{1}{c}{\\textbf{GPT-4 (IT)}}
            %&  \multicolumn{1}{c}{\\textbf{GPT-4 (IT) Explanation}}
            \\\\  \hline
            '''
        )
    )

    date_txt_el_ref_source = [
        (d, t, ei, el, r_en, r_lang, s) for d, t, ei, el, r_en, r_lang, s in
        zip(dates, txt_lang, emojitaliano, emojilingo, ref_EN, ref_lang, source_lang)
    ]

    # default sorted by month and date
    date_txt_el_ref_source_sorted = date_txt_el_ref_source

    # date_txt_el_ref_source_sorted = sorted(
        # sorted alpha by term (parenthesis at the end)
        # date_txt_el_ref_source, key=lambda x: (not x[1][0].isalnum(), x[1].lower())
        # sorted by month and date
        # date_txt_el_ref_source, key=lambda x: date_sorter(x[0]) # TODO: fix me
    # )

    # debug: take first few
    # date_txt_el_ref_source_sorted = date_txt_el_ref_source_sorted[:100]

    # filter only current months
    date_txt_el_ref_source_sorted = [
        row for row in date_txt_el_ref_source_sorted
        if int(row[0].split('.')[1]) in months
    ]

    for d, term, ei, el, ref_en, ref_lang, source in date_txt_el_ref_source_sorted:
        ref_book_EN, ref_canto_roman, ref_line_num = ref_en.split(',')
        ref_book_EN = ref_book_EN.strip()
        ref_canto_num = roman.fromRoman(ref_canto_roman.strip())
        ref_line_num = int(ref_line_num)
        # ei = ei.replace('\n','').replace("'","^") # emojitaliano
        ei_tex = get_emoji_tex(ei) # emojitaliano tex (\emoji{thumb-up})
        el_tex = get_emoji_tex(el) # emojilingo tex (\emoji{thumb-up})

        terzina_lang = get_terzina(
            dc_json, lang, ref_book_EN, ref_canto_num, ref_line_num, term,
            debug=False
        )

        tex_output.extend([
            f'\\raggedright \\textbf{{{term}}} % term', # term
            f'& \multicolumn{{1}}{{r}}{{{d}}} % date', # date
            f'& \\tiny {terzina_lang} % verse', # verse
            # f'& \multicolumn{{1}}{{c}}{{{expl}}} % AC expl', # ac. Crusca Explanation
            f'& \multicolumn{{1}}{{c}}{{\\normalsize {ei_tex}}} % emojitaliano', # emojitaliano
            f'& \multicolumn{{1}}{{c}}{{\\normalsize {el_tex}}} % emojilingo', # emojilingo
            # f'& \multicolumn{{1}}{{c}}{{\\LARGE {{{gpt35}}}}}',
            # f'& \multicolumn{{1}}{{c}}{{\\LARGE {{{gpt4}}}}}',
            # f'& \multicolumn{{1}}{{c}}{{\\LARGE {{{gpt4_expl}}}}}',
            '\\\\  \hline'
        ])

    # end of tbody
    tex_output.append(
        '\end{tabular}'
    )

    output_filepath = f'/Users/fedja/GDrive/CloudDocs/University/MyWorks/24CLiC_Emojilingo/poster/table_auto_{col_num}.tex'
    with open(output_filepath, 'w') as f:
        f.write('\n'.join(tex_output))

if __name__ == "__main__":
    main('IT', months=[1,2,3], col_num=1)
    main('IT', months=[4,5,6], col_num=2)
    main('IT', months=[7,8,9], col_num=3)
    main('IT', months=[10,11,12], col_num=4)