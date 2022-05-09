
# DaNews

*Version*: 1.0.0

*Homepage*: https://github.com/centre-for-humanities-computing/danish-foundation-models

*license*: Not publicly available.

---

DaNews consist of articles from Danish news and tabloid media from 1 December 2000 to 
30 April 2021. It consists of ~25 million articles across 1362 news
sources. Note that newspapers, such as Politiken with multiple outlets, e.g. physically
and online, are counted as multiple sources.
DaNews consists of 9.29 billion tokens of which 8.67 Billion (0.93\%) were left after
quality filtering and deduplication.

## Datasheet

### Motivation

**For what purpose was the dataset created? Who created the dataset? Who funded the
creation of the dataset?**

The dataset was created with the purpise of pre-training Danish language models. It was
created by a team of researchers at Center for Humanities Computing Aarhus (CHCAA) using
a codebase jointly developed with partners from industry and industry, including KMD,
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

The dataset consists of 25 874 862 documents and 24 826 047 (0.96%) documents in the 
filtered dataset.

**Does the dataset contain all possible instances or is it a sample (not necessarily
random) of instances from a larger set?**

Prior to filtering DaNews dataset contains all digitized news articles from the given
period across the sources.

**If the dataset is a sample from a larger set, what was the sampling strategy?**

The dataset is not a sample, but _is_ filtered of the dataset, see 
Preprocessing/cleaning/labeling for more on this.

**Who was involved in the data collection process?**

A team of researchers at Center for Humanities Computing Aarhus (CHCAA) obtained this
dataset in a using the Infomedia API and would like to thanks the dataset owners for
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

A total of 2 338 728 (0.09%) were considered low quality and 1 048 815 (0.04%) documents
were considered near-duplicates.

## Quality Filter:

For the quality filtering DaNews applies a filter akin to [2] which filters text which
does not:

- Contain at least 2 Danish stopwords. For the stopword list we use the one used in
SpaCy v.3.1.4.
- Have a mean word length between 3-10.
- Have a token length between 50-100 000.
- Have less than 5 000 000 characters.
- Have less than 60% of words containing an alphabetic character.
- Have a symbol to word ratio lower than 10% for hashtags and ellipsis.
- Have less than 90% of lines starting with a bullet point.
- have less than 30% of lines ending with an ellipsis.

- Have low high degree of repitiuous text:
  - Less than 20% duplicate lines.
  - Less than 20% duplicate paragraphs.
  - Where the top 2-4 grams constitute less than 20%, 18%, 16%, respectively, of the text. 
  - Where the duplicate 5-10 grams constitute less than 25%, 24%, 23%, 22%, 21%, 20%
of the text, respectively.

## Deduplication

The deduplication removed all documents with a 13-gram similarity higher than 80%
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
summerization models.

**Is there anything about the composition of the dataset or the way it was collected and
preprocessed/cleaned/labeled that might impact future uses?**

This dataset is static and thus does not evolve over time with the language. 
A consequence of this is that it will become increasingly outdated over time.


**Are there tasks for which the dataset should not be used?**

This dataset contains Danish articles and thus should not be used for non-Danish
language task.

As the writers of the content are predominantly journalists, it reflects a certain
writing style which is unlikely to reflect the Danish language as a whole.

## Distribution

**Will the dataset be distributed to third parties outside of the entity (e.g., company,
institution, organization) on behalf of which the dataset was created?**

No.


### Citation
If you wish to cite this work please see our GitHub page for an up to date citation:
https://github.com/centre-for-humanities-computing/danish-foundation-models

### References:

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