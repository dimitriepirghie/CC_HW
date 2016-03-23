from google.appengine.ext import ndb


class Device(ndb.Model):
    device_owner = ndb.StringProperty()
    device_name = ndb.StringProperty()
    device_description = ndb.StringProperty()