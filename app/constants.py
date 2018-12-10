
class Names:
    '''Names for routers. These are in a separate module so they can be used as references regardless of import hierarchy'''
    CHOOSE_TASK = 'choose_task'
    MORNING_CONFIRMATION = 'morning_confirmation'
    DID_YOU_DO_IT = 'did_you_do_it'


class Outbounds:
    HOW_IT_WORKS = """How this works: every weekday, you input your most important task of the day. At the end of the day, you confirm that you did it.
If you did, then you get a point. If you are consistent, you get extra points. Makes sense? (y/n)"""

# TODO(Nico) instead ask what city you're in. this makes it better to find their locale for analytics
# all good solutions require API access : https://stackoverflow.com/questions/16505501/get-timezone-from-city-in-python-django
    WHAT_TIMEZONE = """What's your timezone?
a) PT
b) MT
c) CT
d) ET
"""

    MAIN_MENU = """What do you want to do?
a) choose a brick for today
b) choose a new timezone
c) how does this work?
d) how many points do I have?
"""