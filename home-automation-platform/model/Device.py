from google.appengine.ext import ndb


class Device(ndb.Model):
    device_name = ndb.StringProperty()
    device_data = ndb.StringProperty()