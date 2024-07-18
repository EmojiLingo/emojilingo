import re
import json
import os


def process_file_lines_canto(filepath):
    with open(filepath) as f:
        canto_lines = f.readlines()
    line_num = 0
    it_json = {}
    en_json = {}
    result = [it_json, en_json]
    for l in canto_lines:
        l = l.strip()
        re_patt = re.compile(r'\t\d+\t')
        mo = re_patt.search(l)
        if (mo):
            line_num += 1
            start, end = mo.span()
            it_line = l[:start]
            en_line = l[end:]
            # print(f'{line_num}\n\tIT: {it_line}\n\tEN: {en_line}')
            it_json[line_num] = it_line
            en_json[line_num] = en_line
    return result

def process_IT_EN():
    dirname = os.path.dirname(__file__)
    dirpath = os.path.join(dirname, '../_sources/dc_Hollander')
    books = ['Hell','Purgatory','Paradise']
    full_json = {}
    '''
    {
        'hell':
            1: {
                'IT': {
                    1: 'line 1 IT canto 1',
                    2: ...,
                    136: ...,
                },
                'EN': {
                    1: 'line 1 EN canto 1',
                    2: ...,
                    136: ...,
                },
            },
        'purgatory': {...},
        'paradise': {...},
    }
    '''
    for book in books:
        full_json[book] = {}
        len_canti = 34 if book=='Hell' else 33
        for canto_num in range(1,len_canti+1):
            canto_num_str = f'{canto_num}'.zfill(2) # two digits
            filepath = os.path.join(dirpath, f'{book}{canto_num_str}.txt')
            it_json, en_json = process_file_lines_canto(filepath)
            full_json[book][canto_num] = {
                'IT': it_json,
                'EN': en_json,
            }
    dirname = os.path.dirname(__file__)
    output_file_json = os.path.join(dirname, '../_sources/dc_Hollander.json')
    with open(output_file_json, 'w') as fout:
        json.dump(full_json, fout, indent=3, ensure_ascii=False)

if __name__ == "__main__":
    process_IT_EN()
