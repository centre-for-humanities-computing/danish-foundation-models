
# NAT: Netarkivet Text

*Version*: 1.0.0

*Homepage*: https://github.com/centre-for-humanities-computing/danish-foundation-models

*license*: Not publicly available.

---

Netarkivet Text (NAT) consists of a subsection of [Netarkivet](https://www.kb.dk/find-materiale/samlinger/netarkivet) and 
contains 2,332 million sites across 1.6 million domains. 
Netarkivet includes sites from the period 2006 to 2016.

NAT has been filtered using a series of heuristic filters and removing repetitious texts. 
Following the filtering, NAT is further deduplicated to remove exact and near-duplicates. For more on data cleaning,
see the post processing section below.

The sites which passed the quality filter were deduplicated per year. NAT consist of 865 billion tokens of which 134 (15%) billion were left after filtering and deduplication.

## Datasheet

Following the recommendation and framework of [3], we add the following datasheet. 

### Motivation:

**For what purpose was the dataset created? Who created the dataset? Who funded the creation of the dataset?**

Netarkivet is created following the Danish [archival law](https://www.retsinformation.dk/eli/lta/2004/1439),
from which a text-only corpus was derived for research purposes, see [4,5]. This is the
part from which this dataset is derived.
This subsection have then been filtered with the intention of training Danish language
This part has then been filtered with the intention of training Danish language
models by a team of researchers at Center for Humanities Computing Aarhus (CHCAA) using
a codebase jointly developed with partners from industry (e.g. KMD, Ekstra Bladet) and
other research institutions (e.g. Bristol University, Alexandra Institute).
For more on collaborators on this project see the [GitHub repository](https://github.com/centre-for-humanities-computing/danish-foundation-models
).

**Any other comments?**

No.


## Composition

**What do the instances that comprise the dataset represent (e.g., documents, photos, people, countries)?**

Instances of the dataset are Danish domain sites, which further include metadata such as:


|     | Column      | Dtype  |
| --- | ----------- | ------ |
| 0   | harvest_id  | int32  |
| 1   | job_id      | int32  |
| 2   | sha1        | object |
| 3   | mime_served | object |
| 4   | language    | object |
| 5   | mime_droid  | object |
| 6   | timestamp   | object |
| 7   | uri         | object |
| 9   | domain_key  | object |

Where `harvest_id` is the id of the associated Netarkivet web harvest. Each web harvest
consists of jobs, each with their associated `job-id`. 

Language is the language classified using the following language detection [library](https://github.com/optimaize/language-detector). `uri` is the URI of the site e.g. `"http://www.apple.com/podcasting"`. 
`timestamp` is the date given on the format `"20060612105533"`, indicating year, month, date, time.
The `sha1` is the website hash.
`mime_*` indicates the [mime/media type](https://en.wikipedia.org/wiki/Media_type).
`mime_served` could for instance be `"text/html; charset=iso-8859-1"` and `mime_droid` could be `"text/html; version=2.0"` and is the mime type identified by the server and by [DROID](https://github.com/digital-preservation/droid), respectively.
**How many instances are there in total (of each type, if appropriate)?**

NAT contains a total of 2,332 million sites distributed over 1.6 million domains.  
1,370 million of these sites are Danish, with the largest secondary language being English
with 718 million sites.

**Does the dataset contain all possible instances or is it a sample (not necessarily random) of instances from a larger set?**

These domains are a subset of Netarkivet, which again is a sample of all the Danish content on the internet.

**If the dataset is a sample from a larger set, what was the sampling strategy?**

Netarkivet has being scraped from the internet using the following procedures:

- Cross-sectional collection of all Danish websites up to four times a year.
- Selective collection of the following domains: All Danish newsmedia (with a frequency
ranging from 12 times a day to weekly), political parties, organisations and unions,
legal bodies such as ministeries og agencies, selected social media profiles, YouTube videos. 
- Event collections of 2-3 events yearly (e.g. elections and the corona pandemic)
- Miscellaneous/on-demand webscrapes (for instance in collaboration with researchers)

A selective subset of Netarkivet is then extracted per year from 2006 to 2016 such that 
it contain no duplicate sites. Apache Tika (v. 1.15) is then used to extract the text from the sites.
During extract all HTML markup is removed, along with javascript and CSS code. 
The content of textual HTML elements, such as ´\<P\>´ and ´\<H1\>´ are concatenated into one piece of text.

**Who was involved in the data collection process?**

The Royal Danish Library collects Netarkivet and along with Brügger et al. [4,5]
helped with the construction of the Netarkivet text.

**Over what timeframe was the data collected?**

The dataset include articles from the period 2006 to 2016.

**Were any ethical review processes conducted?**

Netarkivet in collected in adherence to an update to the Danish archival law in 2005,
which extended the law to also include internet domains.
Our text subset was constructed for a research project and have thus a project proposal
have been accepted by the Royal Danish Library. Besides these the author is not aware of
any ethical approvals.

## Preprocessing/cleaning/labeling

**Was any preprocessing/Cleaning/Labeling of the data done 
(e.g., discretization or bucketing, tokenization, part-of-speech tagging, 
SIFT feature extraction, removal of instances, processing of missing values)?**

NAT has been filtered using a series of heuristic filters as well as removing
repetitious texts. Following the filtering, the corpus is deduplicated to remove exact and
near-duplicates.


For the quality filtering, NAT applies a filter akin to [2] which contains text
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
[here](https://github.com/centre-for-humanities-computing/danish-foundation-models/tree/main/src/application/nat). 
the scripts use version 0.0.2 of the
[dfm package](https://github.com/centre-for-humanities-computing/danish-foundation-models). 

## Uses

**Has the dataset been used for any tasks already?**

Yes, the dataset has been used to pre-train Danish language models.
Furthermore, the unfiltered dataset has also been used in [4] and [5], for examining
of the development on the Danish web.

**Is there a repository that links to any or all papers or systems that use the dataset?**

No.

**What (other) tasks could the dataset be used for?**

The scale of the dataset makes it suitable for NLP tasks such as language modelling.
It is likely possible to extract reviews, social media posts and similar semi-labelled
datasets from the dataset which can be used for NLP task such as sentiment analysis or
hate-speech detection.

The content of dataset makes it useable in a wide range of other applications in media
studies, social science or humanities, including development of written Danish,
emerging conspiracy theories, and online information dynamics.

**Is there anything about the composition of the dataset or the way it was collected and
preprocessed/cleaned/labeled that might impact future uses?**

This dataset is static and thus does not evolve over time with the language, thus will
become increasingly outdated over time. Netarkivet, from which it is derived, is
not static however, and is thus likely to further develop, which will allow us to update the 
dataset going forward.


## Distribution

**Will the dataset be distributed to third parties outside of the entity (e.g., company, institution, organization) on behalf of which the dataset was created?**

No.


### Citation
If you wish to cite this work please see our GitHub page for an up to date citation: https://github.com/centre-for-humanities-computing/danish-foundation-models


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
- [3] T. Gebru, J. Morgenstern, B. Vecchione, J. W. Vaughan, H. Wallach, H. Daumé III,
        and K. Crawford. Datasheets for datasets. arXiv preprint arXiv:1803.09010, 2018.
- [4] Brügger, N., Nielsen, J., & Laursen, D. (2020). Big data experiments with the 
        archived Web: Methodological reflections on studying the development of a
        nation’s Web. First Monday. https://doi.org/10.5210/fm.v25i3.10384
- [5] Brügger, N. (2021). Digital humanities and web archives: Possible new paths for 
        combining datasets. International Journal of Digital Humanities, 2(1), 145–168.
        https://doi.org/10.1007/s42803-021-00038-z

