#!/bin/env python
# -*- coding: utf-8 -*-

"""

 Base_Tickets
 Log application errors to the database

 Copyright Jan-Karel Visser - all rights are reserved
 Licensed under the LGPL v3

 This program is distributed in the hope that it will be useful, but
 WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

"""

import sys

class Base_Tickets:

    def __init__(self, SCMS):
        self.app = SCMS
        
    def add_ticket(self, refer=None, message=None):
        """
        Called by SimpleCMS server on fail

        """
        self.scms_tickets.insert(refer=refer, message=message)
        self.app.db.commit()

    def create_models(self):

        if not hasattr(self.app.db, 'scms_tickets'):
            self.scms_tickets = self.app.db.define_table("scms_tickets",
                            self.app.field("refer", 'string'),
                            self.app.field("sys_exc", 'string', default=sys.exc_info()[0]), #no need to filter
                            self.app.field("userip", 'string', default=self.app.request.env.get('REMOTE_ADDR', 'unknown')),
                            self.app.field("request", 'string', default=self.app.url),
                            self.app.field("datetime", 'datetime', default=self.app.request.now),
                            self.app.field("message", 'text')
                            )
        else:
            self.scms_tickets = self.app.db.scms_tickets