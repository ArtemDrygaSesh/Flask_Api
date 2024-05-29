from enum import Enum
from app import db, bcrypt

class Status(Enum):
    pending = "Pending"
    in_review = "In review"
    closed = "Closed"

class Role(Enum):
    admin = 'Admin'
    manager = 'Manager'
    analyst = 'Analyst'

class Group(Enum):
    dev = 'Dev'
    security = 'Security Team'
    qa = 'QA'


'''
It was decided to make a field for both users and groups, 
as it is more convenient to assign groups, but sometimes it is necessary to assign only a user, 
and it is not reasonable to add him to a group for this reason
'''

tickets_users = db.Table('tickets_users',
                db.Column('ticket_id', db.Integer, db.ForeignKey('ticket.id')),
                db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

tickets_groups = db.Table('tickets_groups',
                db.Column('ticket_id', db.Integer, db.ForeignKey('ticket.id')),
                db.Column('group_id', db.Integer, db.ForeignKey('group.id'))
)

users_groups = db.Table('users_groups',
                db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                db.Column('group_id', db.Integer, db.ForeignKey('group.id'))
)


class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Enum(Status).values_callable)
    note = db.Column(db.Text)

    def __init__(self, status, note):
        self.status = status
        self.note = note

    def __repr__(self):
        return '<Ticket {}>'.format(self.id)


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Enum(Group).values_callable)
    tickets = db.relationship('Ticket', secondary=tickets_groups, backref='assigned_groups')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Group {}>'.format(self.name)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum(Role).values_callable)
    tickets = db.relationship('Ticket', secondary=tickets_users, backref='assigned_users')
    groups = db.relationship('Group', secondary=users_groups, backref='members')

    def __init__(self, username, password, role):
        self.username = username
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        self.role = role

    def __repr__(self):
        return '<User {}>'.format(self.username)






