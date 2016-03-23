from google.appengine.ext import ndb


class DeviceData(ndb.Model):
    device_data = ndb.StringProperty()


class Device(ndb.Model):
    device_owner = ndb.StringProperty()
    device_name = ndb.StringProperty()
    device_description = ndb.StringProperty()
    device_data_records = ndb.StructuredProperty(DeviceData, repeated=True)
