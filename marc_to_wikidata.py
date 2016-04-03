# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from lxml import objectify

import pywikibot
from pywikibot import pagegenerators, WikidataBot

import TestCopier

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

# a dictionary of professions and "hints" that might reinforce confidence in their parsing in case of
# ambiguous meanings
# TODO: change this from map to a different data structure that contains synonyms and clues, separately!!!
profession_map = {
    'רב': ['קהילה','קהילות','קהילת'],
    'אב\"ד': ['אב בית דין'],
    'אדמו\"ר': ['אדמור'],
    'אדירכל': [],
    'מדען': [],
    'איש-צבא': ['מצביא','איש צבא', 'ראש המטה הכללי', 'רמטכ\"ל'],
    'אמן': [],
    'דיין': [],
    'דרשן': [],
    'היסטוריון': [],
    'חבר כנסת': ['חבר-כנסת','ח\"כ'],
    'מורה': [],
    'משורר': [],
    'מלחין': ['מלחינה'],
    'סופר': ['סופרת']
}


class MarcClaimRobot(WikidataBot):
    def __init__(self, records, **kwargs):
        super(WikidataBot, self).__init__(**kwargs)
        self.records = records

    i = 0
    def run(self):
        
        for record in self.records:
            if 'P214' in record:
                item = get_entity_by_viaf(record['P214'])
            # if no viaf exist
            if not item:
                item = get_suggested_entity(record)
            if not item:
                create_new_record_in_wikidata(record)
                continue

            wikidata_record = self.constructRecordFromMarc(record)
            item.get()
            self.treat(item, record)
            self.i = self.i +1

    # Convert a record from MarcXML to Wikidata record (in memory)
    # This will enable the treat function to perform comparisons of claims before saving data into Wikidata
    def constructRecordFromMarc(self,record):
        wikidata_record = ""
        return record

    # Deals with existing records from WikiData
    # should check if existing attributes equal
    # add reference or new claim accordingly
    def treat(self, item, nliProposedUnparsedClaim):
        print("claim "+str(self.i))
        print("the wiki data item: ")
        print(item)
        print("nliProposedUnparsedClaim: ")

#        for (key, value) in sorted(nliProposedUnparsedClaim.items()):
#            print('%s:: %s' % (key, unicode(value)))

        ## print('\n'.join(['%s:: %s' % (key, unicode(str(value))) for (key, value) in sorted(nliProposedUnparsedClaim.items())]))
        # TODO: create wikidata claims. see claimit to see how to do it

        # several options here:
        #   either the wikidata item does not contain the proposed NLI claim
        #   or the wikidata item DOES contain the proposed NLI claim
        #
        # If the wikidata item does not contain the NLI claim
        #      let's create this claim, add a wikidata reference to NLI database, add save(?) that.
        #
        # If the wikidata item DOES contain the proposed NLI claim
        #      it's either the proposed property value is the same as the property in wikidata
        #           and then - it's either the NLI reference is already there, or not...
        #                      if it's not there - let's add it.
        #      Or, the proposed property value is not contained in this property,
        #           so - let's add it, along with a reference to NLI.

        print (item.id)
        wikidata_record = TestCopier.new_test_item_from_production(item.id)
        print("TestCopier created a new record under test.wikidata.org %s" % wikidata_record)

        data = item.get("wikidata")
        wdClaims = data.get("claims")
        print ("there are %d claims in wd" % len(wdClaims))
        print ("there are %d proposed claims in nli" % len(nliProposedUnparsedClaim))

        nli_p_Claims = filter(lambda aClaim : isinstance(aClaim, str) and aClaim.startswith('P'), nliProposedUnparsedClaim)

        for nliClaim in nli_p_Claims:
            print (nliClaim + " passed the P test!")

        for nlipClaim in nli_p_Claims:
            if nlipClaim in wdClaims.keys():
                print ("nlipClaim %s is also in wdClaims" % nlipClaim)

#        nliProposedClaims

        raise NotImplemented
        for wdClaimPropertyName in sorted(wdClaims.keys()):
            print("claim's id property: " + wdClaimPropertyName)
            wdClaim = wdClaims[wdClaimPropertyName][0]

            ## diff the found wikidata claim

#            print('\n'.join(['%s:: %s' % (key, value) for (key, value) in sorted(wdClaim.__dict__.items())]))
            print("-----------------------")
        #item.addClaim()
        raise NotImplemented

def parse_records(marc_records):
    i = 0
    for record in marc_records:
        print("record"+str(i))
        i = i + 1
        wikidata_rec = dict()
        person_names_dict = dict()
        birth_place_dict = dict()
        death_place_dict = dict()
        professions_dict = dict()

        ### parse local names
        names = record.findall('slim:datafield[@tag="100"]/slim:subfield[@code="9"]/..', namespaces)


        for name in names:

            lang = name.find('slim:subfield[@code="9"]', namespaces)
            localname = name.find('slim:subfield[@code="a"]', namespaces).text
            localname_parts = localname.split(',')
            person_names_dict[lang] = localname_parts[0].strip()
            if len(localname_parts) > 1:
                person_names_dict[lang] = localname_parts[1].strip() + ' ' + person_names_dict[lang]
            
        wikidata_rec["person_names"]=person_names_dict

        ### place of birth / death
        historic_comments = record.findall('slim:datafield[@tag="678"]/slim:subfield[@code="a"]/..', namespaces)
        #print('***parse historic comments***')
        for comment in historic_comments:
                #print(birth_or_death)
                historic_comment = comment.find('slim:subfield[@code="a"]', namespaces)
                #get the text for the historic comment in unicode
                encoded_comment = u''.join(historic_comment.text).encode('utf-8').strip()
                if encoded_comment.decode('utf-8').startswith(u"מקום לידה: "):
                    #parse birth date parameter
                    birth_place = parse_birth_or_death_place("birth_place",encoded_comment.decode('utf-8').partition(u"מקום לידה: ")[2])
                    if (birth_place is not None):
                        birth_place_dict[birth_place[1]]=birth_place[2]   
                if encoded_comment.decode('utf-8').startswith(u"מקום פטירה: "):
                    #parse death place
                    death_place = parse_birth_or_death_place("death_place",encoded_comment.decode('utf-8').partition(u"מקום פטירה: ")[2])
                    if (death_place is not None):
                        death_place_dict[death_place[1]]=death_place[2] 

                if encoded_comment.decode('utf-8').startswith(u"מקצוע: "):
                    #parse death place
                    profession = parse_profession(encoded_comment.decode('utf-8').partition(u"מקצוע: ")[2])
                    if (death_place is not None):
                        death_place_dict[death_place[1]]=death_place[2] 

        
        wikidata_rec["birth_places"]=birth_place_dict
        wikidata_rec["death_places"]=death_place_dict

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
    print ('output tuple: {0}'.format(tup))
    return tup

def parse_profession(profession):
    print ("Got input profession {0}".format(profession));
    for (accepted_professions, hints) in profession_map.iteritems():
        if (accepted_professions == profession):
            print ("found accepted profession!")
            return profession
        elif (profession in hints):
            print ("profession is in hints!!")
            return profession
    
    print("Input for {0} did not yield a profession".format(profession))
    return None
        


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

def create_new_record_in_wikidata(record):
    raise NotImplemented

def main():
    # TODO: for now we use the example XML. in post development this should be argument
    marc_records = objectify.parse(open('marcxml_example.xml', 'r')).getroot().find('slim:record', namespaces)
    claims = parse_records(marc_records)
    bot = MarcClaimRobot(claims)
    bot.run()


if __name__ == '__main__':
    main()
