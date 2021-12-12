"""script for converting the HopeTweet corpus into HF format"""


import os
from typing import Dict, List
import datasets


_CITATION = """\
None yet
"""

_DESCRIPTION = """\
A scrape of Danish Twitter collected as a part of the HOPE project.
"""

_HOMEPAGE = "https://hope-project.dk/#/"
_LICENSE = "Not public"
_DATA_URL = "Not public"


class HopeTweetConfig(datasets.BuilderConfig):
    """BuilderConfig for DAGW."""

    def __init__(self, data_url, **kwargs):
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
        self.data_url = data_url


class HopeTweet(datasets.GeneratorBasedBuilder):
    """The HopeTweet is a Corpus contains tweets spanning from 2019-2021 collected as a part of the HOPE project"""

    VERSION = datasets.Version("1.0.0")
    BUILDER_CONFIGS = [
        HopeTweetConfig(
            name="HopeTweet",
            data_url=_DATA_URL,
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
                    "id": datasets.Value("string")
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

    def _get_filepaths(self, path: str) -> Dict[str, List[str]]:
        """
        Gets the path to all text files in HopeTweet

        Returns:
            Dict[str, List[str]] -- Dictionary with sektion as key, and list of filepaths as stringshu
        """
        pass
    

        return filepaths


    def _split_generators(self, dl_manager):
        """Returns SplitGenerators."""
        # dl_manager is a datasets.download.DownloadManager that can be used to
        # download and extract URLs
        if self.config.name == "HopeTweet-v1":
            data_file = dl_manager.download_and_extract(self.config.data_url)

            return [
                datasets.SplitGenerator(
                    name=datasets.Split.TRAIN,
                    gen_kwargs={
                        "data_file": os.path.join(data_file, "dagw", "sektioner"),
                        "split": "train",
                    },
                )
            ]

    def _generate_examples(self, data_file, split):
        """Yields examples."""
        filepaths = self._get_filepaths(data_file)
        row_n = 0
        for origin in filepaths.keys():
            for path in filepaths[origin]:
                with open(path) as f:
                    text = f.read()
                yield row_n, {"text": text, "origin": origin}
                row_n += 1