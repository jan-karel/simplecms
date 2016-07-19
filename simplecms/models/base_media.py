#!/bin/env python
# -*- coding: utf-8 -*-

"""
 Base_media
 File management 


 SimpleCMS
 Copyright Jan-Karel Visser - all rights are reserved
 Licensed under the LGPL v3

 This program is distributed in the hope that it will be useful, but
 WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

"""


class Base_Media:

    def __init__(self, SCMS):
        self.app = SCMS

    def get(self):
        return self.app.db((self.scms_cdn.id == self.app.request.arg(1)) & \
                           (self.scms_cdn.soort == 'image')).select(\
                            self.scms_cdn.soort, self.scms_cdn.rel,
                            self.scms_cdn.name, self.scms_cdn.filename,
                         self.scms_cdn.source, self.scms_cdn.soort).first()

    def info(self, x):
        return self.app.db(self.jexjex_cdn.id == x).select(self.scms_cdn.id,self.scms_cdn.name,self.scms_cdn.filename,
            self.scms_cdn.soort,
self.scms_cdn.mime,self.scms_cdn.source,self.scms_cdn.rel,
self.scms_cdn.size,self.scms_cdn.via,self.scms_cdn.datum).first()

    def serve_file(self):
        rw = self.app.db((self.scms_cdn.filename == self.app.request.arg(1))\
                           & (self.scms_cdn.rel == 'local')).select(\
                        self.scms_cdn.mime, self.scms_cdn.uploaded).first()
        if rw:
            self.app.headers = [('Cache-Control', 'public, max-age=290304000'),
                                ('Content-type', rw.mime),
                                ('Content-Length', str(len(rw.uploaded)))]
            return rw.uploaded
        else:
            return False

    def files(self, soort='image'):
        g = ''
        row = self.app.db(self.scms_cdn.soort == soort).select(\
              self.scms_cdn.name, self.scms_cdn.id, self.scms_cdn.source)
        for x in row:
            g += g + '<figure><img src="' + x.source + '" alt="' + x.name + '"\
                  /><figcaption><a href="#">' + x.name + '</a> <a rel="'\
                  + str(x.id) + '" class="pull-right figure-verwijder \
                  icon-trash">'+self.app.T('Verwijder', l='nl')+'</a></figcaption></figure>'
        return g

    def upload(self):
        """
        upload file
        """


    def create_models(self):

        if not hasattr(self.app.db, 'scms_cdn'):
            self.scms_cdn = self.app.db.define_table("scms_cdn",
                        self.app.field("name", 'string'),
                        self.app.field("filename", 'string'),
                        self.app.field("soort", 'string'),
                        self.app.field("mime", 'string'),
                        self.app.field("project", 'string'),
                        self.app.field("mnok", 'string'),
                        self.app.field("source", 'string'),
                        self.app.field("rel", 'string'),
                        self.app.field("moved", 'string'),
                        self.app.field("size", 'string'),
                        self.app.field("bes", 'string'),
                        self.app.field("via", 'string'),
                        self.app.field("gebruiker", 'string', default=-1, writable=False),
                        self.app.field("datum", 'datetime', \
                                                 default=self.app.request.now),
                        self.app.field("uploaded", 'blob', writable=False)
                        )
        else:
            self.scms_cdn = self.app.db.scms_cdn
