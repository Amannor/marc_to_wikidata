from pywikibot import pagegenerators
from Util import language_map

repo = pywikibot.Site().data_repository()

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
