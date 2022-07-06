
# DaNews

*Version*: 1.0.0

*Homepage*: https://github.com/centre-for-humanities-computing/danish-foundation-models

*license*: Not publicly available.

---

DaNews consist of articles from Danish news and tabloid media from 1 December 2000 to 
30 April 2021. It consists of articles derived from infomedia API through the [HOPE project](https://hope-project.dk/#/). The articles stems from multiple news sources such as Politiken, including both online of physical news papers.
DaNews consists of 9.29 billion tokens of which 8.67 Billion (93%) were left after
quality filtering and deduplication.

## Datasheet

Following the recommendation and framework of [5] we add the following datasheet. 

### Motivation

**For what purpose was the dataset created? Who created the dataset? Who funded the
creation of the dataset?**

The preprocessed dataset was created with the purpose of pre-training Danish language models. It was
created by a team of researchers at the Center for Humanities Computing Aarhus ([CHCAA](https://chcaa.io/#/))  using
a codebase jointly developed with partners from academia and industry, including KMD,
Ekstra Bladet, Bristol University and Deepdivr. For more on collaborators on this
project see the
[GitHub repository](https://github.com/centre-for-humanities-computing/danish-foundation-models
).


**Any other comments?**

No.

## Composition

**What do the instances that comprise the dataset represent (e.g., documents, photos,
people, countries)?**

Instances of the dataset are Danish articles derived from Danish tabloids or news media. 

**How many instances are there in total (of each type, if appropriate)?**

There are 25,874,862 documents in the unfiltered dataset, with 24,826,047 (96%) remaining
after filtering.

**Does the dataset contain all possible instances or is it a sample (not necessarily
random) of instances from a larger set?**

Prior to filtering DaNews dataset contains all digitized news articles from the given
period across the sources.

**What data does each instance consist of? “Raw” data (e.g., unprocessed text or images)
or features? In either case, please provide a description.**

Each instance constist of the following columns
```
'ArticleUrl', 'Heading', 'SubHeading', 'Lead', 'Paragraph', 'PublishDate', 'BodyText', 
'Captions', 'Authors', 'Source', 'WordCount', 'ArticleId', 'PageIds', 'Section', 'text'
```

Where we constructed the columns `text` column by joining the `Heading`, `SubHeading`
using newline. If the textfield is empty it is ignored and no newline is added. The we
join the resulting string with the `BodyText` using two newlines.

During the quality filtering we add the following indicator columns:
```
'passed_quality_filter', 'filtered_by_max_chr_length', 'filtered_by_doc_length', 
'filtered_by_mean_word_length', 'filtered_by_alpha_ratio', 'filtered_by_stop_word', 
'filtered_by_symbol_2_word_hashtag', 'filtered_by_symbol_2_word_ellipsis',
'filtered_by_line_bullets_or_ellipsis', 'filtered_by_duplicate_lines_chr_fraction',
'filtered_by_duplicate_paragraph_chr_fraction', 'filtered_by_top_ngram_chr_fraction',
'filtered_by_duplicate_ngram_chr_fraction', 'is_duplicate'
```

**Is there a label or target associated with each instance? If so, please provide a
description.**

No.

**Is any information missing from individual instances? If so, please provide a
description, explaining why this information is missing (e.g., because it was
unavailable). This does not include intentionally removed information, but might
include, e.g., redacted text.**

The team of researchers at the Humanities Computing Aarhus (CHCAA) have not
removed any information from the instances.

**Are relationships between individual instances made explicit (e.g., users’ movie
ratings, social network links)? If so, please describe how these relationships are made
explicit.**

The metadata columns, denote the relationship between articles including date of
publication, sections, and authors.


**Are there recommended data splits (e.g., training, development/validation, testing)?
If so, please provide a description of these splits, explaining the rationale behind
them.**

There is not splits performed on this dataset.

**Are there any errors, sources of noise, or redundancies in the dataset? If so, please
provide a description.**

News sources can publish their content both in an online and printed format which would
lead to similar instances in the dataset. To alleviate this redundancy by removing
near-duplicates (see Preprocessing/cleaning/labeling).

**Is the dataset self-contained, or does it link to or otherwise rely on external
resources (e.g., websites, tweets, other datasets)?**

Articles are intended to tell a self-contained story, but can include external
references such as tweets or website urls.


**Does the dataset contain data that, if viewed directly, might be offensive, insulting,
threatening, or might otherwise cause anxiety?**

Articles often describe content which is considered offensive, insulting or threatening. 

## Collection Process

**What mechanisms or procedures were used to collect the data (e.g., hardware
apparatuses or sensors, manual human curation, software programs, software APIs)?**

A team of researchers at the Center for Humanities Computing Aarhus (CHCAA) obtained this
dataset using the Infomedia API.

**If the dataset is a sample from a larger set, what was the sampling strategy?**

The dataset is not a sample, but _is_ a filtered version of the full dataset, see
Preprocessing/cleaning/labeling for more on this.

**Who was involved in the data collection process?**

A team of researchers at the Center for Humanities Computing Aarhus (CHCAA) obtained this
dataset using the Infomedia API and would like to thank the dataset owners for
access to their articles.

**Over what timeframe was the data collected?**

The dataset includes articles from 1 December 2000 to 
30 April 2021.

**Were any ethical review processes conducted?**

No.


## Preprocessing/cleaning/labeling

**Was any preprocessing/Cleaning/Labeling of the data done 
(e.g., discretization or bucketing, tokenization, part-of-speech tagging, 
SIFT feature extraction, removal of instances, processing of missing values)?**

DaNews has been filtered using a series of heuristic filters as well as removing
repetitious texts. Following the filtering, DaNews is deduplicated to remove exact and
near-duplicates.

Of all documents, 2,338,728 (9%) were filtered based due to low-quality and 1,048,815
(4%) because they were near-duplicates.

For the quality filtering, DaNews applies a filter akin to [2] which contains text
that:

- Contain at least 2 Danish stopwords. For the stopword list we use the one used in
SpaCy v.3.1.4.
- Have a mean word length between 3 and 10.
- Have a token length between 50 and 100,000.
- Have less than 5,000,000 characters.
- Have less than 60% of words containing an alphabetic character.
- Have a symbol to word ratio lower than 10% for hashtags and ellipsis.
- Have less than 90% of lines starting with a bullet point.
- have less than 30% of lines ending with an ellipsis.

- Have low high degree of repetitious text:
  - Have less than 20% of characters contained within duplicate lines.
  - Have less than 20% of characters contained within duplicate paragraphs.
  - Where the top 2-4 grams constitute less than 20%, 18%, 16%, respectively, of the text. 
  - Where the duplicate 5-10 grams constitute less than 25%, 24%, 23%, 22%, 21%, 20%
of the text, respectively.

The deduplication removed all documents with a 13-gram Jaccard similarity higher than 80%
following the MinHash algorithm [1] using 128 permutations. The MinHash algorithm is a
probabilistic data structure for approximating the Jaccard similarity between two sets.

**Is the software used to preprocess/clean/label the instances available?**

Yes, the scripts are available
[here](https://github.com/centre-for-humanities-computing/danish-foundation-models/tree/main/src/application/danews). 
the scripts use version 0.0.2 of the
[dfm package](https://github.com/centre-for-humanities-computing/danish-foundation-models). 

## Uses

**Has the dataset been used for any tasks already?**

Yes, the dataset has been used to pre-train Danish language models.
Parts of the dataset have also been used in [3] and [4]

**Is there a repository that links to any or all papers or systems that use the dataset?**

No.

**What (other) tasks could the dataset be used for?**

The scale of the dataset makes it suitable for NLP tasks such as language modelling.
Similarly, the structure of the articles makes it a suitable dataset for training text
summarisation models.

**Is there anything about the composition of the dataset or the way it was collected and
preprocessed/cleaned/labeled that might impact future uses?**

This dataset is static and thus does not evolve over time with the language. 
A consequence of this is that it will become increasingly outdated over time.


**Are there tasks for which the dataset should not be used?**

This dataset contains Danish articles and thus should not be used for non-Danish
language tasks.

As the writers of the content are predominantly journalists, it reflects a certain
writing style which is unlikely to reflect the Danish language as a whole.

## Distribution

**Will the dataset be distributed to third parties outside of the entity (e.g., company,
institution, organization) on behalf of which the dataset was created?**

No. 


### Citation

If you wish to cite this work please see our GitHub page for an up to date citation:
https://github.com/centre-for-humanities-computing/danish-foundation-models

# References:

- [1] Broder, Andrei Z. "On the resemblance and containment of documents."
        Proceedings. Compression and Complexity of SEQUENCES 1997
        (Cat. No. 97TB100171). IEEE, 1997.
- [2] Rae, J. W., Borgeaud, S., Cai, T., Millican, K., Hoffmann, J., Song, F.,
        Aslanides, J., Henderson, S., Ring, R., Young, S., Rutherford, E., Hennigan,
        T., Menick, J., Cassirer, A., Powell, R., Driessche, G. van den, Hendricks,
        L. A., Rauh, M., Huang, P.-S., … Irving, G. (2021).
        Scaling Language Models: Methods, Analysis & Insights from Training Gopher.
        https://arxiv.org/abs/2112.11446v2
- [3] Baglini, R. B., Nielbo, K. L., Hæstrup, F., Enevoldsen, K., Vahlstrup, P. B., & 
        Roepstorff, A. (2021, June 2). When no news is bad news: Detection of negative
        events from news media content. https://2021.dhbenelux.org/
- [4] Nielbo, K. L., Baglini, R. B., Vahlstrup, P. B., Enevoldsen, K. C., Bechmann, A.,
        & Roepstorff, A. (2021, January). News information decoupling: An information
        signature of catastrophes in legacy news media. https://eadh2020-2021.org/
- [5] T. Gebru, J. Morgenstern, B. Vecchione, J. W. Vaughan, H. Wallach, H. Daumé III,
        and K. Crawford. Datasheets for datasets. arXiv preprint arXiv:1803.09010, 2018.
