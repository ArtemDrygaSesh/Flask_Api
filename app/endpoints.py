from sqlalchemy import or_
from app import app, db, bcrypt, auth
from flask import request, abort, make_response, jsonify
from .models import Ticket, User, Group, tickets_groups, users_groups
from .schemas import user_schema, users_schema, group_schema, groups_schema, ticket_schema, tickets_schema


#error handling
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(500)
def server_error(error):
    return make_response(jsonify({'error': 'Internal server error'}), 500)

@app.errorhandler(422)
def incorrect_input(error):
    return make_response(jsonify({'error': 'Unprocessable Entity'}), 422)

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)



#auth and roles check
@auth.verify_password
def verify_password(username, password):
    if password == '':
        return None
    user = User.query.filter(User.username == username).one_or_none()
    if user is not None and bcrypt.check_password_hash(user.password, password):
        return username
    else:
        return None

@auth.get_user_roles
def get_user_roles(username):
    user = User.query.filter(User.username == username).one_or_none()
    return user.role




#endpoints for tickets
@app.route('/auth/api/v1.0/tickets', methods=['GET'])
@auth.login_required(role=['Admin', 'Manager', 'Analyst'])
def get_tickets():
    user = User.query.filter(User.username == auth.current_user()).one_or_none()
    groups_id = [group.id for group in user.groups]

    tickets = Ticket.query.join(tickets_groups).join(Group).join(users_groups).filter(
        or_(
            Ticket.assigned_groups.any(Group.id.in_(groups_id)),
            Ticket.assigned_users.any(User.username == auth.current_user())
        )
    ).all()
    return tickets_schema.dump(tickets)

@app.route('/auth/api/v1.0/tickets/<id>', methods=['GET'])
@auth.login_required(role=['Admin', 'Manager', 'Analyst'])
def get_ticket(id):
    user = User.query.filter(User.username == auth.current_user()).one_or_none()
    groups_id = [group.id for group in user.groups]

    ticket = Ticket.query.join(tickets_groups).join(Group).join(users_groups).filter(
        or_(
            Ticket.assigned_groups.any(Group.id.in_(groups_id)),
            Ticket.assigned_users.any(User.id == user.id)
        )
    ).filter(Ticket.id == id).one_or_none()

    if ticket is not None:
        return ticket_schema.dump(ticket)
    else:
        abort(404)

@app.route('/auth/api/v1.0/tickets', methods=['POST'])
@auth.login_required(role=['Admin', 'Manager'])
def add_ticket():
    status = request.json.get('status')
    note = request.json.get('note')
    new_ticket = Ticket(status, note)
    db.session.add(new_ticket)
    db.session.commit()

    return ticket_schema.dump(new_ticket)


@app.route('/auth/api/v1.0/tickets/<id>', methods=['PUT'])
@auth.login_required(role=['Admin', 'Manager'])
def update_ticket(id):
    user = User.query.filter(User.username == auth.current_user()).one_or_none()
    groups_id = [group.id for group in user.groups]

    ticket = Ticket.query.join(tickets_groups).join(Group).join(users_groups).filter(
        or_(
            Ticket.assigned_groups.any(Group.id.in_(groups_id)),
            Ticket.assigned_users.any(User.id == user.id)
        )
    ).filter(Ticket.id == id).one_or_none()

    if ticket is not None:
        if 'status' in request.json:
            status = request.json.get('status')
            ticket.status = status
        if 'note' in request.json:
            note = request.json.get('note')
            ticket.note = note
        if 'assigned_groups' in request.json:
            groups_id = request.json.get('assigned_groups')
            groups = Group.query.filter(Group.id.in_(groups_id)).all()
            ticket.assigned_groups = groups
        if 'assigned_users' in request.json:
            users_id = request.json.get('assigned_users')
            users = User.query.filter(User.id.in_(users_id)).all()
            ticket.assigned_users = users

        db.session.commit()

        return ticket_schema.dump(ticket)
    else:
        abort(404)

@app.route('/auth/api/v1.0/tickets/<id>', methods=['DELETE'])
@auth.login_required(role=['Admin', 'Manager'])
def delete_ticket(id):
    user = User.query.filter(User.username == auth.current_user()).one_or_none()
    groups_id = [group.id for group in user.groups]

    ticket = Ticket.query.join(tickets_groups).join(Group).join(users_groups).filter(
        or_(
            Ticket.assigned_groups.any(Group.id.in_(groups_id)),
            Ticket.assigned_users.any(User.id == user.id)
        )
    ).filter(Ticket.id == id).one_or_none()

    if ticket is not None:
        db.session.delete(ticket)
        db.session.commit()
        return ticket_schema.dump(ticket)
    else:
        abort(404)



#endpoints for users
@app.route('/auth/api/v1.0/users', methods=['GET'])
def get_users():
    users = User.query.all()

    return users_schema.dump(users)

@app.route('/auth/api/v1.0/users/<id>', methods=['GET'])
def get_user(id):
    user = User.query.filter(User.id == id).one_or_none()
    if user is not None:
        return user_schema.dump(user)
    else:
        abort(404)

@app.route('/auth/api/v1.0/users', methods=['POST'])
def add_user():
    username = request.json.get('username')
    password = request.json.get('password')
    role = request.json.get('role')
    new_user = User(username, password, role)
    db.session.add(new_user)
    db.session.commit()

    return user_schema.dump(new_user)


@app.route('/auth/api/v1.0/users/<id>', methods=['PUT'])
def update_user(id):
    user = User.query.filter(User.id == id).one_or_none()
    if user is not None:
        if 'username' in request.json:
            username = request.json.get('username')
            user.username = username
        if 'password' in request.json:
            password = request.json.get('password')
            user.password = bcrypt.generate_password_hash(password).decode('utf-8')
        if 'role' in request.json:
            role = request.json.get('role')
            user.role = role
        if 'tickets' in request.json:
            tickets_id = request.json.get('tickets')
            tickets = Ticket.query.filter(Ticket.id.in_(tickets_id)).all()
            user.tickets = tickets
        if 'groups' in request.json:
            groups_id = request.json.get('groups')
            groups = Group.query.filter(Group.id.in_(groups_id)).all()
            user.groups = groups

        db.session.commit()
        return user_schema.dump(user)
    else:
        abort(404)

@app.route('/auth/api/v1.0/users/<id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.filter(User.id == id).one_or_none()
    if user is not None:
        db.session.delete(user)
        db.session.commit()
        return user_schema.dump(user)
    else:
        abort(404)



#endpoints for groups
@app.route('/auth/api/v1.0/groups', methods=['GET'])
def get_groups():
    groups = Group.query.all()

    return groups_schema.dump(groups)

@app.route('/auth/api/v1.0/groups/<id>', methods=['GET'])
def get_group(id):
    group = Group.query.filter(Group.id == id).one_or_none()
    if group is not None:
        return group_schema.dump(group)
    else:
        abort(404)

@app.route('/auth/api/v1.0/groups', methods=['POST'])
def add_group():
    name = request.json.get('name')
    new_group = Group(name)
    db.session.add(new_group)
    db.session.commit()
    return group_schema.dump(new_group)


@app.route('/auth/api/v1.0/groups/<id>', methods=['PUT'])
def update_group(id):
    group = Group.query.filter(Group.id == id).one_or_none()
    if group is not None:
        if 'name' in request.json:
            name = request.json.get('name')
            group.name = name
        if 'tickets' in request.json:
            tickets_id = request.json.get('tickets')
            tickets = Ticket.query.filter(Ticket.id.in_(tickets_id)).all()
            group.tickets = tickets
        if 'members' in request.json:
            users_id = request.json.get('members')
            users = User.query.filter(User.id.in_(users_id)).all()
            group.members = users

        db.session.commit()
        return group_schema.dump(group)
    else:
        abort(404)

@app.route('/auth/api/v1.0/groups/<id>', methods=['DELETE'])
def delete_group(id):
    group = Group.query.filter(Group.id == id).one_or_none()
    if group is not None:
        db.session.delete(group)
        db.session.commit()
        return group_schema.dump(group)
    else:
        abort(404)