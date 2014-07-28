from core.models import Template, Category, Alias, Layout, Paper, flush

from os import listdir
from os.path import dirname, isfile, join
from xml.dom.minidom import parseString

GLABELS_TEMPLATES = dirname(__file__) + '/../../static/templates' 
GLABELS_PAPER_SIZE_TEMPLATE = dirname(__file__) + '/../../static/paper-sizes.xml'

class GlabelsParser(object):
    def __init__(self):
        self._import()
        
    def _import(self):
        flush() # Flush all data
        self.parsePaperSizeTemplate()
        self.parseTemplates()

    def parsePaperSizeTemplate(self):
        with open(GLABELS_PAPER_SIZE_TEMPLATE, 'r') as xmlfile:
            data = xmlfile.read()
            dom = parseString(data)
            
            for papersize in dom.getElementsByTagName('Paper-size'):
                ps = self.parsePaperSize(papersize)
                ps = Paper.get_or_insert(ps['id'], **ps)
                ps.put()
    
    def parsePaperSize(self, papersize):
        attrs = { x: papersize.getAttribute(x) for x in ('id', '_name', 'pwg_size', 'width', 'height')}
        attrs['title'] = attrs.pop('_name')
         
        return attrs
    
    def parseTemplates(self):
        files = [ f for f in listdir(GLABELS_TEMPLATES) if isfile(join(GLABELS_TEMPLATES, f))]
    
        for f in files:
            with open(join(GLABELS_TEMPLATES, f), 'r') as xmlfile:
                data = xmlfile.read()
                dom = parseString(data)
                
                for template in dom.getElementsByTagName('Template'):
                    t = self.parseTemplate(template)
                    t = Template.get_or_insert('-'.join((t['brand'], t['part'])), 
                                               **t)
                     
                    for category in [c['title'] for c in self.parseCategory(template)]:
                        try:
                            t.categories.append(Category.get_or_insert(category, 
                                                                       title=category).key)
                        except ValueError:
                            pass 
                    
                    for alias in self.parseAlias(template):
                        t.aliases.append(Alias.get_or_insert('-'.join((alias['brand'], alias['part'])),
                                                             **alias).key)
                    
                    for layout in self.parseLayout(template):
                        t.layouts.append(Layout(**layout).put())
                    
                    t.put()
            
    def parseTemplate(self, template): 
        attrs = { x: template.getAttribute(x) for x in ('brand', 'part', 'size', '_description')}
        attrs['description'] = attrs.pop('_description')
        attrs['size'] = Paper.get_or_insert(attrs['size']).key
         
        return attrs
    
    def parseCategory(self, template):
        attrs = list()
        for category in template.getElementsByTagName('Meta'):
            attrs.append({'title': category.getAttribute('category')})
        
        return attrs
    
    def parseAlias(self, template):
        attrs = list()
        for alias in template.getElementsByTagName('Alias'):
            attrs.append({'brand': alias.getAttribute('brand'), 
                          'part': alias.getAttribute('part')})
        return attrs
    
    def parseLayout(self, template):
        attrs = list()
        for layout in template.getElementsByTagName('Layout'):
            attrs.append({'nx': int(layout.getAttribute('nx')),
                          'ny': int(layout.getAttribute('ny')),
                          'x0': layout.getAttribute('x0'),
                          'y0': layout.getAttribute('y0'),
                          'dx': layout.getAttribute('dx'),
                          'dy': layout.getAttribute('dy')})
        return attrs