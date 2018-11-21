from models import User, Notification
from run import db, create_app
import datetime as dt

app = create_app()
with app.app_context():
    db.init_app(app)
    # Test the ORM
    db.drop_all()
    db.create_all()

    user1 = User(phone_number='3124505312')
    notif1 = Notification(tag='fake tag',
        body="sqlalchemy is hard",
        trigger_type='cron',
        day_of_week='mon-fri',
        hour=18,
        minute=57,
        jitter=30,
        end_date=dt.datetime(2018,11,30),
        timezone='America/Denver',
        user=user1)

    db.session.add(user1)
    db.session.add(notif1)
    db.session.commit()

    print(User.query.all())

    print(Notification.query.filter_by(user_id=user1.id).first() )

    userList = Notification.query.join(User)\
        .add_columns(User.phone_number).all()

    print("userList",userList)

    user = User.query.filter_by(phone_number='312450531').first()

    print("USER filtered: ", user)

    print(len(Notification.query.filter_by(user=user1).all()))

    print(notif1.__dict__)