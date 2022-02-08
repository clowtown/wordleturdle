import pandas as pd


def letter_prob():
    """
    https://www.iflscience.com/editors-blog/linguistic-expert-recommends-the-best-opening-wordle-word/
    """
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
                "word",
            ]
        )
        f.readline()  # throw away header
        for line in f.readlines():
            record = list()
            record.append(line.strip())
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
                "word",
                "wordfreq",
            ]
        )
        for line in f.readlines():
            line, freq = line.split(",")
            if len(line) > 5:
                continue
            record = list()
            record.append(line.strip())
            record.append(int(freq.strip()))
            lines.append(record)
    return lines


def build_frame() -> pd.DataFrame:
    lines = Stanford()
    df1 = pd.DataFrame(data=lines[1:], columns=lines[0])
    df1["Standford"] = True
    lines = GoogleNGram()
    df2 = pd.DataFrame(data=lines[1:], columns=lines[0])
    df2["Google"] = True
    dfm = pd.merge(df1, df2, "outer", left_on="word", right_on="word")
    dfm["w0"] = dfm["word"].apply(lambda word: list(word)[0])
    dfm["w1"] = dfm["word"].apply(lambda word: list(word)[1])
    dfm["w2"] = dfm["word"].apply(lambda word: list(word)[2])
    dfm["w3"] = dfm["word"].apply(lambda word: list(word)[3])
    dfm["w4"] = dfm["word"].apply(lambda word: list(word)[4])
    dfm["letterprobsum"] = dfm["word"].apply(
        lambda word: sum([letter_prob().get(a.upper(), 0) for a in list(word)])
    )
    dfm["uniqueprobsum"] = dfm["word"].apply(
        lambda word: sum([letter_prob().get(a.upper(), 0) for a in set(word)])
    )
    return update_pos_freq(dfm=dfm)


def update_pos_freq(dfm: pd.DataFrame) -> pd.DataFrame:
    dfm = dfm.drop(
        columns=["w0pf", "w1pf", "w2pf", "w3pf", "w4pf", "posprobsum"], errors="ignore"
    )
    df_pos = build_pos_freq(df=dfm)
    dfm_pos0 = pd.merge(dfm, df_pos["w0pf"], "left", left_on=["w0"], right_index=True)
    dfm_pos1 = pd.merge(
        dfm_pos0, df_pos["w1pf"], "left", left_on=["w1"], right_index=True
    )
    dfm_pos2 = pd.merge(
        dfm_pos1, df_pos["w2pf"], "left", left_on=["w2"], right_index=True
    )
    dfm_pos3 = pd.merge(
        dfm_pos2, df_pos["w3pf"], "left", left_on=["w3"], right_index=True
    )
    dfm_pos4 = pd.merge(
        dfm_pos3, df_pos["w4pf"], "left", left_on=["w4"], right_index=True
    )
    dfm_pos4["posprobsum"] = (
        dfm_pos4["w0pf"]
        + dfm_pos4["w1pf"]
        + dfm_pos4["w2pf"]
        + dfm_pos4["w3pf"]
        + dfm_pos4["w4pf"]
    )
    return dfm_pos4


def build_pos_freq(df: pd.DataFrame) -> pd.DataFrame:
    w0 = df["w0"].value_counts().sort_values()
    w1 = df["w1"].value_counts().sort_values()
    w2 = df["w2"].value_counts().sort_values()
    w3 = df["w3"].value_counts().sort_values()
    w4 = df["w4"].value_counts().sort_values()
    pf_df = pd.concat([w0, w1, w2, w3, w4], axis=1)
    df_pf = pf_df.rename(
        columns={"w0": "w0pf", "w1": "w1pf", "w2": "w2pf", "w3": "w3pf", "w4": "w4pf"}
    )
    return df_pf
