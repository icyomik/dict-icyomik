# coding:utf-8 #

# Project 'dict-icyomik@appspot.com' By:
# iCyOMiK(蒋骏):		http://icyomik.tk/
# David and Boyi:	http://yodao-free.sourceforge.net/

# 从 Google App Engine 导入一些该程序必要的模块
from google.appengine.api import xmpp
from google.appengine.api import urlfetch
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

# 对请求查询的语句以及从有道返回的数据进行正则处理，有以下函数：
# get_elements_by_path(xml, elem), get_elements(xml, elem), get_text(xml)
import re
single = re.compile("^[A-Z]+$", re.IGNORECASE)
textre = re.compile("\!\[CDATA\[(.*?)\]\]", re.DOTALL)

def get_elements_by_path(xml, elem):
	if type(xml) == type(''):
		xml = [xml]
	if type(elem) == type(''):
		elem = elem.split('/')
	if (len(xml) == 0):
		return []
	elif (len(elem) == 0):
		return xml
	elif (len(elem) == 1):
		result = []
		for item in xml:
			result += get_elements(item, elem[0])
		return result
	else:
		subitems = []
		for item in xml:
			subitems += get_elements(item, elem[0])
		return get_elements_by_path(subitems, elem[1:])

def get_elements(xml, elem):
	p = re.compile("<" + elem + ">" + "(.*?)</" + elem + ">", re.DOTALL)
	it = p.finditer(xml)
	result = []
	for m in it:
		result.append(m.group(1))
	return result

def get_text(xml):
	match = re.search(textre, xml)
	if not match:
		return xml
	return match.group(1)

# 以下的函数用于查询并将查询到的结果进行分析格式化
def crawl_xml(queryword):
	# 不是一个英文单词的时候执行翻译操作
	if single.match(queryword) == None:
		xml = urlfetch.fetch(
				"http://fanyi.youdao.com/translate?doctype=xml&xmlVersion=1.3&i=%s"
				% urlfetch.urllib2.quote(queryword))
		xml = xml.content
		translation = get_elements(xml, "translation")
		return get_text(translation[0])
	# 只是一个英文单词的时候使用字典查询
	else:
		results = ''
		asterisk = '-' * 25
		xml = urlfetch.fetch(
				"http://dict.yodao.com/search?doctype=xml&xmlDetail=true&q=%s"
				% urlfetch.urllib2.quote(queryword))
		xml = xml.content
		return_phrase = get_elements(xml, "return-phrase")
		# 如果没有查询到这个英文单词就返回下面的 if 语句
		if return_phrase == []:
			results = ":-( _CAN NOT FIND THE WORD:_ *" \
					+ get_text(get_elements(xml, "original-query")[0]) \
					+ "* :-("
			return results.strip()
		# 对查询到的英文单词进行格式化处理，然后返回到上层调用函数的位置
		return_phrase = get_text(return_phrase[0])
		phonetic_symbol = get_elements(xml, "phonetic-symbol")
		phonetic_symbol = get_text(phonetic_symbol[0])
		results = return_phrase + ' [' + phonetic_symbol + '] ' + '\n'
		custom_translations = get_elements(xml, "custom-translation")
		for cus in custom_translations:
			if get_text(get_elements(cus, "type")[0]) == 'ee':
				break
			contents = get_elements_by_path(cus, "translation/content")
			if contents:
				results = results + asterisk + '\n'
				for content in contents[0:]:
					results = results + get_text(content) + '\n'
		for cus in custom_translations:
			contents = get_elements_by_path(cus, "word-forms/word-form")
			if contents:
				results = results + asterisk + '\n'
				for content in contents[0:]:
					results = results + get_text(get_elements(content, 'name')[0]) \
							+ ':' + get_text(get_elements(content, 'value')[0]) + '\n'
		results = results + asterisk
		return results.strip()

# 以下的类用于接收用户提交的语句和返回结果给用户
class XMPPHandler(webapp.RequestHandler):
	def post(self):
		message = xmpp.Message(self.request.POST)
		results = crawl_xml(message.body.encode("utf-8"))
		message.reply(results)

# 以下语句相当于在主函数中的语句 （if __name__ == "__main__":）
application = webapp.WSGIApplication([('/_ah/xmpp/message/chat/', XMPPHandler)])
run_wsgi_app(application)

