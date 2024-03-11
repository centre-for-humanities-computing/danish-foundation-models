"""
This script uses the Dolma parallel processing pipeline to count domains of the documents in
a dataset.

Example:
    python dolma_domain_count.py "/dataset/documents/*.jsonl.gz" domaincount_report
"""

from collections import Counter
from contextlib import ExitStack
from io import TextIOWrapper
import shutil
import sys
from tempfile import TemporaryDirectory
from typing import Dict, List, Any, Iterator, Optional

from dolma.core.data_types import InputSpecWithMetadata
from dolma.core.loggers import get_logger
from dolma.core.parallel import BaseParallelProcessor, QueueType
from dolma.core.paths import glob_path, mkdir_p
from dolma.core.errors import DolmaError, DolmaConfigError

import msgspec
from msgspec.json import Decoder
import multiprocessing
import smart_open
import tqdm
import urllib3
import urllib3.util

class DomainCounter:
    def __init__(self):
        self.domain_counter_docs: Counter[str] = Counter()
        self.domain_counter_characters: Counter[str] = Counter()

    def add_domain(self, domain: str, text: str):
        self.domain_counter_docs[domain] += 1
        self.domain_counter_characters[domain] += len(text)

    def add_url(self, url: str, text: str):
        parsed_url = urllib3.util.parse_url(url)
        if parsed_url.host is not None:
            self.add_domain(parsed_url.host, text)

    def counts(self) -> Iterator[tuple[str, int, int]]:
        for domain, doc_count in self.domain_counter_docs.most_common():
            character_count = self.domain_counter_characters[domain]
            yield domain, doc_count, character_count

    def merge(self, other: "DomainCounter") -> None:
        for domain, doc_count, character_count in other.counts():
            self.domain_counter_docs[domain] += doc_count
            self.domain_counter_characters[domain] += character_count

class DomainCountSpec(msgspec.Struct):
    domain: str
    count_docs: int
    count_characters: int

    def to_domaincounter(self) -> DomainCounter:
        counter = DomainCounter()
        counter.domain_counter_docs[self.domain] = self.count_docs
        counter.domain_counter_characters[self.domain] = self.count_characters
        return counter

    @classmethod
    def from_domaincounter(cls, counter: DomainCounter) -> Iterator["DomainCountSpec"]:
        for domain, doc_count, character_count in counter.counts():
            yield DomainCountSpec(domain=domain, count_docs=doc_count, count_characters=character_count)

class DomainCountProcessor(BaseParallelProcessor):
    @classmethod
    def increment_progressbar(  # type: ignore
        cls,
        queue: QueueType,  # queue must be the first argument, and it should be a positional-only argument
        /,
        files: int = 0,
        documents: int = 0,
    ) -> Dict[str, int]:
        """We override this method to specify which units we want to keep track of in a progress bar.
        Specifically, we keep track of files and documents in this example. Their default value must be zero."""

        # we call the super method to increment the progress bar
        return super().increment_progressbar(queue, files=files, documents=documents)

    @classmethod
    def process_single(
        cls,
        source_path: str,
        destination_path: str,
        queue: QueueType,
        **kwargs: Any,
    ):
        # instantiate a decoder for faster decoding
        decoder = Decoder(InputSpecWithMetadata)

        # interval at which to update the progress bar; will double if queue is too full
        update_interval = 1

        # running document count; gets reset every time we update the progress bar
        docs_cnt = 0

        domain_counter = DomainCounter()

        with smart_open.open(source_path) as f: #type: ignore
            assert isinstance(f, TextIOWrapper)
            for ln in f:
                try:
                    row = decoder.decode(ln)
                except Exception as e:
                    raise DolmaError(
                        f"Failed to decode line {ln} in {source_path}; "
                        f"are you sure {source_path} is an documents file?"
                    ) from e

                if len(row.text) > 0:
                    assert row.metadata is not None
                    url: str = row.metadata["url"]
                    domain_counter.add_url(url, row.text)

                # increment the number of documents processed so far
                docs_cnt += 1

                if docs_cnt % update_interval == 0:
                    # update the progress bar every 1000 documents to prevent
                    # buffering
                    cls.increment_progressbar(queue, documents=docs_cnt)
                    docs_cnt = 0

                    if queue.qsize() >= multiprocessing.cpu_count():
                        # double the update interval if the queue is full
                        update_interval *= 2

        with smart_open.open(destination_path, "w") as f: #type: ignore
            assert isinstance(f, TextIOWrapper)
            for domain, count_docs, count_characters in domain_counter.counts():
                domain_count = DomainCountSpec(domain=domain, count_docs=count_docs, count_characters=count_characters)
                f.write(msgspec.json.encode(domain_count).decode("utf-8") + "\n")

        # update the progress bar one last time
        cls.increment_progressbar(queue, files=1, documents=docs_cnt)


def aggregate_counts(summaries_path: str) -> DomainCounter:
    total_domain_counter = DomainCounter()

    # instantiate a decoder for faster decoding
    decoder = Decoder(DomainCountSpec)

    # iterator with nice progress bar
    it = tqdm.tqdm(list(glob_path(summaries_path)), desc="Aggregating counts", unit=" files", unit_scale=True)

    # load partial summaries and aggregate it
    for path in it:
        with smart_open.open(path, "rt") as f: #type: ignore
            assert isinstance(f, TextIOWrapper)
            for ln in f:
                domain_count_spec = decoder.decode(ln)
                domain_count = domain_count_spec.to_domaincounter()
                total_domain_counter.merge(domain_count)

    return total_domain_counter

def create_and_run_domain_counter(
    documents: List[str],
    summaries_path: Optional[str] = None,
    metadata_path: Optional[str] = None,
    report: Optional[str] = None,
    debug: bool = False,
    seed: int = 0,
    num_processes: int = 1,
    name_regex: Optional[str] = None,
):
    # create the report directory if it doesn't exist
    if report:
        mkdir_p(report)

    with ExitStack() as stack:
        # use temporary directories if no paths are provided
        summaries_path = summaries_path or stack.enter_context(TemporaryDirectory())
        metadata_path = metadata_path or stack.enter_context(TemporaryDirectory())

        # make sure these locations exist
        mkdir_p(summaries_path)
        mkdir_p(metadata_path)

        try:
            domain_counter = DomainCountProcessor(
                source_prefix=documents,
                destination_prefix=summaries_path,
                metadata_prefix=metadata_path,
                debug=debug,
                seed=seed,
                ignore_existing=True,
                retries_on_error=0,
                num_processes=num_processes,
            )
            domain_counter(name_regex=name_regex)

            total_count = aggregate_counts(summaries_path=summaries_path)
            write_output(
                counters=DomainCountSpec.from_domaincounter(total_count),
                report=report
            )

        finally:
            shutil.rmtree(summaries_path)
            shutil.rmtree(metadata_path)

def write_output(counters: Iterator[DomainCountSpec], report: Optional[str] = None):
    if report is None:
        return

    mkdir_p(report)
    with smart_open.open(f"{report}/summaries.jsonl.gz", "w") as f: #type: ignore
        for counter in counters:
            assert isinstance(f, TextIOWrapper)
            f.write(msgspec.json.encode(counter).decode("utf-8") + "\n")

def main(documents: List[str], report: str, num_processes: int=8, regex: Optional[str]=None) -> None:
    logger = get_logger("analyzer")

    # perform some path validation to make sure we don't call the mixer with invalid config
    total_matching_documents = 0
    for document in documents:
        current_matching_documents = sum(1 for _ in glob_path(document))
        if current_matching_documents == 0:
            # only raise a warning if no documents are found for a single path
            logger.warning("No documents found for path %s", document)
        total_matching_documents += current_matching_documents

    if total_matching_documents == 0:
        # but raise an error if no documents are found for all paths
        raise DolmaConfigError(f"No documents found for paths {documents}.")

    create_and_run_domain_counter(
        documents=documents,
        report=report,
        num_processes=num_processes,
        name_regex=regex,
    )

if __name__ == "__main__":
    documents = sys.argv[1:-1]
    report = sys.argv[-1]

    main(documents, report)
