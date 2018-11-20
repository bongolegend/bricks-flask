""""this is a dummy db implemented with a Pandas dataframe"""
import pandas as pd

NOTIFICATIONS = {
    0: [
        "3124505311",
        "Whats your brick for today?",
        "interval",
        dict(
            seconds=3
        )
    ],
    1: [
        "3124505311",
        "Did you finish your brick?",
        "interval",
        dict(
            seconds=2
        )
    ], 
}

notifications_df = pd.DataFrame.from_dict(NOTIFICATIONS, 
    orient='index',
    columns=['to_number', 'output', 'trigger_type', 'kwargs'])