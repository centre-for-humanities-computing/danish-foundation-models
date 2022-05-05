
# NAT: Netarkivet Text

*Version*: 1.0.0

*Homepage*: https://github.com/centre-for-humanities-computing/danish-foundation-models

*license*: Not publicly available.

---

Netarkivet Text (NAT) consist of a subsection of [Netarkivet](missing) and 
contains XXX sites across XXX domains. Netarkivet include
sites from the period XX/XX/2006 to  XX/XX/2016.

NAT have been filters out quality using a series of heuristic filters and removing repitious texts. 
Following the filtering NAT is deduplicated to remove exact and near-duplicates. For more on data cleaning
see post processing.

NAT includes a total of XXX tokens of which XXX (XXX%) are left after filtering.

## Datasheet:

### Motivation:
**For what purpose was the dataset created? Who created the dataset? Who funded the creation of the dataset?**

Netarkivet is created for XXX. The subsection is created for a project by XXX. The filtered subsection which constitute this
dataset was created for pre-training Danish language models by a team of researchers at Center for Humanities
Computing Aarhus (CHCAA) using a codebase jointly developed with partners from industry (e.g. KMD, Ekstra Bladet) and other
research institutions (e.g. Briston University, Alexandra Institute). For more on collaborators on this project see
the [GitHub repository](https://github.com/centre-for-humanities-computing/danish-foundation-models
).

**Any other comments?**
No.

## Composition
**What do the instances that comprise the dataset represent (e.g., documents, photos, people, countries)?**

All instances of the dataset are a domain site including metadata such as XXX and XXX 


**How many instances are there in total (of each type, if appropriate)?**
The dataset consist of XXX documents where XXX (XXX%) are left after filtering. 

**Does the dataset contain all possible instances or is it a sample (not necessarily random) of instances from a larger set?**
This is instances from a larger set. 

**If the dataset is a sample from a larger set, what was the sampling strategy?**
it is sampled in the following way XXX.

**Who was involved in the data collection process?**
The royal library of Denmark collects Netarkivet and helped with the construction of the
subset along with XXX.

**Over what timeframe was the data collected?**
The dataset include articles from the period XX/XX/2006 to  XX/XX/2016.

**Were any ethical review processes conducted?**
Unknown

## Preprocessing/cleaning/labeling

**Was any preprocessing/Cleaning/Labeling of the data done 
(e.g., discretization or bucketing, tokenization, part-of-speech tagging, 
SIFT feature extraction, removal of instances, processing of missing values)?**

We filter documents that are not in Danish. We remove low-quality text and deduplicate documents based on their 
document-level n-gram similarity across each year. The full pre-processing details are given in the post processing section.

**Is the software used to preprocess/clean/label the instances available?**
Yes, the script are avaiable [here](https://github.com/centre-for-humanities-computing/danish-foundation-models/tree/main/src/application/danews). 
Which used version 0.0.1 of the [dfm package](https://github.com/centre-for-humanities-computing/danish-foundation-models). 

## Uses
**Has the dataset been used for any tasks already?**
Yes, the dataset has been used to pre-train Danish language models.
The dataset of the dataset have also been used in
XXX
XXX

**Is there a repository that links to any or all papers or systems that use the dataset?**
No.

**What (other) tasks could the dataset be used for?**
The scale of the dataset makes it suitable for NLP tasks such as language modelling. It is
likely possible to extract reviews, social media post and similar semi-labelled datasets from the dataset which can 
nlp task such as sentiment analysis or hate-speech detection.
The content of dataset makes it useable in a wide range of other applications in media studies.


**Is there anything about the composition of the dataset or the way it was collected and preprocessed/cleaned/labeled that might impact future uses?**

This dataset is static and thus does not evolve over time with the language, thus will become increasingly outdated over time. The Netarkivet
of which it is derived is however not static and is thus likely to develop further.


**Are there tasks for which the dataset should not be used?**
XXX


## Distribution
**Will the dataset be distributed to third parties outside of the entity (e.g., company, institution, organization) on behalf of which the dataset was created?**
No.


# Post processing
NAT have been filtered for quality using a series of heuristic filters and removing repitious texts. 
Following the filtering NAT is deduplicated to remove exact and near-duplicates across each year in the dataset.

A total of XXX (XXX%) were considered low quality and a 
total of XXX (XXX%) documents were considered duplicates.

## Quality Filter:
For the quality filtering DaNews applies a filter akin to [2] which filters text which does not:

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


### Citation
If you wish to cite this work please see our GitHub page for an up to date citation: https://github.com/centre-for-humanities-computing/danish-foundation-models


