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
        
        templates, aliases = Template.query().order(Template.key).fetch(), Alias.query().order(Template.key).fetch()
        #templates.extend(aliases)
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
                t = Template.query(Template.aliases == t.key).fetch()[0]
    
            blob = csvfile[0]
            iterator = BlobIterator(blobstore.BlobReader(blob.key()))

            labels = list()
            for row in csv.reader(iterator):
                if row: labels.append(row)
            
            blobstore.delete(blob.key())
    
            template = JINJA_ENVIRONMENT.get_template('labels.html')
            self.response.write(template.render({'key': t.key.string_id(),
                                                 'labels': labels,
                                                 'labels_per_page': int(t.layout.get().nx * t.layout.get().ny),
                                                 'label_orientation': cgi.escape(self.request.get('label-orientation')),
                                                 'label_font-size:': cgi.escape(self.request.get('label-font-size'))}))
        else:
            self.redirect('/') #TODO

class CssHandler(webapp2.RequestHandler):
    def get(self, key):
        key = key.replace('.css', '')
        
        t = Template.get_by_id(key) or Alias.get_by_id(key)
        if t.__class__ == Alias:
            t = Template.query(Template.aliases == t.key).fetch()[0]
        
        template = JINJA_ENVIRONMENT.get_template('css/template.css')
        self.response.headers['Content-Type'] = 'text/css'
        self.response.write(template.render({'name': t.key.string_id(),
                                             'paper_width': t.size[0],
                                             'left_margin': t.left_margin,
                                             'top_margin': t.top_margin,
                                             'label_width': t.label_width - t.label_margin,
                                             'label_height': t.label_height - t.label_margin,
                                             'vertical_space': t.vertical_space,
                                             'horizontal_space': t.horizontal_space,
                                             'label_margin': t.label_margin,
                                             'dx': t.layout.get().dx,
                                             'dy': t.layout.get().dy,}))

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