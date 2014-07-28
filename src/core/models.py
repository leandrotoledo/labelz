from google.appengine.ext import ndb

class Alias(ndb.Model):
    brand = ndb.StringProperty()
    part = ndb.StringProperty()

class Category(ndb.Model):
    title = ndb.StringProperty()
    
class Layout(ndb.Model):
    nx = ndb.IntegerProperty()
    ny = ndb.IntegerProperty()
    x0 = ndb.StringProperty()
    y0 = ndb.StringProperty()
    dx = ndb.StringProperty()
    dy = ndb.StringProperty()    

class Paper(ndb.Model):
    title = ndb.StringProperty()
    pwg_size = ndb.StringProperty()
    width = ndb.StringProperty()
    height = ndb.StringProperty() 

class Template(ndb.Model):
    brand = ndb.StringProperty()
    part = ndb.StringProperty()
    description = ndb.StringProperty()
    
    size = ndb.KeyProperty(kind=Paper)
    aliases = ndb.KeyProperty(kind=Alias, repeated=True)
    categories = ndb.KeyProperty(kind=Category, repeated=True)
    layouts = ndb.KeyProperty(kind=Layout, repeated=True)
    
def flush():
    for entry in ('Alias', 'Category', 'Layout', 'Paper', 'Template'):
        query = eval(entry).query()
        entries = query.fetch()
        ndb.delete_multi([ e.key for e in entries ])