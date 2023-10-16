# DaRadio Datasheet

*Version*: 1.0.0

*Homepage*: https://github.com/centre-for-humanities-computing/danish-foundation-models

*License*: Not publicly available.

---

DaRadio consists of radio broadcasts from the Danish radio stations DR P1 and Radio24Syv, and contains approximately 140.000 hours of speech. DaRadio includes all shows aired on DR P1 from 2005 to 2021, and all shows aired on Radio24Syv from 2011 to 2019.

DaRadio has been deduplicated using a series of heuristics based on metadata. For more on deduplication, see the data cleaning section further below.


## Datasheet

Following the recommendation and framework of [1], we add the following datasheet. 

### Motivation:

**For what purpose was the dataset created? Who created the dataset? Who funded the creation of the dataset?**

Data included in DaRadio was collected following the Danish [Legal Deposit Act](https://www.retsinformation.dk/eli/lta/2004/1439) by the Royal Danish Library (RDL). From this, a dataset of Danish speech-only radio was derived by RDL. The dataset was created for research purposes, including training a Danish wav2vec2.0 model. 

The dataset was preprocessed to remove duplicates by a team of researchers at the Center for Humanities Computing, Aarhus University (CHC) with collaborators from the Danish speech-processing company [Alvenir](alvenir.ai).

**Any other comments?**

No.


## Composition

**What do the instances that comprise the dataset represent (e.g., documents, photos, people, countries)?**

Instances of the dataset include an mp3 file for each show aired on the two staions within the period. Further metadata include information on date and time of airing, title, short description of the show, and various internal identifiers used by DNL.

**How many instances are there in total (of each type, if appropriate)?**

DaRadio consists of a total of 215.582 hours of unprocessed Danish speech radio shows across two stations, DR P1 and Radio24syv. The table below shows the distribution over the stations with and without heuristic rerun removal.


| Source     | Duration (hours) | Reruns removed |
|------------|------------------|----------------|
| P1         | 145.160          | False          |
|            | 97.401           | True           |
| Radio24syv | 70.422           | False          |
|            | 44.569           | True           |


**Does the dataset contain all possible instances or is it a sample (not necessarily random) of instances from a larger set?**

The dataset contains all shows from the two stations in the time period (2005-2021 for DR P1 and 2011-2019 for Radio24syv).

**If the dataset is a sample from a larger set, what was the sampling strategy?**

The dataset is a subset of all Danish radio. The two stations were chosen for the dataset as they are talk-radio only. 


**Who was involved in the data collection process?**

The Royal Danish Library collects Danish radio shows and constructed DaRadio for handing to researchers at CHC.


**Over what timeframe was the data collected?**

The dataset includes radio shows from the period 2005 to 2021.

**Were any ethical review processes conducted?**

The Royal Danish Library collects radio shows in adherence to Danish Archival laws. DaRadio was constructed for a research project, for which a project proposal was accepted by RDL. No other ethical review processes were conducted.


## Preprocessing/cleaning/labeling

**Was any preprocessing/Cleaning/Labeling of the data done 
(e.g., discretization or bucketing, tokenization, part-of-speech tagging, 
SIFT feature extraction, removal of instances, processing of missing values)?**

DaRadio has been deduplicated using a series of heuristic filters and all files have been converted to 16 Khz .wav files. 

Reruns/duplicates were identified by the following rules:

- If the phrase "sendt første gang" ["aired the first time"] or "genudsendelse" ["rerun"] appeared in the show description.
- If the title contained "(G)" (short for "genudsendelse")) 
- If the show was broadcast between 23:00 and 5:00.



**Is the software used to preprocess/clean/label the instances available?**

The scripts are available at the following GitHub repository: [link](https://github.com/centre-for-humanities-computing/Gjallarhorn).

## Uses

**Has the dataset been used for any tasks already?**

Yes, the dataset has been used to pre-train a [Danish wav2vec2.0 model.](https://huggingface.co/chcaa/xls-r-300m-danish) 

**Is there a repository that links to any or all papers or systems that use the dataset?**

No.

**What (other) tasks could the dataset be used for?**

As the dataset only contains un-labelled data, i.e. no transcriptions, it is mainly useful for pre-training language models without further processing. However, given the metadata and re-occuring hosts, further processing might make it possible to train e.g. text-to-speech systems. 

**Is there anything about the composition of the dataset or the way it was collected and
preprocessed/cleaned/labeled that might impact future uses?**

This dataset is static and does not evolve over time with the language, thus will become increasingly outdated over time.


## Distribution

**Will the dataset be distributed to third parties outside of the entity (e.g., company, institution, organization) on behalf of which the dataset was created?**

No.


### Citation
If you wish to cite this work please see our GitHub page for an up to date citation: https://github.com/centre-for-humanities-computing/danish-foundation-models


### References:

- [1] T. Gebru, J. Morgenstern, B. Vecchione, J. W. Vaughan, H. Wallach, H. Daumé III,
        and K. Crawford. Datasheets for datasets. arXiv preprint arXiv:1803.09010, 2018.

