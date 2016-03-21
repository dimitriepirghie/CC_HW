import json, jsonschema
from config import db
from marshmallow import Schema, fields


class Device(db.Model):
    __tablename__ = 'devices'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), index=True)
    description = db.Column(db.String(256))
    node_id = db.Column(db.Integer, db.ForeignKey('nodes.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


class DeviceSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    description = fields.Str()
    node_id = fields.Int(dump_only=True)


def validate_json_device(json_data):
    schema = open('/home/dimitrie/PycharmProjects/CloudRestFull/schema_device.json').read()

    try:
        jsonschema.validate(json.loads(json_data), json.loads(schema))
    except jsonschema.ValidationError as e:
        print e.message
        return False
    except jsonschema.SchemaError as e:
        print e.message
        return False
    return True
