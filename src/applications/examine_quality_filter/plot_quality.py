"""
A script for plotting and examining the effect of the quality filter.
"""

import pandas as pd
import os
import random


f_path = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(f_path, "..", "..", "..", "DAGW_filter.ndjson")

df = pd.read_json(path, lines=True)
df["Counts"] = df.index

mapping_dict = {
    "retsinformationdk": "Legal",
    "skat": "Legal",
    "retspraksis": "Legal",
    "hest": "Social Media",
    "cc": "Web",
    "adl": "Wiki & Books",
    "botxt": "Other",
    "danavis": "News",
    "dannet": "dannet",
    "depbank": "Other",
    "ep": "Conversation",
    "ft": "Conversation",
    "gutenberg": "Wiki & Books",
    "jvj": "Wiki & Books",
    "naat": "Conversation",
    "opensub": "Conversation",
    "relig": "Wiki & Books",
    "spont": "Conversation",
    "synne": "Other",
    "tv2r": "News",
    "wiki": "Wiki & Books",
    "wikibooks": "Wiki & Books",
    "wikisource": "Wiki & Books",
}


mapping_dict2 = {
    "retsinformationdk": "Retsinformation",
    "skat": "Skat.dk",
    "retspraksis": "H-Sø/retspraksis",
    "hest": "Hestenettet",
    "cc": "CommonCrawl",
    "adl": "Danish Litterature",
    "botxt": "Botxt (Bornholmsk)",
    "danavis": "DanAvis",
    "dannet": "dannet (Danish wordnet)",
    "depbank": "Danish Dependendency treebank",
    "ep": "European Parlament",
    "ft": "Folketinget",
    "gutenberg": "Gutenberg",
    "jvj": "Johannes V. Jensen",
    "naat": "NAAT",
    "opensub": "Open subtitles",
    "relig": "Religiuous texts",
    "spont": "spontaneous speech",
    "synne": "Synnejysk forening/Sønderjysk",
    "tv2r": "TV2 Regionerne",
    "wiki": "Wikipedia",
    "wikibooks": "WikiBooks",
    "wikisource": "WikiSource",
}

# df[["source", "filtered", "Counts"]].groupby(["source", "filtered"]).count()
df = df[df["text"].str.strip() != ""]
df["source_cat"] = df["source"].apply(lambda x: mapping_dict[x])

df[["source_cat", "filtered", "Counts"]].groupby(["source_cat", "filtered"]).count()

df[["source_cat", "filtered", "Counts"]].groupby(["filtered"]).count()

sum(df["filtered"] == "None") / (
    len(df["filtered"])
)  # proportion removed (excluding empty docs)

# l = df["text"][df["filtered"] == "max_chr_length"].tolist()
l = df["text"][(df["filtered"] == "doc_length" ) & (df["source_cat"] == "Web")].tolist()
random.shuffle(l)
print(l[4])
len(l[0])

import spacy

nlp = spacy.blank("da")
doc = nlp(l[0])

# potentially remove: duplicate_paragraph_fraction and duplicate_line_fraction


# doc_length: wiki, social media, and news is very short texts (which I think we should
# remove regardless)
#