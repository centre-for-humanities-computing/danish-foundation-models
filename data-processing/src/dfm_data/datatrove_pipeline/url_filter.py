import itertools
import re
import os
import smart_open
import socket
from typing import Generator, Optional

from huggingface_hub import cached_assets_path
from loguru import logger

from datatrove.data import Document
from datatrove.io import safely_create_file

from datatrove.pipeline.writers.disk_base import DiskWriter
from datatrove.pipeline.filters.base_filter import BaseFilter

SOFT_DOMAIN_WORD_BANLIST_EXTRA = (
        'bbw',
        'beauties',
        'butt',
        'cock',
        'cum',
        'cuties',
        'fap',
        'fuck',
        'gay',
        'granny',
        'horny',
        'jerk',
        'jizz',
        'mature',
        'moms',
        'porn',
        'pussy',
        'sex',
        'shemale',
        'spicytranny',
        'tits',
        'tube',
        'xvideos',
        'xxx',
)

class AdultTldFilter(BaseFilter):
    """
    Filter documents based on URL TLDs
    """
    name = "😈 AdultTLD filter"
    DEFAULT_ADULT_TLD = (
        "xxx",
        "adult",
        "sex",
        "porn",
        "sexy",
        "dating",
        "cam",
        "tube",
        "chat",
    )
    _requires_dependencies = ["tldextract", "fasteners"]

    def __init__(
        self,
        adult_tld: Optional[tuple[str]] = None,
        exclusion_writer: Optional[DiskWriter] = None,
        ) -> None:
        super().__init__(exclusion_writer)

        from tldextract import TLDExtract

        if adult_tld is not None:
            self.adult_tld = adult_tld
        else:
            self.adult_tld = self.DEFAULT_ADULT_TLD

        self.tldextractor = TLDExtract()

    def check_url(self, url: str) -> bool:

        return url.endswith(self.adult_tld)

    def filter(self, doc: Document) -> bool | tuple[bool, str]:
        url = doc.metadata.get("url")

        assert url, "Document does not have url in its metadata"
        assert isinstance(url, str), "url metadata is not a string"
        url_info = self.tldextractor(url)

        if url_info.suffix in self.adult_tld:
            return False, "adult_tld"

        return True

DOLMA_DOMAIN_BLOCKLIST_PATHS = {
    "domain_blocklist_utp_v1": ["https://dolma-artifacts.org/blocklist_utp/blocklist_utp-20240205/adult/domains"],
    "link_blocklist_phishing_v1": [ "https://dolma-artifacts.org/blocklist_phishing_db/blocklist_phishing_db-20240205/domains.txt.gz" ],
    "domain_blocklist_phishing_v1": ["https://dolma-artifacts.org/blocklist_phishing_db/blocklist_phishing_db-20240205/domains.txt.gz"],
    "blocklist_project_nsfw_v1": ["https://dolma-artifacts.org/blocklist_project/blocklist_project-20240207/porn.txt"],
    "blocklist_project_social_v1": [
        "https://dolma-artifacts.org/blocklist_project/blocklist_project-20240207/facebook.txt",
        "https://dolma-artifacts.org/blocklist_project/blocklist_project-20240207/fortnite.txt",
        "https://dolma-artifacts.org/blocklist_project/blocklist_project-20240207/tiktok.txt",
        "https://dolma-artifacts.org/blocklist_project/blocklist_project-20240207/twitter.txt",
        "https://dolma-artifacts.org/blocklist_project/blocklist_project-20240207/whatsapp.txt",
        "https://dolma-artifacts.org/blocklist_project/blocklist_project-20240207/youtube.txt",
    ],
    "blocklist_project_crime_v1": [
        "https://dolma-artifacts.org/blocklist_project/blocklist_project-20240207/abuse.txt",
        "https://dolma-artifacts.org/blocklist_project/blocklist_project-20240207/fraud.txt",
        "https://dolma-artifacts.org/blocklist_project/blocklist_project-20240207/malware.txt",
        "https://dolma-artifacts.org/blocklist_project/blocklist_project-20240207/phishing.txt",
        "https://dolma-artifacts.org/blocklist_project/blocklist_project-20240207/piracy.txt",
        "https://dolma-artifacts.org/blocklist_project/blocklist_project-20240207/ransomware.txt",
        "https://dolma-artifacts.org/blocklist_project/blocklist_project-20240207/scam.txt",
        "https://dolma-artifacts.org/blocklist_project/blocklist_project-20240207/redirect.txt",
    ],
    "blocklist_project_vice_v1": [
        "https://dolma-artifacts.org/blocklist_project/blocklist_project-20240207/crypto.txt",
        "https://dolma-artifacts.org/blocklist_project/blocklist_project-20240207/drugs.txt",
        "https://dolma-artifacts.org/blocklist_project/blocklist_project-20240207/gambling.txt",
        "https://dolma-artifacts.org/blocklist_project/blocklist_project-20240207/vaping.txt",
    ],
    "blocklist_project_ads_v1": [
        "https://dolma-artifacts.org/blocklist_project/blocklist_project-20240207/adobe.txt",
        "https://dolma-artifacts.org/blocklist_project/blocklist_project-20240207/ads.txt",
        "https://dolma-artifacts.org/blocklist_project/blocklist_project-20240207/basic.txt",
        "https://dolma-artifacts.org/blocklist_project/blocklist_project-20240207/smart-tv.txt",
        "https://dolma-artifacts.org/blocklist_project/blocklist_project-20240207/tracking.txt",
    ],
    "blocklist_firebog_ads_v1": [
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/ads/blue/hosts.txt",
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/ads/green/AdguardDNS.txt",
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/ads/green/Admiral.txt",
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/ads/green/adservers.txt",
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/ads/green/Easylist-2.txt",
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/ads/green/hosts-2.txt",
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/ads/green/hosts-3.txt",
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/ads/green/hosts.txt",
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/ads/green/serverlist.txt",
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/ads/green/simple_ad.txt",
    ],
    "blocklist_firebog_crypto_v1": [
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/crypto/green/hosts_browser.txt",
    ],
    "blocklist_firebog_malicious_v1": [
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/malicious/blue/phishing-filter-hosts.txt",
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/malicious/blue/Prigent-Malware.txt",
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/malicious/green/AntiMalwareHosts.txt",
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/malicious/green/hostfile.txt",
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/malicious/green/hosts-2.txt",
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/malicious/green/hosts.txt",
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/malicious/green/latestdomains.txt",
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/malicious/green/main-blacklist.txt",
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/malicious/green/Mandiant_APT1_Report_Appendix_D.txt",
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/malicious/green/notrack-malware.txt",
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/malicious/green/phishing_army_blocklist_extended.txt",
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/malicious/green/Prigent-Crypto.txt",
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/malicious/green/RPiList-Malware.txt",
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/malicious/green/RPiList-Phishing.txt",
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/malicious/green/simple_malvertising.txt",
    ],
    "blocklist_firebog_nsfw_v1": [
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/nsfw/blue/pi_blocklist_porn_top1m.list.txt",
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/nsfw/blue/Prigent-Adult.txt",
    ],
    "blocklist_firebog_social_v1": [
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/social/blue/facebook.txt",
    ],
    "blocklist_firebog_suspicious_v1": [
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/suspicious/blue/hosts-2.txt",
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/suspicious/blue/hosts-3.txt",
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/suspicious/blue/hosts-4.txt",
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/suspicious/blue/hosts-file.txt",
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/suspicious/blue/neohostsbasic.txt",
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/suspicious/blue/SNAFU.txt",
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/suspicious/blue/spammers.txt",
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/suspicious/green/hosts.txt",
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/suspicious/green/KADhosts.txt",
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/suspicious/green/w3kbl.txt",
    ],
    "blocklist_firebog_trackers_v1": [
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/trackers/blue/ads-and-tracking-extended.txt",
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/trackers/blue/AmazonFireTV.txt",
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/trackers/blue/android-tracking.txt",
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/trackers/blue/notrack-blocklist.txt",
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/trackers/blue/SmartTV.txt",
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/trackers/green/Easyprivacy.txt",
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/trackers/green/firstparty-trackers-hosts.txt",
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/trackers/green/hosts.txt",
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/trackers/green/Prigent-Ads.txt",
        "https://dolma-artifacts.org/blocklist_firebog/blocklist_firebog-20240208/trackers/green/spy.txt",
    ],
    "blocklist_hosts_adware_malware_v1": ["https://dolma-artifacts.org/blocklist_hosts/blocklist_hosts-20240208/adware_malware.txt"],
    "blocklist_hosts_fakenews_v1": ["https://dolma-artifacts.org/blocklist_hosts/blocklist_hosts-20240208/fakenews.txt"],
    "blocklist_hosts_gambling_v1": ["https://dolma-artifacts.org/blocklist_hosts/blocklist_hosts-20240208/gambling.txt"],
    "blocklist_hosts_porn_v1": ["https://dolma-artifacts.org/blocklist_hosts/blocklist_hosts-20240208/porn.txt"],
    "blocklist_hosts_social_v1": ["https://dolma-artifacts.org/blocklist_hosts/blocklist_hosts-20240208/social.txt"],
}

DOLMA_ABP_BLOCKLIST_PATHS = {
    "oisd_small_abp_v1": ["https://dolma-artifacts.org/blocklist_oisd/blocklist_oisd-20240205/oisd_small_abp.txt.gz"],
    "oisd_big_abp_v1": ["https://dolma-artifacts.org/blocklist_oisd/blocklist_oisd-20240205/oisd_big_abp.txt.gz"],
    "oisd_nsfw_abp_v1": ["https://dolma-artifacts.org/blocklist_oisd/blocklist_oisd-20240205/oisd_nsfw_abp.txt.gz"],
    "brave_core_abp_v1": [
        "https://dolma-artifacts.org/blocklist_brave/blocklist_brave-20240206/brave_ad_block_first_party_filters.txt",
        "https://dolma-artifacts.org/blocklist_brave/blocklist_brave-20240206/brave_ad_block_updater.txt",
    ],
    "brave_nsfw_abp_v1": ["https://dolma-artifacts.org/blocklist_brave/blocklist_brave-20240206/blocklists_anti_porn.txt"],
}

def check_ipv6(n):
    """
    Check if the given string represents a valid IPv6 address.

    Args:
        n (str): The string to be checked.

    Returns:
        bool: True if the string represents a valid IPv6 address, False otherwise.
    """
    try:
        socket.inet_pton(socket.AF_INET6, n)
        return True
    except socket.error:
        return False


def check_ipv4(n):
    """
    Check if the given string represents a valid IPv4 address.

    Args:
        n (str): The string to be checked.

    Returns:
        bool: True if the string represents a valid IPv4 address, False otherwise.
    """
    try:
        socket.inet_pton(socket.AF_INET, n)
        return True
    except socket.error:
        return False

class UrlNotParsedError(ValueError):
    pass

class DolmaDomainFilter(BaseFilter):
    """
    Implements URL filtering rules from Dolma
    """
    name = "😈 Dolma Domain filter"
    _requires_dependencies = ["dolma", "urllib3"]

    URL_METADATA_KEY = "url"
    MAYBE_IP_REGEX = re.compile(r"([0-9a-f\.\:]+)")
    IGNORE_IP_REGEX = re.compile(r"(127\.0\.0\.1|0\.0\.0\.0|::1)")
    IGNORE_IP_REGEX_START = re.compile(r"^{IGNORE_IP_REGEX.pattern}")
    URL_REGEX = re.compile(r"(([a-z0-9\-_]+\.?){2,}|localhost|localdomain)")
    ONLY_URL_REGEX = re.compile(f"^{URL_REGEX.pattern}")
    ADP_FORMAT_REGEX = re.compile(f"\\|+{URL_REGEX.pattern}\\^")
    MAYBE_IP_AND_URL_REGEX = re.compile(f"{MAYBE_IP_REGEX.pattern}\\s+{URL_REGEX.pattern}")

    def __init__(
        self,
        blocklist_paths: Optional[list[str]] = None,
        exclusion_writer: Optional[DiskWriter] = None,
    ) -> None:
        super().__init__(exclusion_writer)

        import urllib3.util
        self.parse_url = urllib3.util.parse_url
        self.blocklist: set[str] = set()
        self._downloaded = False

        if blocklist_paths:
            self.blocklist_paths = blocklist_paths
        else:
            self.blocklist_paths = itertools.chain(*DOLMA_DOMAIN_BLOCKLIST_PATHS.values())

    def parse_line(self, ln: str) -> Generator[str, None, None]:
        if not (ln := ln.strip().lower()) or ln.startswith("#") or ln.startswith(";") or ln.startswith("!"):
            # either empty or a comment
            return
        if expr := self.MAYBE_IP_AND_URL_REGEX.match(ln):
            # the line contains both an IP and a URL; we yield both
            maybe_ipv6_or_ipv4 = expr.group(1)
            url = expr.group(2)

            # further check if the IP is valid
            if not check_ipv6(maybe_ipv6_or_ipv4) and not check_ipv4(maybe_ipv6_or_ipv4):
                raise UrlNotParsedError(f"Invalid IP: {maybe_ipv6_or_ipv4}")

            if not self.IGNORE_IP_REGEX_START.match(maybe_ipv6_or_ipv4):
                # do not yield the IP if it a localhost
                yield maybe_ipv6_or_ipv4

            if url != "localhost" and url != "localdomain":
                # do not yield the URL if it is a localhost
                yield from self.clean_url_base(url)
        elif expr := self.ONLY_URL_REGEX.match(ln):
            # the line contains only a URL; we yield it
            yield from self.clean_url_base(ln)
        elif expr := self.ADP_FORMAT_REGEX.match(ln):
            # this is in case we need to deal with data with ADP format
            yield expr.group(1)
        else:
            raise UrlNotParsedError(f"Invalid line: {ln}")

    def download_data(self) -> None:
        if self._downloaded:
            return
        import dolma.core.paths
        download_dir = cached_assets_path(library_name="dfm_data", namespace="datatrove_pipeline", subfolder="dolma_domain_filter")

        for path in self.blocklist_paths:
            fname = dolma.core.paths.resource_to_filename(path)
            file_to_lock = os.path.join(download_dir, fname)

            def get_file():
                import smart_open
                logger.info(f"Downloading {path} to {file_to_lock}")
                with smart_open.open(path, "rb") as src, smart_open.open(file_to_lock, "wb") as dest:
                    dest.write(src.read())

            safely_create_file(file_to_lock, get_file)

            with smart_open.open(file_to_lock, "r") as blocklist_file:
                for i, ln in enumerate(blocklist_file):
                    try:
                        for url in self.parse_line(ln):
                            self.blocklist.add(url)
                    except UrlNotParsedError:
                        message = f"Invalid line {i} in {path}: '{ln}'"
                        logger.info(message)

        assert len(self.blocklist) > 0, f"Blocklist is empty for {self.__class__.__name__} tagger"

        self._downloaded = True
        logger.info(f"Total number of blocked domains {len(self.blocklist)}")

    def clean_url_base(self, url: Optional[str]) -> Generator[str, None, None]:
        """Remove query parameters and protocol from a URL."""
        if url is None or not url.strip():
            return
        # remove non-printable characters
        if not url.isprintable():
            url = "".join(c for c in url if c.isprintable())

        try:
            parsed = self.parse_url(url)
        except Exception as e:
            message = f"Failed to parse url: {url}"
            logger.info(message)
            return

        yield f"{parsed.host}{(f':{parsed.port}') if parsed.port else ''}{parsed.path or ''}".rstrip("/").lower()

    def clean_url_domain(self, url: Optional[str]) -> Generator[str, None, None]:
        if url is None or not url.strip():
            return

        for url in self.clean_url_base(url):
            hostname = self.parse_url(url).host
            if not hostname:
                return
            yield (hostname := hostname.lstrip("www."))
            yield f"www.{hostname}"

    def filter(self, doc: Document) -> bool | tuple[bool, str]:
        self.download_data()
        url = doc.metadata.get("url")

        assert url, "Document does not have url in its metadata"
        assert isinstance(url, str), "url is not a string"

        for cleaned_url in self.clean_url_domain(url):
            if cleaned_url in self.blocklist:
                return False, "dolma_domain_filter"

        return True

class DolmaAdbFilter(DolmaDomainFilter):
    """
    Implements ABP URL filtering rules from Dolma
    """
    name = "😈 Dolma ABP URL filter"

    def __init__(
        self,
        exclusion_writer: Optional[DiskWriter] = None,
    ) -> None:
        super().__init__(
            blocklist_paths=list(itertools.chain(*DOLMA_ABP_BLOCKLIST_PATHS.values())),
            exclusion_writer=exclusion_writer,
        )

        self.engine = None

    def download_data(self) -> None:
        import dolma.core.paths
        from dolma.core.url_blocker import UrlBlocker

        if self._downloaded:
            return
        download_dir = cached_assets_path(library_name="dfm_data", namespace="datatrove_pipeline", subfolder="dolma_domain_filter")

        dest_files: list[str] = []
        for path in self.blocklist_paths:
            fname = dolma.core.paths.resource_to_filename(path)
            file_to_lock = os.path.join(download_dir, fname)

            def get_file():
                import smart_open
                logger.info(f"Downloading {path} to {file_to_lock}")
                with smart_open.open(path, "rb") as src, smart_open.open(file_to_lock, "wb") as dest:
                    dest.write(src.read())

            safely_create_file(file_to_lock, get_file)
            dest_files.append(file_to_lock)

        self.engine = UrlBlocker.from_adb_paths(*dest_files)
        self._downloaded = True

    def filter(self, doc: Document) -> bool | tuple[bool, str]:
        self.download_data()
        url = doc.metadata.get("url")

        assert url, "Document does not have url in its metadata"
        assert isinstance(url, str), "url is not a string"

        for cleaned_url in self.clean_url_base(url):
            assert self.engine is not None
            if self.engine.check_network_urls(cleaned_url):
                return False, "dolma_adb_filter"

        return True

