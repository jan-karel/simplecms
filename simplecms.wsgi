#!/bin/env python
# -*- coding: utf-8 -*-

"""
 WSGI
 Startpoint for apache & mod_wsgi 

 SimpleCMS
 a simplistic, minimal not-so-full stack webframework

 Copyright Jan-Karel Visser - all rights are reserved
 Licensed under the LGPLv3 (http://www.gnu.org/licenses/lgpl.html)

 This program is distributed in the hope that it will be useful, but
 WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

"""

import sys
import os

path = os.path.dirname(os.path.abspath(__file__))
os.chdir(path)  
sys.path = [path] + [p for p in sys.path if not p == path]  
    
import simplecms_server

def application(environ, start_response):
    return simplecms_server.server(environ, start_response)
