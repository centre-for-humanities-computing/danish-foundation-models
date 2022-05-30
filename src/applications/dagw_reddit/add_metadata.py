"""
Add initial metadata to the DFM compositite dataset consisting of dagw and reddit-da
dataset.
"""

import os

from datasets import load_from_disk
from wasabi import msg
import spacy


path = os.path.join("/work", "dagw-clean", "dfm_dagw_reddit.arrow")
write_path = os.path.join("/work", "dagw-clean", "dfm_dagw_reddit.arrow")
ds = load_from_disk(path)
ds = ds.shuffle(seed=42)


def word_count(batch):
    nlp = spacy.blank("da")
    nlp.max_length = 100000000000000
    batch["n_tokens"] = [len(doc) for doc in nlp.pipe(batch["text"])]
    return batch


msg.info("Add n_tokens column")
ds = ds.map(word_count, batched=True, batch_size=1024 * 2 * 2, num_proc=16)


n_docs = len(ds)
reddit = ds.filter(lambda b: b["source"] == "reddit-da")
n_reddit_docs = len(reddit)
reddit_tokens = sum(reddit["n_tokens"])
n_categories = len(set(ds["source"]))
n_tokens_ = ds["n_tokens"]
is_duplicate_ = ds["is_13_gram_duplicate"]
n_tokens = sum(ds["n_tokens"])
n_clean_tokens = sum([ntok for ntok, isdup in zip(n_tokens_, is_duplicate_) if isdup])
n_duplicates = len([d for d in is_duplicate_ if d is True])
n_non_duplicates = len([d for d in is_duplicate_ if d is not None])
passed_quality_filter = ds["passed_quality_filter"]
n_low_quality = sum(1 for is_good in passed_quality_filter if is_good is False)

ds.info.description = f"""
DAGW_DFM is a variant of Danish Gigaword (Derczynski et al., 2021, v2) which excludes the sections 
containing tweets Twitter and modified news contained in danavis20.
Twitter were excluded as an it was a sample of an dataset whiich was available to the authors.

DanAvis20 (or danavis) were excluded due to preprocessing desribed in
(Derczynski et al., 2021, v1 on arvix: https://arxiv.org/pdf/2005.03521v1.pdf) including 
shuffling of sentences, pseudonymization of prober names and the replacement of infrequent
content wordswith statistical cognates, which could lead sentences such as 
"Der er skilsmissesager i forsikringsselskabet".

Additionally DAGW_DFM includes addtionally the reddit-da dataset (hf citation), which include
Reddit post derived from (NCC) which includes
a total {reddit_tokens} tokens over {n_reddit_docs} documents.


A subsection of DAGW_DFM, henceforth DAGW_DFM_c, have been filtered out to only include Danish tweets
and low-quality text have been removed using a series of heuristic filters and removing repitious texts. 
Following the filtering DAGW_DFM_c is deduplicated to remove exact and near-duplicates. For more on data cleaning
see section on post processing.

DAGW_DFM includes a total of {n_tokens} tokens and DAGW_DFM_c includes {n_clean_tokens} ({n_clean_tokens/n_tokens:.2f}%).

## Dataset information
as DFM_DAGW is a composite dataset consisting of DAGW (ref) and reddit-da (ref). For more information on
this dataset will not contain a datasheet, but we recommend checking the documentation of the respective datasets.

### Motivation:

**For what purpose was the dataset created? Who created the dataset? Who funded the creation of the dataset? **

DFM_DAGW, was created for pre-training Danish language models by a team of researchers at Center for Humanities
Computing Aarhus (CHCAA) using a codebase jointly developed with partners from industry (e.g. KMD, Ekstra Bladet) and other
research institutions (e.g. Briston University, Alexandra Institute). For more on collaborators on this project see
the [GitHub repository](https://github.com/centre-for-humanities-computing/danish-foundation-models
).

## Quality Filter:
For the quality filtering DFM_DAGW_c applies a filter akin to [2] which filters text which does not:

- Contain at least 2 Danish stopwords. For the stopword list we use the one used in SpaCy v.3.1.4.
- Have mean word length between 3-10.
- Have a token length between 50-100 000.
- Have a less than 5 000 000 characters.
- Have a less than 70% words containing an alphabetic character.
- Have a symbol to word ratio lower than 10% for hashtags an ellipsis.
- Have less than 90% of lines starting with a bullet point.
- have less than 30% of lines ending with an ellipsis.

- Have low high degree of repitiuous text:
  - Less than 30% duplicate lines.
  - Less than 30% duplicate paragraphs.
  - Less than 30% of the characters is contained within duplicate line.
  - Where the top 2-4 grams constitute less than 20%, 18%, 16%, respectively, of the characters. 
  - Where the duplicate 5-10 grams constitute less than 15%, 14%, 13%, 12%, 11%, 10% of the characters, respectively.

## Deduplication
The deduplication removed all documents with a 13-gram similarity higher than 80% following the MinHash algorithm [1] using 64 permutation.
The MinHash algorithm is a probabilistic data structure for approximating the Jaccard similarity between two sets.

References:

- [1] Broder, Andrei Z. "On the resemblance and containment of documents."
    Proceedings. Compression and Complexity of SEQUENCES 1997
    (Cat. No. 97TB100171). IEEE, 1997.
- [2] Rae, J. W., Borgeaud, S., Cai, T., Millican, K., Hoffmann, J., Song, F., 
    Aslanides, J., Henderson, S., Ring, R., Young, S., Rutherford, E., Hennigan, 
    T., Menick, J., Cassirer, A., Powell, R., Driessche, G. van den, Hendricks, 
    L. A., Rauh, M., Huang, P.-S., … Irving, G. (2021).
    Scaling Language Models: Methods, Analysis & Insights from Training Gopher.
    https://arxiv.org/abs/2112.11446v2
"""

ds.info.license = "See the respective dataset"

ds.info.version = "1.0.0"
ds.info.citation = "If you wish to cite this work please see our GitHub page for an up to date citation: https://github.com/centre-for-humanities-computing/danish-foundation-models"
ds.info.homepage = (
    "https://github.com/centre-for-humanities-computing/danish-foundation-models"
)

# write markdown file
print("\tWriting markdown file")
md = f"""
# DFM_DAGW

*Version*: {ds.info.version}

*Homepage*: {ds.info.homepage}

*license*: {ds.info.license}

{ds.info.description}

### Citation
{ds.info.citation}
"""

print("Saving description markdown")
with open("danish-foundation-models/docs/dagw_reddit.md", "w") as f:
    f.write(md)

# write dataset with added metadata
print("Saving dataset")
ds.save_to_disk(write_path)
