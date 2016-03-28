from google.appengine.ext import ndb


class User(ndb.Model):
    identity = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)


class DeviceData(ndb.Model):
    device_data = ndb.StringProperty()
    update_time = ndb.DateTimeProperty(auto_now_add=True)


class Device(ndb.Model):
    device_owner = ndb.StringProperty()
    device_email = ndb.StringProperty()
    device_name = ndb.StringProperty()
    device_description = ndb.StringProperty()
    device_alert_timeout = ndb.IntegerProperty()
    device_data_records = ndb.StructuredProperty(DeviceData, repeated=True)
