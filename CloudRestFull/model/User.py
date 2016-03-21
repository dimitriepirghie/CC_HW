from marshmallow import Schema, fields
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature)
from config import app, db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(64))
    admin = db.Column(db.Boolean)
    userNodes = []

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=300):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dump({'id:': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        user = User.query.get(data['id'])
        return user


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str()
    # password_hash = fields.Str()
    admin = fields.Boolean()
