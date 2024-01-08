import requests
import pandas as pd
from io import BytesIO
import json

def download_table():
    spreadsheet_key = '1b6fA1vZU8TabjlTFUy6-ittG-tH65V4g6JqYnCwzU0k'
    url = f'https://docs.google.com/spreadsheets/d/{spreadsheet_key}/export?gid=0&format=csv'
    r = requests.get(url, allow_redirects=True)
    data = r.content    
    df = pd.read_csv(BytesIO(data))
    table = df.to_dict()
    return table

def main():
    table = download_table()
    # print(json.dumps(table, indent=3))
    table_it = table['IT']
    table_en = table['EN']
    table_emojilingo = table['EMOJILINGO']
    strings_it = table_it.values()
    strings_en = table_en.values()
    strings_emojilingo = table_emojilingo.values()
    
    md_output_en_emojilingo = []
    md_output_en_emojilingo.append('# Pinocchio')
    md_output_en_emojilingo.append('')
    md_output_en_emojilingo.append('| English | EmojiLingo |')
    md_output_en_emojilingo.append('| ------- | ---------- |')
    for en,el in zip(strings_en, strings_emojilingo):
        en = en.replace('\n','')
        el = el.replace('\n','').replace("'","^") # "＇"
        md_output_en_emojilingo.append(
            '| ' + en + ' | <span class="emojitext">' + el + '</span> |'
        )

    md_output_it_emojilingo = []
    md_output_it_emojilingo.append('# Pinocchio')
    md_output_it_emojilingo.append('')
    md_output_it_emojilingo.append('| Italiano | EmojiLingo |')
    md_output_it_emojilingo.append('| ------- | ---------- |')
    for it,el in zip(strings_it, strings_emojilingo):
        it = it.replace('\n','')
        el = el.replace('\n','').replace("'","^") # "＇"
        md_output_it_emojilingo.append(
            '| ' + it + ' | <span class="emojitext">' + el + '</span> |'
        )
    
    with open('_i18n/en/examples.md', 'w') as f:
        f.write('\n'.join(md_output_en_emojilingo))

    with open('_i18n/it/examples.md', 'w') as f:
        f.write('\n'.join(md_output_it_emojilingo))


if __name__ == "__main__":
    main()
