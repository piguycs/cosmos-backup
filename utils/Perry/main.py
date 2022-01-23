from utils.Perry import component, pageView, Composite, style

# Create our pages, we want them to inherit pageView behaviour. 
# As well as other components
Homepage = component(pageView, _Inherit = True)

from utils.Perry import ComponentSource, pageView
from utils.Perry.Perry.components import Label

HomepageContents = ComponentSource(
  Label('Cosmos is live!','p')
)

# Assign page contents
Homepage <= {
  'title': 'Home',
  'path':'',
  'styles': [],
  'DOM': pageView.DOM,
  'components': HomepageContents
}

Pages = Composite(Homepage)

# Flask
from flask import Flask, render_template
app = Flask(__name__)

def ext_serve(port, debug, host, pages):
  
  routes = [ ['/'+page['path'], page['func']] for page in pages]
  
  for route, func in routes:
    print('[Flask] Mapped route',route,'with',func)
    view_func = app.route(route)(func)
  
  app.run(debug=debug, port=port, host=host)


class _Serve:
  def __init__(self, _Pages: 'Composite class of pages', debug=False, port=8080, host='0.0.0.0'):
    ext_serve(debug=debug, port=port, host=host, pages=_Pages.pages)


from threading import Thread
def run(Pages):
    server = Thread(target=_Serve, args=[Pages])
    server.start()

# Multiple types of serving the pages are supported
# 
'Flask'
# from PerryFlask import serve
# Serve our pages as a composite collection
run(Pages)