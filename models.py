from google.appengine.ext import ndb

class Event(ndb.Model):
    userId = ndb.StringProperty()
    title = ndb.StringProperty()
    event_date = ndb.DateProperty()
    location = ndb.StringProperty(default='')
    description = ndb.TextProperty(default='')
    event_photos = ndb.IntegerProperty(repeated=True)
    event_people = ndb.IntegerProperty(repeated=True)
    event_sharing = ndb.IntegerProperty(repeated=True)

class Person(ndb.Model):
    userId = ndb.StringProperty()
    display_name = ndb.StringProperty()
    plus_id = ndb.StringProperty()
    image_url = ndb.StringProperty(default='/img/default_icon.png')
    email = ndb.StringProperty(default='')
    notes = ndb.TextProperty(default='')
    person_sharing = ndb.IntegerProperty(repeated=True)

class Photo(ndb.Model):
    userId = ndb.StringProperty()
    drive_id = ndb.StringProperty()
    thumbnailLink = ndb.StringProperty()
    title = ndb.StringProperty()
    location = ndb.StringProperty(default='')
    date_taken = ndb.StringProperty(default='')
    photo_id = ndb.StringProperty()
    notes = ndb.TextProperty(default='')
    photo_people = ndb.IntegerProperty(repeated=True)
    photo_sharing = ndb.IntegerProperty(repeated=True)
   
