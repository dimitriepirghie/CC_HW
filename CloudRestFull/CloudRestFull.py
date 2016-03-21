#!/usr/bin/env python
import os
from sqlalchemy import exc
from flask import abort, request, jsonify, g, make_response
from config import db, app, auth
from model.User import UserSchema, User
from model.Node import NodeSchema, Node
from model.Device import Device, DeviceSchema


def make_response(status_code, sub_code, message):
    response = jsonify({
        'status': status_code,
        'sub_code': sub_code,
        'message': message
    })
    response.status_code = status_code
    return response


@app.errorhandler(401)
def method_unauthorized_access(message):
    return make_response(405, 1, str(message))


@app.errorhandler(405)
def method_not_allow(message):
    return make_response(405, "None", str(message))


@auth.verify_password
def verify_password(username_or_token, password):
    user = User.verify_auth_token(username_or_token)
    if not user:
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False

    user.userNodes = Node.query.filter(Node.ownerId == user.id).all()
    g.user = user
    return True


@app.route('/api/user/register', methods=['POST'])
def new_user():
    if request.json:
        if "password" not in request.json or "username" not in request.json:
            return make_response(400, 6, "username and password json fields required")
        else:
            username = request.json.get('username')
            password = request.json.get('password')
    else:
        return make_response(400, 6, "Invalid request data")

    if User.query.filter_by(username=username).first() is not None:
        return make_response(409, 1, "Username already exists")
    else:
        user = User(username=username)
        user.hash_password(password)

        try:
            db.session.add(user)
            db.session.commit()

            return jsonify({'hypermedia': {
                'info': {
                    'resource': str('/api/user/' + str(user.id)),
                    'method': 'GET'
                },
                'self': {
                    'resource': str('/api/user' + str(user.id)),
                    'method': 'GET'
                }
            },
                'message': 'Created.'
            }), 201
        except Exception:
            return make_response(500, 2, "Database exception")


@app.route('/api/user/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    user_schema = UserSchema()
    result_user = user_schema.dump(user)

    if not user:
        return make_response(404, 0, "Not found")
    return jsonify(result_user.data)


@app.route('/api/user', methods=['GET'])
@auth.login_required
def user_info():
    g.user.userNodes = Node.query.filter(Node.ownerId == g.user.id).all()
    user_schema = UserSchema()
    nodes_schema = NodeSchema(many=True)

    result_user = user_schema.dump(g.user)
    result_nodes = nodes_schema.dump(g.user.userNodes)
    return jsonify({
        'user': result_user.data,
        'nodes': result_nodes.data
    })


@app.route('/api/node', methods=['GET'])
@auth.login_required
def get_user_nodes():
    nodes_schema = NodeSchema(many=True)
    user_nodes = Node.query.filter(Node.ownerId == g.user.id).all()
    result = nodes_schema.dump(user_nodes)
    return jsonify({'nodes': result.data})


@app.route('/api/user/delete/<int:id>', methods=['DELETE'])
@auth.login_required
def delete_user_admin(id):
    if not g.user.admin:
        abort(401)

    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'state : ': 'success'})


@app.route('/api/device/delete/<int:id>', methods=['DELETE'])
@auth.login_required
def device_delete(id):
    db_device = Device.query.filter(id == id).first()

    if not db_device:
        return make_response(404, 0, "Not found")

    node_id = db_device.node_id
    db_node = Node.query.filter_by(id=node_id).first()

    if g.user.id != db_node.ownerId:
        return make_response(401, 2, "Unauthorized")

    else:
        db.session.delete(db_device)
        try:
            db.session.commit()
            return make_response(200, 0, 'Succes.')
        except exc.SQLAlchemyError:
            return make_response(500, 2, "Database exception")


@app.route('/api/device/<int:id>', methods=['GET', 'PUT'])
@auth.login_required
def device_info(id):
    if request.method == 'PUT':
        return device_add()

    db_device = Device.query.filter(Device.id == id, Device.owner_id == g.user.id).first()

    if db_device:
        device_schema = DeviceSchema()
        result_device = device_schema.dump(db_device)
        return jsonify({'device': result_device.data,
                        'hypermedia': {
                            'self': {
                                'resource': str('/api/device/' + str(db_device.id)),
                                'method': 'GET'
                            },
                            'delete': {
                                'resource': str('/api/device/delete/' + str(db_device.id)),
                                'method': 'DELETE'
                            }
                        }
                        }), 200
    else:
        return make_response(404, 0, "Not found")


@app.route('/api/device', methods=['GET'])
@auth.login_required
def get_devices_info():
    devices_schema = DeviceSchema(many=True)
    user_devices = Device.query.filter(Device.owner_id == g.user.id).all()

    result_devices = devices_schema.dump(user_devices)
    return jsonify({'devices:', result_devices.data})


@app.route('/api/device/add', methods=['POST', 'PUT'])
@auth.login_required
def device_add():
    device_json = request.json.get('device')

    device_name = device_json['name']
    device_description = device_json['description']
    device_node_id = device_json['node_id']

    device = Device(name=device_name, description=device_description, node_id=device_node_id)
    device.owner_id = g.user.id

    db_device = Device.query.filter(Device.name == device_name, Device.node_id == device_node_id).first()

    if db_device is not None:
        if request.method == 'PUT':
            device_delete(db_device.id)
        else:
            return make_response(409, 1, str('device name `' +
                                             device_name + '` already exists in node ' + str(device_node_id)))

    try:
        db.session.add(device)
        db.session.commit()
    except exc.SQLAlchemyError:
        return make_response(500, 2, "Database exception")

    return jsonify({'hypermedia': {
        'self': {
            'resource': str('/api/device/' + str(device.id)),
            'method': 'GET'
        },
        'replace': {
            'resource': str('/api/device/' + str(device.id)),
            'method': 'PUT'
        },
        'delete': {
            'resource': str('/api/device/delete/' + str(device.id)),
            'method': 'DELETE'
        }
    },
        'message': 'Created.'}), 201


@app.route('/api/node/delete/<int:id>', methods=['DELETE'])
@auth.login_required
def node_remove(id):
    node = Node.query.filter(Node.id == id, Node.ownerId == g.user.id).first()

    if node:
        db.session.delete(node)
        try:
            db.session.commit()
            return jsonify({'message': 'success'}), 200

        except exc.SQLAlchemyError:
            return make_response(500, 2, "Database exception")

    else:
        return make_response(404, 0, "Not found")


@app.route('/api/node/add', methods=['PUT', 'POST'])
@auth.login_required
def node_add():

    if request.json:
        if ("node" in request.json) and ('name' not in request.json.get('node') or 'description' not in request.json.get('node')):
            return make_response(400, 6, "name and description json fields required")
        else:
            node_json = request.json.get('node')
            node_description = node_json['description']
            node_name = node_json['name']
    else:
         return make_response(400, 6, "Invalid request data")


    node = Node(name=node_name)
    node.ownerId = g.user.id
    node.description = node_description

    db_node = Node.query.filter(Node.name == node_name, Node.ownerId == g.user.id).first()

    if db_node:
        if request.method == 'PUT':
            node_remove(db_node.id)
        else:
            return make_response(409, 1, str("user " + g.user.username + ' already have node ' + node_name))

    try:
        db.session.add(node)
        db.session.commit()
    except exc.SQLAlchemyError:
        return make_response(500, 2, "Database exception")

    return jsonify({'hypermedia': {
        'self': {
            'resource': str('/api/node/' + str(node.id)),
            'method': 'GET'
        },
        'replace': {
            'resource': str('/api/node/' + str(node.id)),
            'method': 'PUT'
        },
        'delete': {
            'resource': str('/api/node/delete/' + str(node.id)),
            'method': 'DELETE'
        }
    },
        'message': 'Created.'}), 201


@app.route('/api/node/<int:id>', methods=['GET', 'PUT'])
@auth.login_required
def node_info(id):
    if request.method == 'PUT':
        return node_add()

    db_node = Node.query.filter(Node.id == id, Node.ownerId == g.user.id).first()
    if db_node:
        node_schema = NodeSchema()
        result_node = node_schema.dump(db_node)
        return jsonify({'node': result_node.data}), 200
    else:
        return make_response(404, 0, "Not found")


if __name__ == '__main__':
    if not os.path.exists('db.sqlite'):
        db.create_all()
    app.run(debug=True)
