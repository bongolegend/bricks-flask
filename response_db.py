""""this is a dummy db implemented with a Pandas dataframe"""
import pandas as pd

HOW_IT_WORKS = "It is pure magic"

WELCOME = """
Hey! Welcome to Bricks, a tool that helps you outperform your friends. Respond with the number of what you want to do:
(a) choose my first brick
(b) how does this work?
"""

FIRST_CONTACT = {
    0: [
        None,
        None,
        WELCOME        
    ],
    1: [
        0,
        'a',
        "Ok, so what’s the most important thing you want to get done today?"
    ],
    2: [
        1,
        None,
        "gotcha. I’ll text you tonight at 9 pm to follow up and make sure you did that."
    ],
    3: [
        0,
        'b',
        HOW_IT_WORKS
    ],
}

first_contact_df = pd.DataFrame.from_dict(FIRST_CONTACT, 
    orient='index',
    columns=['last_output_id', 'input', 'response']
)