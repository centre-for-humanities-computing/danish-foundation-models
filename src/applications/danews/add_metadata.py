"""
Add description to dataset and generate documentation report from
dataset description.

Run after deduplication

Author:
Kenneth 

"""
from datetime import datetime
from datasets import load_from_disk
from pathlib import Path

def word_count(batch):
    nlp = spacy.blank("da")
    batch["n_tokens"] = [len(doc) for doc in nlp.pipe(batch["text"])]
    return batch

print("Loading dataset")
path = Path("/work/hope-infomedia_cleaned/infomedia_2000-2021")
news = load_from_disk(path)

# TODO: fiks
print("Add n_tokens column")
news = news.map(word_count, batched = True, batch_size=1024*2*2, num_proc=16)

# Add description
print("Creating metadata")
dates = news["PublishDate"]
start_date = min(dates).strftime("%d/%m/%Y")
end_date = max(dates).strftime("%d/%m/%Y")

print("\tCounting unique sources")
sources = news["Source"]
n_sources = len(set(sources))

print("\tExtracting duplicate counts")
n_tokens_ = news["n_tokens"]
n_tokens = sum(n_tokens_)
is_duplicate_ =  news["is_duplicate"]
n_clean_tokens = sum(n_tok for n_tok, is_dup in zip(n_tokens_, is_duplicate_) if is_dup is False)
n_non_duplicates = sum([1 for is_dup in is_duplicate_ if is_dup is False])
n_duplicates = sum([1 for is_dup in is_duplicate_ if is_dup is True])
n_docs = len(news)
print("\tExtracting number of low-quality text")
passed_quality_filter = news["passed_quality_filter"] 
n_low_quality = sum(1 for is_good in passed_quality_filter if is_good is False)

news.info.description = f"""
DaNews consist of articles collected from the [Infomedia](https://infomedia.dk) and 
consists of {n_docs} articles across {n_sources} news sources. DaNews include
articles from the period {start_date} to  {end_date}.

DaNews have been filters out quality using a series of heuristic filters and removing repitious texts. 
Following the filtering DaNews is deduplicated to remove exact and near-duplicates. For more on data cleaning
see post processing.

DaNews includes a total of {n_tokens} tokens of which {n_clean_tokens} ({n_clean_tokens/n_tokens:.2f}%) are left after filtering.

## Datasheet:

### Motivation:
**For what purpose was the dataset created? Who created the dataset? Who funded the creation of the dataset? **

The dataset was created for pre-training Danish language models by a team of researchers at Center for Humanities
Computing Aarhus (CHCAA) using a codebase jointly developed with partners from industry (e.g. KMD, Ekstra Bladet) and other
research institutions (e.g. Briston University, Alexandra Institute). For more on collaborators on this project see
the [GitHub repository](https://github.com/centre-for-humanities-computing/danish-foundation-models
).

**Any other comments?**
No.

## Composition
**What do the instances that comprise the dataset represent (e.g., documents, photos, people, countries)?**

All instances of the dataset are Danish articles depending on the source these are derived from tabloid media or 
mainstream news. 

**How many instances are there in total (of each type, if appropriate)?**
The dataset consist of {n_docs} documents where {n_duplicates} ({n_duplicates/n_docs:.2f}%) are left after filtering. 

**Does the dataset contain all possible instances or is it a sample (not necessarily random) of instances from a larger set?**
Prior to filtering this dataset contains all instances of new articles from the given period across the sources.

**If the dataset is a sample from a larger set, what was the sampling strategy?**
The dataset is not a sample, however it is filtered as described in post processing.

**Who was involved in the data collection process?**
A team of researchers at Center for Humanities
Computing Aarhus (CHCAA) recieved this dataset in a collaboration with Infomedia.

**Over what timeframe was the data collected?**
The dataset include articles from the period {start_date} to  {end_date}.

**Were any ethical review processes conducted?**
No.

## Preprocessing/cleaning/labeling

**Was any preprocessing/Cleaning/Labeling of the data done 
(e.g., discretization or bucketing, tokenization, part-of-speech tagging, 
SIFT feature extraction, removal of instances, processing of missing values)?**

We filter documents that are not in Danish. We remove low-quality text and deduplicate documents based on their 
document-level n-gram similarity. The full pre-processing details are given in the post processing section.

**Is the software used to preprocess/clean/label the instances available?**
Yes, the script are avaiable [here](https://github.com/centre-for-humanities-computing/danish-foundation-models/tree/main/src/application/danews). 
Which used version 0.0.1 of the [dfm package](https://github.com/centre-for-humanities-computing/danish-foundation-models). 

## Uses
**Has the dataset been used for any tasks already?**
Yes, the dataset has been used to pre-train Danish language models.
Parts of the dataset have also been used in
Baglini, R. B., Nielbo, K. L., Hæstrup, F., Enevoldsen, K., Vahlstrup, P. B., & Roepstorff, A. (2021, June 2). When no news is bad news: Detection of negative events from news media content. https://2021.dhbenelux.org/
Nielbo, K. L., Baglini, R. B., Vahlstrup, P. B., Enevoldsen, K. C., Bechmann, A., & Roepstorff, A. (2021, January). News information decoupling: An information signature of catastrophes in legacy news media. https://eadh2020-2021.org/

**Is there a repository that links to any or all papers or systems that use the dataset?**
No.

**What (other) tasks could the dataset be used for?**
The scale of the dataset makes it suitable for NLP tasks such as language modelling. Similarly, the structure
of the articles make it a suitable dataset for training text-summerization models.

**Is there anything about the composition of the dataset or the way it was collected and preprocessed/cleaned/labeled that might impact future uses?**

This dataset is static and thus does not evolve over time with the language, thus will become increasingly outdated over time.


**Are there tasks for which the dataset should not be used?**
This dataset contains Danish articles and thus should not be used for Danish language task.
As the writers of the content is predominantly journalists, it reflect a certain social group which is unlikely to reflect Danish language as a whole.

## Distribution
**Will the dataset be distributed to third parties outside of the entity (e.g., company, institution, organization) on behalf of which the dataset was created?**
No.
"""

news.info.license = "Not publicly available."
news.info.post_processed = f"""
# Post processing
DaNews have been filtered for quality using a series of heuristic filters and removing repitious texts. 
Following the filtering DaNews is deduplicated to remove exact and near-duplicates.

A total of {n_low_quality} ({n_low_quality/n_docs:.2f}%) were considered low quality and a 
total of {n_duplicates} ({n_duplicates/(n_non_duplicates+n_duplicates):.2f}%) documents were considered duplicates.

## Quality Filter:
For the quality filtering DaNews applies a filter akin to [2] which filters text which does not:

- Contain at least 2 Danish stopwords. For the stopword list we use the one used in SpaCy v.3.1.4.
- Have mean word length between 3-10.
- Have a token length between 50-100 000.
- Have a less than 5 000 000 characters.
- Have a less than 60% words containing an alphabetic character.
- Have a symbol to word ratio lower than 10% for hashtags an ellipsis.
- Have less than 90% of lines starting with a bullet point.
- have less than 30% of lines ending with an ellipsis.

- Have low high degree of repitiuous text:
  - Less than 20% duplicate lines.
  - Less than 20% duplicate paragraphs.
  - Where the top 2-4 grams constitute less than 20%, 18%, 16%, respectively, of the text. 
  - Where the duplicate 5-10 grams constitute less than 25%, 24%, 23%, 22%, 21%, 20% of the text, respectively.

## Deduplication
The deduplication removed all documents with a 13-gram similarity higher than 80% following the MinHash algorithm [1] using 128 permutation.
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

news.info.version = "1.0.0"
news.info.citation = "If you wish to cite this work please see our GitHub page for an up to date citation: https://github.com/centre-for-humanities-computing/danish-foundation-models"
news.info.homepage = "https://github.com/centre-for-humanities-computing/danish-foundation-models"

# write markdown file
print("\tWriting markdown file")
md = f"""
# DaNews

*Version*: {news.info.version}

*Homepage*: {news.info.homepage}

*license*: {news.info.license}

{news.info.description}
{news.info.post_processed}

### Citation
{news.info.citation}
"""

print("Saving description markdown")
with open("danish-foundation-models/docs/danews.md", "w") as f:
    f.write(md)

# write dataset with added metadata
print("Saving dataset")
save_path = Path("/work/hope-infomedia_cleaned/infomedia_2000-2021.arrow")
news.save_to_disk(save_path)


# write meta file
news_sub = news.remove_columns([c for c in news.features.keys() if c not in {"n_tokens", "is_duplicate", "passed_quality_filter", "Source"}])
news_sub.to_csv("news_meta.csv")
    
    
    
    
