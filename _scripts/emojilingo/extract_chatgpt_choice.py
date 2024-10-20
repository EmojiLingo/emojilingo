import time
from dotenv import load_dotenv
import os
import textwrap
import time
from openai import OpenAI
import json
from tqdm import tqdm
from .utils import download_table, ensure_strings_dict
from collections import Counter

SPREADSHEET_KEY = '13vkH3a-C0OpVTm9r5daFg_y0MN8lPASwGICaa72zaGg'
SPREADSHEET_GID = 262347955

# https://platform.openai.com/docs/overview
# MODEL = "gpt-3.5-turbo"
# MODEL = "gpt-4-turbo"
MODEL = "gpt-4" # gpt-4-0613

# LANG = 'IT'
LANG = 'IT'

CHATGPT_JSON = os.path.join('../_chatgpt/', f'{MODEL}_{LANG}_choice.json')

COLS_EMOJI_DICT_SIMPLIFIED = {
    'Emojilingo': 'Emojilingo',
    'Emojilingo\nChat-GPT\n3.5-turbo-0125\n(Italian)': 'GPT-3.5',
    'Emojilingo\nChat-GPT\n4-0613\n(Italian)': 'GPT-4'
}
COL_EMOJI1, COL_EMOJI2, COL_EMOJI3 = COLS_EMOJI = \
    list(COLS_EMOJI_DICT_SIMPLIFIED.keys())


NUM_ITERATIONS = 10 # how many time to ask to evaluate the same emoji pair
WINNER_DIFFERENCE = 2 # how many votes winner should have more than second

TXT_TRANSLATIONS = {
    'IT': {
        'CHOICE': '- Scelta: ',
        'EXPLANATION': '- Spiegazione: '
    },
    'EN': {
        'CHOICE': '- Choice: ',
        'EXPLANATION': '- Explanation: '
    }
}

PROMPT = {
    'IT': textwrap.dedent(\
            """\
            Vorrei chiederti di valutare 3 traduzioni di parole arcaiche italiane estratte dalla Divina Commedia di Dante in emoji.

            Ti fornirò:
            - La parola italiana
            - Traduzione in emoji A
            - Traduzione in emoji B
            - Traduzione in emoji C

            Ti chiedo di dirmi quale traduzione in emoji preferisci e perché.
            Rispondi con 2 righe di testo semplice (senza formattazione) con le seguenti informazioni:
            - Scelta: <stringa emoji>
            - Spiegazione: <Breve spiegazione della scelta>

            Ecco qui:
            - Parola italiana: {term}
            - Traduzione A: {emoji1}
            - Traduzione B: {emoji2}
            - Traduzione C: {emoji3}"""
        ),
    'EN': textwrap.dedent(\
            """\
            I would like to ask you to evaluate 3 translations from archaic Italian words extracted from Dantes's Divina Commedia into emoji.

            I will provide you  with:
            - The Italian word
            - Emoji translation A
            - Emoji translation B
            - Emoji translation C

            I ask you to tell me which translation into emoji do you prefer and why.
            Respond with 2 lines of plain text (without formatting) with the following info:
            - Choice: <emoji string>
            - Explanation: <Brief explanation of the choice>

            Here you are:
            - Italian word: {term}
            - Translation A: {emoji1}
            - Translation B: {emoji2}
            - Translation C: {emoji3}"""
        )
}

load_dotenv()

client = OpenAI(
    api_key = os.getenv('CHATGPT_API_KEY')
)

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

@retry_with_exponential_backoff
def send_request_to_chatgpt(messages):

    response = client.chat.completions.create(

        # the model
        model = MODEL,

        # the message
        messages = messages,

        #  only the new GPT-4 Turbo models support reproducible outputs
        # seed = 7263081721,
        temperature = 1, # default 1

        # request_timeout = 10
    )
    return response

def chat_with_gpt(term, emoji1, emoji2, emoji3, debug=True):

    # single message with prompt and term
    messages = [
        {
            "role": "user",
            "content": PROMPT[LANG].format(
                term=term,
                emoji1=emoji1,
                emoji2=emoji2,
                emoji3=emoji3
            )
        }
    ]

    response = send_request_to_chatgpt(messages)
    choice = response.choices[0]

    response_txt = choice.message.content

    # if debug:
        # print('Term: ', term)
        # print('Response: ', response_txt)

    response_txt_lines = [
        l.strip()
        for l in response_txt.splitlines()
        if l.strip() != ''
    ]

    if len(response_txt_lines)!=2:
        print(f'Error in num of lines ({len(response_txt_lines)})')
        print(f'Repeating request...\n')
        return chat_with_gpt(term, emoji1, emoji2, emoji3)
    else:
        emojilingo_choice, explanation = response_txt_lines
        emojilingo_split = emojilingo_choice.split(
            TXT_TRANSLATIONS[LANG]['CHOICE']) # '- Choice: '
        explanation_split = explanation.split(
            TXT_TRANSLATIONS[LANG]['EXPLANATION']) # 'Explanation: '
        emoji_choice_list = [emoji1, emoji2, emoji3]

        emojilingo_correct = \
            len(emojilingo_split)==2 and \
            emojilingo_split[1] in emoji_choice_list
        explanation_correct = len(explanation_split)==2
        if emojilingo_correct and explanation_correct:
            emojilingo_choice = emojilingo_split[1]
            choice_col_name = COLS_EMOJI[emoji_choice_list.index(emojilingo_choice)]
            explanation = explanation_split[1]
        else:
            print(f'Error in formatting')
            print(f'Response Lines:', response_txt_lines)
            print(f'Repeating request...\n')
            return chat_with_gpt(term, emoji1, emoji2, emoji3)


    # if debug:
    #     print('Emojilingo choice: ', emojilingo_choice)
    #     print('Explanation: ', explanation)

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
            'term': term,
            'choice': emojilingo_choice,
            'choice_source': choice_col_name,
            'explanation': explanation
        }
    }

    return result_json

def get_table_terms_and_emojis():
    table = download_table(SPREADSHEET_KEY, SPREADSHEET_GID)
    termini_lang_dict = ensure_strings_dict(table[LANG]) # index -> term
    termini_lang = list(termini_lang_dict.values())
    emoji1_values = list(ensure_strings_dict(table[COL_EMOJI1]).values())
    emoji2_values = list(ensure_strings_dict(table[COL_EMOJI2]).values())
    emoji3_values = list(ensure_strings_dict(table[COL_EMOJI3]).values())
    return (
        termini_lang,
        emoji1_values,
        emoji2_values,
        emoji3_values
    )

def main(debug=True):
    # retrieve terms from spreadsheet

    (
        termini_lang,
        emoji1_values,
        emoji2_values,
        emoji3_values
    ) = get_table_terms_and_emojis()

    # test first 10 by uncommenting this line
    # termini_lang = termini_lang[:10]

    num_termini_lang = len(termini_lang)

    if os.path.exists(CHATGPT_JSON):
        with open(CHATGPT_JSON) as fin:
            term_all_results_dict = json.load(fin)
            if debug:
                print(f'Found {len(term_all_results_dict)} stored terms')
    else:
        term_all_results_dict = {}


    num_terms_stored = len(term_all_results_dict)
    model = None

    for index in range(num_terms_stored, num_termini_lang):

        term = termini_lang[index]
        emoji1 = emoji1_values[index]
        emoji2 = emoji2_values[index]
        emoji3 = emoji3_values[index]

        if debug:
            print(index)

        iter_results = []

        for _ in tqdm(range(NUM_ITERATIONS)):

            response_json = chat_with_gpt(term, emoji1, emoji2, emoji3)
            response_processed = response_json['response_processed']

            if model is None:
                # print out model once
                model = response_json['model']
                print('Chat-GPT Model', model)

            iter_results.append(response_processed)
            # response_processed keys:
            # - term
            # - choice
            # - choice_source
            # - explanation

        term_all_results_dict[index] = iter_results

        if debug:
            print('\n-----------------------\n')

        # rewrite full json file for every term
        with open(CHATGPT_JSON, 'w') as fout:
            json.dump(
                term_all_results_dict,
                fout,
                indent=3,
                ensure_ascii=False
            )

def test():
    for i in range(5):
        r = chat_with_gpt('trasumanar', '🪐', '🚀👽', '🚶‍♂️➡️👼')
        print(r)
        print('----------\n')

def analysis():

    (
        termini_lang,
        emoji1_values,
        emoji2_values,
        emoji3_values
    ) = get_table_terms_and_emojis()

    with open(CHATGPT_JSON) as fin:
         term_all_results_dict = json.load(fin)

    def get_term_winner_most_common(iter_results):
        term_winner_counter = Counter(
            (el['choice_source'], el['choice'])  # model (full name), emoji
            for el in iter_results
        )
        return term_winner_counter.most_common()

    def print_term_winner_most_common(term_winner_most_common):
        for source, freq in term_winner_most_common:
            print(
                '\n'.join([
                    f'  - {freq}: {COLS_EMOJI_DICT_SIMPLIFIED[source]}'
                ])
            )

    # idx -> NUM_ITERATIONS dicts
    # {'term', 'choice', 'choice_source', 'explanation'}

    # how many rows each model has winned
    model_winner_counter = Counter()

    term_winner_freq = []
    for idx, iter_results in term_all_results_dict.items():
        idx = int(idx)
        term = iter_results[0]['term']
        term_winner_most_common = get_term_winner_most_common(iter_results)
        (first_winner_source, first_winner_emoji), first_winner_freq = term_winner_most_common[0]
        winner_model_simplified = COLS_EMOJI_DICT_SIMPLIFIED[first_winner_source]
        if len(term_winner_most_common)==1:
            # only one winner
            term_winner_freq.append(
                (term, first_winner_emoji, winner_model_simplified, first_winner_freq)
            )
        else:
            # second winner
            (_, _), second_most_common_freq = term_winner_most_common[1]
            diff = first_winner_freq - second_most_common_freq
            if diff >= WINNER_DIFFERENCE:
                model_winner_counter.update([winner_model_simplified])
                term_winner_freq.append(
                    (term, first_winner_emoji, winner_model_simplified, first_winner_freq)
                )
            else:
                # print term winner counter for undecided term
                print(f'Undecided results for: `{term}`')
                print_term_winner_most_common(term_winner_most_common)

                ###########
                # Rerun until WINNER_DIFFERENCE cap
                ###########
                assert termini_lang[idx] == term
                emoji1 = emoji1_values[idx]
                emoji2 = emoji2_values[idx]
                emoji3 = emoji3_values[idx]
                while diff < WINNER_DIFFERENCE:
                    response_json = chat_with_gpt(term, emoji1, emoji2, emoji3)
                    response_processed = response_json['response_processed']
                    winner_model_simplified = COLS_EMOJI_DICT_SIMPLIFIED[
                        response_processed['choice_source']
                    ]
                    print(f'   New run and winner: {winner_model_simplified}')

                    # appending new vote result in iter_results and update counter
                    iter_results.append(response_processed)
                    term_winner_most_common = get_term_winner_most_common(iter_results)
                    (_, first_winner_emoji), first_winner_freq = term_winner_most_common[0]
                    (_, _), second_most_common_freq = term_winner_most_common[1]
                    diff = first_winner_freq - second_most_common_freq

                # print term winner counter for undecided term
                print(f'Decided results for: `{term}`')
                print_term_winner_most_common(term_winner_most_common)
                term_winner_freq.append(
                    (term, first_winner_emoji, winner_model_simplified, first_winner_freq)
                )

                # rewrite to file all updated results
                with open(CHATGPT_JSON, 'w') as fout:
                    json.dump(
                        term_all_results_dict,
                        fout,
                        indent=3,
                        ensure_ascii=False
                    )

                # print new line
                print()

    # winners per term
    print('\n--------------\n')
    print('Rows with winners:', len(term_winner_freq))
    print('\n--------------')
    with open('winner_analysis.txt', 'w') as fout:
        for term_choice_source_freq in term_winner_freq:
            fout.write('\t'.join([str(e) for e in term_choice_source_freq]))
            fout.write('\n')

    # how many rows each model has winned
    print('\n--------------')
    print('Model Winners')
    print('--------------')
    print(model_winner_counter.most_common())

if __name__ == "__main__":
    # test()
    # main()
    analysis()




