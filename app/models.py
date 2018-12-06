from datetime import datetime as dt
from sqlalchemy import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects import postgresql
from app import db


class Base:
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=func.now(), server_default=func.now())
    updated = db.Column(db.DateTime, nullable=False, default=func.now(), server_default=func.now(), onupdate=func.current_timestamp())

Base = declarative_base(cls=Base)


class AppUser(db.Model, Base):
    username = db.Column(db.String(64), default='NEW_USER')
    phone_number = db.Column(db.String(32), unique=True)
    timezone = db.Column(db.String(32))

    def to_dict(self):
        return dict(
            id = self.id, 
            username = self.username,
            phone_number = self.phone_number,
            timezone = self.timezone,
            created = self.created
        )

    def __repr__(self):
        return '<AppUser %r>' % self.phone_number


class Notification(db.Model, Base):
    tag = db.Column(db.String(32), nullable=False)
    body = db.Column(db.Text, nullable=False)
    trigger_type = db.Column(db.String(32), nullable=False)
    day_of_week = db.Column(db.String(32)) 
    hour = db.Column(db.Integer, nullable=False)
    minute = db.Column(db.Integer, nullable=False)
    jitter = db.Column(db.Integer)
    end_date = db.Column(db.DateTime)
    timezone = db.Column(db.String(32), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('app_user.id'),
        nullable=False)
    user = db.relationship('AppUser',
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


class Exchange(db.Model, Base):
    router_id = db.Column(db.String(32), nullable=False)
    outbound = db.Column(db.String(256))
    inbound = db.Column(db.String(256))
    actions = db.Column(postgresql.ARRAY(db.String))
    inbound_format = db.Column(db.String(32), nullable=False)
    next_router_id = db.Column(db.String(32))
    confirmation = db.Column(db.String(64))
    pre_actions = db.Column(postgresql.ARRAY(db.String))
    next_exchange_id = db.Column(db.Integer) # this needs to be nullable because it is not known when an exchange is first created

    user_id = db.Column(db.Integer, db.ForeignKey('app_user.id'),
        nullable=False)
    user = db.relationship('AppUser',
        backref=db.backref('exchanges', lazy=True))
    
    def to_dict(self):
        if type(self.actions) is list:
            actions = tuple(self.actions)
        else:
            actions = self.actions

        return dict(
            id = self.id,
            router_id = self.router_id, 
            outbound = self.outbound,
            inbound = self.inbound,
            actions = actions,
            inbound_format = self.inbound_format,
            next_router_id = self.next_router_id,
            confirmation = self.confirmation,
            pre_actions = self.pre_actions,
            created = self.created,
            next_exchange_id = self.next_exchange_id,
            user_id = self.user_id,
        )
    
    def __repr__(self):
        return '<Exchange %r>' % self.router_id
    

class Point(db.Model, Base):
    value = db.Column(db.Integer, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('app_user.id'),
        nullable=False)
    user = db.relationship('AppUser',
        backref=db.backref('points', lazy=True))
    
    def __repr__(self):
        return f'<Point user={self.user_id}; value={self.value} >'
        