from flask import Flask, jsonify, request, redirect, Response
from google.appengine.api import users
from google.appengine.ext import ndb
from Device import Device
import json
import logging

app = Flask(__name__)


class User(ndb.Model):
    identity = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)


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


@app.route('/api/user/register', methods=['GET'])
def login_required():
    if not users.get_current_user():
        return redirect(users.create_login_url(request.url))
    else:
        # user = users.get_current_user()
        return "ok"


@app.route('/api/user/<int:id>', methods=['GET'])
def get_user(id):
    return make_response(404, 0, "Not found")


@app.route('/api/device/add', methods=['POST', 'PUT'])
def device_add():
    device_json = request.json.get('device')
    device_name = device_json['name']
    device_description = device_json['description']
    device_owner = "test_o"

    # if device name is key guarantees uniqueness in database
    device_name_key = ndb.Key(Device, device_name)
    device = Device(key=device_name_key, device_owner=device_owner, device_name=device_name,
                    device_description=device_description)

    logging_message = str('User ' + device_owner)
    if request.method == 'POST' and Device.query(Device.device_owner == device_owner).fetch():
        logging_message += " tried to add existing device"
        logging.info(logging_message)
        return make_response(409, 1, "Device name exists")

    put_return = device.put()  # Device.get_or_insert(device_name)

    if put_return:
        logging_message += (" added device " + device_name)
        logging.info(logging_message)
        return str(put_return)
    else:
        logging.error("Update data store error ?")
        make_response(500, 1, "Update data store error ?")


@app.route('/api/device', methods=['GET'])
def show_devices():
    device_owner = "test_o"
    # owner_devices = Device.query(Device.device_owner == device_owner).fetch()

    return Response(json.dumps([p.to_dict() for p in Device.query(Device.device_owner == device_owner).fetch()]), mimetype='application/json')


@app.route('/', methods=['GET'])
def hello_world():
    return 'Hello from home-automation-platform'


if __name__ == '__main__':
    app.run()
