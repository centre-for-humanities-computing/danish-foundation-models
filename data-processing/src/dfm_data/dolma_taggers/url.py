"""
Url taggers

This module expands upon the collection of default dolma URL taggers
"""

import os
from pathlib import Path

from dolma.taggers.url import BaseDomainTagger
from dolma.core.registry import TaggerRegistry

def create_domain_blocklist_tagger(blocklist_path: Path) -> type[BaseDomainTagger]:
    """Dynamically create taggers based on custom domain blocklist files specified in environment variable
    The enironment variable is DOLMA_URL_CUSTOM_BLOCKLIST_PATH and is a comma-separated list of files.
    Each file will spawn one tagger with the name custom_domain_blocklist_{path.stem}_v1
    so it is important that each list of domains have different stem (filename)."""

    class_name = f"CustomDomainBlocklistTagger{blocklist_path.stem}"
    tagger_name = f"custom_domain_blocklist_{blocklist_path.stem}_v1"

    # Build the class dynamically
    cls = type(
        class_name,
        (BaseDomainTagger, ),
        {
            "BLOCKLIST_PATHS": [str(blocklist_path)]
        },
    )
    # Add the class decorator explcitly to add the tagger to the registry
    cls = TaggerRegistry.add(tagger_name)(cls)
    return cls


tagger_paths = os.environ.get("DOLMA_URL_CUSTOM_BLOCKLIST_PATH")

if tagger_paths is not None:
    for path in tagger_paths.split(","):
        create_domain_blocklist_tagger(Path(path))

@TaggerRegistry.add("adult_tld_v1")
class AdultTldTagger(BaseDomainTagger):
    BLOCKLIST_PATHS = []
    ADULT_TLD = (
        ".adult",
        ".porn",
        ".sex",
        ".sexy",
        ".xxx",
        )
    def __init__(self) -> None:
        pass

    def check_url(self, url: str) -> bool:
        return url.endswith(self.ADULT_TLD)

@TaggerRegistry.add("adult_domain_pattern_v1")
class AdultDomainPatternTagger(BaseDomainTagger):
    BLOCKLIST_PATHS = []
    ALLOWLIST_TLD = (
        ".dk",
        ".se",
        ".is",
        ".no",
        ".org",
        )
    WORD_BANLIST = (
        'bbw',
        'beauties',
        'butt',
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
    def __init__(self) -> None:
        pass

    def check_url(self, url: str) -> bool:
        if url.endswith(self.ALLOWLIST_TLD):
            return False
        else:
            for word in self.WORD_BANLIST:
                if word in url:
                    return True

        return False

