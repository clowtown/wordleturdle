from functools import partial, reduce
import pandas as pd


def reduce_known(letter, result, index, row) -> bool:
    keep_it = True
    # x = letter not in word
    # y = letter in word
    # y = letter not this position
    # g = letter in this position
    # TODO: handle case of repeating letters which are x's while others are green (yellow?)
    keep_it &= not letter in row["word"] if result == "x" else True
    keep_it &= row[f"w{index}"] != letter if result == "y" else True
    keep_it &= row[f"w{index}"] == letter if result == "g" else True
    keep_it &= letter in row["word"] if result == "y" else True
    return keep_it

def reduce_unknown(letter, result, index, row) -> bool:
    keep_it = True
    # x = letter not in word, best thing ever
    # y = letter in word
    # y = letter not this position
    # g = do not pick these
    # TODO: handle case of repeating letters which are x's while others are green (yellow?)
    # keep_it &= not letter in row["word"] if result == "x" else True
    # keep_it &= row[f"w{index}"] != letter if result == "y" else True
    keep_it &= row[f"w{index}"] != letter if result == "g" else True
    # keep_it &= letter in row["word"] if result == "y" else True
    return keep_it


def process_result(df, word_result,reducer) -> pd.DataFrame:
    df_word = df.copy()
    for c_r_i in word_result:
        letter, result, index = c_r_i
        result = int(result)
        index = int(index)
        df_word = df_word[
            df_word.apply(partial(reducer, letter, result, index), axis=1)
        ]
    return df_word


def in_prep(word, result) -> tuple[str, str, str]:
    word_result_index = list(zip(word, result, range(0, 5)))
    return word_result_index


def do_guess(df, word, result) -> pd.DataFrame:
    word_result = in_prep(word, result)
    df = process_result(df=df, word_result=word_result,reducer=reduce_known)
    return df

def do_eliminate(df, word, result) -> pd.DataFrame:
    word_result = in_prep(word, result)
    df = process_result(df=df, word_result=word_result,reducer=reduce_unknown)
    return df
