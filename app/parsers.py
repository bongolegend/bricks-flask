import phonenumbers as phone
from app.models import Team
from app.constants import Redirects, Sizes
from tests.constants import TEST_TEAM_ID


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
}

YES_NO = {
    'yes': ['yes', 'y', 'ye', 'ya', 'yea', 'yep', 'yup', 'yeah'],
    'no': ['no', 'n', 'na', 'nope'],
}

ADD_MEMBER = (f"{TEST_TEAM_ID}, 3124505311",)

INTEGER = "INTEGER_PARSER"

ZERO_TO_TEN = ('0','1','2','3','4','5','6','7','8','9','10')

def parse(inbound, inbound_format):
    '''combine all parsers'''
    if len(inbound) > Sizes.INBOUND_MAX_LENGTH:
        return None
    if inbound_format == ANY:
        return inbound
    elif inbound_format == ADD_MEMBER:
        return parse_add_member(inbound)
    elif inbound_format == INTEGER:
        try:
            return int(inbound)
        except:
            return None
    elif inbound_format == ZERO_TO_TEN:
        try:
            assert inbound in ZERO_TO_TEN
            inbound = int(inbound)
            assert 0 <= inbound <= 10
            return inbound
        except:
            return None
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
    If inbound == 'menu', return to menu
    '''

    if inbound.lower() == 'menu':
        return Redirects.MAIN_MENU

    parts = inbound.split(',')
    if len(parts) != 2:
        return None

    team_id = int(parts[0])

    parsed = phone.parse(parts[1], "US")

    phone_number = f"+{parsed.country_code}{parsed.national_number}"

    return team_id, phone_number
    