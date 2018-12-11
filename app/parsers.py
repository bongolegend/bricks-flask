ANY = '*'

MULTIPLE_CHOICE = {
    'a': ['a', 'a)'],
    'b': ['b', 'b)'],
    'c': ['c', 'c)'],
    'd': ['d', 'd)'],
    'e': ['e', 'e)'],
}

YES_NO = {
    'yes': ['yes', 'y', 'ye', 'ya', 'yea', 'yep', 'yup', 'yeah'],
    'no': ['no', 'n', 'na', 'nope'],
}


def parse(inbound, inbound_format):
    '''combine all parsers'''
    if inbound_format == ANY:
        return inbound
    else:
        inbound = inbound.lower()
        for term, matches in inbound_format.items():
            if inbound in matches:
                return term
    # returning None signals to the app that parsing the inbound failed
    return None
