"""script for converting DAGW into HF format"""

import os

import datasets


_CITATION = """\
@inproceedings{dagw,
 title = {{The Danish Gigaword Corpus}},
 author = {Leon Derczynski and Manuel R. Ciosici and Rebekah Baglini and Morten H. Christiansen and Jacob Aarup Dalsgaard and Riccardo Fusaroli and Peter Juel Henrichsen and Rasmus Hvingelby and Andreas Kirkedal and Alex Speed Kjeldsen and Claus Ladefoged and Finn Årup Nielsen and Jens Madsen and Malte Lau Petersen and Jonathan Hvithamar Rystrøm and Daniel Varab},
 year = 2021,
 booktitle = {Proceedings of the 23rd Nordic Conference on Computational Linguistics},
 publisher = {NEALT}
}
"""

_DESCRIPTION = """\
 The Danish Gigaword Corpus contains raw text spanning several different domains and forms. The dataset is available under the Creative Commons Attribution-ShareAlike
 License.
"""
_HOMEPAGE = "https://gigaword.dk"
_LICENSE = "Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)"
_DATA_URL = "https://bit.ly/danishgigaword10"


class DAGWConfig(datasets.BuilderConfig):
    """BuilderConfig for DAGW."""

    def __init__(self, data_url, **kwargs):
        """BuilderConfig for DAGW

        Args:
          data_url: `string`, url to the dataset
          **kwargs: keyword arguments forwarded to super.
        """
        super(DAGWConfig, self).__init__(
            version=datasets.Version(
                "1.0.0",
            ),
            **kwargs,
        )
        self.data_url = data_url


class DAGW(datasets.GeneratorBasedBuilder):
    """The Danish Gigaword Corpus contains raw text spanning several different domains and forms. The dataset is available under the Creative Commons Attribution-ShareAlike
    License."""

    VERSION = datasets.Version("0.1.0")
    BUILDER_CONFIGS = [
        DAGWConfig(
            name="DAGW-v1",
            data_url=_DATA_URL,
            description="Document level dataset. Each row contains one document (of greatly varying length)",
        )
    ]

    def _info(self):
        return datasets.DatasetInfo(
            # This is the description that will appear on the datasets page.
            description=_DESCRIPTION,
            features=datasets.Features(
                {
                    "text": datasets.Value("string"),
                    "origin": datasets.Value("string")
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

    def _get_filepaths(self, dagw_sektion_path):
        """Gets the path to all text files in DAGW

        Returns:
            Dict[str, List[str]] -- Dictionary with sektion as key, and list of filepaths as stringshu
        """
        sections = os.listdir(dagw_sektion_path)

        filepaths = {}
        for p in sections:
            subpath = os.path.join(dagw_sektion_path, p)
            filepaths[p] = [
                os.path.join(subpath, p)
                for p in os.listdir(subpath)
                if p != "LICENSE" and not p.endswith(".jsonl")
            ]

        def handle_subdir(section):
            return [
                os.path.join(filepaths[section][0], p)
                for p in os.listdir(filepaths[section][0])
            ]

        filepaths["twfv19"] = handle_subdir("twfv19")
        filepaths["datwitter"] = handle_subdir("datwitter")

        return filepaths

    def _split_generators(self, dl_manager):
        """Returns SplitGenerators."""
        # dl_manager is a datasets.download.DownloadManager that can be used to
        # download and extract URLs
        if self.config.name == "DAGW-v1":
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
            # ),
            # datasets.SplitGenerator(
            #     name=datasets.Split.TRAIN,
            #     gen_kwargs={"data_file": os.path.join(data_dir, "wiki.train.tokens"), "split": "train"},
            # ),
            # datasets.SplitGenerator(
            #     name=datasets.Split.VALIDATION,
            #     gen_kwargs={"data_file": os.path.join(data_dir, "wiki.valid.tokens"), "split": "valid"},
            # ),

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