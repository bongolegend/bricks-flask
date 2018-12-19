import phonenumbers as phone
from app.models import Team


ANY = '*'

MULTIPLE_CHOICE = {
    'a': ['a', 'a)'],
    'b': ['b', 'b)'],
    'c': ['c', 'c)'],
    'd': ['d', 'd)']
}

MAIN_MENU = {
    'a': ['a', 'a)'],
    'b': ['b', 'b)'],
    'c': ['c', 'c)'],
    'd': ['d', 'd)'],
    'e': ['e', 'e)'],
    'f': ['f', 'f)'],
    'g': ['g', 'g)'],
}

YES_NO = {
    'yes': ['yes', 'y', 'ye', 'ya', 'yea', 'yep', 'yup', 'yeah'],
    'no': ['no', 'n', 'na', 'nope'],
}

ADD_MEMBER = 'add_member_parser'


def parse(inbound, inbound_format):
    '''combine all parsers'''
    if inbound_format == ANY:
        return inbound
    elif inbound_format == ADD_MEMBER:
        return parse_add_member(inbound)
    else:
        inbound = inbound.lower()
        for term, matches in inbound_format.items():
            if inbound in matches:
                return term
    # returning None signals to the app that parsing the inbound failed
    return None


def parse_add_member(inbound):
    '''
    Take inbound as a string "123, 123-456-7890" and return Tuple(int(123), int(1234567890)).
    This can handle many phone number formats.
    '''

    parts = inbound.split(',')
    if len(parts) != 2:
        return None

    team_id = int(parts[0])

    parsed = phone.parse(parts[1], "US")

    phone_number = f"+{parsed.country_code}{parsed.national_number}"

    return team_id, phone_number
    