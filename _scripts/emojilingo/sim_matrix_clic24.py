import numpy as np
import emoji
from tqdm import tqdm
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from emojilingo.extract_parole_di_dante import download_table
from emojilingo.extract_parole_di_dante import ensure_strings_dict
from scipy.spatial.distance import hamming


SPREADSHEET_KEY = '13vkH3a-C0OpVTm9r5daFg_y0MN8lPASwGICaa72zaGg'
SPREADSHEET_GID = 262347955
EMOJITIALINO_HEADER = 'Emojitaliano'
# EMOJILINGO_GPT_COLUMN_HEADER = 'Eval GPT-4-0613\nItalian\nWinner, Emoji'
EMOJILINGO_GPT35_COLUMN_HEADER = 'Emojilingo\nChat-GPT\n3.5-turbo-0125\n(Italian)'
EMOJILINGO_GPT4_COLUMN_HEADER = 'Emojilingo\nChat-GPT\n4-0613\n(Italian)'

def get_clean_emoji_list(e):
    return [a.value.emoji for a in emoji.analyze(e)]

def normalize_pair(a,b):
    # make sure they are the same length
    len_a = len(a)
    len_b = len(b)
    if len_a != len_b:
        pair = [a, b]
        pair_len = [len_a, len_b]
        max_len = max(len_a, len_b)
        max_i = max_len == len_b
        other_i = 1 - max_i
        other_len = pair_len[other_i]
        diff = max_len - other_len
        padding = [''] * diff
        pair[other_i].extend(padding)

def plot_confusioon_matrix(similarity_matrix, chat_gpt_name):
    # Y: emojitaliano
    # X: chat_gpt
    size_y, size_x = similarity_matrix.shape
    fig, ax = plt.subplots(figsize=(10,10))
    sns.heatmap(
        similarity_matrix,
        annot = False,
        cmap = 'gray_r', # inverted gray
        # linewidths = 0.,
        square = True,
        cbar_kws={"shrink": .82},
        ax = ax
    )
    x_ticks = np.linspace(0, size_x, 10)
    y_ticks = np.linspace(0, size_y, 10)
    ax.set_yticks(x_ticks)
    ax.set_xticks(y_ticks)
    ax.set_xticklabels([str(int(x)) for x in x_ticks])
    ax.set_yticklabels([str(int(y)) for y in y_ticks])
    plt.xlabel(f'{chat_gpt_name}', fontsize=20)
    plt.ylabel('Emojitaliano', fontsize=20)
    plt.savefig(f'img/sim_matrix_{chat_gpt_name}.pdf')
    plt.savefig(f'img/sim_matrix_{chat_gpt_name}.png')

def extract_emojis(chat_gpt_header, chat_gpt_name):
    table = download_table(SPREADSHEET_KEY, SPREADSHEET_GID)
    table_emojitaliano = ensure_strings_dict(table[EMOJITIALINO_HEADER]) # manually translated (by Francesca)
    table_chatgpt = ensure_strings_dict(table[chat_gpt_header])
    emojitaliano = list(table_emojitaliano.values())
    chat_gpt = list(table_chatgpt.values())
    chat_gpt_header_one_line = chat_gpt_header.replace('\n',' ')
    len_emojitaliano = len(emojitaliano)
    len_chat_gpt = len(chat_gpt)
    assert len_emojitaliano == len_chat_gpt
    print(f'Extracted {len_emojitaliano} emojis from column `{EMOJITIALINO_HEADER}`')
    print(f'Extracted {len_chat_gpt} emojis from column `{chat_gpt_header_one_line}`')
    combination = len_emojitaliano * len_chat_gpt
    print('Combinations:', combination)
    bar = tqdm(total=combination)
    similarity_matrix = np.zeros((len_emojitaliano, len_chat_gpt))
    identical_counts = 0
    for i in range(len_emojitaliano):
        for j in range(len_chat_gpt):
            bar.update()
            ei = emojitaliano[i]
            el = chat_gpt[j]
            ei_list = get_clean_emoji_list(ei)
            el_list = get_clean_emoji_list(el)
            normalize_pair(ei_list, el_list)
            assert len(ei_list) == len(el_list)
            identical = ei == el
            same_list = ei_list == el_list
            if same_list:
                identical_counts += 1
            # assert identical == same_list
            distance = hamming(ei_list, el_list)
            similarity_matrix[i,j] = 1. - distance
    print('Identical counts:', identical_counts)
    plot_confusioon_matrix(similarity_matrix, chat_gpt_name)


if __name__ == "__main__":
    extract_emojis(EMOJILINGO_GPT35_COLUMN_HEADER, 'Chat-GPT-3.5')
    extract_emojis(EMOJILINGO_GPT4_COLUMN_HEADER, 'Chat-GPT-4')