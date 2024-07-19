import time
from dotenv import load_dotenv
import os
import textwrap
import time
from openai import OpenAI
import json
from .utils import download_table, ensure_strings_dict

SPREADSHEET_KEY = '13vkH3a-C0OpVTm9r5daFg_y0MN8lPASwGICaa72zaGg'
SPREADSHEET_GID = 262347955

# https://platform.openai.com/docs/overview
# MODEL = "gpt-3.5-turbo"
# MODEL = "gpt-4-turbo"
MODEL = "gpt-4"

# LANG = 'IT'
LANG = 'EN'

CHATGPT_JSON = os.path.join('../_chatgpt/', f'{MODEL}_{LANG}.json')

PROMPT_WITH_TERM = {
    'IT': textwrap.dedent(
            """\
            Ti darò una parola dalla Divina Commedia di Dante e ti chiedo di inventare una traduzione in emoji.

            Rispondimi con una singola traduzione in 2 righe di testo puro (senza formattazione):
            - traduzione in emoji
            - breve frase di spiegazione della scelta.

            La parola è `{term}`"""
        ),
    'EN': textwrap.dedent(
            """\
            I will give you a word from Dante's Divine Comedy and ask you to invent a translation in emoji.

            Respond with a single translation in 2 lines of plain text (without formatting):
            - translation in emoji
            - brief explanation of the choice.

            The word is {term}"""
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

def chat_with_gpt(term, debug=True):

    # single message with prompt and term
    messages = [
        {
            "role": "user",
            "content": PROMPT_WITH_TERM[LANG].format(term=term)
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
            f'term_{LANG.lower()}': term,
            'emojilingo_chatgpt': emojilingo_chatgpt,
            'explanation': explanation
        }
    }

    return result_json

def main(debug=True):
    # retrieve terms from spreadsheet
    table = download_table(SPREADSHEET_KEY, SPREADSHEET_GID)
    termini_lang_dict = ensure_strings_dict(table[LANG]) # index -> term
    termini_lang = list(termini_lang_dict.values())

    # test first 10 by uncommenting this line
    # termini_lang = termini_lang[:10]

    num_termini_it = len(termini_lang)

    if os.path.exists(CHATGPT_JSON):
        with open(CHATGPT_JSON) as fin:
            full_result_json = json.load(fin)
            if debug:
                print(f'Found {len(full_result_json)} stored terms')
    else:
        full_result_json = {}


    num_terms_stored = len(full_result_json)

    for index in range(num_terms_stored, num_termini_it):

        term = termini_lang[index]

        if debug:
            print(index)

        term_result_json = chat_with_gpt(term)
        full_result_json[index] = term_result_json

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

# there are repeated terms in the english version of the dante dictionary
# (e.g., scrab, dead)
def find_duplicates(filepath):
    with open(filepath) as fin:
        full_result_json = json.load(fin)

    term_set = set()
    duplicate_set = set()

    for idx, value in full_result_json.items():
        term_lang = value['response_processed'][f'term_{LANG.lower()}']
        if term_lang in term_set:
            duplicate_set.add(term_lang)
        else:
            term_set.add(term_lang)

    print(f'Duplicatess ({len(duplicate_set)}): {duplicate_set}')

# use idx instead of term in keys to avoid duplications
def fix_chatgpt_json(filepath):
    with open(filepath) as fin:
        full_result_json = json.load(fin)

    new_dict = {
        idx: value
        for idx, (term, value)
        in enumerate(full_result_json.items())
    }

    filepath = filepath.replace('.json','_fixed.json')

    with open(filepath, 'w') as fout:
        json.dump(new_dict, fout, indent=3, ensure_ascii=False)
'''
Create a test.txt file with a field from chatgpt.json
'''
def extract_chatgpt_emojilingo_explanations():

    with open(CHATGPT_JSON) as fin:
        full_result_json = json.load(fin)

    with open('em_expl_tmp.txt', 'w') as fout:
        fout.write(
            '\n'.join([
                '\t'.join([
                    value['response_processed'][f'term_{LANG.lower()}'],
                    value['response_processed']['emojilingo_chatgpt'],
                    value['response_processed']['explanation']
                ])
                for
                    term, value
                    in full_result_json.items()
            ])
        )


def test_chatgpt():
    messages = [
        {
            "role": "user",
            "content": 'Tell me a joke'
        }
    ]
    response = send_request_to_chatgpt(messages)
    print(response)

if __name__ == "__main__":
    # test_chatgpt()

    main()
    extract_chatgpt_emojilingo_explanations()

    # fix_chatgpt_json('../_chatgpt/gpt-4_EN.json')

    # find_duplicates('../_chatgpt/gpt-3.5-turbo_EN.json')
    # {'fear', 'scab', 'dead'}




