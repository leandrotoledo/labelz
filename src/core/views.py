import os
import webapp2
import jinja2

from models import flush

from import2 import parseTemplates, parsePaperSizeTemplate

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + '/../templates'),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        #flush()
        parsePaperSizeTemplate()
        parseTemplates()
        template = JINJA_ENVIRONMENT.get_template('main.html')
        self.response.write(template.render())
        
app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)