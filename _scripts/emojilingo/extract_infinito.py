import requests
import pandas as pd
from io import BytesIO
import json

languages = {
    'IT': 'Italiano',
    'EN': 'English'
}

title = {
    'IT': "L'infinito di Giacomo Leopardi",
    'EN': 'The Infinity by Giacomo Leopardi'
}

def download_table():
    # Specimens spreadsheet
    spreadsheet_key = '1WjbNJpujytIiY3spG_kPBgoEgL3g372zKqm-Lk6kRdQ'
    gid = 0
    url = f'https://docs.google.com/spreadsheets/d/{spreadsheet_key}/export?gid={gid}&format=csv'
    r = requests.get(url, allow_redirects=True)
    data = r.content
    df = pd.read_csv(BytesIO(data))
    table = df.to_dict()
    return table

def main():
    table = download_table()
    # print(json.dumps(table, indent=3))
    for lang in ['IT','EN']:
        table_lang = table[lang]
        table_emojilingo = table['EMOJILINGO']
        words = table_lang.values()
        emojilingo = table_emojilingo.values()

        md_output = []

        md_output.extend([
            f'<h1>{title[lang]}</h1>',
        ])

        md_output.extend([
            '<div>',
                '<table>'
                    '<colgroup>',
                        '<col width="50%">',
                        '<col width="50%">',
                    '</colgroup>'
        ])

        # header
        md_output.extend([
            '<thead>',
                '<tr class="table-header">',
                    f'<th>{languages[lang]}</th>',
                    f'<th>Emojilingo</th>',
                '</tr>',
            '</thead>',
        ])

        # start of tbody
        md_output.extend([
            '<tbody>'
        ])

        words_emojilingo_lines = [
            (l, el) for l, el in
            zip(words, emojilingo)
        ]

        for txt, el in words_emojilingo_lines:
            el = el.replace('\n','').replace("'","^")

            md_output.extend([
                '<tr class="notfirst">',
                    '<td> <span>' + txt + '</span> </td>',
                    '<td> <span class=emojitext>' + el + '</span> </td>',
                '</tr>',
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

        with open(f'_i18n/{lang.lower()}/infinito.html', 'w') as f:
            f.write('\n'.join(md_output))

if __name__ == "__main__":
    main()
