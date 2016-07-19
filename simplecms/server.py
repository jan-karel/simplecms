#!/bin/env python
# -*- coding: utf-8 -*-

"""
 Base

 SimpleCMS
 a simplistic, minimal not-so-full stack webframework

 Copyright Jan-Karel Visser - all rights are reserved
 Licensed under the LGPLv3 (http://www.gnu.org/licenses/lgpl.html)

 This program is distributed in the hope that it will be useful, but
 WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

"""

import os
import sys
import gc
import __main__
import hashlib
import datetime
import string
from random import choice
from simplecms.template import TemplateParser
from simplecms.helpers import echo, serve_file, default_config, HTML, \
                              parse_qsl, timeparts, fetch_url, Tools, tag, \
                              extension, cookiedate, literal_evil
from simplecms.dal import BaseAdapter, DAL, Field
from simplecms.vorm import vorm_validate, Vorm
from simplecms.grid import Grid
from wsgiref import simple_server
import traceback

func = False
app = False

__autor__ = "Jan-Karel Visser"
__version__ = '0.2'
__release__ = '0'
__license__ = 'LGPLv3'

py = sys.version_info
py3 = py >= (3, 0, 0)
py25 = py <= (2, 5, 9)

if py25:
    def bytes(e):
        return str(e)
if not py3:
    from simplecms.mail import Mail

# Fix Python 2.x.
try:
    input = raw_input
except NameError:
    pass


class Storage(dict):
    """
    This sucks
    Eventually this should replace class Storage but causes memory leak
    because of http://bugs.python.org/issue1469629

    """
    __slots__ = ()
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
    __getitem__ = dict.get
    __getattr__ = dict.get
    __repr__ = lambda self: '<Storage %s>' % dict.__repr__(self)
    __getstate__ = lambda self: None
    __copy__ = lambda self: Storage(self)


class Request(Storage):
    """
    WSGI, Get and Post container

    """
    def __init__(self):
        Storage.__init__(self)
        self.wsgi = Storage()
        self.env = Storage()
        self.post = Storage()
        self.vars = Storage()
        self.args = Storage()
        self.now = datetime.datetime.now()
        self.utcnow = datetime.datetime.utcnow()

    def arg(self, req=0):
        leeg = ''
        return self.args[req] if self.args[req] != leeg else False


class Memory(Storage):
    """
    Holds stuff in memory

    """
    def __init__(self):
        Storage.__init__(self)
        self.settings = Storage()
        self.vuurmuur = Storage()
        self.csrftoken = Storage()
        self.language = Storage()
        self.now = datetime.datetime.now()
        self.hits = 0

    def load_languages(self, folder='languages', extend=False):
        pad = str(self.folder) + '/' + str(self.appfolder) + '/' + str(folder)
        for root, dirs, files in os.walk(pad):
            for taal in files:
                if taal.endswith('.lang') and not taal.startswith('__'):
                    try:
                        d = {}
                        c = taal.split('.lang')[0]

                        b = pad + '/' + taal
                        waarde = serve_file(b)
                        opt = literal_evil(waarde)

                        for k, v in opt.items():
                            v = v.decode('string-escape')
                            v = v.decode('utf8')
                            d[hash(k)] = v
                            if extend:
                                self.language[c].append(d)
                            else:
                                self.language[c] = d
                    except:
                        pass

    def config(self, waarde):

        opt = default_config()

        if waarde != '404':
            opt.update(literal_evil(waarde))

        for k, v in opt.items():
            if k == 'cdn_string':
                self.cdn_string = v
            elif k == 'gae_cdn_string':
                self.gae_cdn_string = v
            elif k == 'app_folder':
                self.appfolder = v
            elif k == 'migrate':
                self.migrate = v
            elif k == 'base_template':
                self.base_template = v
            elif k == 'migrate':
                self.fake_migrate = v
            elif k == 'secure':
                self.secure = v
            elif k == 'secure_controller':
                self.secure_controller = v
            else:
                self.settings[k] = v
        self.load_languages()


class Simplecms:

    def __init__(self, environ=False, memory=False):
        """

        m = memory
        r = request
        h = headers
        p = post
        g = get
        c = css
        j = javascript

        """


        if memory:
            self.r = Request()
            self.m = memory
            self.m.hits = self.m.hits + 1 
            self.headers = []
            self.post_vars = False
            self.query = False
            self.db = False
            self.mail = False
            self.auth = False
            self.post = False
            self.loggedin = False
            self.fingerprint = False
            self.isadmin = False
            self.status = '200 ok'
            self.field = False
            self.route = False
            self.protocol = False
            self.javascript_inc = []
            self.javascript_file = []
            self.css_inc = []
            self.css_file = []
            self.tools = False
            self.http = False
            self.csp = self.csp_nonce()
            self.domain = False
            self.html = Storage()
            self.data = False
            if 'apppath' in self.m.settings:
                self.apppath = self.m.settings['dbpath']
            else:
                self.apppath = self.m.folder + '/' + self.m.appfolder
            if 'dbpath' in self.m.settings:
                self.dbpath = self.m.settings['dbpath']
            else:
                self.dbpath = self.apppath
            if environ:
                self.build_request(environ)

    def get_headers(self, environ):
        """
        Extracts the requested headers

        """
        headers = {}
        for k in environ:
                if k.startswith('HTTP_'):
                    e = k[5:].replace('_', '-').title()
                    headers[e] = environ[k]
                if k.startswith('SSL_'):
                    e = k[4:].replace('_', '-').title()
                    headers[e] = environ[k]
        headers['REMOTE_ADDR'] = environ.get('REMOTE_ADDR', '')
        headers['SERVER_NAME'] = environ.get('SERVER_NAME', '')
        headers['REMOTE_HOST'] = environ.get('REMOTE_HOST', '')
        # for detecting appengine
        headers['APPENGINE_RUNTIME'] = environ.get('APPENGINE_RUNTIME', '')
        # our path
        headers['PATH_INFO'] = environ.get('PATH_INFO', '')

        # TODO check csrf header
        return headers

    def database(self, cdn=False):
        # init a connection with a database
        if not self.db and not cdn and not hasattr(self.db, '_tables'):
            self.field = Field
            if not self.r.env.get('APPENGINE_RUNTIME', False):
                # check if exsist else create directory
                if not os.path.exists(self.dbpath + '/database'):
                    os.makedirs(self.dbpath + '/database')

                self.db = DAL(cdn or self.m.cdn_string, 
                            folder=self.dbpath + '/database', 
                            migrate=self.m.migrate, 
                            fake_migrate=self.m.fake_migrate)
                self.gae = False
            else:
                self.db = DAL(self.m.gae_cdn_string)
                self.gae = True
        else:
            return DAL(cdn or self.m.cdn_string, 
                        folder=self.dbpath + '/databases', 
                        migrate=False)

    def model(self, name=False, path='models', cdn=False, blanc_env=False, 
              func=False):
        """
        Database modellen en logica
        geeft een database model terug of None

        """
        if not hasattr(self.db, '_tables'):
            self.database(cdn=cdn)
        if not name:
            name = self.m.settings.data_model

        if not blanc_env:
            blanc_env = self.environment()

        if name in ['base_tickets','base_auth','base_media','base_meuk']:
            #change
            forcepath = self.m.localfolder
            q_model = self.load_class(name, path, blanc_env, func, forcepath)

        else:
            q_model = self.load_class(name, path, blanc_env, func)

        if hasattr(q_model, 'create_models'):
            q_model.create_models()
            return q_model
        else:
            return q_model

    def build_request(self, environ):
        """
        Very ugly but effective

        """
        # build the request http://www.python.org/dev/peps/pep-0333/
        self.r.wsgi.version = environ.get('wsgi.version', False)
        self.r.wsgi.input = environ.get('wsgi.input', False)
        self.r.wsgi.errors = environ.get('wsgi.errors', False)
        self.r.wsgi.multithread = environ.get('wsgi.multithread', False)
        self.r.wsgi.multiprocess = environ.get('wsgi.multiprocess', 
                                                    False)
        self.r.wsgi.run_once = environ.get('wsgi.run_once', False)
        self.r.env = self.get_headers(environ)
        # set the prefered language from the Accept-Language
        try:
            self.lang = self.r.env['Accept-Language'][0:2].lower()
            # if self lang in available languages

            # elif if [2:4] in available languages

            # else force the default
        except:
            self.lang = self.m.settings.default_lang

        #basic
        self.domain = self.r.env.get('Host')
        if self.r.env.get('Tls-Sni'):
            self.protocol = 'https'
        else:
            self.protocol = 'http'

        if self.lang not in self.m.settings.language:
            self.lang = self.m.settings.default_lang
        self.gae = self.r.env.get('APPENGINE_RUNTIME', False)
        self.url = environ.get('PATH_INFO', '')
        cache = _(self.url + '_' + self.lang)
        self.is_cached = hashlib.md5(cache).hexdigest()
        aanvraag = self.url.split('/')[1:]
        if aanvraag:
            for i, x in enumerate(aanvraag):
                self.r.args[i] = x
        if environ.get('REQUEST_METHOD', '') in ('POST', 'PUT') \
                        and int(environ.get('CONTENT_LENGTH', False)):
            request_body_size = int(environ.get('CONTENT_LENGTH'))
            invoer = environ['wsgi.input'].read(request_body_size)
            self.post_vars = invoer
            dpost = parse_qsl(invoer)
            self.post = True
            for (k, v) in dpost:
                self.r.post[k] = v

        dget = parse_qsl(environ.get('QUERY_STRING', ''))

        if dget:
            for (key, value) in dget:
                self.r.vars[key] = value

        zout = str(self.m.settings.cookie_salt)
        self.cookie_salt = self.encrypt(zout, algo='sha1')
        userkey = hashlib.md5() #for speed?, ofcourse not

        userkey.update(_(self.cookie_salt))
        userkey.update(_(environ.get('SERVER_NAME', zout)))
        userkey.update(_(environ.get('HTTP_USER_AGENT', zout)))
        userkey.update(_(environ.get('HTTP_ACCEPT_LANGUAGE', self.lang)))
        userkey.update(_(environ.get('REMOTE_ADDR', zout)))
        fingerprint  = userkey.copy()
        fingerprint = fingerprint.hexdigest()
        # set time window

        # two predictable keys
        oldkey  = userkey.copy()
        tijdplus = self.r.now.year + self.r.now.day \
                 + self.r.now.hour + self.r.now.month
        tijdmin = self.r.now.year + self.r.now.day \
                 + (self.r.now.hour-1) + self.r.now.month

        zet = fingerprint[22:30] + str(tijdplus + 30)
        # previous hour
        zetoud = fingerprint[22:30] + str(tijdmin +30)


        userkey.update(self.encrypt(zet, algo='sha1'))
        oldkey.update(self.encrypt(zetoud, algo='sha1'))


        oldauthkey = oldkey.hexdigest()
        authkey = userkey.hexdigest()
        
        self.cookie = _(authkey[0:16])
        oldcookie = _(oldauthkey[0:16])
        self.cookie_value = self.encrypt(self.cookie_salt \
                                         + _(authkey[16:32]))
        oldcookie_value = self.encrypt(self.cookie_salt \
                                         + _(oldauthkey[16:32]))
        self.cookie_old_value = oldcookie_value
        sl = str(self.cookie) + '=' + str(self.cookie_value)
        oc = str(oldcookie) + '=' + str(oldcookie_value)

        self.fingerprint = self.encrypt(fingerprint[4:12])[12:20]
        # assume sha1 is available every where
        admin = self.encrypt(authkey, algo='sha1')
        oldadmin = self.encrypt(oldauthkey, algo='sha1')

        self.admin_cookie = _(admin[0:16])
        oldadmin_cookie = _(oldadmin[0:16])
        self.admin_cookie_value = self.encrypt(self.cookie_salt + admin)
        oldadmin_cookie_value = self.encrypt(self.cookie_salt + oldadmin)
        self.admin_cookie = _(admin[0:16])
        asl = str(self.admin_cookie) + '=' + str(self.admin_cookie_value)
        bsl = str(oldadmin_cookie) + '=' + str(oldadmin_cookie_value)

        if self.r.env.get('Cookie'):
        # now lets find out if there's a session active
            if [k for k in [sl] if k in self.r.env.get('Cookie', [])]:
                self.loggedin = self.cookie


                self.set_cookie(userlevel=1)
            elif self.r.now.minute <=30 and [k for k in [oc] if k in self.r.env.get('Cookie', [])]:
                self.loggedin = self.cookie

                #update session
                self.update_session(oldcookie_value)
                self.set_cookie(userlevel=1)
            elif [k for k in [asl] if k in self.r.env.get('Cookie', [])]:
                self.isadmin = self.admin_cookie

                self.loggedin = self.cookie
                self.set_cookie(userlevel=101)
            elif self.r.now.minute <=30 and [k for k in [bsl] if k in self.r.env.get('Cookie', [])]:
                self.isadmin = self.admin_cookie

                #update session
                self.update_session(oldadmin_cookie_value)
                self.loggedin = self.cookie
                self.set_cookie(userlevel=101)
            else:
                self.loggedin = False
                self.isadmin = False
    """
    segment functionaliteit

    -before
    -after
    -has
    -int
    -inarray



    """
    def segment(self, wat):
        """
        Fixes shift in self.requests for modules 
        Returns the request in more logical parts
        request url /hello/there
        self.segment(1) will return hello

        """

        if int(wat) >=1: 

            modules = self.m.settings.modules
            if self.r.arg(0) and self.r.arg(0) in modules:
                d = self.r.arg(int(wat))
                if d:
                    d = d.replace('.html','')
                    return d
            else:
                if self.r.arg(0) == self.m.secure:
                    d = self.r.arg(int(wat))
                    if d:
                        d = d.replace('.html','')
                        return d

                d = self.r.arg(int(wat)-1)
                if d:
                    d = d.replace('.html','')
            return d
        else:

            #nul of tekststring
            return False

    def segment_int(self, wat):
        """
        is digit

        """
        d = self.segment(wat)
        if d and str(d).isdigit():
            return d
        return False

    def segment_inarray(self, wat, lijst=[]):
        """
        is inarray

        """
        d = self.segment(wat)
        if d and d in lijst:
            return d
        return False

    def segment_if(self, wat, heeft):
        """
        is inarray

        """
        d = self.segment(wat)
        if d and d == heeft:
            return d
        return False

    def segment_has(self, wat, heeft):
        """
        is inarray

        """
        d = self.segment(wat)
        if d and d.find(heeft) >=1:
            return True
        return False


    def user(self):
        """
        Returns an user object, if logged in
        else returns False
        """
        if self.loggedin:
            user = self.model('base_auth')
            return user.get_user()
        else:
            return False

    def update_session(self, oud):
        if self.loggedin:
            user = self.model('base_auth')
            return user.update_session(oud)
        else:
            return False

    def serve(self):
        """
        Webservice Serves the request
        check if it's a media request else check the world directory
        if not then kickin the controllers

        """        
        verzoek = self.url[1:] or 'index.html'
        if self.url.startswith('/' + self.m.settings.dbmedia_folder + '/'):
            return self.download()

        else:      
            w = self.apppath + '/world/'
            # the result
            sttc = serve_file(w + verzoek)
            if sttc != '404':   
                data = self.alt_view(sttc)         
                return self.commit([self.status, self.headers, data])
            else:
                return self.create_page()

    def download(self):
        """
        If we are on GAE, serve images from database

        """
        bestand = self.model('base_media')
        data = bestand.serve_file()
        if data:
            return [self.status, self.headers, data]
        else:
            return self.forbidden()

    def forbidden(self):
        # serve a 403 page
        self.status = '403 forbidden'
        output = serve_file(self.apppath + '/views/' \
                    + memory.base_template + '/http/403.html')
        return output

    def render_view(self, view='404.html', getfile=False):
        """
        Fetches the raw HTML temlate from the given directory

        """
        #basic templates

        if not getfile:
            getfile = self.apppath + '/views/' + str(view)
        else:
            getfile = getfile.replace('.', '') + '/views/' + str(view)
        return serve_file([getfile, self.m.localfolder+'/simplecms/views/'+ str(view))

    def view(self, view, **zargs):
        """
        returns a generated view

        """
        # de view
        if not 'getfile' in zargs:
            getfile = False
        pagina = self.render_view(view=view, getfile=getfile)
        # parse the template
        if not 'getfile' in zargs:
            getfile = self.apppath
        parser = TemplateParser(pagina, path=self.apppath + '/views/')
        # render the template, added with some functionality
        if not zargs:
            zargs = {}
        if not 'environment' in zargs:
            data = parser.render(self.environment(), **zargs)
        else:
            data = parser.render(zargs['environment'], **zargs)
        # commit!
        if not 'commit' in zargs:
            return self.commit(data)
        else:
            return data

    def alt_view(self, pagina, **kwargs):
        if not 'getfile' in kwargs:
            getfile = self.apppath
        parser = TemplateParser(pagina, path=getfile + '/views/')
        if not 'environment' in kwargs:
            return parser.render(self.environment(), **kwargs)
        else:
            return parser.render(kwargs['environment'], **kwargs)

    def raw_view(self, pagina, **kwargs):
        #quick and dirty
        path = self.apppath+ '/views/'
        if 'getfile' in kwargs:
            path = kwargs['getfile']
        return serve_file(path + pagina)

    def commit(self, data):
        global rmeuk 
        rmeuk = ('rmeuk' in globals()) and (rmeuk + 1) % 100 or 0 
        if not rmeuk and not self.post: 
            gc.collect()
        if self.db:
            BaseAdapter.close_all_instances('commit')
        return data

    def load_class(self, module, path='controllers', blanc_env=False, 
                    func=False, forcepath=False):
        if not forcepath:
            forcepath = self.apppath
        try:
            if not blanc_env:
                blanc_env = dict()
            ophalen = forcepath + '/' + path + '/' + module + '.py'
            exec(serve_file(ophalen), blanc_env)
            if not func and module.title() in blanc_env:
                q = blanc_env[module.title()]
                return q(self)
            else:
                return blanc_env
        except:
            return False

    def controller(self, module=False):
        """
        Controller, returns the request handled by class or function

        """
        if not module:
            # get the first request
            module = self.m.settings.modules[self.r.args[0]]

        if module in ['cms']:
            q = self.load_class(module, blanc_env=self.environment(), forcepath=self.m.localfolder+'/simplecms/')
        else:
            q = self.load_class(module, blanc_env=self.environment())


        if hasattr(q, module.title()) or hasattr(q, '_run'):
            # run as class
            return q._run()
        else:
            # run as function
            segment = 1 if self.r.arg(0) and self.r.arg(0) == module else 0
            function = self.r.arg(segment) or 'index'
            functie = function.split('.')[0]
            # stripout function
            if functie in q:

                return q[functie]()
            else:
               #fallback 
               return str('404')

    def environment(self):
        """
        Hello RAM

        Returns global functions for controller, models and views
        doc: https://jan-karel.nl/simplecms/functions.html#environment

        """
        return dict(request=self.r, T=self.T, SCMS=self, db=self.db,
                    time=self.time, date=self.date,model=self.model,
                    javascript=self.javascript, prettydate = self.prettydate,
                    css=self.css, xhtml=self.xhtml, segment = self.segment,
                    segment_int = self.segment_int, segment_inarray = self.segment_inarray,
                    segment_if = self.segment_if,timediff=self.timediff,
                    grid = self.grid, user = self.user, vorm = self.vorm,
                    post=self.r.post, validate=self.validate,
                    now=self.r.now, get=self.r.vars, field=Field,
                    view=self.view, alt_view=self.alt_view, encrypt=self.encrypt, memory=self.m)

    def delete_cookie(self, duur=-95000, cookie=False):
        self.status = '307 Temporary Redirect'
        if self.isadmin:
            waard = self.admin_cookie + ' = 1;' + self.cookie \
                    + ' = 1 ;Path = /; Expires =' + cookiedate(duur) + ';'
        else:
            waard = self.cookie + ' = 1; Path = /; Expires =' \
                    + cookiedate(duur) + ';'
        self.headers = [('Content-type', 'text/html'),
                        ('Set-Cookie', str(waard))]

    def set_cookie(self, userlevel=1, sduur=1800):
        if userlevel < 100:
            waard = self.cookie + '=' + self.cookie_value \
                + '; Path = /; Expires =' + cookiedate(sduur) \
                + '; HttpOnly; Session;'
        else:
            waard = self.admin_cookie + '=' + self.admin_cookie_value \
                + '; Path = /; Expires =' + cookiedate(sduur) \
                + '; HttpOnly; Session;'
        self.headers = [('Content-type', 'text/html'), 
                        ('Set-Cookie', str(waard))]

    def create_page(self):
        """
        The create page function
        prepares conditions for the main controller

        """

        if self.loggedin and self.r.arg(0) in ['logout','uitloggen']:
            auth=self.model('base_auth')
            auth.user_logout(ret=True)
            return [self.status, self.headers, 'redirect']



        if self.r.arg(0) and self.r.arg(0) == self.m.secure:

            
            aanvraag = self.r.arg(1)
            functie = self.r.arg(2)
            modul = self.r.arg(3)

            if not self.isadmin:
                """
                This will setup the main account
                if there are any, login will be shown

                """
                data = self.view( memory.base_template + '/login/setup_login.html')

                return [self.status, self.headers, data]

            items = []
            for x in self.m.settings.backend_modules:
                items.append(x[1])
            for x in self.m.settings.backend_pages:
                items.append(x[1])
            if aanvraag and aanvraag in items:
                
                e = self.load_class(aanvraag, func=False, 
                        blanc_env=self.environment(), path='controllers/cms')
                
                if hasattr(e, aanvraag.title()) or hasattr(e, '_run'):
                    dmn = e._run()

                elif functie in e:
                    dmn = e[functie]()
                else:
                    try:
                        dmn = e['index']()
                    except KeyError:
                        dmn = e._run()
            else:
                

                e = self.load_class(self.m.secure_controller, 
                        path='controllers/cms', blanc_env=self.environment())

                if hasattr(e, '_run'):
                    dmn = e._run()
                else:
                    try:
                        dmn = e[aanvraag]()
                    except KeyError:
                        
                        dmn = e['index']()

            return self.commit([self.status,  self.headers, dmn])
        elif self.r.arg(0) and self.r.arg(0) in self.m.settings.modules:
            data = self.controller()
            return self.commit([self.status, self.headers, data])
        else:
            # run the default application
            uitvoer = self.controller(self.m.settings.default_application)
            # adjust some headers
            return self.commit([self.status, self.headers, uitvoer])

    def create_password(self, email=False, password=False):
        """

        """
        hashed = hashlib.sha1(str(self.m.settings.salt)).hexdigest()
        key = hashlib.new(self.m.settings.algorithm)
        key.update(hashed)
        key.update(hashlib.md5(str(hashed + email)).hexdigest())
        key.update(hashlib.sha1(str(hashed + password)).hexdigest())
        word = hashlib.md5(key.hexdigest()).hexdigest()
        return word

    def send_email(self, email=False, subject=False, message=False, 
                    bcc=False, tls=True):
        if self.gae:
            mailserver = 'gae'
        else:
            mailserver = self.m.settings.mailserver
        if email and subject and message:
        # build the string
            if not hasattr(self.mail, 'send'):
                self.mail = Mail(server=str(mailserver), \
                                 sender=str(self.m.settings.mailsender), \
                                 login=str(self.m.settings.maillogin), \
                                 tls=tls)
        return self.mail.send(email, subject, message, bcc=bcc)

    def create_ticket(self, ticket=None, data=None):
        """
        Logs error messages to the database

        """
        ticket = self.model('base_tickets')
        ticket.add_ticket(refer=ticket, message=data)

    def T(self, woord=False, waarden=False, l=False):
        """
        Shortcut for translate

        """
        if woord:
            return self.translate(woord, waarden, l)
        return ''

    def translate(self, woord, waarden=False, l=False):
        """
        Translates strings if translation is found in memory
        Default language does not get translated, by the way

        """
        lang = l if l else self.lang              
        if lang == self.m.settings.default_lang:
            return echo(woord, waarden)
        elif woord and self.m.language[lang]:
            try:
                find = self.m.language[lang][hash(woord)]
                if find:
                    return echo(find.encode('utf8', 'xmlcharrefreplace'), 
                                waarden)
                else:
                    if self.m.settings.fix_lang:
                        self.model('language')
                        return echo(woord, waarden)
                    else:
                        return echo(woord, waarden)
            except:
                return echo(woord, waarden)
        else:
            # is there a sh
            return echo(woord, waarden)

    def encrypt(self, text, algo='md5', get='hexdigest'):
        key = hashlib.new(algo)
        key.update(_(text))
        if get == 'hexdigest':
            return _(key.hexdigest())
        else:
            return _(key)

    def redirect(self, location='/'):
        self.status = '307 Temporary Redirect'
        self.headers = [('Content-type', 'text/html'), ('Location', location)]
        return 'redirect'

    def evil(self, waarde):
        """
        Set here to make a port available to tweakevil

        """
        return literal_evil(waarde)

    """
    Form, crud helpers

    """

    def validate(self, wat, waarde):
        return vorm_validate(wat, waarde)

    def vorm(self, table, id=0):
        return Vorm(self, table, id)

    def grid(self, table, fields, q=False, menu=False, extra=False,
               well=False, path=False, edit=False, search=False, 
               delete=False, new=False, view=False, smart=False):
        grid = Grid(self, table, fields, q, menu, extra, well, path, edit, 
                    search, delete, new, view, smart)
        return grid.show()

    """
    HTML helpers
    Need to move to a better place

    """

    def class_active(self, home, items=False, req=0, f=False):
        wat = self.r.arg(req)
        if wat:
            wat = wat.replace('.html','')
        if items:
            if wat not in items:
                if f:
                    return ' active'
                return ' class="active"'
            else:
                return ''
        else:
            if wat == home:
                if f:
                    return ' active'
                return ' class="active"'
            else:
                return ''

    def xhtml(self, reqstring='body,html,div,span,a,ul,li,p,h1,h2,h3,h4'):
        """
        XHTML generator, generates html tags

        """
        for name in reqstring.split(','):
            if not name in self.html:
                self.html[name] = HTML(tag[name])
        return self.html

    def csp_nonce(self, lengte=22):
        return ''.join([choice(string.letters + string.digits) for i in range(int(lengte))])

    def javascript(self, code=None, include=None):
        """
        javascript
        ads requested javascript to the page

        """
        #zetscripts = "img-src {prot}://* data: blob: ; connect-src {prot}://*; media-src {prot}://* ; object-src {prot}://{domein}/static/ ; default-src 'self' ; font-src {prot}://* data: ; frame-src {prot}://* ; style-src {prot}://* 'unsafe-inline' 'unsafe-eval' ; script-src 'unsafe-eval' 'unsafe-inline' 'self' {prot}://{domein}/ 'nonce-{nonce}' ;"
        zetscripts = "default-src 'self'; script-src 'self' 'nonce-{nonce}'; frame-ancestors 'self';"
        altscripts = "default-src 'self'; script-src 'self' 'unsafe-eval' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; frame-src 'self';"

        e = ''
        e2 = ''
        html = self.xhtml('script')
        if code == 'show':

            nonce = self.csp.capitalize()
            cked = '/'+self.m.settings.media_folder+'/editor/editor.js'
            if cked in self.javascript_file:
                #relaxes csp header
                self.headers.append(('Content-Security-Policy', altscripts))
            else:
                self.headers.append(('Content-Security-Policy', zetscripts.replace('{nonce}',nonce).replace('{prot}',self.protocol).replace('{domein}',self.domain)))

            for script in self.javascript_file:
                if script.startswith('js'):
                    script = '/' + str(self.m.settings.media_folder) + '/' \
                            + str(script)
                e += str(html.script.tag('', _type="text/javascript", _nonce=nonce, 
                                        _src=script))
            if self.javascript_inc:
                for inc in self.javascript_inc:
                    e2 += inc + '\n'
                e += str(html.script.tag(e2, _type="text/javascript", _nonce=nonce))
            return e
        elif include:
            if include not in self.javascript_file:
                self.javascript_file.append(include)
        else:
            if include not in self.javascript_inc:
                self.javascript_inc.append(code)

    def css(self, code=None, include=None):

        e = ''
        e2 = ''
        html = self.xhtml('link, style')
        if code == 'show':
            for script in self.css_file:
                if script.startswith('css'):
                    script = '/' + str(self.m.settings.media_folder) + '/' \
                            + str(script)
                e += str(html.link.tag(_href=str(script), _rel='stylesheet'))
            if self.css_inc:
                for inc in self.css_inc:
                    e2 += inc + '\n'
                e += str(html.style.tag(e2, _type="text/css"))
            return e
        elif include:
            if include not in self.css_file:
                self.css_file.append(include)
        else:
            if include not in self.css_inc:
                self.css_inc.append(code)

    def fetch(self, url):
        return fetch_url(url)

    def geocode(self, waarde):
        if not self.tools:
            self.tools = Tools(self)
        return self.tools.geocode(waarde)

    def prettydate(self, waarde, dagen=False):
        if not self.tools:
            self.tools = Tools(self)
        return self.tools.prettydate(waarde, dagen)

    def timediff(self, datum, teruggave=False, **kwargs):
        """
        get the difference between current and givven in timedelta

        """
        return self.prettydate(datum, dagen=True)

    def date(self, datum, teruggave=False):
        return self.time(datum, teruggave, date=True)

    def time(self, datum, teruggave=False, **kwargs):
        """
        based on the user language, rebuilds the datetime object
        completly disregarding utc or datetime.now

        _timestr
        _datestr
        _diff

        """
        wtime = 0
        timestring = False
        datestring = False
        [year, month, day, hour, seconds, millisec] = timeparts(datum)
        if self.m.language[self.lang]:
            try:
                timestring = self.m.language[self.lang][hash('_timestr')]
                datestring = self.m.language[self.lang][hash('_datestr')]
                try:
                    wtime = int(self.m.language[self.lang][hash('_diff')])
                except:
                    wtime = 0
            except:
                timestring = False
                datestring = False
                wtime = 0
        if 'date' in kwargs:
            tstr = datestring or self.m.settings.server_datestring
        else:
            tstr = timestring or self.m.settings.server_timestring

        server = datetime.datetime(year, month, day, hour, seconds, millisec)
        # need to adjust the time
        tijd = server + datetime.timedelta(minutes=wtime)

        if teruggave:
            return tijd
        else:
            # return the string
            # set the time
            [year, month, day, hour, seconds, millisec] = timeparts(tijd)
            if hour < 10:
                hour = str('0' + str(hour))
            if seconds < 10:
                seconds = str('0' + str(seconds))
            return echo(tstr, [year, month, day, hour, seconds, millisec])


class simplecms_server(simple_server.WSGIServer):
    # To increase the backlog
    request_queue_size = 500


class simplecms_handler(simple_server.WSGIRequestHandler):
    # to disable logging
    def log_message(self, *args):
        pass


def server(environ, start_response):
    app = ''
    eget = environ.get
    if not eget('PATH_INFO', None) and eget('REQUEST_URI', None):
        items = environ['REQUEST_URI'].split('?')
        environ['PATH_INFO'] = items[0]
        if len(items) > 1:
            environ['QUERY_STRING'] = items[1]
    # some vars
    ip = environ['REMOTE_ADDR']
    uri = environ['PATH_INFO']
    ext = extension(uri)
    response_headers = False
    status = '200 ok'
    output = ' '

    """
     block some bogus request
     show our unimplemented idiot filter by to many bad requests

    """

    if ip in memory.vuurmuur and memory.vuurmuur[ip] >= 8:
        #to many errors from this ip, idiot filter not implemented
        status = '501 Not Implemented'
        pad = [memory.folder + '/' + memory.appfolder + '/views/' + memory.base_template \
            + '/http/blocked.html', memory.localfolder + '/simplecms/views/base/http/307.html']
        output = serve_file(pad)
        start_response(status, [('Content-type', 'text/html')])

        # to many errors from this ip
        return [_(output)]

    elif [k for k in memory.settings.blacklist if k in uri.lower()]:

        if ip in memory.vuurmuur:
            memory.vuurmuur[ip] = memory.vuurmuur[ip] + 1
        else:
            memory.vuurmuur.update({ip: 1})
        
        status = '403 forbidden'
        output = serve_file([memory.folder + '/' + memory.appfolder + '/views/' \
                            + memory.base_template + '/http/403.html',
                            memory.localfolder + '/simplecms/views/base/http/307.html']
                            )
        start_response(status, [('Content-type', 'text/html')])
        return [_(output)]
    else:
        try:
            # static requests
            if uri.lower() in ['/favicon.ico', '/robots.txt', '/humans.txt']:
                output = serve_file([memory.folder + '/' + memory.settings.media_folder + uri,
                                    memory.localfolder + '/simplecms/static'+ uri]
                                    )
                
            elif uri.startswith('/' + memory.settings.media_folder + '/'):
                bst = uri.replace('/' + memory.settings.media_folder + '/', '')
                output = serve_file([memory.folder + '/' + memory.settings.media_folder + '/' + str(bst),memory.localfolder+'/simplecms/static/'+str(bst)])
            # output    directly + cache

            else:
                app = Simplecms(environ, memory)
                status, response_headers, output = app.serve()
                # del app
        except:
            print traceback.format_exc()
            if memory.settings.log:
                try:
                    fout = traceback.format_exc()
                    print(fout)
                    output = '404'
                    if app:
                        if not hasattr(app, 'create_ticket'):
                            app = Simplecms(environ, memory)
                    app.create_ticket(ticket=app.encrypt(str(fout)),\
                                  data=fout)
                except:
                    output = '404'
            else:
                # testing
                output = '404'
    """
    if a request returns a simple 404 string we'll show an error page
    or

    """
    del app

    if output == '404':
        status = '404 not found'
        ext = 'text/html'
        output = serve_file([memory.folder + '/' + memory.appfolder \
                    + '/views/' + memory.base_template + '/http/404.html',
                    memory.localfolder+ '/views/base/http/404.html'])
    elif output == 'redirect':
        output = serve_file([memory.folder + '/' + memory.appfolder \
                    + '/views/' + memory.base_template + '/http/307.html',
                    memory.localfolder + '/views/base/http/307.html']
                    )

    if not response_headers:
        req = ext.split('/')
        if [k for k in ['image', 'css', 'javascript'] if k in req]:
            
            response_headers = [('Content-type', ext),
                                ('Cache-Control', 'public, max-age=290304000')]

        else:
            response_headers = [('Content-type', ext)]
    else:
        #if not content type in responseheaders
        response_headers.append(('Content-type', ext))


    start_response(status, response_headers)
    return [_(output)]


def _(s, enc='utf8', err='strict'):
    # Fix mixed encodings, force returning bytes, ignored on 2.5
    if isinstance(s, bytes):
        return s
    else:
        return bytes(s.encode(enc))



def get_folder():
    p = __main__.__file__
    folder = os.path.abspath(p).rsplit('/',1)[0]
    sys.path.append(folder)
    return folder

def get_myfolder():
    p = __file__.split('simplecms/server')
    folder = os.path.abspath(p[0])
    sys.path.append(folder)
    return folder



memory = Memory()
memory.localfolder = get_myfolder()
memory.folder = get_folder()
# enforce the local default path

memory.config(serve_file(memory.folder + '/config.scms'))
# ad import path
sys.path.append(memory.folder + '/' + memory.appfolder)

# overwrite on sys.args request
if len(sys.argv) == 2:
   memory.settings.port  = int(sys.argv[1])  
if len(sys.argv) == 3:
    memory.settings.port  = int(sys.argv[1]) 
    memory.settings.hostname  = str(sys.argv[2])


def startserver(port=memory.settings.port, hostname=memory.settings.hostname):
    pid = os.getpid()
    echo("SimpleCMS - v{0}.{1}", 
        [__version__, __release__], ret=False)
    echo("A fast,stable,secure and minimalistic framework", ret=False)
    echo("Copyright {0} - all rights are reserved", 
        [__autor__], ret=False)
    echo("Licensed under the {0} license", 
        [__license__], ret=False)
    echo("Serving on port {0}...", 
        [port], ret=False)
    echo('use "kill -SIGTERM {0}" or ^C to shutdown simplecms', 
        [pid], ret=False)
    httpd = simplecms_server((hostname, port), simplecms_handler)
    httpd.set_app(server)
    httpd.serve_forever()

#if __name__ == '__main__':
#    startserver()
