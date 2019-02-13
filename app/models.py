from datetime import datetime as dt
from flask import current_app
from sqlalchemy import func, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects import postgresql
from passlib.hash import pbkdf2_sha256
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

from app import db
from app.constants import Reserved, Sizes

class Base:
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=func.now(), server_default=func.now())
    updated = db.Column(db.DateTime, nullable=False, default=func.now(), server_default=func.now(), onupdate=func.current_timestamp())

Base = declarative_base(cls=Base)


class AppUser(db.Model, Base):
    username = db.Column(db.String(64), default=Reserved.NEW_USER)
    phone_number = db.Column(db.String(32), unique=True)
    timezone = db.Column(db.String(32))
    google_id =  db.Column(db.String(128), unique=True, nullable=False)

    # source: https://blog.miguelgrinberg.com/post/restful-authentication-with-flask/page/3
    def generate_auth_token(self, expiration = 600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in = expiration)
        return s.dumps({ 'id': self.id })

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user = AppUser.query.get(data['id'])
        return user

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
    router = db.Column(db.String(32), nullable=False)
    day_of_week = db.Column(db.String(32)) 
    hour = db.Column(db.Integer, nullable=False)
    minute = db.Column(db.Integer, nullable=False)
    active = db.Column(db.Boolean, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('app_user.id'),
        nullable=False)
    user = db.relationship('AppUser',
        backref=db.backref('notifications', lazy=True))

    __table_args__ = (UniqueConstraint('user_id', 'router', 'active', name='unique_router_user_active'),)
    
    def to_dict(self):
        return dict(
            router = self.router,
            day_of_week = self.day_of_week, 
            hour = self.hour,
            minute = self.minute,
            active = self.active)


    def __repr__(self):
        return '<Notification %r>' % self.router


class Exchange(db.Model, Base):
    router = db.Column(db.String(32), nullable=False)
    outbound = db.Column(db.String(Sizes.INBOUND_MAX_LENGTH))
    inbound = db.Column(db.String(Sizes.INBOUND_MAX_LENGTH))
    confirmation = db.Column(db.String(128))
    next_router = db.Column(db.String(32))
    next_exchange_id = db.Column(db.Integer) # this needs to be nullable because it is not known when an exchange is first created

    user_id = db.Column(db.Integer, db.ForeignKey('app_user.id'),
        nullable=False)
    user = db.relationship('AppUser',
        backref=db.backref('exchanges', lazy=True))
    
    def to_dict(self):
        return dict(
            id = self.id,
            router = self.router, 
            outbound = self.outbound,
            inbound = self.inbound,
            confirmation = self.confirmation,
            next_router = self.next_router,
            next_exchange_id = self.next_exchange_id,
            user_id = self.user_id,
            created = self.created,
            updated = self.updated
        )
    
    def __repr__(self):
        return '<Exchange %r>' % self.router
    

class Point(db.Model, Base):
    value = db.Column(db.Integer, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('app_user.id'),
        nullable=False)
    user = db.relationship('AppUser',
        backref=db.backref('points', lazy=True))
    
    def __repr__(self):
        return f'<Point user={self.user_id}; value={self.value}>'


class Task(db.Model, Base):
    description = db.Column(db.String(612), nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    active = db.Column(db.Boolean, nullable=False)

    exchange_id = db.Column(db.Integer, db.ForeignKey('exchange.id'), nullable=False)
    exchange = db.relationship('Exchange', backref=db.backref('tasks', lazy=True))

    user_id = db.Column(db.Integer, db.ForeignKey('app_user.id'), nullable=False)
    user = db.relationship('AppUser', backref=db.backref('tasks', lazy=True))
    
    def __repr__(self):
        return f'<Task {self.description[:10]}>'


class Team(db.Model, Base):
    founder_id = db.Column(db.Integer, db.ForeignKey('app_user.id'), nullable=False)
    name = db.Column(db.String(32), nullable=False)

    founder = db.relationship('AppUser', backref=db.backref('teams', lazy=True))

    def to_dict(self):
        return dict(
            id = self.id,
            founder_id = self.founder_id,
            name = self.name)

    def __repr__(self):
        return f"<Team {self.name}>"


class TeamMember(db.Model, Base):
    user_id = db.Column(db.Integer, db.ForeignKey('app_user.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    inviter_id = db.Column(db.Integer, db.ForeignKey('app_user.id'), nullable=False)
    status = db.Column(db.String(32), nullable=False)

    user = db.relationship('AppUser', foreign_keys=[user_id], backref=db.backref('is_member', lazy=True))
    team = db.relationship('Team', backref=db.backref('members', lazy=True))
    inviter = db.relationship('AppUser', foreign_keys=[inviter_id], backref=db.backref('inviter', lazy=True))

    def to_dict(self):
        return dict(
            user_id = self.user_id,
            team_id = self.team_id,
            inviter_id = self.inviter_id,
            status = self.status)


    def __repr__(self):
        return f"<TeamMember {self.user} team={self.team} >"
