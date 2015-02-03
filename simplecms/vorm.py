#!/bin/env python
# -*- coding: utf-8 -*-

"""
 Vorm
 A simple form creator

 Copyright Jan-Karel Visser - all rights are reserved
 Licensed under the LGPLv3 (http://www.gnu.org/licenses/lgpl.html)

 This program is distributed in the hope that it will be useful, but
 WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

"""

import re

try:
    from cgi import escape as eskape
except:
    from html import escape as eskape

vorm_divstart = ''
vorm_divend = ''
vorm_label = '<label for="{id}">{label}</label>'
vorm_input = '<input type="{type}" id="{id}" name="{name}"{value}{opt}/>'
vorm_comment = '<small>{comment}</small>'
vorm_textarea = '<textarea name="{name}" id="{id}"{opt}>{value}</textarea>'
vorm_html5 = ['email', 'range', 'password', 'datetime', 'date', 'url',
              'number','upload','image','join', 'alias']
#sets the input fields
vorm_valid = {'username': 'text', 'telephone': 'tel'}

def schoon(s):
    if not isinstance(s, (str, unicode)):
        s = str(s)
    elif isinstance(s, unicode):
        s = s.decode('utf8', 'xmlcharrefreplace')
    s = re.sub('<[^<]+?>', '', s)
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")

    s = s.replace("'", "&#x27;")
    s = s.replace('"', "&quot;")
    try:
        return eskape(s).encode('utf8', 'xmlcharrefreplace')
    except:
        return s

def alias(s):
    s = schoon(s)
    s = s.replace(' ','-')
    s = s.replace("&lt;", '')
    s = s.replace("&gt;", '')
    s = s.replace("&#x27;", '')
    s = s.replace("&amp;", '')
    s = s.replace("#x27;", '')
    s = s.replace("amp;", '')
    s = s.replace('&quot;', '')
    s=s.replace('&nbsp;','')
    return s


def vorm_validate(soort, invoer, options=False):
    if not invoer:
        return False
    vorm_types = {
        "email": \
        "^[a-zA-Z0-9._%-]+@[a-zA-Z0-9._%-]+.[a-zA-Z]{2,6}$",
        "telephone": \
        "^([\+][0-9]{1,3}([ \.\-])?)?([\(]{1}[0-9]{3}[\)])?([0-9A-Z \.\-]\
        {1,32})((x|ext|extension)?[0-9]{1,4}?)$",
        "username": \
        "^([a-zA-Z])[a-zA-Z_-]*[\w_-]*[\S]$|^([a-zA-Z])[0-9_-]*[\S]$|\
        ^[a-zA-Z]*[\S]$",
        "imageurl": \
        "^(http\:\/\/[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(?:\/\S*)?(?:[a-zA-Z0-9_])\
        +\.(?:jpg|jpeg|gif|png))$",
        "domainname": \
        "(?:[^0-9][a-zA-Z0-9]+(?:(?:\-|\.)[a-zA-Z0-9]+)*)",
        "number": \
        "^(?:\d+,\s*)*\d+\s*$",
        "password": \
        "^[a-zA-Z0-9._%-+]+@[a-zA-Z0-9._%-]+.[a-zA-Z]{2,8}$",
        "name": \
        "^[a-zA-Z0-9._%-+]+@[a-zA-Z0-9._%-]+.[a-zA-Z]{2,8}$",
        "url": \
        "^[a-zA-Z0-9._%-+]+@[a-zA-Z0-9._%-]+.[a-zA-Z]{2,8}$",
        "date": \
        "([0-9]{4})-([0-9]{1,2})-([0-9]{1,2})",
        "datetime": \
        "([0-9]{4})-([0-9]{1,2})-([0-9]{1,2})",
        "time": \
        "([0-1][0-9]|2[0-3]):[0-5][0-9]",
        "alphanumeric": \
        "^[a-zA-Z0-9\s]+$",
        "null": \
        "^.{0,0}",
        "comma_integer": \
        "^((\d{1,3}(,\d{3})*)|(\d{1,3}))$",
        "postcode": \
        "^[0-9]{4}\s{0,2}[a-zA-z]{2}$",
        "age": \
        "^(1[89]|[2-9]\d)$",
        "number": \
        "^[-+]?([0-9]{1,3}[,]?)?([0-9]{3}[,]?)*[.]?[0-9]*$"
        }
    #
    if soort == 'image':
        return True
    elif soort == 'join':
        return True
    elif soort == 'f':
        return False
    elif re.match(vorm_types[soort], invoer) != None:
        return True
    else:
        return False


class Vorm:

    def __init__(self, SCMS, table, id=0):
        self.app = SCMS
        self.table = table
        self.veld = ''
        self.plaatje = False
        self.waarden = dict()
        self.form = ''
        self.postkey = []
        self.javascript = False
        self.upload = False
        self.fileupload = False
        self.opslaan = {}
        self.valideer = {}
        self.widget = {}
        try:
            self.id = id.split('?')[0]
        except:
            self.id = id
        self.enhanced = False
        self.create_form()

    def fields(self, item):
        #set the id
        #set the label


        if item.writable and not item.compute:
            tid = str(item)
            tid = tid.split('.')[1]
            self.postkey.append(tid)
            if item.widget:
                self.valideer[tid] = item.widget
            label = vorm_label.replace('{id}', str(tid))
            label = label.replace('{label}', str(item.label))
            if item.type == 'text':
                invoer = vorm_textarea.replace('{id}', str(tid))
                if self.waarden:
                    invoer = invoer.replace('{value}', str(self.waarden[tid]))

                        
            else:
                invoer = vorm_input.replace('{id}', str(tid))
            if item.widget in vorm_html5:
                if item.widget == 'image':
                    if not self.plaatje:
                        self.app.javascript(code="function afbeelding(itd){t_popup('/"+self.app.memory.secure+"/afbeelding/'+itd);return false}")
                        self.app.javascript(code="function sluit(){$('#m_popup').fadeOut()}")
                        self.plaatje = True

                    self.app.javascript(code="$('#"+str(tid)+"').click(function(){afbeelding('"+str(tid)+"')})")
                    invoer = invoer.replace('{type}', 'text')
                if item.widget == 'alias':
                    invoer = invoer.replace('{type}', 'text')
                    if self.waarden:
                        self.waarden[tid] = alias(self.waarden[tid])
                elif item.widget == 'join':
                    invoer = '<select name="'+str(tid)+'" name="'+str(tid)+'"><option value="-1">---</option>'
                    refer = item.type.split(' ')[1]
                    p=self.app.db(self.app.db[refer]).select('id','naam')
                    for x in p:
                        wo = ''
                        #wo = ' selected="selected"' if str(x['id']) == self.waarden[tid] else ''
                        if self.waarden:
                            wo = ' selected="selected"' if x['id'] == int(self.waarden[tid]) else ''
                        invoer = invoer + '<option value="'+str(x['id'])+'"'+wo+'>'+str(x['naam'])+'</option>'
                    invoer = invoer + '</select>'
                else:
                    invoer = invoer.replace('{type}', str(item.widget))
            if item.widget in vorm_valid:
                invoer = invoer.replace('{type}', vorm_valid[item.widget])
            if item.type == 'upload':
                self.fileupload = True
                invoer = invoer.replace('{type}', 'file')
            if item.comment:
                invoer = invoer.replace('{opt}', ' placeholder="' \
                                                + str(item.comment) + '"{opt}')
            if item.required:
                invoer = invoer.replace('{opt}', ' required')

            if item.wysiwyg:
                #hopsakeee
                if self.javascript == False:
                    self.app.javascript(include='/static/editor/ckeditor.js')
                    #is gebruiker op be[aa;d niveau] dan mag ie uploaden
                    #anders beperkt
                    self.app.javascript(code='CKEDITOR.config.filebrowserBrowseUrl = "/'+self.app.memory.secure+'/ckbrowser/files";')
                    self.app.javascript(code='CKEDITOR.config.filebrowserImageBrowseUrl = "/'+self.app.memory.secure+'/ckbrowser/images";')
                    self.app.javascript(code='CKEDITOR.config.filebrowserFlashBrowseUrl = "/'+self.app.memory.secure+'/ckbrowser/flash";')
                    self.javascipt = True
                self.app.javascript(code='CKEDITOR.replace( "'+ tid +'" );')

                invoer = vorm_textarea.replace('{id}', str(tid))
                if self.waarden:
                    invoer = invoer.replace('{value}', str(self.waarden[tid]))

            #hide the id
            if item.label == 'Id':
                if self.waarden:
                    label = ''
                    invoer = invoer.replace('{type}', 'hidden')
                else:
                    if self.id == 0:
                        self.widget[tid] = ''
                        return
            else:
                invoer = invoer.replace('{type}', 'text')

            invoer = invoer.replace('{name}', str(tid))
            invoer = invoer.replace('{opt}', '')
            if self.waarden:
                if self.waarden[tid] == None:
                    self.waarden[tid] = ''
                invoer = invoer.replace('{value}',\
                                    ' value="' + str((schoon(self.waarden[tid]) if self.waarden[tid] else '')) + '" ')
            if item.default:
                invoer = invoer.replace('{value}',\
                                    ' value="' + str(item.default) + '" ')
            invoer = invoer.replace('{value}', '')
            self.widget[tid] = vorm_divstart + label + invoer + vorm_divend
            
            self.form += self.widget[tid]


    def show(self):
        return self.form

    def form_id(self):
        if self.id > 0:
            return '<input type="hidden" name="id" value="'\
                                                        + str(self.id) + '" />'
        else:
            return ''

    def delete(self):
        if self.id > 0:
            try:
                del self.table[self.id]
            except:
                pass

    def save(self, post=False, save=True):
        if post:

            #check for CSRF token
            #check for referer

            #check for valid user


            for k in self.postkey:
                if not k == 'id':
                    if k in post:
                        if k in self.valideer:
                            if self.valideer[k] == 'alias':
                                self.opslaan[k] = alias(post[k])
                            elif vorm_validate(self.valideer[k], post[k]):
                                if self.valideer[k] != 'alias':
                                    self.opslaan[k] = post[k]
                            else:
                                return False
                        self.opslaan[k] = post[k]
                else:
                    if k == 'id' and post['id']:
                        self.id = post[k]
            if save:
                self.table[self.id] = self.opslaan
                self.form = ''
                self.postkey = []
                self.opslaan = {}
                self.widget = {}
                self.valideer = {}
                self.create_form()
                if self.id:
                    self.app.audit_trail(1,'Verwerkte tabel '+str(self.table)+' met id:' + str(self.id))
                else:
                    self.app.audit_trail(1,'Voegde een nieuw onderdeel aan tabel '+str(self.table)+' toe')
                #audit trail
                #datum, ip, gebruiker, aanpassingen, reden

            return True

        #audit trail
        #datum, ip, aanpassingen, reden

        return False

    def row(self):
        return self.waarden

    def get(self, id):
        return self.table[id]

    def create_form(self):
        if self.id > 0:
            try:
                self.waarden = self.table[self.id]
            except:
                pass
        for items in self.table:
            self.fields(items)
