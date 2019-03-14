from datetime import datetime as dt
from flask import current_app
from sqlalchemy import func, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects import postgresql

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
    google_id =  db.Column(db.String(128), unique=True)
    device_token = db.Column(db.String(128), unique=False)
    firebase_token = db.Column(db.String(256), unique=False)

    def to_dict(self):
        return dict(
            id = self.id, 
            username = self.username,
            phone_number = self.phone_number,
            timezone = self.timezone,
            created = self.created
        )

    def __repr__(self):
        return '<AppUser %r>' % self.username


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
    due_date = db.Column(db.DateTime(timezone=False), nullable=False)
    active = db.Column(db.Boolean, nullable=False)
    grade = db.Column(db.Integer)
    exchange_id = db.Column(db.Integer, db.ForeignKey('exchange.id'))
    points_earned = db.Column(db.Integer)

    exchange = db.relationship('Exchange', backref=db.backref('tasks', lazy=True))
    user_id = db.Column(db.Integer, db.ForeignKey('app_user.id'), nullable=False)
    user = db.relationship('AppUser', backref=db.backref('tasks', lazy=True))

    def to_dict(self):
        return dict(
            task_id=self.id,
            description=self.description,
            due_date=self.due_date,
            grade=self.grade,
            points_earned=self.points_earned
        )
    
    def __repr__(self):
        return f'<Task {self.description[:10]}>'


class Team(db.Model, Base):
    founder_id = db.Column(db.Integer, db.ForeignKey('app_user.id'), nullable=False)
    name = db.Column(db.String(32), nullable=False)

    founder = db.relationship('AppUser', backref=db.backref('teams', lazy=True))

    def to_dict(self):
        return dict(
            id = self.id,
            name = self.name,
            # members = self.members)
        )

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
            username = self.user.username,
            user_id = self.user_id,
            member_id = self.id,
            team_id = self.team_id,
            # tasks = self.user.tasks,
            inviter_id = self.inviter_id,
            status = self.status)


    def __repr__(self):
        return f"<TeamMember {self.user} team={self.team} >"


class Feedback(db.Model, Base):
    user_id = db.Column(db.Integer, db.ForeignKey('app_user.id'), nullable=False)
    text = db.Column(db.String(612), nullable=False)

    user = db.relationship('AppUser', foreign_keys=[user_id], backref=db.backref('feedback', lazy=True))