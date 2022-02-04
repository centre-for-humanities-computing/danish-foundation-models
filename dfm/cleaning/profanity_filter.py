"""
Danish of a simple Profanity filter

Authors:
    Jens Dahl Møllerhøj
"""

from unicodedata import normalize
from typing import Iterable
import re

class ProfanityFilter:
    """
    Danish implementation of a profanity filter.
    """
    def __init__(self):
        self.danish_swear_words = set([
            "skide",
            "forbandede",
            "pokkers",
            "æsler",
            "helvede",
        ])

        self.danish_pornograpic_words = set([
            "amatør",
            "amatører",
            "anal",
            "anus",
            "babes",
            "bdsm",
            "begær",
            "bestialitet",
            "blodig",
            "blowjob",
            "bordel",
            "bordeller",
            "bryster",
            "bøsse",
            "bøssefilm",
            "c-skål",
            "damer",
            "dating",
            "dildo",
            "dildoer",
            "dildomaskine",
            "dyrisk",
            "ejakulation",
            "ejakulere",
            "ejakulerede",
            "ejakulerer",
            "elskerinde",
            "endetarm",
            "erotik",
            "erotisk",
            "erotiske",
            "escort",
            "escortpige",
            "escortpiger",
            "escortpigerne",
            "fanden",
            "fisse",
            "fisser",
            "fræk",
            "frække",
            "frækt",
            "fucked",
            "fucker",
            "gangbang",
            "gay",
            "hardcore",
            "hentai",
            "homo",
            "hore",
            "intim",
            "intime",
            "kinky",
            "klitoris",
            "kneppe",
            "kusse",
            "kvinder",
            "latex",
            "latino",
            "lesbisk",
            "liderlig",
            "liderlige",
            "lort",
            "lorte",
            "luder",
            "masochist",
            "massage",
            "massageescort",
            "massageklinik",
            "massagen",
            "massagepige",
            "massagepiger",
            "massagepigerne",
            "milf",
            "nigger",
            "niggere",
            "nøgenbillede",
            "nøgenbilleder",
            "nøgenbillederne",
            "nøgne",
            "onanere",
            "orgasme",
            "orgasmer",
            "patter",
            "pecker",
            "penis",
            "piger",
            "pigesex",
            "pik",
            "pis",
            "pisse",
            "pisser",
            "pisses",
            "porn",
            "porno",
            "porno-casting",
            "pornofilm",
            "pornografi",
            "pornostar",
            "pornostjerne",
            "pornostjernen",
            "pornostjerner",
            "prostitueret",
            "røv",
            "røvhul",
            "røvhuller",
            "sadist",
            "samleje",
            "sex",
            "sexcam",
            "sexdating",
            "sexdatingsites",
            "sexfilm",
            "sexfoto",
            "sexhistorier",
            "sexparadis",
            "sexshop",
            "sexstillinger",
            "sexvideo",
            "sexvideoer",
            "sexvideoerne",
            "sexvideoen",
            "sexy",
            "shemale",
            "shemales",
            "sjofelhed",
            "sjofelheder",
            "sjofelhederne",
            "skamlæber",
            "skider",
            "sluger",
            "sm",
            "spanking",
            "sprække",
            "sprøjteorgasme",
            "sprøjteorgasmer",
            "sprøjteorgasmen",
            "sprøjteorgasmerne",
            "strip",
            "svans",
            "swinger",
            "swingerdating",
            "swingerklub",
            "sæd",
            "sædafgang",
            "tantra",
            "telefonsex",
            "testikel",
            "thai",
            "thaimassage",
            "thaipiger",
            "tranny",
            "tæve",
            "tæver",
            "tøs",
            "tøser",
            "urin",
            "vagina",
            "vaginaen",
            "viagra",
            "viagraen",
            "voldtage",
            "voldtager",
            "voldtægt"
            "vulva",
            "webcam",
            "webcam-chat",
            "x-bedømt",
            "xxx"])

    def __call__(self, docs: Iterable[str]) -> Iterable[str]:
        """Applies profanity filter
        """
        for raw_doc in docs:
            # normalize
            doc = raw_doc
            doc = normalize("NFKC", doc)
            doc = re.sub(r"[\.\,\:\;\!\?\(\)\[\]\{\}]", " ", doc)
            doc = re.sub(" +", " ", doc)

            # lowercase
            doc = doc.lower()

            # count occurrences of known profanities in document
            tokens = doc.split(' ')
            words = set(tokens)
            profanities = []

            for word in words:
                if word in self.danish_pornograpic_words:
                    profanities.append(word)

            percentage = (100.0 * len(profanities))/ len(tokens)

            # flag document based on heuristic
            if len(profanities) < 3:
                # yield if not filtered
                yield raw_doc
            else:
                # print possible violating documents
                print("--------------")
                print("profanities: ", profanities)
                print("percentage: ", percentage)
                if (percentage > 4):
                    print(words - self.danish_pornograpic_words)
                print("--------------")

