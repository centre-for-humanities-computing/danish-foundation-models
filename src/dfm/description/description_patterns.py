from typing import Dict, List

from .match_counter import MatchCounter

# Terms for religions are:
# * The person-noun singular (e.g. "kristen") and conjugated
# * The adjective (e.g. kristent)
# * The religion-noun singular (e.g. "kristendom") and conjugated
religion_labelled_match_patterns = [
    {"muslim": ["muslim", "muslimen", "muslimer", "muslimerne", "muslimsk", "islam"]},
    {
        "christian": [
            "kristen",
            "kristne",
            "kristent",
            "kristendom",
            "kristendomme",
            "kristendommen",
            "kristendommene",
        ]
    },
    {
        "jew": [
            "jøde",
            "jøden",
            "jøder",
            "jøderne",
            "jødisk",
            "jødedom",
            "jødedommen",
            "jødedomme",
            "jødedommene",
        ]
    },
    {
        "buddhist": [
            "buddhist",
            "buddhisten",
            "buddhister",
            "buddhisterne",
            "buddhistisk",
            "buddhisme",
            "buddhismen",
            "buddhismer",
            "buddhismerne",
        ]
    },
    {
        "hindu": [
            "hinduist",
            "hinduisten",
            "hinduister",
            "hinduisterne",
            "hindu",
            "hinduen",
            "hinduer",
            "hinduerne",
            "hinduistisk",
            "hinduisme",
            "hinduismen",
            "hinduismer",
            "hinduismerne",
        ]
    },
    {
        "atheist": [
            "atheist",
            "atheisten",
            "atheister",
            "atheisterne",
            "atheistisk",
            "atheisme",
            "ahteismen",
            "atheismer",
            "atheismerne",
        ]
    },
]


def get_religion_patterns():
    return MatchCounter.list_of_labelled_term_lists_to_spacy_match_patterns(
        religion_labelled_match_patterns, label_prefix="rel_"
    )


occupation_labelled_match_patterns = [
    {
        "revisor": [
            "revisor",
            "revisoren",
            "revisorer",
            "revisorerne",
        ],
    },
    {
        "administrator": [
            "administrator",
            "administratoren",
            "administratorer",
            "administratorerne",
        ]
    },
    {
        "analytiker": [
            "analytiker",
            "analytikeren",
            "analytikere",
            "analytikerne",
        ]
    },
    {
        "arkitekt": [
            "arkitekt",
            "arkitekten",
            "arkitekter",
            "arkitekterne",
        ]
    },
    {
        "assistent": [
            "assistent",
            "assistenten",
            "assistenter",
            "assistenterne",
        ]
    },
    {
        "bager": [
            "bager",
            "bageren",
            "bagere",
            "bagerne",
        ]
    },
    {
        "bartender": [
            "bartender",
            "bartenderen",
            "bartendere",
            "bartenderne",
        ]
    },
    {
        "ejendomsmægler": [
            "ejendomsmægler",
            "ejendomsmægleren",
            "ejendomsmæglere",
            "ejendomsmæglerne",
        ]
    },
    {
        "tømrer": [
            "tømrer",
            "tømreren",
            "tømrere",
            "tømrerne",
        ]
    },
    {
        "kassemedarbejder": [
            "kassemedarbejder",
            "kassemedearbejderen",
            "kassemedarbejdere",
            "kassemedarbejderne",
        ]
    },
    {
        "kok": [
            "kok",
            "kokken",
            "kokke",
            "kokkene",
        ]
    },
    {
        "kemiker": [
            "kemiker",
            "kemikeren",
            "kemikere",
            "kemikerne",
        ]
    },
    {
        "chef": [
            "chef",
            "chefen",
            "chefer",
            "cheferne",
        ]
    },
    {
        "rengøringshjælp": [
            "rengøringshjælp",
            "rengøringshjælpen",
            "rengøringshjælpere",
            "rengøringshjælperne",
        ]
    },
    {
        "ekspedient": [
            "ekspedient",
            "ekspedienten",
            "ekspedienter",
            "ekspedienterne",
        ]
    },
    {
        "terapeut": [
            "terapeut",
            "terapeuten",
            "terapeuter",
            "terapeuterne",
        ]
    },
    {
        "advokat": [
            "advokat",
            "advokaten",
            "advokater",
            "advokaterne",
        ]
    },
    {
        "diætist": [
            "diætist",
            "diætisten",
            "diætister",
            "diætisterne",
        ]
    },
    {
        "læge": [
            "læge",
            "lægen",
            "læger",
            "lægerne",
        ]
    },
    {
        "chauffør": [
            "chauffør",
            "chaufføren",
            "chauffører",
            "chaufførerne",
        ]
    },
    {
        "redaktør": [
            "redaktør",
            "redatøren",
            "redaktører",
            "redaktørerne",
        ]
    },
    {
        "elektriker": [
            "elektriker",
            "elektrikeren",
            "elektrikere",
            "elektrikerne",
        ]
    },
    {
        "ingeniør": [
            "ingeniør",
            "ingeniøren",
            "ingeniører",
            "ingeniørerne",
        ]
    },
    {
        "landmand": [
            "landmand",
            "landmanden",
            "landmænd",
            "landmændene",
        ]
    },
    {
        "brandmand": [
            "brandmand",
            "brandmanden",
            "brandmænd",
            "brandmændene",
        ]
    },
    {
        "vagt": [
            "vagt",
            "vagten",
            "vagter",
            "vagterne",
        ]
    },
    {
        "frisør": [
            "frisør",
            "frisøren",
            "frisører",
            "frisørerne",
        ]
    },
    {
        "instruktør": [
            "instruktør",
            "instruktøren",
            "instruktører",
            "instruktørerne",
        ]
    },
    {
        "efterforsker": [
            "efterforsker",
            "efterforskeren",
            "efterforskere",
            "efterforskerne",
        ]
    },
    {
        "pedel": [
            "pedel",
            "pedellen",
            "pedeller",
            "pedellerne",
        ]
    },
    {
        "advokat": [
            "advokat",
            "advokaten",
            "advokater",
            "advokaterne",
        ]
    },
    {
        "biliotekar": [
            "bibliotekar",
            "bibliotekaren",
            "bibliotekarer",
            "bibliotekarerne",
        ]
    },
    {
        "mekaniker": [
            "mekaniker",
            "makanikeren",
            "mekanikere",
            "mekanikerne",
        ]
    },
    {
        "sygeplejerske": [
            "sygeplejerske",
            "sygeplersken",
            "sygeplejersker",
            "sygeplejeskerne",
        ]
    },
    {
        "politibetjent": [
            "politibetjent",
            "politibetjenten",
            "politibetjente",
            "politibetjentene",
        ]
    },
    {
        "maler": [
            "maler",
            "maleren",
            "malerne",
            "malere",
        ]
    },
    {
        "ambulanceredder": [
            "ambulanceredder",
            "ambulanceredderen",
            "ambulancereddere",
            "ambulanceredderne",
        ]
    },
    {
        "ambulancebehandler": [
            "ambulancebehandler",
            "ambulancebehandleren",
            "ambulancebehandlere",
            "ambulancebehandlerne",
        ]
    },
    {
        "patolog": [
            "patolog",
            "patologen",
            "patologer",
            "patologerne",
        ]
    },
    {
        "farmaceut": [
            "farmaceut",
            "farmaceuten",
            "farmaceuter",
            "farmaceuterne",
        ]
    },
    {
        "blikkenslager": [
            "blikkenslager",
            "blikkenslageren",
            "blikkenslagere",
            "blikkenslagerne",
        ]
    },
    {
        "programmør": [
            "programmør",
            "programmøren",
            "programmører",
            "programmørerne",
        ]
    },
    {
        "psykolog": [
            "psykolog",
            "psykologen",
            "psykologer",
            "psykologerne",
        ]
    },
    {
        "receptionist": [
            "receptionist",
            "receptionisten",
            "receptionister",
            "receptionisterne",
        ]
    },
    {
        "sekretær": [
            "sekretær",
            "sekretæren",
            "sekretærer",
            "sekretærerne",
        ]
    },
    {
        "kirurg": [
            "kirurg",
            "kirurgen",
            "kirurger",
            "kirurgerne",
        ]
    },
    {
        "skrædder": [
            "skrædder",
            "skrædderen",
            "skræddere",
            "skrædderne",
        ]
    },
    {
        "tekniker": [
            "tekniker",
            "teknikeren",
            "teknikere",
            "teknikerne",
        ]
    },
    {
        "terapeut": [
            "terapeut",
            "terapeuten",
            "terapeuter",
            "terapeuterne",
        ]
    },
    {
        "dyrlæge": [
            "dyrlæge",
            "dyrlægen",
            "dyrlæger",
            "dyrlægerne",
        ]
    },
    {
        "forfatter": [
            "forfatter",
            "forfatteren",
            "forfattere",
            "forfatterne",
        ]
    },
]


def get_occupation_patterns():
    return MatchCounter.list_of_labelled_term_lists_to_spacy_match_patterns(
        occupation_labelled_match_patterns, label_prefix="occu_"
    )


# List is a partial translation of Rae et al. 2022, p. 95
female_gendered_terms = set(
    [
        "pige",
        "pigen",
        "piger",
        "pigerne",
        "søster",
        "søsteren",
        "søstere",
        "søsterne",
        "mor",
        "moren",
        "mødre",
        "mødrene",
        "kone",
        "konen",
        "koner",
        "konerne",
        "brud",
        "bruden",
        "brude",
        "brudene",
        "dame",
        "damen",
        "damer",
        "damerne",
        "datter",
        "datteren",
        "døtre",
        "døtrene",
    ]
)


def get_female_gendered_patterns():
    return MatchCounter.term_list_to_spacy_match_patterns(
        female_gendered_terms, label="gender_female_terms"
    )


male_gendered_terms = set(
    [
        "dreng",
        "drengen",
        "drenge",
        "drengene",
        "bror",
        "broren",
        "brødre",
        "brødrene",
        "far",
        "faren",
        "fædre",
        "fædrene",
        "mand",
        "manden",
        "mænd",
        "mændene",
        "brudgom",
        "brudgommen",
        "brudgomme",
        "brudgommene",
        "herre",
        "herren",
        "herrer",
        "herrerne",
        "søn",
        "sønnen",
        "sønner",
        "sønnerne",
    ]
)


def get_male_gendered_patterns():
    return MatchCounter.term_list_to_spacy_match_patterns(
        male_gendered_terms, label="gender_male_terms"
    )


danish_adult_words = set(
    [
        "amatør",
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
        "voldtægt" "vulva",
        "webcam",
        "webcam-chat",
        "x-bedømt",
        "xxx",
    ]
)


def get_muslim_name_patterns() -> List[Dict[str, list]]:
    """Gets a list of all muslim first names in Denmark from DaCy, and converts to a list of lowercase spacy patterns.

    Returns:
        List[Dict[str, list]]: list of lowercase spacy match patterns
    """
    from dacy.datasets import muslim_names
    from dfm.description.match_counter import MatchCounter

    muslim_names_list = [name.lower() for name in muslim_names()["first_name"]]

    return MatchCounter.term_list_to_spacy_match_patterns(
        term_list=muslim_names_list, label="rel_muslim_names"
    )


def get_gender_name_patterns() -> List[Dict[str, list]]:
    """Gets a list of all gendered first names in Denmark from DaCy, and converts to a list of lowercase spacy patterns.

    Returns:
        List[Dict[str, list]]: list of lowercase spacy match patterns
    """
    from dacy.datasets import female_names, male_names
    from dfm.description.match_counter import MatchCounter

    female_names_list = [name.lower() for name in female_names()["first_name"]]
    female_names_patterns = MatchCounter.term_list_to_spacy_match_patterns(
        female_names_list, label="gender_female_names"
    )

    male_names_list = [name.lower() for name in male_names()["first_name"]]
    male_name_patterns = MatchCounter.term_list_to_spacy_match_patterns(
        male_names_list, label="gender_male_names"
    )

    return female_names_patterns + male_name_patterns


def get_positive_word_patterns() -> List[Dict[str, list]]:
    """Loads a list of word- and sentiment pairs from "da_lexicon_afinn_v1.txt", splits it by tabs, then sorts them into lists depending on whether the sentiment is positive or negative.

    Returns:
        List[Dict[str, list]]: list of lowercase spacy patterns
    """
    import pathlib

    from dfm.description.match_counter import MatchCounter

    path = pathlib.Path(__file__).parent / "da_lexicon_afinn_v1.txt"

    with open(path, "r") as f:
        lines = f.readlines()

    lines = [line.split("\t") for line in lines]

    positive_words = [line[0] for line in lines if int(line[1]) > 0]

    positive_patterns = MatchCounter.term_list_to_spacy_match_patterns(
        positive_words, label="positive_words"
    )

    return positive_patterns


def get_negative_word_patterns() -> List[Dict[str, list]]:
    """Loads a list of word- and sentiment pairs from "da_lexicon_afinn_v1.txt", splits it by tabs, then sorts them into lists depending on whether the sentiment is positive or negative.

    Returns:
        List[Dict[str, list]]: list of lowercase spacy patterns
    """
    import pathlib

    from dfm.description.match_counter import MatchCounter

    path = pathlib.Path(__file__).parent / "da_lexicon_afinn_v1.txt"

    with open(path, "r") as f:
        lines = f.readlines()

    lines = [line.split("\t") for line in lines]

    negative_words = [line[0] for line in lines if int(line[1]) < 0]

    negative_patterns = MatchCounter.term_list_to_spacy_match_patterns(
        negative_words, label="negative_words"
    )

    return negative_patterns
