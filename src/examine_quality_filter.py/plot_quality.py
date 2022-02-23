"""
A script for plotting and examining the effect of the quality filter.
"""

import pandas as pd
import os


f_path = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(f_path, "..", "..", "DAGW_filter.ndjson")

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
    "spont": "spontaneaus speech",
    "synne": "Synnejysk forening/Sønderjysk",
    "tv2r": "TV2 Regionerne",
    "wiki": "Wikipedia",
    "wikibooks": "WikiBooks",
    "wikisource": "WikiSource",
}

# df[["source", "filtered", "Counts"]].groupby(["source", "filtered"]).count()
df["source_cat"] = df["source"].apply(lambda x: mapping_dict[x])
df[["source_cat", "filtered", "Counts"]].groupby(["source_cat", "filtered"]).count()
