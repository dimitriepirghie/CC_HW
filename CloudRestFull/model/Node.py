import json, jsonschema
from config import db
from marshmallow import Schema, fields


class Node(db.Model):
    __tablename__ = 'nodes'
    id = db.Column(db.Integer, primary_key=True)
    ownerId = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(32), nullable=False)
    description = db.Column(db.String(256))
    __table_args__ = (db.UniqueConstraint('ownerId', 'name', name='node_node_ownerid_uc'),)


class NodeSchema(Schema):
    id = fields.Int(dump_only=True)
    ownerId = fields.Int(dump_only=True)
    name = fields.Str()
    description = fields.Str()


def validate_json_node(json_data):
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
