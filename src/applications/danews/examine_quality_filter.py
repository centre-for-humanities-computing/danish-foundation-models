from datasets import load_dataset

path = "/work/hope-infomedia_cleaned/0.jsonl"
dataset = load_dataset("json", data_files=path)
ds = dataset["train"]
df = ds.to_pandas()


import numpy as np
counts = [(c, sum(df[c].isin({True}))) for c in df.columns if c.startswith("filtered_by")]
frac = [(c[0], np.round(c[1]/df.shape[0], 4)) for c in counts]
frac


most_pop = df[["text", "Source"]].groupby(["Source"]).count().sort_values(["text"], ascending=False).head(30)

d = {}
for news_source in most_pop.index:
    sub_df = df[df["Source"] == news_source]
    counts = [(c, sum(sub_df[c].isin({True}))) for c in df.columns if c.startswith("filtered_by")]
    frac = [(c[0], np.round(c[1]/sub_df.shape[0], 4)) for c in counts]
    d[news_source] = frac
    print("\n", news_source, "\n\t", frac)



texts = df["text"][df["filtered_by_duplicate_ngram_chr_fraction"].isin({True})].tolist()
print(texts[200])

gtexts = df["text"][df["passed_quality_filter"].isin({True})].tolist()
print(gtexts[200])


df_f = df[df["filtered_by_duplicate_ngram_chr_fraction"].isin({True})]
df_f = df_f.reset_index()

df_f.loc[300]

len(df_f["Paragraph"][300])
len(df_f["BodyText"][300])