"""script for converting the HopeTweet corpus into HF format"""


import os
from typing import Dict, List
import datasets
import ndjson

_CITATION = """\
None yet
"""

_DESCRIPTION = """\
A scrape of Danish Twitter collected as a part of the HOPE project.

# Twitter

Tweets are streamed continuously using queried a set of the highest frequency scandinavian-specific words from da/no/sv and then using 
witter’s language classifier to separate them into lang-specific lists. 

In our case filtering out Danish only tweet as well and 
["possibly_sensitive"](https://developer.twitter.com/en/docs/twitter-api/v1/data-dictionary/object-model/tweet) tweets.


Here is the list:
```
aften, aldrig, alltid, altid, andet, arbejde, bedste, behöver, behøver, beklager, berätta, betyr, blev, blevet, blir, blitt, blive, bliver, bruge, burde,
bättre, båe, bør, deim, deires, ditt, drar, drepe, dykk, dykkar, där, död, döda, død, døde, efter, elsker, endnu, faen, fandt, feil, fikk, finner, flere,
forstår, fortelle, fortfarande, fortsatt, fortælle, från, få, fået, får, fått, förlåt, första, försöker, før, først, første, gick, gikk, gillar, gjennom,
gjerne, gjorde, gjort, gjør, gjøre, godt, gå, gång, går, göra, gør, gøre, hadde, hallå, havde, hedder, helt, helvete, hende, hendes, hennes, herregud,
hjelp, hjelpe, hjem, hjälp, hjå, hjælp, hjælpe, honom, hossen, hvem, hvis, hvordan, hvorfor, händer, här, håll, håller, hør, høre, hører, igjen, ikkje,
ingenting, inkje, inte, intet, jeres, jävla, kanske, kanskje, kender, kjenner, korleis, kvarhelst, kveld, kven, kvifor, känner, ledsen, lenger, lidt,
livet, längre, låt, låter, længe, meget, menar, mycket, mykje, må, måde, många, mår, måske, måste, måtte, navn, nogen, noget, nogle, noko, nokon, nokor,
nokre, någon, något, några, nån, når, nåt, nødt, också, også, pengar, penger, pratar, prøver, på, redan, rundt, rätt, sagde, saker, samma, sammen, selv,
selvfølgelig, sidan, sidste, siger, sikker, sikkert, själv, skete, skjedde, skjer, skulle, sluta, slutt, snakke, snakker, snill, snälla, somt, stadig,
stanna, sted, står, synes, säger, sätt, så, sådan, såg, sånn, tager, tiden, tilbage, tilbake, tillbaka, titta, trenger, trodde, troede, tror, två, tycker,
tänker, uden, undskyld, unnskyld, ursäkta, uten, varför, varit, varte, veldig, venner, verkligen, vidste, vilken, virkelig, visste, väg, väl, väldigt, vän,
vår, våra, våre, væk, vær, være, været, älskar, åh, år, åt, över
```

"""

_HOMEPAGE = "https://hope-project.dk/#/"
_LICENSE = "Not public"



class HopeTweetConfig(datasets.BuilderConfig):
    """BuilderConfig for HopeTweet."""

    def __init__(self, **kwargs):
        """BuilderConfig for HopeTweet

        Args:
          data_url: `string`, url to the dataset
          **kwargs: keyword arguments forwarded to super.
        """
        super(HopeTweetConfig, self).__init__(
            version=datasets.Version(
                "1.0.0",
            ),
            **kwargs,
        )



class HopeTweet(datasets.GeneratorBasedBuilder):
    """The HopeTweet is a Corpus contains tweets spanning from 2019-2021 collected as a part of the HOPE project"""

    BUILDER_CONFIGS = [
        HopeTweetConfig(
            name="HopeTweet",
            description="Document level dataset. Each row contains one tweet along with its metadata",
        )
    ]

    def _info(self):
        return datasets.DatasetInfo(
            # This is the description that will appear on the datasets page.
            description=_DESCRIPTION,
            features=datasets.Features(
                {
                    "text": datasets.Value("string"),
                    "id": datasets.Value("string"),
                    "lang": datasets.Value("string"),
                    "possibly_sensitive": datasets.Value("bool"),
                    # TODO add more metadata here
                    # These are the features of your dataset like images, labels ...
                }
            ),
            # If there's a common (input, target) tuple from the features,
            # specify them here. They'll be used if as_supervised=True in
            # builder.as_dataset.
            supervised_keys=None,
            homepage=_HOMEPAGE,
            license=_LICENSE,
            citation=_CITATION,
        )

    def _split_generators(self, dl_manager):
        """Returns SplitGenerators."""
        # dl_manager is a datasets.download.DownloadManager that can be used to
        # download and extract URLs
        if self.config.name == "HopeTweet":
            data_path = os.path.join("/work", "data", "twitter")
            print(f"path: {data_path}")

            return [
                datasets.SplitGenerator(
                    name=datasets.Split.TRAIN,
                    gen_kwargs={
                        "data_path": data_path,
                        "split": "train",
                    },
                )
            ]

    def _generate_examples(self, data_path, split):
        """Yields examples."""
        filepaths = [os.path.join(data_path, p) for p in os.listdir(data_path)]
        row_n = 0
        for fp in filepaths:
            with open(fp) as f:
                reader = ndjson.reader(f)

                for row in reader:
                    row_ = {k: row.pop(k) for k in ["text", "lang", "id", "possibly_sensitive"]}
                    yield row_n, row_
                    row_n += 1
