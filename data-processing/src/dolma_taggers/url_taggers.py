from collections import defaultdict
import hashlib
import io
from pathlib import Path
import requests
import re
import tarfile
from urllib.parse import urlparse
from trieregex import TrieRegEx

from dolma.core.registry import TaggerRegistry
from dolma.core.taggers import BaseTaggerWithMetadata
from dolma.core.data_types import DocResult, DocumentWithMetadata, Span


class Ut1URLClassifier:
    def __init__(self, data_dir: Path=Path("data_url_ut1")):
        self.data_dir = data_dir
        self.md5_to_domains, self.md5_to_categories = self._build_ut1lists()

        self.md5_to_re: dict[str, re.Pattern[str]] = {}
        for md5, domains in self.md5_to_domains.items():
            tre = TrieRegEx(*domains)
            regex: re.Pattern[str] = re.compile(tre.regex()) # type:ignore
            self.md5_to_re[md5] = regex

    def _build_ut1lists(self) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
        md5_url = "https://dsi.ut-capitole.fr/blacklists/download/MD5SUM.LST"

        # List of files in MD5SUM.LST that should not be downloaded
        ignore_files = [
            "exceptions_liste_bu.tar.gz", # Does not exist
            "good.tar.gz", # Does not exist
            "blacklists.tar.gz", # Contains all the lists again
            "jstor.tar.gz",
        ]
        Path.mkdir(self.data_dir, parents=True, exist_ok=True)

        # Download list of archives
        if not Path.exists(self.data_dir / "md5sum.lst"):
            response = requests.get(md5_url)
            if response.status_code == requests.codes.ok:
                with open(self.data_dir / "md5sum.lst", "wb") as f:
                    f.write(response.content)
            else:
                raise RuntimeError("Failed to download %s" % md5_url)

        # Open list and build dictionary of md5sum -> list of filenames
        # Some files have multiple aliases, so they will have the same md5sum
        domain_files: defaultdict[str, list[str]] = defaultdict(list)
        with open(self.data_dir / "md5sum.lst", "r") as f:
            for line in f:
                md5sum, filename = line.strip().split()
                if filename.endswith(".tar.gz"):
                    if not (filename.startswith("README") or filename.startswith("LICENSE")):
                        if not filename in ignore_files:
                            domain_files[md5sum].append(filename)

        # Download all files
        domain_sets: dict[str, set[str]] = dict()
        for md5sum, filenames in domain_files.items():
            url=f"https://dsi.ut-capitole.fr/blacklists/download/{filenames[0]}"
            output_path = self.data_dir / filenames[0]
            # Only download the file if it does not already exist
            if not Path.exists(output_path):
                response = requests.get(url)
                if response.status_code == requests.codes.ok:
                    with open(output_path, "wb") as f:
                        f.write(response.content)
                else:
                    raise RuntimeError("Failed to download %s" % url)

            # Check the md5sum of the downloaded file
            with open(output_path, "rb") as f:
                md5sum_dl = hashlib.file_digest(f, "md5")
            assert md5sum==md5sum_dl.hexdigest(), "The downloaded content md5sum must match the expected md5sum"

            # Read the domain lists from the downloaded file
            domain_names: set[str] = set()
            with tarfile.open(output_path, "r") as tarf:
                for member in tarf.getmembers():
                    if Path(member.name).name.startswith("domain"):
                        byte_reader = tarf.extractfile(member)
                        assert byte_reader is not None
                        textreader = io.TextIOWrapper(byte_reader, encoding="utf-8")
                        domain_names = domain_names.union(set(l.strip() for l in textreader))

            domain_sets[md5sum] = domain_names

        categories = {md5sum: set(fn.replace(".tar.gz", "") for fn in fname) for md5sum, fname in domain_files.items()}

        # Drop categories with 1 domain or less
        md5_to_delete: list[str] = []
        for md5sum, domain in domain_sets.items():
            if len(domain) < 2:
                md5_to_delete.append(md5sum)
        for key in md5_to_delete:
            del categories[key]
            del domain_sets[key]

        return domain_sets, categories

    def classify_url(self, url: str) -> list[str]:
        return self.classify_url_trie(url)

    def classify_url_naive(self, url:str) -> list[str]:
        """Classify url by looping through all domains in
        the ban lists and see if they match part of the url.
        This is very slow."""
        cats: list[str] = []
        for md5sum, domains in self.md5_to_domains.items():
            for dom in domains:
                if dom in url:
                    cats.extend(self.md5_to_categories[md5sum])
                    break
        return cats

    def classify_url_parse_domain(self, url:str) -> list[str]:
        """Classify url by first extracting the domain from url
        and check if the extracted domain exists in the ban list.
        This method does not always work, because the domain can
        be parsed differently. The scheme part, i.e. http:// must
        be part of the url for this parser to work."""
        parse_res = urlparse(url)
        url_dom = parse_res.netloc

        cats: list[str] = []
        for md5sum, domains in self.md5_to_domains.items():
            if url_dom in domains:
                cats.extend(self.md5_to_categories[md5sum])
        return cats

    def classify_url_trie(self, url:str) -> list[str]:
        """Classify url by checking if any of the domains
        in the ban lists can be found as a substring of the url.
        This is similar to the naive approach, but uses an efficient
        regex implementation."""
        cats: list[str] = []
        for md5sum, regex in self.md5_to_re.items():
            if regex.search(url):
                cats.extend(self.md5_to_categories[md5sum])
        return cats

@TaggerRegistry.add("ut1_url_banlist_tagger_v1")
class Ut1UrlBanlistTagger(BaseTaggerWithMetadata):
    """This tagger tags documents if they are on one of the UT1 URL banlists.
    The url is expected to be in metadata["url"].
    """
    def __init__(self):
        super().__init__()
        self.classifier = Ut1URLClassifier()

    def predict(self, doc: DocumentWithMetadata) -> DocResult:
        url = doc.metadata.get("url", None)
        spans: list[Span] = []
        if url is None:
            url = doc.metadata.get("URL", None)
        if url is not None:
            categories = self.classifier.classify_url(url)
            for cat in categories:
                positive_span = Span(
                    start=0,
                    end=len(doc.text),
                    type=f"{cat}",
                    score=1.0
                )
                spans.append(positive_span)

        return DocResult(doc=doc, spans=spans)


if __name__ == "__main__":
    import time
    url_classifier = Ut1URLClassifier()
    urls: list[str] = []
    with open("all_urls.txt", "r") as f:
        for line in f:
            urls.append(line.strip())
    #urls = urls[0:100]
    #start = time.time()
    #for url in urls:
    #    print(url)
    #    cats1 = url_classifier.classify_url_naive(url)
    #    cats2 = url_classifier.classify_url_parse_domain(url)
    #    cats3 = url_classifier.classify_url_trie(url)
    #    print("c1", cats1)
    #    print("c2", cats2)
    #    print("c3", cats3)
    #end = time.time()
    #print("classified %d urls in %f seconds" % (len(urls), end-start))
    #
    #start = time.time()
    #for url in urls:
    #    cats1 = url_classifier.classify_url_naive(url)
    #end = time.time()
    #print("naive classified %d urls in %f seconds" % (len(urls), end-start))

    start = time.time()
    for url in urls:
        cats2 = url_classifier.classify_url_parse_domain(url)
    end = time.time()
    print("domain parse classified %d urls in %f seconds" % (len(urls), end-start))

    start = time.time()
    for url in urls:
        cats3 = url_classifier.classify_url_trie(url)
    end = time.time()
    print("with trie classified %d urls in %f seconds" % (len(urls), end-start))
