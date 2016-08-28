# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from lxml import objectify

import pywikibot
from pywikibot import pagegenerators, WikidataBot
from Fields.datebirthndeath import *
from Fields.profession import parse_profession
from searchEntityNoViaf import get_suggested_entity
from storeInWikidata import create_new_record_in_wikidata
import TestCopier
from Util import language_map

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
    def __init__(self, records, **kwargs):
        super(WikidataBot, self).__init__(**kwargs)
        self.records = records

    i = 0
    def run(self):
        
        for record in self.records:
            if 'P214' in record:
                print ("***************** New Record with VIAF *****************")
                print (record)
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
        # TODO: this should actually be removed - this is TESTING ONLY
        # wikidata_record = TestCopier.new_test_item_from_production(item.id)
        # print("TestCopier created a new record under test.wikidata.org %s" % wikidata_record)

        data = item.get("wikidata")
        wdClaims = data.get("claims")
        print ("there are %d claims in wd" % len(wdClaims))
        print ("there are %d proposed claims in nli" % len(nliProposedUnparsedClaim))

        # find the claims (structure that has an id composed of a string claim that starts with P)
        # these are filtered and added into the nli_p_Claims
        nli_p_Claims = filter(lambda aClaim : isinstance(aClaim, str) and aClaim.startswith('P'), nliProposedUnparsedClaim)

        # notify which claims have passed through the filter
        for nliClaim in nli_p_Claims:
            print (nliClaim + " passed the P test!")

        # check to see if nli claims appear under wikidata claims, and notify.
        for nlipClaim in nli_p_Claims:
            if nlipClaim in wdClaims.keys():
                print ("nlipClaim %s is also in wdClaims" % nlipClaim)

        #### the idea is to have a visitor to go through the two given structures and find out the differences that should 
        #### actually be taken and added into the wikidata structure.

        #### STILL NOT IMPLEMENTED ENOUGH.
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
                    if (profession is not None):
                        print("FOUND PROFESSION! {0}".format(profession))
                        

        
        wikidata_rec["birth_places"]=birth_place_dict
        wikidata_rec["death_places"]=death_place_dict

        # put into wikidata_rec['<<wikidata attribute identifier>>'] =
        for wikidata_prop, xpath_query in property_to_xpath.items():
            query_res = record.find(xpath_query, namespaces)
            if query_res:
                wikidata_rec[wikidata_prop] = query_res

        yield wikidata_rec


# Finds the matching record in Wikidata by VIAF identifier
def get_entity_by_viaf(viaf):
    sparql = "SELECT ?item WHERE { ?item wdt:P214 ?VIAF filter(?VIAF = '%s') }" % viaf
    entities = pagegenerators.WikidataQueryPageGenerator(sparql, site=repo)
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
