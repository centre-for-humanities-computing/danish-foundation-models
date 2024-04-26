```yaml
pretty_name: Augmented_DAGW
description: >
  This is an augmented version of the Danish Gigaword Dataset, which includes texts from several domains and forms. It integrates data from multiple sources, including Danish novels, Reddit comments, and news articles. Texts have undergone cleaning processes such as deduplication and URL filtering.
languages:
  - da
license:
  - cc-by-4.0
multilinguality:
  - multilingual
size_categories:
  - 10M<n<100M
task_categories:
  - text-generation
  - fill-mask
  - summarization
task_ids:
  - language-modeling
configs:
  - name: dagw
    description: "Filtered Danish Gigaword Corpus excluding Twitter data."
    homepage: "https://huggingface.co/datasets/DDSC/partial-danish-gigaword-no-twitter"
    size: "511160 records"
    license: "cc-by-4.0"
  - name: memo
    description: "Data from the MeMo corpus, includes normalized Danish novels from 1870-1899."
    homepage: "https://huggingface.co/datasets/MiMe-MeMo/Corpus-v1.1"
    size: "858 records"
    license: "cc-by-4.0"
  - name: scandi-reddit
    description: "Post-processed corpus of Reddit comments."
    homepage: "https://huggingface.co/datasets/alexandrainst/scandi-reddit"
    size: "13479774 records"
    license: "cc-by-4.0"
  - name: nordjylland-news
    description: "Dataset with text-summary pairs from Danish TV2 Nord news articles."
    homepage: "https://huggingface.co/datasets/alexandrainst/nordjylland-news-summarization"
    size: "75219 records"
    license: "cc-by-4.0"
```

# Augmented DAGW
This is a quick introduction and summarition of an augmented Danish Gigaword Dataset. Here we will describe the different components and how we did the simple cleaning.

## Components
Currently, the augmented DAGW consists of four components, each a smaller dataset on its own:
1. [DAGW (Danish Gigaword)](https://huggingface.co/datasets/DDSC/partial-danish-gigaword-no-twitter): The Danish Gigaword Corpus contains text spanning several domains and forms. This version does not include the sections containing Tweets. ***511160 records*** in total (after filtering)
2. [MeMo](https://huggingface.co/datasets/MiMe-MeMo/Corpus-v1.1): This is data release version 1.1 of the MeMo corpus comprising almost all Danish novels from the period 1870-1899, known as the Modern Breakthrough. Note that we only included the [normalised corpus](https://huggingface.co/datasets/MiMe-MeMo/Corpus-v1.1/tree/main/normalized) in the huggingface repository. ***858 records*** in total.
3. [Scandi-Reddit](https://huggingface.co/datasets/alexandrainst/scandi-reddit/blob/main/README.md): ScandiReddit is a filtered and post-processed corpus consisting of comments from Reddit. ***13479774 records*** in total.
4. [Nordjylland-News](https://huggingface.co/datasets/alexandrainst/nordjylland-news-summarization): This dataset consists of pairs containing text and corresponding summaries extracted from the Danish newspaper TV2 Nord. Note that here we only included [the training dataset](https://huggingface.co/datasets/alexandrainst/nordjylland-news-summarization/blob/main/data/train-00000-of-00001-4fb110c0f6314175.parquet). ***75219 records*** in total.

## Columns/Keys
All the records in the dataset have the following unified columns/keys:

```
{
    "id": "...",             # MANDATORY: source-specific identifier
    "text": "...",           # MANDATORY: textual content of the document
    "source": "...",         # MANDATORY: source of the data, such as peS2o, common-crawl, etc.
    "added": "...",          # OPTIONAL: timestamp ai2 acquired this data
    "created": "..."         # OPTIONAL: timestamp when orig document was created (best-guess if not available)
    "metadata": {...}        # OPTIONAL: source-specific metadata
}
```

Moreover, each component has its own metadata which you can find in the following samples or the section: **Metadata**.
### Samples from components
Here are samples from each components (only the first 50 characters in `'text'` were printed out):
- A sample from DAGW:
```
{'text': "JØRGINE JØRGINE KØBENHAVN HAGE & CLAUSENS FORLAG (J. FR. CLAUSEN) 1926...", 'id': 'jvj_Jørgine', 'added': 'Fri Jun 26 13:06:11 2020 CEST +0200', 'created': '1873-01-01T00:00:00.000Z, 1951-01-01T00:00:00.000Z', 'metadata': {'domain': 'Wiki & Books', 'license': 'Attribution-ShareAlike 4.0 International', 'sub-source': 'Johannes V. Jensen (Danish poet)'}, 'source': 'dagw'}
```
- A sample from MeMo:
```
{'id': '130024227090', 'text': 'I . \nI den fornemste gade lå en prægtig , \ngammeld...', 'source': 'KB', 'added': '2024-03-28T12:46:27.000Z', 'created': '1870-01-01T00:00:00.000Z, 1970-01-01T00:00:00.000Z', 'metadata': {'file_received': 'y', 'filename': '1870_AndersenHC_LykkePeer.pdf', 'firstname': 'H.C.', 'surname': 'Andersen', 'pseudonym': None, 'gender': 'm', 'nationality': 'dk', 'title': 'Lykke-Peer', 'subtitle': None, 'volume': None, 'year': 1870, 'pages': '183', 'illustrations': 'n', 'typeface': 'gothic', 'publisher': 'Reitzel', 'price': '2,25', 'file_status': 'Modtaget fra KB 7.4.2022 DEL2 sending 5', 'notes': "OBS! PDF'en er ren tekst i antikva, men den fysiske bog formentlig fraktur. Det kalder på separate kolonner: pdf-typeface eller file-typeface og book-typeface. /PD", 'filepath': None, 'fileformat': 'pdftxt', 'txt_received': 'y', 'readable': 'y', 'historical': 'n', 'period': None, 'period_notes': None, 'novel_start': '10', 'novel_end': '190', 'novelstart_rescan': None, 'novelend_rescan': None, 'start_end_page_notes': None, 'serialno': 12.0, 'quarantine': None, 'discard': None}}
```
- A sample from Scandi-Reddit:
```
{'text': 'Bergen er ødelagt. Det er ikke moro mer....', 'id': '0', 'source': 'scandi-reddit', 'created': '2005-12-01T00:00:00.000Z, 2022-11-01T00:00:00.000Z', 'added': '2024-04-17T12:50:03.000Z', 'metadata': {'language': 'da', 'language_confidence': 0.7472341657, 'subreddit': 'Norway'}}
```
- A sample from Nordjylland-News:
```
{'id': 'nordjylland-news0', 'text': 'Opdatering: Manden er nu fundet af Nordjyllands Po...', 'source': 'TV2 Nord', 'added': '2024-03-15T14:35:19.000Z', 'created': '2024-03-15T14:35:19.000Z, 2025-03-15T14:35:19.000Z', 'metadata': {'summary': 'Nye oplysninger i sagen om en forsvunden mand har endnu en gang fået politiet til at henvende sig til borgerne.', 'text_len': 1739, 'summary_len': 111}}
```

## Data Collection
Here we list the python scripts for collecting, converting and compressing each sub-dataset.

- DAGW: https://github.com/centre-for-humanities-computing/danish-foundation-models/blob/main/data-processing/scripts/convert_dagw_to_jsonlgz.py
- MeMo: https://github.com/centre-for-humanities-computing/danish-foundation-models/blob/main/data-processing/scripts/memo/convert_memo_to_jsonlgz.py
- Scandi-Reddit: https://github.com/centre-for-humanities-computing/danish-foundation-models/blob/main/data-processing/scripts/convert_scandi_reddit_to_jsonlgz.py
- Nordjylland-News: https://github.com/centre-for-humanities-computing/danish-foundation-models/blob/main/data-processing/scripts/convert_nordjyllandnews_to_jsonlgz.py
## Data Cleaning

1. First, we filtered out all the empty documents (based on `"text"`: either *empty* or totally *white space*) in DAGW: 162051 out of 673211 empty docs found in total.
2. After combining all 4 components, we applied deduplication and URL block list to the augmented DAGW following this [filtering pipeline](https://github.com/centre-for-humanities-computing/danish-foundation-models/blob/main/data-processing/configs/2024-v1/README.md) with [Dolma](https://github.com/allenai/dolma).