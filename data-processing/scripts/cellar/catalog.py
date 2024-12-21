"""
Pull a list of publications from the European Union Publications Office.
"""
import collections
import datetime
import json
import logging
import re
import sys
from pathlib import Path
from string import Template
from typing import Any

import requests
from typer import Typer

APP = Typer(name="Cellar CLI")


def parse_response(content: bytes):
    """
    Parses the JSON response from the European Union Publications Office API.

    Args:
        content: The raw JSON response from the API.

    Yields:
        dict: A dictionary containing information about each publication.
    """
    for row in json.loads(content)["results"]["bindings"]:
        # Split the langs, types, and titles by semicolons
        data = {k: v["value"] for k, v in row.items()}
        langs = data["langs"].split(";")
        types = data["types"]
        titles = data["titles"]

        pattern = "^" + ";".join([f"{lang}:(?P<{lang}>.*)" for lang in langs]) + "$"
        titles = re.match(pattern, titles, re.DOTALL).groupdict()
        titles = {k: v.strip() for k, v in titles.items()}

        types = collections.defaultdict(list)
        for spec in data["types"].split(";"):
            lang, mtype = spec.split(":")
            types[lang].append(mtype)

        subjects = [
            subj for subject in data["subjects"].split(";") if (subj := subject.strip())
        ]

        for lang in langs:
            ret = {
                "language": lang,
                "title": titles[lang],
                "type": types[lang],
                "subjects": subjects,
                "work": data["work"],
                "timestamp": data["timestamp"],
            }
            yield ret


def sparql_query(
    start: str,
    stop: str,
    query: Template,
) -> bytes | Any | None:
    """
    Execute a SPARQL query on the European Union Publications Office API.

    Args:
        start: The starting date for the query.
        stop: The ending date for the query.
        query: A template string containing the SPARQL query.

    Returns:
        bytes | Any | None: The response content if the query is successful, otherwise None.
    """
    logging.info(f"querying {start}-{stop}")
    params = {"query": query.substitute(start=start, stop=stop)}
    headers = {"accept": "application/json"}
    resp = requests.get(
        "http://publications.europa.eu/webapi/rdf/sparql",
        params=params,
        headers=headers,
    )
    if resp.status_code == 200:
        return resp.content

    logging.warning(f"Query failed {resp.status_code}")
    return None


@APP.command(
    name="fetch_cellar",
    help="Fetch publications from the European Union Publications Office.",
)
def main(
    output_file: Path,
    query_template: Path,
    start_date: datetime.datetime = "2016-07-21",
    end_date: datetime.datetime = "2024-12-31",
    delta: int = 5,
):
    """
    Fetch publications from the European Union Publications Office API and write them to an output file.

    Args:
        output_file: The path to the output file where the publications will be written.
        query_template: The path to a template file containing the SPARQL query.
        start_date (optional): The starting date for the query. Defaults to "2016-07-21".
        end_date (optional): The ending date for the query. Defaults to "2024-12-31".
        delta (optional): The number of days between each query. Defaults to 5.
    """
    delta = datetime.timedelta(delta)
    with query_template.open() as handle:
        query = Template(handle.read())

    lb = start_date

    logging.basicConfig(level=logging.INFO)
    with output_file.open("w") as f:
        while lb < end_date:
            ub = min(lb + delta, end_date)
            result = sparql_query(lb.isoformat(), ub.isoformat(), query)
            if not result:
                lb = ub
                continue
            for doc in parse_response(result):
                f.write(json.dumps(doc, ensure_ascii=False) + "\n")
            lb = ub


if __name__ == "__main__":
    APP()
