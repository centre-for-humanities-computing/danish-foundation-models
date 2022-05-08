import os

from datasets import load_from_disk
from wasabi import msg
import spacy

path = os.path.join("/work", "twitter_cleaned", "twitter_da_stopwords_2019-01-01_2021-04-30")
write_path = os.path.join("/work", "twitter_cleaned", "twitter_da_stopwords_2019-01-01_2021-04-30.arrow")
ds = load_from_disk(path)


def word_count(batch):
  nlp = spacy.blank("da")
  batch["n_tokens"] = [len(doc) for doc in nlp.pipe(batch["text"])]
  return batch


msg.info("Add n_tokens column")
ds = ds.map(word_count, batched = True, batch_size=1024*2*2, num_proc=16)



n_docs = len(ds)
n_users = len(set(ds["author_id"]))
n_tokens_ = ds["n_tokens"]
is_duplicate_ = ds["is_duplicate"]
n_tokens = sum(ds["n_tokens"])
n_clean_tokens = sum([ntok for ntok, isdup in zip(n_tokens_, is_duplicate_) if isdup])
n_duplicates = len([d for d in is_duplicate_ if d is True])
n_non_duplicates = len([d for d in is_duplicate_ if d is not None])
passed_quality_filter = ds["passed_quality_filter"] 
n_low_quality = sum(1 for is_good in passed_quality_filter if is_good is False)

ds.info.description = f"""
HopeTwitter consist of tweets collected from the Twitter API using a stopword list
and consists of {n_docs} tweets across {n_users} unique users. HopeTwitter include
tweets from the period 2019-01-01_2021-04-30.

A subsection of HopeTwitter, henceforth HopeTwitter_c, have been filtered out to only include Danish tweets
and low-quality text have been removed using a series of heuristic filters and removing repitious texts. 
Following the filtering HopeTwitter_c is deduplicated to remove exact and near-duplicates. For more on data cleaning
see section on post processing.

HopeTwitter includes a total of {n_tokens} tokens and HopeTwitter_c includes {n_clean_tokens} ({n_clean_tokens/n_tokens:.2f}%).

## Datasheet:

### Motivation:

**For what purpose was the dataset created? Who created the dataset? Who funded the creation of the dataset? **

HopeTwitter was initially collected with the intention of social media monitoring during the COVID-19 pandemic, but the cleaned
version, HopeTwitter_c, was created for pre-training Danish language models by a team of researchers at Center for Humanities
Computing Aarhus (CHCAA) using a codebase jointly developed with partners from industry (e.g. KMD, Ekstra Bladet) and other
research institutions (e.g. Briston University, Alexandra Institute). For more on collaborators on this project see
the [GitHub repository](https://github.com/centre-for-humanities-computing/danish-foundation-models
).

**Any other comments?**
No.

## Composition

**What do the instances that comprise the dataset represent (e.g., documents, photos, people, countries)?**

HopeTwitter consist of all tweets containing at least one of the following stopwords collected through the Twitter API. 
See "If the dataset is a sample from a larger set, what was the sampling strategy?".

HopeTwitter_c filters HopeTwitter by removing non-Danish tweets as determined by metadata and further removed low-quality, repitious text and near-duplicated.


**How many instances are there in total (of each type, if appropriate)?**

The dataset consist of {n_docs} documents where {n_duplicates} ({n_duplicates/n_docs:.2f}%) were considered duplicates. 

**Does the dataset contain all possible instances or is it a sample (not necessarily random) of instances from a larger set?**

No. It does not contain all instances of Danish Twitter as there is likely some "Danish" tweets such as exclamations and links
which does not include a stopword.

**If the dataset is a sample from a larger set, what was the sampling strategy?**

Tweets are streamed continuously using queried a set of the highest 
frequency scandinavian-specific words from Danish, Norwegian (Bokmål) and Swedish. 
Resulting the following list:

```
aften, aldrig, alltid, altid, andet, arbejde, bedste, behöver, behøver, beklager, berätta, betyr, blev, blevet, blir, blitt, blive, bliver, 
bruge, burde, bättre, båe, bør, deim, deires, ditt, drar, drepe, dykk, dykkar, där, död, döda, død, døde, efter, elsker, endnu, faen, fandt, 
feil, fikk, finner, flere, forstår, fortelle, fortfarande, fortsatt, fortælle, från, få, fået, får, fått, förlåt, första, försöker, før, 
først, første, gick, gikk, gillar, gjennom, gjerne, gjorde, gjort, gjør, gjøre, godt, gå, gång, går, göra, gør, gøre, hadde, hallå, havde, 
hedder, helt, helvete, hende, hendes, hennes, herregud, hjelp, hjelpe, hjem, hjälp, hjå, hjælp, hjælpe, honom, hossen, hvem, hvis, hvordan, 
hvorfor, händer, här, håll, håller, hør, høre, hører, igjen, ikkje, ingenting, inkje, inte, intet, jeres, jävla, kanske, kanskje, kender, kjenner, 
korleis, kvarhelst, kveld, kven, kvifor, känner, ledsen, lenger, lidt, livet, längre, låt, låter, længe, meget, menar, mycket, mykje, må, måde, 
många, mår, måske, måste, måtte, navn, nogen, noget, nogle, noko, nokon, nokor, nokre, någon, något, några, nån, når, nåt, nødt, också, også, 
pengar, penger, pratar, prøver, på, redan, rundt, rätt, sagde, saker, samma, sammen, selv, selvfølgelig, sidan, sidste, siger, sikker, sikkert, 
själv, skete, skjedde, skjer, skulle, sluta, slutt, snakke, snakker, snill, snälla, somt, stadig, stanna, sted, står, synes, säger, sätt, så, 
sådan, såg, sånn, tager, tiden, tilbage, tilbake, tillbaka, titta, trenger, trodde, troede, tror, två, tycker, tänker, uden, undskyld, unnskyld, 
ursäkta, uten, varför, varit, varte, veldig, venner, verkligen, vidste, vilken, virkelig, visste, väg, väl, väldigt, vän, vår, våra, våre, væk, vær, 
være, været, älskar, åh, år, åt, över
```


**Who was involved in the data collection process?**

A team of researchers at Center for Humanities
Computing Aarhus (CHCAA), and Rebekah Baglini, school of communcation and culture at Aarhus university.

**Over what timeframe was the data collected?**

The dataset include articles from the period 2019-01-01_2021-04-30.

**Were any ethical review processes conducted?**

XXX

## Preprocessing/cleaning/labeling

**Was any preprocessing/Cleaning/Labeling of the data done 
(e.g., discretization or bucketing, tokenization, part-of-speech tagging, 
SIFT feature extraction, removal of instances, processing of missing values)?**

We filter tweets that are not in Danish. We remove low-quality text and deduplicate documents based on their 
document-level n-gram similarity. The full pre-processing details are given in the post processing section.

**Is the software used to preprocess/clean/label the instances available?**

Yes, the script are avaiable [here](https://github.com/centre-for-humanities-computing/danish-foundation-models/tree/main/src/application/hopetwitter). 
Which used version 0.0.1 of the [dfm package](https://github.com/centre-for-humanities-computing/danish-foundation-models). 

## Uses

**Has the dataset been used for any tasks already?**

Yes, the dataset has been used to pre-train Danish language models.
Parts of the dataset have also been used in
XXX
XXX

**Is there a repository that links to any or all papers or systems that use the dataset?**

No.

**What (other) tasks could the dataset be used for?**

The scale of the dataset makes it suitable for NLP tasks such as language modelling.
Similarly, one could imagine using the conversation structure could be used to train conversational chatbots.

**Is there anything about the composition of the dataset or the way it was collected and preprocessed/cleaned/labeled that might impact future uses?**

This dataset is static and thus does not evolve over time with the language, thus will become increasingly outdated over time.
However, it possible to extend the dataset by a continual collection of tweets.


**Are there tasks for which the dataset should not be used?**

HopeTwitter_c contains Danish tweet and thus should not be used for non-Danish language task.
As the writers of the content is predominantly journalists, politicians, influencers, academics it reflect a certain social group which is unlikely to reflect Danish population as a whole.

## Distribution

**Will the dataset be distributed to third parties outside of the entity (e.g., company, institution, organization) on behalf of which the dataset was created?**

No.



# Post processing

HopeTwitter_c have been filtered for quality using a series of heuristic filters and removing repitious texts. 
Following the filtering HopeTwitter_c is deduplicated to remove exact and near-duplicates.

A total of {n_low_quality} ({n_low_quality/n_docs:.2f}%) were considered low quality and a 
total of {n_duplicates} ({n_duplicates/(n_non_duplicates+n_duplicates):.2f}%) documents were considered duplicates.

## Quality Filter:

For the quality filtering HopeTwitter applies a filter akin to [2] which filters text which does not:

- Contain at least one Danish stopwords. For the stopword list we use the one used in SpaCy v.3.1.4.
- Have mean word length between 2-14.
- Have a token length between 10-10 000.
- Have a less than 5 000 000 characters.
- Have a less than 60% words containing an alphabetic character.

- Have low high degree of repitiuous text:
 - Less than 20% duplicate lines.
 - Less than 20% duplicate paragraphs.
 - Where the top 2-4 grams constitute less than 20%, 18%, 16%, respectively, of the text. 
 - Where the duplicate 5-10 grams constitute less than 25%, 24%, 23%, 22%, 21%, 20% of the text, respectively.

## Deduplication

The deduplication removed all documents with a 10-gram similarity higher than 80% following the MinHash algorithm [1] using 128 permutation.
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

ds.info.license = "Not publicly available."

ds.info.version = "1.0.0"
ds.info.citation = "If you wish to cite this work please see our GitHub page for an up to date citation: https://github.com/centre-for-humanities-computing/danish-foundation-models"
ds.info.homepage = "https://github.com/centre-for-humanities-computing/danish-foundation-models"

# write markdown file
print("\tWriting markdown file")
md = f"""
# HopeTwitter

*Version*: {ds.info.version}

*Homepage*: {ds.info.homepage}

*license*: {ds.info.license}

{ds.info.description}

### Citation
{ds.info.citation}
"""

print("Saving description markdown")
with open("danish-foundation-models/docs/hopetwitter.md", "w") as f:
  f.write(md)

# write dataset with added metadata
print("Saving dataset")
ds.save_to_disk(write_path)

# test = load_from_disk(write_path)