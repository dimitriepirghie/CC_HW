from flask import Flask, jsonify, request, Response
from Utils import MyEncoder
from google.appengine.api import users, mail
from google.appengine.ext import ndb
from Device import Device, DeviceData
import json
import logging

DEFAULT_USER_NAME = "awesome_user"

app = Flask(__name__)

login_response = ('<a href="%s">Sign in or register</a>.' %users.create_login_url('/'))


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


# TODO
@app.route('/api/user/register', methods=['GET'])
def login_required():
    if not users.get_current_user():
        return Response('<html><body>%s</body></html>' % login_response, mimetype='text/html')
    else:
        return "Hello " + users.get_current_user().email()


@app.route('/api/user/<int:id>', methods=['GET'])
def get_user(id):
    return make_response(404, 0, "Not found")


@app.route('/api/device/<device_name>', methods=['POST'])
def insert_new_data(device_name):
    user = users.get_current_user()
    if user:
        device_owner = user.user_id()
    else:
        return Response(login_response)

    device_json = request.json.get('device')
    device_data = device_json['data']
    device = Device.query(ndb.AND(Device.device_owner == device_owner, Device.device_name == device_name)).fetch()

    if len(device) == 0:
        return make_response(404, 1, "Device not found")
    device = device[0]

    new_data = DeviceData(device_data=device_data)
    device.device_data_records.append(new_data)
    device.put()
    logging.info(str("User " + device_owner + " updated device " + device_name))
    return make_response(201, 1, "Device updated")


@app.route('/api/device/add', methods=['POST', 'PUT'])
def device_add():
    user = users.get_current_user()
    if user:
        device_owner = user.user_id()
        device_owner_email = user.email()
    else:
        return Response(login_response)

    device_json = request.json.get('device')
    device_name = device_json['name']
    device_description = device_json['description']

    # if device name is key guarantees uniqueness in database
    device_name_key = ndb.Key(Device, device_name)
    device = Device(key=device_name_key, device_owner=device_owner, device_email=device_owner_email,
                    device_name=device_name,
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
        return make_response(201, 1, "Resource created")
    else:
        logging.error("Update data store error ?")
        make_response(500, 1, "Update data store error ?")


@app.route('/api/device', methods=['GET'])
def show_devices():
    user = users.get_current_user()
    if user:
        device_owner = user.user_id()
    else:
        return Response(login_response)

    logging.info("User " + device_owner + ' viewed devices list')
    return Response(json.dumps([p.to_dict() for p in Device.query(Device.device_owner == device_owner).fetch()],
                               cls=MyEncoder),
                    mimetype='application/json')


@app.route('/tasks/check_devices')
def check_devices():
    sender_address = "home-automation-platform@appspot.gserviceaccount.com"
    subject = "home-automation-platform devices update"
    body = "Every devices is ok"
    logging.info("Check devices availability ")
    mail.send_mail(sender_address, "ionut.pirghie@info.uaic.ro", subject, body)
    return 200


@app.route('/', methods=['GET'])
def hello_world():
    return 'Hello from home-automation-platform'


if __name__ == '__main__':
    app.run()
