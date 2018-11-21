""""this is a dummy db implemented with a Pandas dataframe"""
import pandas as pd

NOTIFICATIONS = {
    2: [
        "3124505311",
        "Testing the time zone and clock",
        "cron",
        dict(
            day_of_week='mon-fri',
            hour=17,
            minute=28,
            jitter=30,
            end_date='2018-11-30',
            timezone='America/Denver'
        )
    ],
    3: [
        "3124505311",
        "Did you finish your brick?",
        "cron",
        dict(
            day_of_week='mon-fri',
            hour=21,
            jitter=30,
            end_date='2018-11-30',
            timezone='America/Denver'
        )
    ],  
}

notifications_df = pd.DataFrame.from_dict(NOTIFICATIONS, 
    orient='index',
    columns=['to_number', 'outbound', 'trigger_type', 'kwargs'])