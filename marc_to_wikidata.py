#!/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
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
    'P214': 'slim:datafield[@tag="901"]/slim:subfield'  # VIAF
}


class MarcClaimRobot(WikidataBot):
    def __init__(self, claims, **kwargs):
        super(WikidataBot, self).__init__(**kwargs)
        self.claims = claims

    def run(self):
        for claim in self.claims:
            # if no viaf exist
            if 'P214' not in claim:
                # TODO: can we find relaxation that isn't based on VIAF?
                # maybe search on the name, then compare all the result with date of birth & date of death & country
                # and other basic information, and if at least 2 of 3 exist and match - it's a goal.
                continue
            item = get_entity_by_viaf(claim['P214'])
            item.get()
            self.treat(item, claim)

    # Deals with existing records from WikiData
    # should check if existing attributes equal
    # add reference or new claim accordingly
    def treat(self, item, claim):
        print(claim)
        # TODO: create wikidata claims. see claimit to see how to do it
        #item.addClaim()
        
        #raise NotImplemented


def parse_records(marc_records):
    for record in marc_records:
        wikidata_rec = dict()

        # parse local names
        names = record.findall('slim:datafield[@tag="100"]/slim:subfield[@code="9"]/..', namespaces)
        for name in names:
            lang = name.find('slim:subfield[@code="9"]', namespaces)
            localname = name.find('slim:subfield[@code="a"]', namespaces)
            wikidata_rec[lang] = localname
            
        # date of birth / death
        historic_comments = record.findall('slim:datafield[@tag="678"]/slim:subfield[@code="a"]/..', namespaces)
        print('***parse historic comments***')
        for comment in historic_comments:
                #print(birth_or_death)
                historic_comment = comment.find('slim:subfield[@code="a"]', namespaces)
                #get the text for the historic comment in unicode
                encoded_comment = u''.join(historic_comment.text).encode('utf-8').strip()
                if encoded_comment.decode('utf-8').startswith(u"מקום לידה: "):
                    #parse birth date parameter
                    parse_birth_or_death_place("birth_place",encoded_comment.decode('utf-8').partition(u"מקום לידה: ")[2])
                if encoded_comment.decode('utf-8').startswith(u"מקום פטירה: "):
                    #parse death place
                    parse_birth_or_death_place("death_place",encoded_comment.decode('utf-8').partition(u"מקום פטירה: ")[2])
                

        # put into wikidata_rec['<<wikidata attribute identifier>>'] =
        for wikidata_prop, xpath_query in property_to_xpath.items():
            query_res = record.find(xpath_query, namespaces)
            if query_res:
                wikidata_rec[wikidata_prop] = query_res

        yield wikidata_rec

#, return tuple (lang code - 'eng' or 'heb', and actual place) or None if input is bad
def parse_birth_or_death_place(place_type,place):
    """
    Parse birth/death place for a person based on NLI authority records
    (clean it from unwanted stuff in square brackets)

    If args is an empty list, sys.argv is used.

    @param place_type: type of place - 'birth_place' or 'death_place'
    @param place: the unicode string of the place
    @return a three item tuple containing (place_type,language ('eng' or 'heb'),parsed place) or None on invalid input
    """
    
    # drop stuff within brackets 
    if place.find('[') >= 0 and place.find(']') >= 0:
        #print ("indexes: [: {0} ]: {1} ".format(birthplace.index('['),birthplace.index(']')))
        place_without_brackets = place.partition(place[place.index('['):place.index(']')+1])
        if (len(place_without_brackets[0])==0 and len(place_without_brackets[2])==0):
            #print('received birthplace within brackets - skipping')
            return None 
        else:
            place = place_without_brackets[0]+place_without_brackets[2]  
        #print(birthplace.decode('utf-8').partition(birthplace[birthplace.index('['):birthplace.index(']')]))

    if any(u"\u0590" <= c <= u"\u05EA" for c in place):
        lang='heb'
    else:
        lang='eng'
    tup = (place_type,lang,place)
    #print ('output tuple: {0}'.format(tup))
    return tup


# Finds the matching record in Wikidata by VIAF identifier
def get_entity_by_viaf(viaf):
    sparql = "SELECT ?item WHERE { ?item wdt:P214 ?VIAF filter(?VIAF = '%s') }" % viaf
    entities = pagegenerators.WikidataSPARQLPageGenerator(sparql, site=repo)
    entities = list(entities)
    if len(entities) == 0:
        # TODO: either associate existing record with VIAF or create a new entity
        raise NotImplemented
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
