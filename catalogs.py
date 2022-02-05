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
            ["w0", "w1", "w2", "w3", "w4", "word", "letterprobsum", "uniqueprobsum","wordfreq"]
        )
        f.readline()  # throw away header
        for line in f.readlines():
            record = list(line.strip())
            record.append(line.strip())
            record.append(sum([letter_prob.get(a.upper(), 0) for a in list(line.strip())]))
            record.append(sum([letter_prob.get(a.upper(), 0) for a in set(line.strip())]))
            record.append(None)
            lines.append(record)
    return lines

def GoogleNGram() -> list[list]:
    """
    from google_ngram_downloader import readline_google_store
    this takes a long time, should be multithreaded. 
    For this reason, here's a txt file of the end result
    """
    lines = []
    with open("google_word_freq.txt") as f:
        lines.append(
            ["w0", "w1", "w2", "w3", "w4", "word", "letterprobsum", "uniqueprobsum","wordfreq"]
        )
        for line in f.readlines():
            line,freq=line.split(",")
            record = list(line.strip())
            record.append(line.strip())
            record.append(sum([letter_prob.get(a.upper(), 0) for a in list(line.strip())]))
            record.append(sum([letter_prob.get(a.upper(), 0) for a in set(line.strip())]))
            record.append(freq)
            lines.append(record)
    return lines