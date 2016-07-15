#!/bin/env python
# -*- coding: utf-8 -*-

from simplecms.server import *

#initaliseren locatie en simplecms omgeving
#memory starten
memory = Memory()
memory.folder = get_folder()
#standaard locatie zetten
localfolder = memory.folder + '/applications'
memory.config(serve_file(memory.folder + '/config.scms'))
#import locatie forceren
sys.path.append(memory.folder + '/' + memory.appfolder)
#argumenten afvangen
if len(sys.argv) == 2:
   memory.settings.port  = int(sys.argv[1])  
if len(sys.argv) == 3:
    memory.settings.port  = int(sys.argv[1]) 
    memory.settings.hostname  = str(sys.argv[2])


#starten wsgi applicatie
if __name__ == '__main__':
	startserver()
