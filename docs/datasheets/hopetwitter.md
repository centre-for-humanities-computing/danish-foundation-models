
# HopeTwitter

*Version*: 1.0.0

*Homepage*: https://github.com/centre-for-humanities-computing/danish-foundation-models

*license*: Not publicly available.

---

HopeTwitter consists of tweets collected from the Twitter API using a stopword list
and consists of 32.5 million tweets across 538,398 unique users. HopeTwitter includes
tweets from 2019-01-01 to 2021-04-30.

HopeTwitter, have been filtered to only include Danish tweets. Similarly, HopeTwitter
have had low-quality tweets have removed and then deduplicated to remove exact and
near-duplicates. For more on data cleaning see section on 
Preprocessing/cleaning/labeling.

HopeTwitter includes a total of 0.97 billion tokens before filtering and includes 0.48
billion (0.50%) after.



## Datasheet:

Following the recommendation and framework of [3] we add the following datasheet. 

### Motivation:

**For what purpose was the dataset created? Who created the dataset? Who funded the 
creation of the dataset? **

HopeTwitter was initially collected as a part of the
[HOPE project](https://hope-project.dk/#/), examining societal behaviour during the
COVID-19 pandemic. Next, HopeTwitter was cleaned in preparation for pre-training Danish language
models by a team of researchers at Center for Humanities Computing Aarhus 
([CHCAA](https://chcaa.io/#/)), using
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

HopeTwitter consists of tweets containing at least one of a series of stopwords,
collected through the Twitter API. See "If the dataset is a sample from a larger set,
what was the sampling strategy?" for the stopword list.

**How many instances are there in total (of each type, if appropriate)?**

The dataset consist of 32,499,019 documents where 14,399,284 (44%) were considered
duplicates. 

**Does the dataset contain all possible instances or is it a sample (not necessarily
random) of instances from a larger set?**

No. It does not contain all instances of Danish Twitter as there are likely some Danish
tweets which does not include a stopword.

**Is there a label or target associated with each instance? If so, please provide a
description.**

No.

**Are there recommended data splits (e.g., training, development/validation, testing)?
If so, please provide a description of these splits, explaining the rationale behind
them.**

No splits are performed on this dataset.


**If the dataset is a sample from a larger set, what was the sampling strategy?**

Tweets are streamed continuously using queried a set of the highest 
frequency Scandinavian-specific keywords from Danish, Norwegian (Bokmål) and Swedish,
resulting in the following list:
```
aften, aldrig, alltid, altid, andet, arbejde, bedste, behöver, behøver, beklager,
berätta, betyr, blev, blevet, blir, blitt, blive, bliver, bruge, burde, bättre, båe
bør, deim, deires, ditt, drar, drepe, dykk, dykkar, där, död, döda, død, døde, efter,
elsker, endnu, faen, fandt, feil, fikk, finner, flere, forstår, fortelle, fortfarande,
fortsatt, fortælle, från, få, fået, får, fått, förlåt, första, försöker, før, først,
første, gick, gikk, gillar, gjennom, gjerne, gjorde, gjort, gjør, gjøre, godt, gå, gång,
går, göra, gør, gøre, hadde, hallå, havde, hedder, helt, helvete, hende, hendes, hennes,
herregud, hjelp, hjelpe, hjem, hjälp, hjå, hjælp, hjælpe, honom, hossen, hvem, hvis,
hvordan, hvorfor, händer, här, håll, håller, hør, høre, hører, igjen, ikkje, ingenting,
inkje, inte, intet, jeres, jävla, kanske, kanskje, kender, kjenner, korleis, kvarhelst,
kveld, kven, kvifor, känner, ledsen, lenger, lidt, livet, längre, låt, låter, længe,
meget, menar, mycket, mykje, må, måde, många, mår, måske, måste, måtte, navn, nogen,
noget, nogle, noko, nokon, nokor, nokre, någon, något, några, nån, når, nåt, nødt,
också, også, pengar, penger, pratar, prøver, på, redan, rundt, rätt, sagde, saker,
samma, sammen, selv, selvfølgelig, sidan, sidste, siger, sikker, sikkert, själv, skete,
skjedde, skjer, skulle, sluta, slutt, snakke, snakker, snill, snälla, somt, stadig,
stanna, sted, står, synes, säger, sätt, så, sådan, såg, sånn, tager, tiden, tilbage,
tilbake, tillbaka, titta, trenger, trodde, troede, tror, två, tycker, tänker, uden,
undskyld, unnskyld, ursäkta, uten, varför, varit, varte, veldig, venner, verkligen,
vidste, vilken, virkelig, visste, väg, väl, väldigt, vän, vår, våra, våre, væk, vær, 
være, været, älskar, åh, år, åt, över
```

**Who was involved in the data collection process?**

A team of researchers at the Center for Humanities
Computing Aarhus (CHCAA), including Kristoffer Nielbo and Peter Bjerregaard Vahlstrup, in collaboration with Rebekah Baglini, at the School of Communcation and Culture at Aarhus university.

###### NOTE: take from version on ucloud


**Over what timeframe was the data collected?**

The dataset includes tweets from the period 2019-01-01 to 2021-04-30.

**Were any ethical review processes conducted?**

No

## Preprocessing/cleaning/labeling

**Was any preprocessing/Cleaning/Labeling of the data done 
(e.g., discretization or bucketing, tokenization, part-of-speech tagging, 
SIFT feature extraction, removal of instances, processing of missing values)?**


Firstly, HopeTwitter had non-Danish tweets removed, after which a series of
heuristic filters were applied, including the removal of repetitious texts. Following the filtering,
HopeTwitter was deduplicated, removing both exact duplicates and near-duplicates.

Of all documents, 3,023,427 (9%) were filtered due to low-quality and
14,399,284 (33%) because they were near-duplicates.

For the quality filtering, HopeTwitter applies a filter akin to [2] which contains text
that:

- Contain at least 2 Danish stopwords. For the stopword list we use the one used in
SpaCy v.3.1.4.
- Have a mean word length between 2 and 14.
- Have a token length between 10 and 100,000.
- Have less than 5,000,000 characters.
- Have less than 60% of words containing an alphabetic character.

- Have low high degree of repetitious text:
  - Have less than 20% of characters contained within duplicate lines.
  - Have less than 20% of characters contained within duplicate paragraphs.
  - Where the top 2-4 grams constitute less than 20%, 18%, 16%, respectively, of the text. 
  - Where the duplicate 5-10 grams constitute less than 25%, 24%, 23%, 22%, 21%, 20%
of the text, respectively.

The deduplication removed all documents with a 10-gram Jaccard similarity higher than 80%
following the MinHash algorithm [1] using 128 permutations. The MinHash algorithm is a
probabilistic data structure for approximating the Jaccard similarity between two sets.


**Is the software used to preprocess/clean/label the instances available?**

Yes, the scripts are available
[here](https://github.com/centre-for-humanities-computing/danish-foundation-models/tree/main/src/application/danews).
The scripts use version 0.0.2 of the
[dfm package](https://github.com/centre-for-humanities-computing/danish-foundation-models). 


## Uses

**Has the dataset been used for any tasks already?**

Yes, the dataset has been used to pre-train Danish language models.
Parts of the dataset have also been used in HOPE project [reports](https://hope-project.au.dk/#/reports) 
and in [4].


**Is there a repository that links to any or all papers or systems that use the dataset?**

There is [a website](https://hope-project.au.dk) for the HOPE project for which the dataset was initially collected. This website contains report and articles regarding the dataset.

**What (other) tasks could the dataset be used for?**

The scale of the dataset makes it suitable for NLP tasks such as language modelling.
Similarly, one could imagine using the conversation structure could be used to train
conversational chatbots.

**Is there anything about the composition of the dataset or the way it was collected and 
preprocessed/cleaned/labeled that might impact future uses?**

This dataset is static and thus does not evolve over time with the language. 
A consequence of this is that it will become increasingly outdated over time. However,
it possible to extend the dataset by a continual collection of tweets.

**Are there tasks for which the dataset should not be used?**

HopeTwitter contains Danish tweets and thus should not be used for non-Danish language tasks.

As the writers of the content is predominantly journalists, politicians, influencers,
and academics, it reflects a certain social group which is unlikely to reflect Danish
population as a whole.

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
- [3] T. Gebru, J. Morgenstern, B. Vecchione, J. W. Vaughan, H. Wallach, H. Daumé III,
    and K. Crawford. Datasheets for datasets. arXiv preprint arXiv:1803.09010, 2018.
- [4] Johansen, N., Marjanovic, S. V., Kjaer, C. V., Baglini, R. B., & Adler-Nissen, R. 
    (2022). Ridiculing the “tinfoil hats:” Citizen responses to COVID-19 misinformation
    in the Danish facemask debate on Twitter. Harvard Kennedy School Misinformation
    Review. https://doi.org/10.37016/mr-2020-93
