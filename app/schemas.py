from marshmallow import fields
from app import db, ms
from .models import User, Group, Ticket

class TicketSchema(ms.SQLAlchemyAutoSchema):
    status = fields.String()
    assigned_groups = fields.List(fields.Nested(lambda: GroupSchema(only=("id", "name"))))
    assigned_users = fields.List(fields.Nested(lambda: UserSchema(only=("id", "username"))))

    class Meta:
        model = Ticket
        load_instance = True
        sqla_session = db.session
        include_fk = True

ticket_schema = TicketSchema()
tickets_schema = TicketSchema(many=True)


class UserSchema(ms.SQLAlchemyAutoSchema):
    role = fields.String()
    tickets = fields.List(fields.Nested(TicketSchema(only=("id", "status"))))
    groups = fields.List(fields.Nested(lambda: GroupSchema(only=("id", "name"))))

    class Meta:
        model = User
        load_instance = True
        sqla_session = db.session
        include_fk = True

user_schema = UserSchema()
users_schema = UserSchema(many=True)


class GroupSchema(ms.SQLAlchemyAutoSchema):
    name = fields.String()
    tickets = fields.List(fields.Nested(TicketSchema(only=("id", "status"))))
    members = fields.List(fields.Nested(UserSchema(only=("id", "username"))))

    class Meta:
        model = Group
        load_instance = True
        sqla_session = db.session
        include_fk = True

group_schema = GroupSchema()
groups_schema = GroupSchema(many=True)
