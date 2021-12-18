"""TODO(DAGW): Add a description here."""


import os

import datasets
from datasets.utils import metadata
import ndjson

from .licenses import *

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


_INDIVIDUAL_LICENSES = {
    "adl": cc0,
    "botxt": cc0,
    "cc": cc0,
    "danavis": cc0,
    "dannet": dannet_license,
    "datwitter": twitter_license,
    "depbank": att_sharealike_4,
    "ep": cc0,
    "ft": cc0,
    "gutenberg": gutenberg_license,
    "hest": cc0,
    "jvj": att_sharealike_4,
    "naat": cc0,
    "opensub": opensub_license,
    "relig": cc0,
    "retsinformationdk": retsinformationdk_license,
    "retspraksis": cc0,
    "skat": cc0,
    "spont": cc0,
    "synne": cc0,
    "tv2r": tv2r_license,
    "twfv19": twitter_license,
    "wiki": cc0,
    "wikibooks": cc0,
    "wikisource": cc0,
}


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

    BUILDER_CONFIGS = [
        DAGWConfig(
            name="dagw",
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
                    "source": datasets.Value("string"),
                    "doc_id": datasets.Value("string"),
                    "LICENSE": datasets.Value("string"),
                    "uri": datasets.Value("string"),
                    "date_built": datasets.Value("string"),
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

    def _generate_examples(self, data_file, split):
        """Yields examples."""

        def _get_filepaths(dagw_sektion_path):
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
                    if p != "LICENSE"
                    and not p.endswith(".json")
                    and not p.endswith(".jsonl")
                    and not p.startswith("README")
                ]

            def handle_subdir(section):
                return [
                    os.path.join(filepaths[section][0], p)
                    for p in os.listdir(filepaths[section][0])
                    if p != "LICENSE"
                    and not p.endswith(".json")
                    and not p.endswith(".jsonl")
                    and not p.startswith("README")
                ]

            filepaths["twfv19"] = handle_subdir("twfv19")
            filepaths["datwitter"] = handle_subdir("datwitter")

            return filepaths

        def _read_metadata(section):
            if section not in ["datwitter", "twfv19"]:
                with open(os.path.join(data_file, section, section + ".jsonl")) as f:
                    meta = ndjson.load(f)
                if section not in ["danavis", "depbank", "botxt"]:
                    # convert list of dicts to dict with doc_id as key
                    try:
                        metadict = {
                            d["doc_id"]: {
                                "uri": d["uri"],
                                "date_built": d["date_built"],
                            }
                            for d in meta
                        }
                    except KeyError:
                        # not all sections have an uri
                        metadict = {
                            d["doc_id"]: {
                                "uri": "NA",
                                "date_built": d["date_built"],
                            }
                            for d in meta
                        }
                # no uri or date_built for danavis
                if section in ["danavis", "botxt"]:
                    metadict = {
                        d["doc_id"]: {
                            "uri": "NA",
                            "date_built": "NA",
                        }
                        for d in meta
                    }
                if section == "depbank":
                    metadict = {
                        d["doc_id"]: {
                            "uri": d["uri"],
                            "date_built": "NA",
                        }
                        for d in meta
                    }

                return metadict

            # for twitter corpora
            else:
                return {
                    "da_all_150420-260520.txt": {"uri": "NA", "date_built": "NA"},
                    "da_fv19.txt": {"uri": "NA", "date_built": "NA"},
                }

        filepaths = _get_filepaths(data_file)
        row_n = 0
        for section in filepaths.keys():
            section_metadata = _read_metadata(section)
            section_license = _INDIVIDUAL_LICENSES[section]
            for path in filepaths[section]:
                with open(path) as f:
                    text = f.read()
                doc_id = path.split("/")[-1]
                yield row_n, {
                    "text": text,
                    "source": section,
                    "doc_id": doc_id,
                    "LICENSE": section_license,
                    "uri": section_metadata[doc_id]["uri"],
                    "date_built": section_metadata[doc_id]["date_built"],
                }
                row_n += 1
