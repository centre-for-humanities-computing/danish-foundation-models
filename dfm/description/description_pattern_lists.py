occupation_pattern_list = [
    "revisor",
    "administrator",
    # "rådgiver",  # Matches many non-occupation tokens, maybe use lemmatizer?
    "analytiker",
    "arkitekt",
    "assistent",
    "bager",
    "bartender",
    "ejendomsmægler",
    "tømrer",
    "kassemedarbejder",
    "kok",
    "kemiker",
    "chef",
    "rengøringshjælp",
    "ekspedient",
    "terapeut",
    "advokat",
    # "designer",  # Matches many non-occupation tokens, maybe use lemmatizer?
    # "udvikler",  # Matches many non-occupation tokens, maybe use lemmatizer?
    "diætist",
    "læge",
    "chauffør",
    "redaktør",
    "elektriker",
    "ingeniør",
    "landmand",
    "brandmand",
    "vagt",
    "frisør",
    "instruktør",
    "efterforsker",
    "pedel",
    "advokat",
    "bibliotekar",
    # "leder", # Matches many non-occupation tokens, maybe use lemmatizer?
    "mekaniker",
    "sygeplejerske",  # Test and replace with regex sygeplejer(ske)+
    "politibetjent",
    # "betjent", # Matches many non-occupation tokens, maybe use lemmatizer?
    "maler",
    "ambulanceredder",
    "ambulancebehandler",
    "patolog",
    "farmaceut",
    "blikkenslager",
    "vvs'er",
    "vvs-installatør",
    "vvs-mand",
    "programmør",
    "psykolog",
    "receptionist",
    # "sælger",  # Matches many non-occupation tokens, maybe use lemmatizer?
    # "forsker",  # Matches many non-occupation tokens, maybe use lemmatizer?
    "sekretær",
    "kirurg",
    "skrædder",
    # "lærer",  # Matches many non-occupation tokens, maybe use lemmatizer?
    "tekniker",
    "terapeut",
    "dyrlæge",
    "forfatter",
]

female_gendered_terms = [
    "pige",
    "søster",
    "mor",
    "kone",
    # "kvinde", # Removed to maintain gender-list parity, since "mand" matches both male and husband
    "brud",
    "hunkøn",
    "dame",
    "moder",
    "datter",
]

male_gendered_terms = [
    "dreng",
    "bror",
    "far",
    "mand",
    "brudgom",
    "hankøn",
    "herre",
    "fader",
    "søn",
]
