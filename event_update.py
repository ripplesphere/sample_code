import os
import json
import jinja2
import webapp2
from google.appengine.ext import ndb
import pdb # pdb.set_trace()
import logging
from models import Event
from models import Person
from models import Photo
from datetime import date

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(
       os.path.join(os.path.dirname(__file__),'../views')),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class EventUpdate(webapp2.RequestHandler):

# drive.files().list(q="'root' in parents and title contains 'CaptureEvent'").execute()['items']
# q="sharedWithMe"

    def post(self):
       user_id = self.request.get('user_id')
       event_id = self.request.get('event_id')
       event = Event.get_by_id(int(event_id))
       operation = self.request.get('operation')
       if (operation == "load"):
          if (user_id == event.userId):

             template_values = {
                 'event': event
             }

             template = JINJA_ENVIRONMENT.get_template('event_update.html')
             self.response.write(template.render(template_values))
          else:
             template = JINJA_ENVIRONMENT.get_template('index.html')
             self.response.write(template.render())
       elif (operation == "people_for_event"):
            user_id = self.request.get('user_id')
            event_id = int(self.request.get('event_id'))
            event = Event.get_by_id(event_id)

            event_people = []
            for person_id in event.event_people:
                person = Person.get_by_id(int(person_id))
                event_people.append({"person_id": person_id, "display_name": person.display_name,
                                   "image_url": person.image_url })
            event_people_set = set(event.event_people)

            person_keys = (Person.query(Person.userId == user_id).fetch(keys_only=True))
            all_people = []
            for key in person_keys:
                all_people.append(key.id())
            clean_people = [x for x in all_people if x not in event_people_set]
            all_people = []
            for person_id in clean_people:
                person = Person.get_by_id(int(person_id))
                all_people.append({"person_id": person_id, "display_name": person.display_name,
                                   "image_url": person.image_url })

            event_sharing_set = set(event.event_sharing)
            my_key = Person.query(Person.plus_id == user_id).get(keys_only=True)
            event_sharing_set.add(my_key.id())
            available_sharing = []
            for key in person_keys:
                available_sharing.append(key.id())
            clean_sharing = [x for x in available_sharing if x not in event_sharing_set]
            available_sharing = []
            for person_id in clean_sharing:
                person = Person.get_by_id(int(person_id))
                available_sharing.append({"person_id": person_id, "display_name": person.display_name,
                                           "image_url": person.image_url, "email": person.email })
            event_sharing = []
            for person_id in event.event_sharing:
                person = Person.get_by_id(int(person_id))
                event_sharing.append({"person_id": person_id, "display_name": person.display_name,
                                        "image_url": person.image_url, "email": person.email })

            ret_data = { "all_people": all_people, "event_people": event_people, 
                         "available_sharing": available_sharing, "event_sharing": event_sharing }

            self.response.write(json.dumps(ret_data))
       elif (operation == "photos_for_event"):
            user_id = self.request.get('user_id')
            event_id = self.request.get('event_id')
            event = Event.get_by_id(int(event_id))

            photo_keys = (Photo.query(Photo.userId == user_id).fetch(keys_only=True))
            event_photos_set = set(event.event_photos)

            event_photos = []
            for photo_id in event.event_photos:
                photo = Photo.get_by_id(int(photo_id))
                event_photos.append({"photo_id": photo_id, "drive_id": photo.drive_id, 
                                       "thumbnailLink": photo.thumbnailLink })

            all_photos = []
            for photo_key in photo_keys:
                all_photos.append(photo_key.id())
            clean_photos = [x for x in all_photos if x not in event_photos_set]

            all_photos = []
            for photo_id in clean_photos:
                photo = Photo.get_by_id(int(photo_id))
                all_photos.append({"photo_id": photo_id, "drive_id": photo.drive_id, 
                                     "thumbnailLink": photo.thumbnailLink })
            ret_data = { "all_photos": all_photos, "event_photos": event_photos }

            self.response.write(json.dumps(ret_data))
       elif (operation == "change_people"):
            person_id = int(self.request.get('person_id'))
            change_to = self.request.get('change_to')
            if (change_to == "connected"):
                event.event_people.append(person_id)
                event.put()
            else:
               if person_id in event.event_people:
                   event.event_people.remove(person_id)
                   event.put()
               else:
                   person = Person.get_by_id(person_id)
                   person.person_events.remove(event_id)
                   person.put()
       elif (operation == "change_photos"):
            photo_id = int(self.request.get('photo_id'))
            change_to = self.request.get('change_to')
            if (change_to == "connected"):
                event.event_photos.append(photo_id)
                event.put()
            else:
               event.event_photos.remove(photo_id)
               event.put()
               user_id = self.request.get('user_id')
               shared = self.request.get('shared_list')
               shared_list = shared.split(',') 
               if (len(shared_list)):
                   shared_list.pop()
               return_shared = "" 
               for person_id in shared_list:
                   eventsForShared = Event.query(Event.userId == user_id).filter(Event.event_sharing.IN([int(person_id)]))
                   if (eventsForShared.count() == 0):
                       return_shared += "%s," % (person_id)
               self.response.write(return_shared)
       elif (operation == "submit_update"):
            event_id = int(self.request.get('event_id'))
            event = Event.get_by_id(event_id)
            ce_date = date(year=int(self.request.get('ce_date_year')),
                    month=int(self.request.get('ce_date_month')),
                    day=int(self.request.get('ce_date_day')))
            event.title = self.request.get('ce_title')
            event.event_date = ce_date
            event.location = self.request.get('ce_location')
            event.description = self.request.get('ce_description')
            event.userId = self.request.get('ce_user_id')
            event.put()
       elif (operation == "change_sharing"):
            event_id = int(self.request.get('event_id'))
            person_id = int(self.request.get('person_id'))
            change = self.request.get('change')
            event = Event.get_by_id(event_id)
            if (change == "available"):
               event.event_sharing.append(person_id)
               event.put()
            else:
               event.event_sharing.remove(person_id)
               event.put()

