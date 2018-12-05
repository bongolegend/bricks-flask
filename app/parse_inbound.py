from app.routers import nodes


MULTIPLE_CHOICE = {
    'yes': ['yes', 'y', 'ye', 'ya', 'yea', 'yep', 'yup', 'yeah'],
    'no': ['no', 'n', 'na', 'nope'],
    'a': ['a', 'a)'],
    'b': ['b', 'b)'],
    'c': ['c', 'c)'],
    'd': ['d', 'd)'],
}


def main(inbound, router_id):
    '''combine all parsers'''
    inbound_format = nodes[nodes.router_id == router_id].inbound_format.iloc[0]
    if inbound_format == '*':
        return inbound
    elif inbound_format == 'multiple_choice':
        return parse_multiple_choice(inbound)
    else:
        raise NotImplementedError(f'The inbound format {inbound_format} does not have a parser.')


def parse_multiple_choice(inbound):
    inbound = inbound.lower()
    for term, matches in MULTIPLE_CHOICE.items():
        if inbound in matches:
            return term
    # None signals to the app that parsing the inbound failed
    return None
