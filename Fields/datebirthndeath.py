# -*- coding: utf-8 -*-
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
        # print ("indexes: [: {0} ]: {1} ".format(birthplace.index('['),birthplace.index(']')))
        place_without_brackets = place.partition(place[place.index('['):place.index(']')+1])
        if (len(place_without_brackets[0])==0 and len(place_without_brackets[2])==0):
            # print('received birthplace within brackets - skipping')
            return None
        else:
            place = place_without_brackets[0]+place_without_brackets[2]
        # print(birthplace.decode('utf-8').partition(birthplace[birthplace.index('['):birthplace.index(']')]))

    if any(u"\u0590" <= c <= u"\u05EA" for c in place):
        lang='heb'
    else:
        lang='eng'
    tup = (place_type,lang,place)
    print ('output tuple: {0}'.format(tup))
    return tup
