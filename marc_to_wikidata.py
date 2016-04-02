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


class MarcClaimRobot(WikidataBot):
    def __init__(self, claims, **kwargs):
        super(WikidataBot, self).__init__(**kwargs)
        self.claims = claims

    i = 0
    def run(self):
        
        for claim in self.claims:
            # if no viaf exist
            if 'P214' not in claim:

                print 'No viaf for claim'+str(i)
                # TODO: can we find relaxation that isn't based on VIAF? maybe just name?
                # maybe search on the name, then compare all the result with date of birth & date of death & country
                # and other basic information, and if at least 2 of 3 exist and match - it's a goal.
                continue
            item = get_entity_by_viaf(claim['P214'])
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
            localname = name.find('slim:subfield[@code="a"]', namespaces)
            wikidata_rec[lang] = localname
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
        # TODO: either associate existing record with VIAF or create a new entity
        print "len(entities) == 0:- NotImplemented\n"
        # raise NotImplemented
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
