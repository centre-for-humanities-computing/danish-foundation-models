"""
Danish of a simple Profanity filter

Authors:
    Jens Dahl Møllerhøj
"""

from typing import Iterable

class ProfanityFilter:
    """
    Danish implementation of a profanity filter.
    """
    def __init__(self):
        self.danish_pornograpic_words = [
            "anal",
            "anus",
            "røv",
            "æsler",
            "røvhul",
            "røvhuller",
            "dyrisk",
            "bestialitet",
            "tæve",
            "tæver",
            "blodig",
            "blowjob",
            "bryster",
            "sprække",
            "klitoris",
            "lort",
            "kusse",
            "dildo",
            "dildoer",
            "ejakulere",
            "ejakulerede",
            "ejakulerer",
            "sædafgang",
            "ejakulation",
            "svans",
            "fanden",
            "fucked",
            "fucker",
            "skide",
            "forbandede",
            "pokkers",
            "helvede",
            "hore",
            "liderlig",
            "skamlæber",
            "begær",
            "masochist",
            "onanere",
            "nigger",
            "niggere",
            "orgasme",
            "orgasmer",
            "pecker",
            "penis",
            "pis",
            "pisser",
            "pisses",
            "pisse af",
            "porno",
            "pornografi",
            "pik",
            "fisse",
            "voldtage",
            "voldtægt"
            "endetarm",
            "sadist",
            "sæd",
            "skider",
            "lorte",
            "tøs",
            "sjofelheder",
            "testikel",
            "vagina",
            "viagra",
            "vulva",
            "luder",
            "x-bedømt",
            "xxx"]

    def __call__(self, docs: Iterable[str]) -> Generator:
        """Applies profanity filter
        """

        # normalize

        # count occurrences of known profanities in document

        # flag document based on heuristic

        # print possible violating documents

        return docs

