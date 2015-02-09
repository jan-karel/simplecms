#!/bin/env python
# -*- coding: utf-8 -*-

"""
 Browser detection

 SimpleCMS
 a simplistic, minimal not-so-full stack webframework

 Copyright Jan-Karel Visser - all rights are reserved
 Licensed under the LGPLv3 (http://www.gnu.org/licenses/lgpl.html)

 This program is distributed in the hope that it will be useful, but
 WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

"""

os = ['Mac', 'Windows', 'Linux', 'BSD']
mobile = ['Android','iPad', 'iPod', 'iPhone', 'PlayBook', 'BlackBerry', 'mobi']
browser = ['Crome', 'Safari', 'Opera', 'Firefox']

def detect(browser):
	d = Browserparser(browser)
	return d.detect()


class Browserparser:

	def __init__(self, browserstring):
		self.string = browserstring
		self.gevonden = {'os':False, 'platform':False, 'browser':False, 'mobile':False, 'kernel':False}

	def heeft(self, zoekterm, type):
		if self.string.find(zoekterm) >1:
			self.gevonden[type] = zoekterm
			return True
		else:
			return False

	def dieper(self, start, eind):
		a = 1

	def detect(self):
		
		for x in mobile:
			if self.heeft(x, 'mobile'):
				a = 1 
				pass

		for x in os:
			if self.heeft(x, 'os'):
				a = 1
				pass
		for x in browser:
			if self.heeft(x, 'browser'):
				a = 1
				pass


		return self.gevonden