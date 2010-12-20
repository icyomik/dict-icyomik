from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

class MainPage(webapp.RequestHandler):
	def get(self):
		self.redirect("http://code.google.com/p/dict-icyomik/")

application = webapp.WSGIApplication([('/.*', MainPage)])
run_wsgi_app(application)
