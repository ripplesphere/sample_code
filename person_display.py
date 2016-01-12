import os
import json
import jinja2
import webapp2
from google.appengine.ext import ndb
from models import Person

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(
       os.path.join(os.path.dirname(__file__),'../views')),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class PersonDisplay(webapp2.RequestHandler):

    def get(self,person_id):

      person = Person.get_by_id(int(person_id))

      variables = {
        'person': person
        }

      template = JINJA_ENVIRONMENT.get_template('person_display.html')
      self.response.write(template.render(variables))

