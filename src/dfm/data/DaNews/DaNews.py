"""script for converting the InfoMedia corpus into HF format"""


import os
from typing import Dict, List

import datasets
import ndjson
from wasabi import msg

_CITATION = """\
None yet
"""

data_base_dir = os.path.join("/work", "data", "hope-infomedia")
data_path = os.path.join(data_base_dir, "yearly")

# description
with open(os.path.join(data_base_dir, "readme_infomedia.md")) as f:
    _DESCRIPTION = f.read()

_HOMEPAGE = "https://hope-project.dk/#/"
_LICENSE = "Not public"


class DaNewsConfig(datasets.BuilderConfig):
    """BuilderConfig for DaNews."""

    def __init__(self, **kwargs):
        """BuilderConfig for DaNews

        Args:
          data_url: `string`, url to the dataset
          **kwargs: keyword arguments forwarded to super.
        """
        super(DaNewsConfig, self).__init__(
            version=datasets.Version(
                "1.0.0",
            ),
            **kwargs,
        )


class DaNews(datasets.GeneratorBasedBuilder):
    """The DaNews is a corpus containing danish news from 2000-12"""

    BUILDER_CONFIGS = [
        DaNewsConfig(
            name="DaNews",
            description="Document level dataset. Each row contains one news article along with its metadata",
        )
    ]

    def _info(self):
        return datasets.DatasetInfo(
            description=_DESCRIPTION,
            features=datasets.Features(
                {
                    "url": datasets.Value("string"),
                    "heading": datasets.Value("string"),
                    "subheading": datasets.Value("string"),
                    "lead": datasets.Value("string"),
                    "paragraph": datasets.Value("string"),
                    "publishdate": datasets.Value("string"),
                    "body": datasets.Value("string"),
                    "captions": datasets.Value("string"),
                    "authors": datasets.Value("string"),
                    "source": datasets.Value("string"),
                    "wordcount": datasets.Value("int64"),
                    "articleid": datasets.Value("string"),
                    "pageids": datasets.Value("string"),
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
        if self.config.name == "DaNews":
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
        mapping = {
            "url": "ArticleUrl",
            "heading": "Heading",
            "subheading": "SubHeading",
            "lead": "Lead",
            "paragraph": "Paragraph",
            "publishdate": "PublishDate",
            "body": "BodyText",
            "captions": "Captions",
            "authors": "Authors",
            "source": "Source",
            "wordcount": "WordCount",
            "articleid": "ArticleId",
            "pageids": "PageIds",
        }

        for fp in filepaths:
            with open(fp) as f:
                msg.info(f"DaNews: Starting reading from:\n {os.path.basename(fp)}")
                reader = ndjson.reader(f)

                for row in reader:
                    row_ = {k: row.pop(k_) for k, k_ in mapping.items()}
                    yield row_n, row_
                    row_n += 1
