from google.appengine.ext import ndb

class Alias(ndb.Model):
    brand = ndb.StringProperty()
    part = ndb.StringProperty()

class Layout(ndb.Model):
    nx = ndb.IntegerProperty()
    ny = ndb.IntegerProperty()
    x0 = ndb.FloatProperty()
    y0 = ndb.FloatProperty()
    dx = ndb.FloatProperty()
    dy = ndb.FloatProperty()
    markup_margin = ndb.FloatProperty()
    width = ndb.FloatProperty()
    height = ndb.FloatProperty()

class Paper(ndb.Model):
    title = ndb.StringProperty()
    width = ndb.FloatProperty()
    height = ndb.FloatProperty() 

class Template(ndb.Model):
    brand = ndb.StringProperty()
    part = ndb.StringProperty()
    description = ndb.StringProperty()
    
    aliases = ndb.KeyProperty(kind=Alias, repeated=True)
    layout = ndb.KeyProperty(kind=Layout)
    paper = ndb.KeyProperty(kind=Paper)   
    
    @property
    def size(self):
        return (self.paper.get().width, self.paper.get().height) 
    
    @property
    def left_margin(self):
        return self.layout.get().x0
    
    @property
    def top_margin(self):
        return self.layout.get().y0
    
    @property
    def vertical_space(self):
        return self.layout.get().dy - self.layout.get().height

    @property
    def horizontal_space(self):
        return self.layout.get().dx - self.layout.get().width
    
    @property
    def label_dims(self):
        return (self.layout.get().nx, self.layout.get().ny)
    
    @property
    def label_width(self):
        return self.layout.get().width

    @property
    def label_height(self):
        return self.layout.get().height
    
    @property
    def label_margin(self):
        if self.layout.get().markup_margin < 0.05:
            return 0.05
        return self.layout.get().markup_margin
    
    @property
    def label_margin_right(self):
        return self.layout.get().dx - self.layout.get().width
    
def flush():
    for entry in ('Alias', 'Layout', 'Paper', 'Template'):
        query = eval(entry).query()
        entries = query.fetch()
        ndb.delete_multi([ e.key for e in entries ])