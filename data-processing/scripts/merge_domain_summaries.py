"""
Merge domain count summaries from multiple datasets into a single summary
"""
from io import TextIOWrapper
import sys
from typing import List

import msgspec
from msgspec.json import Decoder
import smart_open
import tqdm

from dolma_domain_count import write_output, DomainCounter, DomainCountSpec

def aggregate_counts(summaries_paths: List[str]) -> DomainCounter:
    total_domain_counter = DomainCounter()

    # instantiate a decoder for faster decoding
    decoder = Decoder(DomainCountSpec)

    # iterator with nice progress bar
    it = tqdm.tqdm(summaries_paths, desc="Aggregating counts", unit=" files", unit_scale=True)

    # load partial summaries and aggregate it
    for path in it:
        with smart_open.open(path, "rt") as f: #type: ignore
            assert isinstance(f, TextIOWrapper)
            for ln in f:
                domain_count_spec = decoder.decode(ln)
                domain_count = domain_count_spec.to_domaincounter()
                total_domain_counter.merge(domain_count)

    return total_domain_counter

def main(input_files: List[str], aggregated_output: str):
    total_counts = aggregate_counts(input_files)
    write_output(DomainCountSpec.from_domaincounter(total_counts), aggregated_output)


if __name__ == "__main__":
    reports = sys.argv[1:-1]
    aggregated_output = sys.argv[-1]

    main(reports, aggregated_output)
