import pandas as pd

"""
https://www.iflscience.com/editors-blog/linguistic-expert-recommends-the-best-opening-wordle-word/
"""


def letter_prob():
    return dict(
        S=3033,
        E=3009,
        A=2348,
        O=1915,
        R=1910,
        I=1592,
        L=1586,
        T=1585,
        N=1285,
        D=1181,
        U=1089,
        C=964,
        P=955,
        Y=886,
        M=843,
        H=814,
        B=715,
        G=679,
        K=596,
        F=561,
        W=505,
        V=318,
        X=139,
        Z=135,
        J=89,
        Q=53,
    )


def Stanford() -> list[list]:
    """
    https://www-cs-faculty.stanford.edu/~knuth/sgb.html
    """
    lines = []
    with open("stanford_5words.txt") as f:
        lines.append(
            [
                "w0",
                "w1",
                "w2",
                "w3",
                "w4",
                "word",
                "letterprobsum",
                "uniqueprobsum",
                "wordfreq",
                "posprobsum",
            ]
        )
        f.readline()  # throw away header
        for line in f.readlines():
            record = list(line.strip())
            record.append(line.strip())
            record.append(
                sum([letter_prob.get(a.upper(), 0) for a in list(line.strip())])
            )
            record.append(
                sum([letter_prob.get(a.upper(), 0) for a in set(line.strip())])
            )
            record.append(None)
            record.append(None)
            lines.append(record)
    return lines


def GoogleNGram() -> list[list]:
    """
    from google_ngram_downloader import readline_google_store
    readline_google_store(ngram_len=1,indices=[a-z]])
    this takes a long time, should be multithreaded.
    For this reason, here's a txt file of the end result
    """
    lines = []
    with open("google_word_freq.txt") as f:
        lines.append(
            [
                "w0",
                "w1",
                "w2",
                "w3",
                "w4",
                "word",
                "letterprobsum",
                "uniqueprobsum",
                "wordfreq",
                "posprobsum",
            ]
        )
        for line in f.readlines():
            line, freq = line.split(",")
            record = list(line.strip())
            record.append(line.strip())
            record.append(
                sum([letter_prob.get(a.upper(), 0) for a in list(line.strip())])
            )
            record.append(
                sum([letter_prob.get(a.upper(), 0) for a in set(line.strip())])
            )
            record.append(freq)
            record.append(None)
            lines.append(record)
    return lines


def build_frame(lines: list[list]) -> pd.DataFrame:
    df = pd.DataFrame(data=lines[1:], columns=lines[0])
    df_pos = build_pos_freq(df=df)
    # TODO merge df and df_pos to get static positional prob
    # df:w0 char in pos_freq
    return df


def build_pos_freq(df: pd.DataFrame) -> pd.DataFrame:
    w0 = df["w0"].value_counts().sort_values()
    w1 = df["w1"].value_counts().sort_values()
    w2 = df["w2"].value_counts().sort_values()
    w3 = df["w3"].value_counts().sort_values()
    w4 = df["w4"].value_counts().sort_values()
    return pd.concat([w0, w1, w2, w3, w4], axis=1)
