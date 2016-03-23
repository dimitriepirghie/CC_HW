from flask import Flask, jsonify, request, redirect
from google.appengine.api import users
from google.appengine.ext import ndb
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
        user = users.get_current_user()
        if user.email() in USERS:
            return "Ok"
        else:
            return "!Ok"
            



@app.route('/api/user/<int:id>', methods=['GET'])
def get_user(id):
    #user = User.query.get(id)
    #user_schema = UserSchema()
    #result_user = user_schema.dump(user)

    #if not user:
    return make_response(404, 0, "Not found")
    #return jsonify(result_user.data)


@app.route('/api/device/add', methods=['POST', 'PUT'])
@auth.login_required
def device_add():
    device_json = request.json.get('device')
    device_name = device_json['name']
    device_description = device_json['description']


@app.route('/', methods=['GET'])
def hello_world():
    return 'Hello World!'

if __name__ == '__main__':
    app.run()
