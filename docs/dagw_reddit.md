
# DAGW$_{DFM}$

*Version*: 1.0.0

*Homepage*: https://github.com/centre-for-humanities-computing/danish-foundation-models

*License*: See the respective dataset


DAGW$_{DFM}$ is a variant of Danish Gigaword [3] which excludes the sections containing
tweets and modified news contained in danavis20. 

Twitter was excluded as it was a sample of a dataset which was available to the authors only. 

DanAvis20 (or danavis) was excluded due to preprocessing desribed in [3] (version 1 on 
[arxiv](https://arxiv.org/pdf/2005.03521v1.pdf))including shuffling of sentences,
pseudonymization of proper nouns and the replacement of infrequent content-words with
statistical cognates, which could lead sentences such as *"Der er skilsmissesager i
forsikringsselskabet"*.

Additionally DAGW$_{DFM}$ includes the [reddit-da](https://huggingface.co/datasets/DDSC/reddit-da) dataset, which includes 
1,908,887 documents. The DAGW$_{DFM}$ has had low-quality text removed using a series
of heuristic filters. Following filtering,
DAGW$_{DFM}$ is deduplicated to remove exact and near-duplicates. For more on data 
cleaning, see the section on post processing.

DAGW$_{DFM}$ included a a total of 1,310,789,818 tokens before filtering, and833,664,528 (0.64%) after.

# Dataset information
As DAGW$_{DFM}$ is a composite dataset consisting of Danish gigaword and 
[reddit-da](https://huggingface.co/datasets/DDSC/reddit-da), it will not
contain a datasheet. For more information, we recommend checking the documentation of the
respective datasets.

### Motivation:
**For what purpose was the dataset created? Who created the dataset? Who funded the
creation of the dataset?**

DAGW$_{DFM}$ was created with the purpose of pre-training Danish language models. It was created by a team of
researchers at Center for Humanities Computing Aarhus (CHCAA) using a codebase jointly
developed with partners from industry and academia e.g. KMD, Ekstra Bladet, deepdivr,
and Bristol University. For more on collaborators on this project see
the [GitHub repository](https://github.com/centre-for-humanities-computing/danish-foundation-models
).

## Processing

### Quality Filter:

DAGW$_{DFM}$ applies a filter akin to [2]. It keeps documents which:

- Contain at least 2 Danish stopwords. For the stopword list we use the one used in 
  SpaCy v.3.1.4.
- Have a mean word length between 3 and 10.
- Have a token length between 50 and 100,000.
- Contain fewer than 5,000,000 characters.
- Among all words, at least 70% have at least one alphabetic character.
- Have a symbol to word ratio lower than 10% for hashtags and ellipsis.
- Have fewer than 90% of lines starting with a bullet point.
- Have fewer than 30% of lines ending with an ellipsis.
- Have a low degree of repetitious text:
  - Fewer than 30% duplicate lines.
  - Fewer than 30% duplicate paragraphs.
  - Fewer than 30% of characters contained within duplicate lines.
  - The top 2-4 grams constitute less than 20%, 18%, 16% of characters, respectively. 
  - Where, for each document, 5-10 grams which occur more than once constitute less than 15%, 14%, 13%, 12%, 11%, 10% of
    the characters, respectively.

### Deduplication
The deduplication removed all documents with a 13-gram similarity higher than 80%
following the MinHash algorithm [1] using 128 permutations. The MinHash algorithm is a
probabilistic data structure for approximating the Jaccard similarity between two sets.


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
- [3] Strømberg-Derczynski, L., Ciosici, M., Baglini, R., Christiansen, M. H.,
      Dalsgaard, J. A., Fusaroli, R., Henrichsen, P. J., Hvingelby, R., Kirkedal, A.,
      Kjeldsen, A. S., Ladefoged, C., Nielsen, F. Å., Madsen, J., Petersen, M. L.,
      Rystrøm, J. H., & Varab, D. (2021). The Danish Gigaword corpus. Proceedings of the
      23rd Nordic Conference on Computational Linguistics (NoDaLiDa), 413–421.
      https://aclanthology.org/2021.nodalida-main.46


### Citation
If you wish to cite this work please see the GitHub page for an up to date citation: 
https://github.com/centre-for-humanities-computing/danish-foundation-models
