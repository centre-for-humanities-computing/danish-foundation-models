# Dataset: Netarkivet

## Dataset Description

Netarkivet is a historical web archive collected by the Royal Danish Library, our processed subset consist of **N** unique web domains with an average document length of **N...**


## Dataset Processing

### The prefiltered dataset
The sample supplied by netarkivet had exact duplicates removed and is collected **... (ask for report Per mentioned)**

### Filtering
For the dataset filtered we use a similar approach as done by the **Gopher Paper** where the filtering consist of the following steps:

1) Content filtering, Removing pornographic content and keeping only Danish texts
2) Heuristic quality filtering, filters out low quality texts based on a series of filters designed to remove extreme text samples.

#### Step 1: Content Filtering
We removed non-danish text using the language tag provided by the Royal Danish library which used [language-detector](https://github.com/optimaize/language-detector) for language detection.
We logged the number of timestamps (excluding time) and domains. We then removed any domains which only only appear once in the
corpus assuming an website of interest is likely to either appear multiple times in the corpus or contain subsites.
We then ran all the domains through google safesearch and to filter out pornographic content. 
**We manually checked 100 of the domains deemed unsafe and found all to be valid.**

#### Step 2: Quality Filtering

