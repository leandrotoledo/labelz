import os
import webapp2
import jinja2

from management import GlabelsParser
from models import Alias, Template

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + '/../templates'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        templates = Template.query().order(Template.key).fetch()
        aliases = Alias.query().order(Template.key).fetch()
        templates.extend(aliases)
        templates = [ t.key.string_id() for t in templates ]
        templates.sort()
        
        template = JINJA_ENVIRONMENT.get_template('form.html')
        self.response.write(template.render({'templates': templates}))
    def post(self):
        pass
        
class CssHandler(webapp2.RequestHandler):
    def get(self, key):
        key = key.replace('.css', '')
        
        t = Template.get_by_id(key) or Alias.get_by_id(key)
        if t.__class__ == Alias:
            t = Template.query(Template.aliases == t.key).fetch()
        
        template = JINJA_ENVIRONMENT.get_template('css/default.css')
        self.response.write(template.render({'name': t.key.string_id(),
                                             'width': 100}))

class ImportHandler(webapp2.RequestHandler):
    def get(self):
        GlabelsParser()
        self.response.write(u'Importado com sucesso!')
        
app = webapp2.WSGIApplication([
    ('/', MainHandler),
    (r'/css/(.*)', CssHandler),
    ('/import', ImportHandler)
], debug=True)