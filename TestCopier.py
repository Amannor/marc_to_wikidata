#############################################################################
# A simple script that create a new PageItem in the WikiData Test environment
# from an existing WikiData article.
# To use, provide new_test_item_from_production with an article ID from the
# production environment.
# Thanks to https://github.com/multichill for his assistance!
#############################################################################

import pywikibot

# Family Constants
WIKIDATA = 'wikidata'
WIKIDATA_TEST = 'test'

# class TestCopier:
def new_test_item_from_production(original_id):
    """
    Replicates a PageItem from the WikiData production environment to a new
    PageItem in the WikiData Test environment.
    The method only copies the labels, descriptions and aliases attributes
    - no claims or sitelinks.
    @param original_id: an article ID from the production environment (in
    the form "Q0-9+".
    @type original_id: str
    @return: The new WikiData Test PageItem's ID.
    @rtype: str
    """

    # Setting up the repos
    repo = pywikibot.Site(WIKIDATA, fam='wikidata').data_repository()
    test_repo = pywikibot.Site(WIKIDATA_TEST, fam='wikidata').data_repository()
    # The PageItem object
    entity = pywikibot.ItemPage(repo, original_id)

    # Setting up the data containers
    original_data = entity.get()
    new_data = {"labels": {}, "descriptions": {}, 'aliases': []}

    # Transferring and reformating the data from the original repo to the
    # test-ready repo
    for lang,value in original_data["labels"].items():
        new_data["labels"][lang] = {"language": lang, "value": value}

    for lang,value in original_data['descriptions'].items():
        new_data['descriptions'][lang] = {"language": lang, "value": value}

    for lang,value in original_data['aliases'].items():
        for alias in value:
            new_data['aliases'].append({"language": lang,  "value":
                original_data['aliases'][lang][0]})

    # Initializing an empty id to create a new item
    identification = {}
    summary = "Cloning item: %s" % (entity.title(),)
    pywikibot.output(summary)

    # Creating a new PageItem
    result = test_repo.editEntity(identification, new_data, summary)
    new_test_item_id = result.get(u'entity').get('id')
    return new_test_item_id


