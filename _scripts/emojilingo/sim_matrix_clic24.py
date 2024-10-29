import numpy as np
import emoji
from tqdm import tqdm
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from pylab import text
from matplotlib.font_manager import FontProperties
from emojilingo.extract_parole_di_dante import download_table
from emojilingo.extract_parole_di_dante import ensure_strings_dict
from scipy.spatial.distance import hamming
from Levenshtein import distance as lev_dist


SPREADSHEET_KEY = '13vkH3a-C0OpVTm9r5daFg_y0MN8lPASwGICaa72zaGg'
SPREADSHEET_GID = 262347955

EMOJITIALINO_HEADER = 'Emojitaliano' # G
EMOJILINGO_GPT35_IT_COLUMN_HEADER = 'Emojilingo\nChat-GPT\n3.5-turbo-0125\n(Italian)' # I
EMOJILINGO_GPT4_IT_COLUMN_HEADER = 'Emojilingo\nChat-GPT\n4-0613\n(Italian)' # K
EMOJILINGO_GPT4_WINNER_COLUMN_HEADER = 'Eval GPT-4-0613\nItalian\nWinner, Emoji' # N
EMOJILINGO_GPT35_EN_COLUMN_HEADER = 'Emojilingo\nChat-GPT\n3.5-turbo-0125\n(English)' # O
EMOJILINGO_GPT4_EN_COLUMN_HEADER = 'Emojilingo\nChat-GPT\n4-0613\n(English)' # Q


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
    ax.set_yticks(y_ticks)
    ax.set_xticks(x_ticks)
    ax.set_xticklabels([str(int(x)) for x in x_ticks])
    ax.set_yticklabels([str(int(y)) for y in y_ticks])
    plt.xlabel(f'{chat_gpt_name}', fontsize=20)
    plt.ylabel('Emojitaliano', fontsize=20)
    plt.savefig(f'img/sim_matrix_{chat_gpt_name}.pdf')
    plt.savefig(f'img/sim_matrix_{chat_gpt_name}.png')

def make_matrix_old(chat_gpt_header, chat_gpt_name):
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

def get_emoji_data_dict():
    table = download_table(SPREADSHEET_KEY, SPREADSHEET_GID)
    table_emojitaliano = ensure_strings_dict(table[EMOJITIALINO_HEADER]) # manually translated (by Francesca)
    table_chatgpt35it = ensure_strings_dict(table[EMOJILINGO_GPT35_IT_COLUMN_HEADER])
    table_chatgpt4it = ensure_strings_dict(table[EMOJILINGO_GPT4_IT_COLUMN_HEADER])
    table_chatgpt35en = ensure_strings_dict(table[EMOJILINGO_GPT35_EN_COLUMN_HEADER])
    table_chatgpt4en = ensure_strings_dict(table[EMOJILINGO_GPT4_EN_COLUMN_HEADER])
    table_chatgpt4win = ensure_strings_dict(table[EMOJILINGO_GPT4_WINNER_COLUMN_HEADER])

    # values
    emojitaliano = list(table_emojitaliano.values())
    chatgpt35it = list(table_chatgpt35it.values())
    chatgpt4it = list(table_chatgpt4it.values())
    chatgpt35en = list(table_chatgpt35en.values())
    chatgpt4en = list(table_chatgpt4en.values())
    chatgpt4win = list(table_chatgpt4win.values())

    size = len(emojitaliano)
    print('Size:', size)

    emoji_data = {
        'Emojitaliano': emojitaliano,
        'Chat-GPT 3.5 IT': chatgpt35it,
        'Chat-GPT 4 IT': chatgpt4it,
        'Chat-GPT 3.5 EN': chatgpt35en,
        'Chat-GPT 4 EN': chatgpt4en,
        'Chat-GPT 4 WIN': chatgpt4win,
    }

    return emoji_data

def norm_lev_dist(a, b):
    max_l = max(len(a),len(b))
    return lev_dist(a,b) / max_l

def make_heat_bars():

    emoji_data = get_emoji_data_dict()

    emojitaliano = emoji_data['Emojitaliano']
    size = len(emojitaliano)

    # name - 1d array with sim values
    name_sim_bars = dict()
    for n,l in emoji_data.items():
        assert len(l) == size
        name_sim_bars[n] = np.zeros(size)

    for i in range(size):
        ei = emojitaliano[i]
        for el_name, el_values in emoji_data.items():
            el = el_values[i]
            ei_list = get_clean_emoji_list(ei)
            el_list = get_clean_emoji_list(el)
            # normalize_pair(ei_list, el_list) # only needed for hamming distance
            # distance = hamming(ei_list, el_list)
            distance = norm_lev_dist(ei_list, el_list)
            name_sim_bars[el_name][i] = 1. - distance

    df = pd.DataFrame(
            name_sim_bars,
            index = [str(i) for i in range(1, size+1)]
        )
    fig, ax = plt.subplots(figsize=(8,22))
    sns.heatmap(
        df,
        annot = False,
        # fmt="g", # String formatting code to use when adding annotations.
        # square=True,
        # linewidths=.5, #Width of the lines that will divide each cell.
        # cbar=0, # no legend
        cmap='gray_r'
    )
    plt.ylabel('Emojitaliano', fontsize=20)
    y_ticks = np.linspace(1, size, 10)
    ax.set_yticks(y_ticks)
    y_labels = [str(int(y)) for y in y_ticks] # numbers

    # trying with emojis
    # font = FontProperties(fname='/Users/fedja/Code/emojilingo/assets/AppleColorEmoji.ttf')
    # ax.set_ylabel([
    #     text(-0.8, 0.9, e, fontproperties=font)
    #     for e in emojitaliano
    # ])

    ax.set_yticklabels(y_labels)
    ax.set_xticklabels(emoji_data.keys(), fontsize = 16)
    plt.xticks(rotation=45, ha="right")

    # plt.show()
    plt.savefig(f'img/sim_bars.png')
    plt.savefig(f'img/sim_bars.pdf')

def make_heat_plot_final():

    emoji_data = get_emoji_data_dict()
    num_models = len(emoji_data)

    emojitaliano = emoji_data['Emojitaliano']
    size = len(emojitaliano)

    sim_matrix = np.zeros((num_models, num_models))

    for y, ky in enumerate(emoji_data.keys()):
        y_emoji_list = emoji_data[ky]
        for x, kx in enumerate(emoji_data.keys()):
            x_emoji_list = emoji_data[kx]
            sim_array = np.zeros(size)
            for i in range(size):
                ey = y_emoji_list[i]
                ex = x_emoji_list[i]
                ey_list = get_clean_emoji_list(ey)
                ex_list = get_clean_emoji_list(ex)
                # normalize_pair(ei_list, el_list) # only needed for hamming distance
                # distance = hamming(ei_list, el_list)
                distance = norm_lev_dist(ey_list, ex_list)
                sim = 1. - distance
                sim_array[i] = sim
            sim_mean = np.mean(sim_array)
            sim_matrix[y,x] = sim_mean
            # print(f'{ky} - {kx}: {sim_mean}')

    fig, ax = plt.subplots(figsize=(10,10))
    sns.heatmap(
        sim_matrix,
        annot = True,
        cmap = 'gray_r', # inverted gray
        # linewidths = 0.,
        square = True,
        # cbar_kws={"shrink": .82},
        ax = ax
    )
    # x_ticks = np.linspace(0, size_x, 10)
    # y_ticks = np.linspace(0, size_y, 10)
    # ax.set_yticks(y_ticks)
    # ax.set_xticks(x_ticks)
    ax.set_xticklabels(emoji_data.keys(), fontsize = 12)
    ax.set_yticklabels(emoji_data.keys(), fontsize = 12)
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=45, ha="right")
    # ax.set_yticklabels([str(int(y)) for y in y_ticks])
    # plt.xlabel(f'{chat_gpt_name}', fontsize=20)
    # plt.ylabel('Emojitaliano', fontsize=20)
    plt.savefig(f'img/sim_matrix.pdf')
    plt.savefig(f'img/sim_matrix.png')
    # plt.show()



if __name__ == "__main__":
    # make_matrix_old(EMOJILINGO_GPT35_IT_COLUMN_HEADER, 'Chat-GPT-3.5')
    # make_matrix_old(EMOJILINGO_GPT4_IT_COLUMN_HEADER, 'Chat-GPT-4')
    make_heat_bars()
    make_heat_plot_final()