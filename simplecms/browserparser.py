


#'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36'

resultaatstring = {'platform':False,'browser':False, 'mobile':False}
platform = ['Mac', 'Win','Linux','FreeBSD']
mobile = ['Android','iPad','iPod','iPhone','PlayBook','BlackBerry','mobi']
browser = ['Crome','Safari','Opera','Firefox']

def detect(browser):
	d = Browserparser(browser)
	return d.detect()

class Browserparser:

	def __init__(self, browserstring):
		self.string = browserstring
		self.gevonden = resultaatstring


	def heeft(self, zoekterm, type):
		if self.string.find(zoekterm) >1:
			self.gevonden[type] = zoekterm
			return True
		else:
			return False

	def detect(self):
		for x in platform:
			if self.heeft(x, 'platform'):
				a = 1
				pass
		for x in browser:
			if self.heeft(x, 'browser'):
				a = 1
				pass

		for x in mobile:
			if self.heeft(x, 'mobile'):
				a = 1 
				pass
		return self.gevonden