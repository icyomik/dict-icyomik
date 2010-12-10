from google.appengine.api import xmpp;
from google.appengine.api import urlfetch;
from google.appengine.ext import webapp;
from google.appengine.ext.webapp.util import run_wsgi_app;

import re; textre = re.compile("\!\[CDATA\[(.*?)\]\]", re.DOTALL);

def get_text(xml):
	match = re.search(textre, xml);
	if not match:
		return xml;
	return match.group(1);

def get_elements(xml, elem):
	p = re.compile("<" + elem + ">" + "(.*?)</" + elem + ">", re.DOTALL);
	it = p.finditer(xml);
	result = [];
	for m in it:
		result.append(m.group(1));
	return result;

def crawl_xml(queryword):
	xml_file = urlfetch.fetch(
				"http://fanyi.youdao.com/translate?doctype=xml&xmlVersion=1.3&i=%s" %
				urlfetch.urllib2.quote(queryword));
	return xml_file.content;

class XMPPHandler(webapp.RequestHandler):
	def post(self):
		message = xmpp.Message(self.request.POST);
		xml = crawl_xml(message.body.encode("utf8"));
		translation = get_text(get_elements(xml, "translation")[0]);
		message.reply(translation);

application = webapp.WSGIApplication([('/_ah/xmpp/message/chat/', XMPPHandler)]);

if __name__ == "__main__":
	run_wsgi_app(application);

