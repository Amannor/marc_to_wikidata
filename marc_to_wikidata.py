#!/bin/python

from lxml import objectify

import pywikibot
from pywikibot import pagegenerators, WikidataBot

repo = pywikibot.Site().data_repository()
namespaces = {'slim': 'http://www.loc.gov/MARC21/slim'}
property_to_xpath = {

    'P569': 'slim:datafield[@tag="046"]/slim:subfield[@code="f"]',  # date of birth
    'P570': 'slim:datafield[@tag="046"]/slim:subfield[@code="g"]',  # date of death
    'P19': 'slim:datafield[@tag="370"]/slim:subfield[@code="a"]',  # place of birth
    'P20': 'slim:datafield[@tag="370"]/slim:subfield[@code="b"]',  # place of death
    'P214': 'slim:datafield[@tag="901"]/slim:subfield',  # VIAF
    'P21' : 'slim:datafield[@tag="375"]', # gender
    'P1412' : 'slim:datafield[@tag="377"]', # languages spoken or wrriten
    'P949' : 'slim:datafield[@tag="001"]', # National Library of Israel identifier
    'P131' : 'slim:datafield[@tag="371"]/slim:subfield[@code="b"]',  # Address - place name
    'P17' : 'slim:datafield[@tag="371"]/slim:subfield[@code="c"]',  # Address - country
    'P106' : 'slim:datafield[@tag="372"]/slim:subfield[@code="a"]',  # Activity (Person/Intitution)
    'P571' : 'slim:datafield[@tag="046"]/slim:subfield[@code="s"]',  # Start date of organization (110)
    'P576' : 'slim:datafield[@tag="046"]/slim:subfield[@code="t"]',  # End date of organization (110)
    
}
language_map = {
    'ara': 'ar',
    'cyr': 'ru',
    'fre': 'fr',
    'heb': 'he',
    'lat': 'en',
}


class MarcClaimRobot(WikidataBot):
    def __init__(self, claims, **kwargs):
        super(WikidataBot, self).__init__(**kwargs)
        self.claims = claims

    i = 0
    def run(self):
        
        for claim in self.claims:
            if 'P214' in claim:
                item = get_entity_by_viaf(claim['P214'])
            # if no viaf exist
            if not item:
                item = get_suggested_entity(claim)
            if not item:
                continue

            item.get()
            self.treat(item, claim)
            self.i = self.i +1

    # Deals with existing records from WikiData
    # should check if existing attributes equal
    # add reference or new claim accordingly
    def treat(self, item, claim):
        print "claim "+str(self.i)
        print claim
        # TODO: create wikidata claims. see claimit to see how to do it
        raise NotImplemented

def parse_records(marc_records):
    i = 0
    for record in marc_records:
        print "record"+str(i)
        i = i + 1
        wikidata_rec = dict()

        names = record.findall('slim:datafield[@tag="100"]/slim:subfield[@code="9"]/..', namespaces)


        for name in names:

            lang = name.find('slim:subfield[@code="9"]', namespaces)
            localname = name.find('slim:subfield[@code="a"]', namespaces).text
            localname_parts = localname.split(',')
            wikidata_rec[lang] = localname_parts[0].strip()
            if len(localname_parts) > 1:
                wikidata_rec[lang] = localname_parts[1].strip() + ' ' + wikidata_rec[lang]
            # date of birth
        # add here parsing of data from 670 fields
        # put into wikidata_rec['<<wikidata attribute identifier>>'] =
        for wikidata_prop, xpath_query in property_to_xpath.items():
            query_res = record.find(xpath_query, namespaces)
            if query_res:
                wikidata_rec[wikidata_prop] = query_res

        yield wikidata_rec


# Finds the matching record in Wikidata by VIAF identifier
def get_entity_by_viaf(viaf):
    sparql = "SELECT ?item WHERE { ?item wdt:P214 ?VIAF filter(?VIAF = '%s') }" % viaf
    entities = pagegenerators.WikidataSPARQLPageGenerator(sparql, site=repo)
    entities = list(entities)
    if len(entities) == 0:
        return None
    elif len(entities) > 1:
        # TODO: is it possible to have multiple VIAFs?
        raise Exception('VIAF is expected to be unique')
    return entities[0]


def get_suggested_entity(claim):
    """Search for people by names and dates."""

    # Matching names
    languages_sparql = []
    for lang in claim:
        if lang in language_map:
            languages_sparql.append('{ ?item rdfs:label "%(name)s"@%(lang)s }' % {
                'name': claim[lang],
                'lang': language_map[lang],
            })
    if not len(languages_sparql):
        return None
    languages_sparql = ' UNION '.join(languages_sparql)

    # Matching birth date
    birth_sparql = ''
    if 'P569' in claim:
        birth_sparql = """
            . {
                ?item wdt:P569 ?birthDate .
                FILTER (datatype(?birthDate) != xsd:dateTime)
            } UNION {
                ?item wdt:P569 ?birthDate .
                FILTER (year(?birthDate) = year("%(birth_date)s"^^xsd:dateTime))
                FILTER (month(?birthDate) = month("%(birth_date)s"^^xsd:dateTime))
                FILTER (day(?birthDate) = day("%(birth_date)s"^^xsd:dateTime))
            }
        """ % { 'birth_date': claim['P569'] }

    # Matching death date
    death_sparql = ''
    if 'P570' in claim:
        death_sparql = """
            . {
                ?item wdt:P570 ?deathDate .
                FILTER (datatype(?deathDate) != xsd:dateTime)
            } UNION {
                ?item wdt:P570 ?deathDate .
                FILTER (year(?deathDate) = year("%(death_date)s"^^xsd:dateTime))
                FILTER (month(?deathDate) = month("%(death_date)s"^^xsd:dateTime))
                FILTER (day(?deathDate) = day("%(death_date)s"^^xsd:dateTime))
            }
        """ % { 'death_date': claim['P570'] }

    # Final request
    sparql = """
        SELECT DISTINCT ?item WHERE {
            %(languages)s
            %(birth)s
            %(death)s
        }
    """ % {
        'languages': languages_sparql,
        'birth': birth_sparql,
        'death': death_sparql,
    }

    entities = pagegenerators.WikidataSPARQLPageGenerator(sparql.encode('utf8'), site=repo)
    entities = list(entities)
    if len(entities) == 0:
        return None
    elif len(entities) > 1:
        # TODO: is it possible to have multiple VIAFs?
        raise Exception('VIAF is expected to be unique')
    return entities[0]


def main():
    # TODO: for now we use the example XML. in post development this should be argument
    marc_records = objectify.parse(open('marcxml_example.xml', 'r')).getroot().find('slim:record', namespaces)
    claims = parse_records(marc_records)
    bot = MarcClaimRobot(claims)
    bot.run()


if __name__ == '__main__':
    main()
