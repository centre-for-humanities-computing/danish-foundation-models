


from datasets import load_dataset

path = "/work/twitter_cleaned/twitter_da_stopwords_2019-01-01_2021-04-30.jsonl"
dataset = load_dataset("json", data_files=path)
ds = dataset["train"]
df = ds.to_pandas()


for c in df.columns:
    if c.startswith("filtered_by"):
        break

import numpy as np
counts = [(c, sum(df[c].isin({True}))) for c in df.columns if c.startswith("filtered_by")]
frac = [(c[0], np.round(c[1]/df.shape[0], 4)) for c in counts]
frac
# [('filtered_by_max_chr_length', 0.0), ('filtered_by_doc_length', 0.0098), ('filtered_by_mean_word_length', 0.0001), ('filtered_by_alpha_ratio', 0.0016), 
# ('filtered_by_stop_word', 0.0034), ('filtered_by_duplicate_lines_chr_fraction', 0.0), ('filtered_by_duplicate_paragraph_chr_fraction', 0.0), 
# ('filtered_by_top_ngram_chr_fraction', 0.0006), ('filtered_by_duplicate_ngram_chr_fraction', 0.0003)]