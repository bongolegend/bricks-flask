from datetime import datetime as dt
from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), default='NEW_USER')
    phone_number = db.Column(db.String(32), unique=True)
    timezone = db.Column(db.String(32))
    created = db.Column(db.DateTime, nullable=False, default=dt.utcnow)

    def to_dict(self):
        return dict(
            id = self.id, 
            username = self.username,
            phone_number = self.phone_number,
            timezone = self.timezone,
            created = self.created
        )

    def __repr__(self):
        return '<User %r>' % self.phone_number


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(32), nullable=False)
    body = db.Column(db.Text, nullable=False)
    trigger_type = db.Column(db.String(32), nullable=False)
    day_of_week = db.Column(db.String(32)) 
    hour = db.Column(db.Integer, nullable=False)
    minute = db.Column(db.Integer, nullable=False)
    jitter = db.Column(db.Integer)
    end_date = db.Column(db.DateTime)
    timezone = db.Column(db.String(32), nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=dt.utcnow)
    # TODO(Nico) implement updated

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
        nullable=False)
    user = db.relationship('User',
        backref=db.backref('notifications', lazy=True))

    def to_cron(self):
        '''return only values needed for cron job'''
        return dict(
            day_of_week = self.day_of_week, 
            hour = self.hour,
            minute = self.minute,
            jitter = self.jitter,
            end_date = self.end_date,
            timezone = self.timezone
        )

    def __repr__(self):
        return '<Notification %r>' % self.tag


class Exchange(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    router_id = db.Column(db.String(32), nullable=False)
    inbound = db.Column(db.String(128))
    outbound = db.Column(db.String(128))
    created = db.Column(db.DateTime, nullable=False, default=dt.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
        nullable=False)
    user = db.relationship('User',
        backref=db.backref('exchanges', lazy=True))
    
    def __repr__(self):
        return '<Exchange %r>' % self.router_id