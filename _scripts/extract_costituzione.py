import requests
import pandas as pd
from io import BytesIO
import json

def download_table():
    # Specimens spreadsheet
    spreadsheet_key = '1WjbNJpujytIiY3spG_kPBgoEgL3g372zKqm-Lk6kRdQ'
    gid = 2037170684
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
        '<div class="tableFixHeadScrollBody">',
            '<table>'
                '<colgroup>',
                    '<col width="5%">',
                    '<col width="30%">',
                    '<col width="30%">',
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

    with open('_i18n/en/costituzione.html', 'w') as f:
        f.write('\n'.join(md_output))

if __name__ == "__main__":
    main()
