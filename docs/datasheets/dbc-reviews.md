---
pretty_name: dbc-reviews
language:
  - da
  - en
  - "no"
  - sv
  - de
license: other
license_name: agreement (public models, private data)
size_categories:
  - 0.1-1m
task_categories:
  - text-generation
  - fill-mask
task_ids:
  - language-modeling
---
# dbc-reviews: all reviews from DBC D1G1TAL

*Version*: 1.0.0

*Homepage*: https://github.com/centre-for-humanities-computing/danish-foundation-models

*license*: Not publicly available.

---

dbc-reviews consists of more than 214 thousand reviews of books and other materials collected and created by DBC D1G1TAL (former Dansk Bibliotekscenter).

The dataset contains thousands of reviews in Danish lamnugage, which are supplemented by English, Norwegian, Swedish, German, and other language reviews.

## Datasheet

Following the recommendation and framework of [1], we add the following datasheet. 

### Motivation:

**For what purpose was the dataset created? Who created the dataset? Who funded the creation of the dataset?**

The dataset was collected and created by DBC D1G1TAL A/S as one of the backbones for their catalogue of books and other materials.

## Composition

**What do the instances that comprise the dataset represent (e.g., documents, photos, people, countries)?**

Instances that comprise this dataset represent reviews of books or other materials.

**How many instances are there in total (of each type, if appropriate)?**

There are 214,035 reviews in this dataset.

**Does the dataset contain all possible instances or is it a sample (not necessarily random) of instances from a larger set?**

The dataset contains all the instances underlying DBC D1G1TAL's database.

**If the dataset is a sample from a larger set, what was the sampling strategy?**

There was no sampling involved.

**Who was involved in the data collection process?**

The data was collected by DBC D1G1TAL.

**Over what timeframe was the data collected?**

The dataset includes reviews created between 1991 and 2024.

**Were any ethical review processes conducted?**

No ethical review processes were conducted.

## Preprocessing/cleaning/labeling

**Was any preprocessing/Cleaning/Labeling of the data done**

THe only pre-processing applied is a lossless transformation of the JSONL format to the one preferred by the Danish Foundation Models project, including the addition of timestamps.

**Is the software used to preprocess/clean/label the instances available?**

The following Python script was used to convert this and the other dbc datasets:
```python
import datetime
import json
import subprocess
import tqdm

FILE_NAMES = {
    "abstracts.jsonl": "abstract",
    "faktalink.jsonl": None,
    "forfatterweb.jsonl": None,
    "reviews.jsonl": "content",
}

for file_name, text in tqdm.tqdm(FILE_NAMES.items()):
    length = int(subprocess.check_output(["wc", "-l", file_name]).split()[0])
    with open(f"dfm-{file_name}", "wt") as f:
        for line in tqdm.tqdm(open(file_name, "rt"), total=length, desc=file_name):
            d = json.loads(line)
            if text is None:
                meta = d["metadata"]["@graph"][0]
                lines = [meta["headline"]]
                for key, items in d.pop("text").items():
                    if not key.startswith("empty_"):
                        lines.append(key)
                        lines.extend(items)
                i, t = meta["mainEntityOfPage"].split("//", maxsplit=1)[1], "\n".join(lines)
            else:
                i, t = d.pop("id"), d.pop(text)
            e = {
                "id": i,
                "text": t,
                "source": "dbc",
                "added": datetime.datetime.now().strftime("%Y-%m-%d"),
                "created": "1991-04-18, 2024-04-18",
                "metadata": d,
            }
            print(json.dumps(e), file=f)
```

## Uses

**Has the dataset been used for any tasks already?**

Yes, the dataset has been used to pre-train a Danish encoder-decoder model using a T5 architecture.

**Is there a repository that links to any or all papers or systems that use the dataset?**

No, but as of 2024-06-05, no others have used the dataset.

**What (other) tasks could the dataset be used for?**

The dataset contains high-quality texts, many of which are written in Danish. Thus, the dataset could be used for pre-training Danish decocer-only and encoder-only models.

**Is there anything about the composition of the dataset or the way it was collected and preprocessed/cleaned/labeled that might impact future uses?**

No

## Distribution

**Will the dataset be distributed to third parties outside of the entity (e.g., company, institution, organization) on behalf of which the dataset was created?**

Data will only be available at the entity during the project. Requests regarding access to the dataset should be directed to the data owner DBC D1G1TAL.

### Citation
If you wish to cite this work please see our GitHub page for an up to date citation: https://github.com/centre-for-humanities-computing/danish-foundation-models


### References:

- [1] T. Gebru, J. Morgenstern, B. Vecchione, J. W. Vaughan, H. Wallach, H. Daumé III,
        and K. Crawford. Datasheets for datasets. arXiv preprint arXiv:1803.09010, 2018.

