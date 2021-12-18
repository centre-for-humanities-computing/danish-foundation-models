"""script for converting the HopeTweet corpus into HF format"""


import os
from typing import Dict, List
import datasets
import ndjson

_CITATION = """\
None yet
"""


data_path = os.path.join("/work", "data", "twitter")

with open(os.path.join(data_path, "readme.md")) as f:
    _DESCRIPTION = f.read()


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
        id = set()
        for fp in filepaths:
            texts_dedup = set()
            with open(fp) as f:
                reader = ndjson.reader(f)

                for row in reader:
                    if row["id"] in id:
                        continue
                    if row["text"] in texts_dedup:
                        continue
                    id.add(row["id"])
                    texts_dedup.add(row["text"])
                    row_ = {
                        k: row.pop(k)
                        for k in ["text", "lang", "id", "possibly_sensitive"]
                    }
                    yield row_n, row_
                    row_n += 1


