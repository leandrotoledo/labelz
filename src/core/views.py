import os
import csv
import cgi
import webapp2
import jinja2

from management import GlabelsParser, BlobIterator
from models import Alias, Template
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + '/../templates'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        upload_url = blobstore.create_upload_url('/upload')
        
        templates = Template.query().order(Template.key).fetch()
        aliases = Alias.query().order(Template.key).fetch()
        templates.extend(aliases)
        templates = [ t.key.string_id() for t in templates ]
        templates.sort()
        
        template = JINJA_ENVIRONMENT.get_template('form.html')
        self.response.write(template.render({'upload_url': upload_url,
                                             'templates': templates}))
        
class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        csvfile = self.get_uploads('label-upload')
        key = cgi.escape(self.request.get('label-type'))

        if key and csvfile:
            t = Template.get_by_id(key) or Alias.get_by_id(key)
            if t.__class__ == Alias:
                t = Template.query(Template.aliases == t.key).fetch()
    
            blob = csvfile[0]
            iterator = BlobIterator(blobstore.BlobReader(blob.key()))

            labels = list()
            for row in csv.reader(iterator):
                if row: labels.append(row)
            
            blobstore.delete(blob.key())
    
            template = JINJA_ENVIRONMENT.get_template('labels.html')
            self.response.write(template.render({'key': t.key.string_id(),
                                                 'labels': labels,
                                                 'labels_per_page': 33}))

class CssHandler(webapp2.RequestHandler):
    def get(self, key):
        key = key.replace('.css', '')
        
        t = Template.get_by_id(key) or Alias.get_by_id(key)
        if t.__class__ == Alias:
            t = Template.query(Template.aliases == t.key).fetch()
        
        template = JINJA_ENVIRONMENT.get_template('css/template.css')
        self.response.write(template.render({'name': t.key.string_id(),
                                             'width': 100}))

class ImportHandler(webapp2.RequestHandler):
    def get(self):
        GlabelsParser()
        self.response.write(u'Importado com sucesso!')
        
app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/upload', UploadHandler),
    (r'/css/(.*)', CssHandler),
    ('/import', ImportHandler)
], debug=True)