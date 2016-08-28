# -*- coding: utf-8 -*-
# a dictionary of professions and "hints" that might reinforce confidence in their parsing in case of
# ambiguous meanings
# TODO: change this from map to a different data structure that contains synonyms and clues, separately!!!
profession_map = {
    'רב': {
            'hints': ['קהילה','קהילות','קהילת'],
            'wikidata_item': ['Q133485'],
            'synonyms': ['רבה'],
    },
    'אב\"ד': {
            'hints': ['אב בית דין'],
            'wikidata_item': ['Q694994'],
            'synonyms': []
    },
    'אדמו\"ר': {
            'hints': [],
            'wikidata_item': ['Q359351'],
            'synonyms': ['אדמור'],
    },
    'אדירכל': {
        'hints': [],
        'wikidata_item': ['Q42973'],
        'synonyms': ['אדריכלית'],
    },
    'מדען': {
        'hints': [],
        'wikidata_item': ['Q901'],
        'synonyms': ['מדענית'],
    },
    'איש-צבא': {
        'hints': [],
        'wikidata_item': ['Q220098'],
        'synonyms':['מצביא','איש צבא', 'ראש המטה הכללי', 'רמטכ\"ל'],
    },
    'אמן':  {
        'hints': [],
        'wikidata_item': ['Q483501'],
        'synonyms':['אמנית']
    },
    'דיין': {
        'hints': [],
        'wikidata_item': ['Q3570351'],
        'synonyms':['דיינית']
    },
    'דרשן': {
        'hints': [],
        'wikidata_item': ['Q1884050'],
        'synonyms':[]
    },
    'היסטוריון': {
        'hints': [],
        'wikidata_item': ['Q201788'],
        'synonyms':['']
    },
    'חבר כנסת': {
        'hints': [],
        'wikidata_item': ['Q4047513'],
        'synonyms':['חבר-כנסת','ח\"כ'],
    },

    'מורה': {
        'hints': [],
        'wikidata_item': ['Q37226'],
        'synonyms':['']
    },
    'משורר': {
        'hints': [],
        'wikidata_item': ['Q49757'],
        'synonyms':['משוררת']
    },
    'מלחין': {
        'hints': [],
        'wikidata_item': ['Q36834'],
        'synonyms': ['מלחינה'],
    },
    'סופר': {
        'hints': [],
        'wikidata_item': ['Q36180'],
        'synonyms': ['סופרת']
    }
}


def parse_profession(profession):
    profession = profession.encode("utf-8")
    print ("Got input profession {0}".format(profession));
    for (accepted_professions, hints) in profession_map.items():
        if (accepted_professions == profession):
            print ("found accepted profession!")
            return profession
        elif (profession in hints['synonyms']):
            print ("profession is in hints!!")
            return profession

    print("Input for {0} did not yield a profession".format(profession))
    return None