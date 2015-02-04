#!/bin/env python
# -*- coding: utf-8 -*-

"""
 Main controller

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
import hashlib
import datetime
from simplecms.template import TemplateParser
from simplecms.helpers import echo, serve_file, default_config, literal_evil, parse_qsl, \
                  timeparts, fetch_url, cookiedate, extension, Tools, HTML, tag
from simplecms.dal import BaseAdapter, DAL, Field
from simplecms.vorm import vorm_validate, Vorm
from simplecms.grid import Grid
#import simplecms.httpagentparser as httpagent
from wsgiref import simple_server
import traceback

func = False
app = False

__autor__ = "Jan-Karel Visser"
__version__ = '0.1'
__license__ = 'LGPLv3'

py = sys.version_info
py3 = py >= (3, 0, 0)
py25 = py <= (2, 5, 9)

if py25:
    def bytes(e):
        return str(e)
if not py3:
    #not yet complete, rewritten
    from simplecms.mail import Mail
else:
    from simplecms.mailpy3 import Mail


# Fix Python 2.x.
try: input = raw_input
except NameError: pass


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
    Holds stuff in memory

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
        self.data = Storage()
        self.cache = Storage()
        self.view = Storage()
        self.now = datetime.datetime.now()
        self.utcnow = datetime.datetime.utcnow()
        self.language = Storage()
        self.hits = 0


    def clear_mem(self):
        tot = len(self.cache) + len(self.view)
        for key in self.cache:
                self.cache[key] = False
        for key in self.view:
                self.view[key] = False
        return tot

    def load_languages(self, folder='languages', extend=False):
        #scan language dir
        #fetch files
        #build strings
        for root, dirs, files in os.walk(self.folder + '/' + self.appfolder + '/' + folder):
            for taal in files:
                if taal.endswith('.lang') and not taal.startswith('__'):
                    try:
                        d = {}
                        c = taal.split('.lang')[0]

                        b = self.folder + '/' + self.appfolder + '/' + folder + '/' + taal
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


class simplecms:

    def __init__(self, environ=False, memory=False):
        #we need some values :)
        if environ and memory:
            self.request = Request()
            self.memory = memory
            self.memory.hits = self.memory.hits + 1
            self.headers = False
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
            self.stats = False
            self.javascript_inc = []
            self.javascript_file = []
            self.css_inc = []
            self.css_file = []
            self.tools = False
            self.http = False
            self.domain = False
            self.html = Storage()
            self.data = False
            self.apppath = self.memory.folder + '/' + self.memory.appfolder
            if 'dbpath' in self.memory.settings:
                self.dbpath = self.memory.settings['dbpath']
            else:
                self.dbpath = self.apppath
            self.build_request(environ)

    def get_headers(self, environ):
        headers = {}
        for k in environ:
                if k.startswith('HTTP_'):
                    e = k[5:].replace('_', '-').title()
                    headers[e] = environ[k]
        headers['REMOTE_ADDR'] = environ.get('REMOTE_ADDR', '')
        headers['SERVER_NAME'] = environ.get('SERVER_NAME', '')
        headers['REMOTE_HOST'] = environ.get('REMOTE_HOST', '')
        #for detecting appengine
        headers['APPENGINE_RUNTIME'] = environ.get('APPENGINE_RUNTIME', '')
        headers['PATH_INFO'] = environ.get('PATH_INFO', '')
        return headers

    def T(self, woord=False, waarden=False, l=False):
        if woord:
            return self.translate(woord, waarden, l)

    def database(self, cdn=False):
        #init a connection with a database
        if not self.db and not cdn and not hasattr(self.db, '_tables'):
            self.field = Field
            if not self.request.env.get('APPENGINE_RUNTIME', False):
                #check if exsist else create directory
                if not os.path.exists(self.dbpath + '/database'):
                    os.makedirs(self.dbpath + '/database')

                self.db = DAL(cdn or self.memory.cdn_string, folder=self.dbpath + '/database', migrate=self.memory.migrate, fake_migrate=self.memory.fake_migrate)
                self.gae = False
            else:
                self.db = DAL(self.memory.gae_cdn_string)
                self.gae = True
        else:
            return DAL(cdn or self.memory.cdn_string, folder=self.dbpath + '/databases', migrate=False)

    def model(self, name=False, path='models', cdn=False, blanc_env=False, func=False):
        if not hasattr(self.db, '_tables'):
            self.database(cdn=cdn)
        if not name:
            name = self.memory.settings.data_model
        try:
            q_model = self.load_class(name, path, blanc_env, func)
            q_model.create_models()
            return q_model
        except:
            return False

    def build_request(self, environ):
        #build the request http://www.python.org/dev/peps/pep-0333/
        self.request.wsgi.version = environ.get('wsgi.version', False)
        self.request.wsgi.input = environ.get('wsgi.input', False)
        self.request.wsgi.errors = environ.get('wsgi.errors', False)
        self.request.wsgi.multithread = environ.get('wsgi.multithread', False)
        self.request.wsgi.multiprocess = environ.get('wsgi.multiprocess', \
                                                                         False)
        self.request.wsgi.run_once = environ.get('wsgi.run_once', False)
        self.request.env = self.get_headers(environ)
        #set the language Accept-Language
        try:
            self.lang = self.request.env['Accept-Language'][0:2].lower()
        except:
            self.lang = self.memory.settings.default_lang
        if self.lang == 'zh':
            #later patchen
            self.lang = 'cn'
        if self.lang == 'be':
            #later patchen
            self.lang = 'nl'
        if self.lang == 'us':
            #later patchen
            self.lang = 'en'

        if self.lang not in self.memory.settings.language:
            self.lang = self.memory.settings.default_lang
        self.gae = self.request.env.get('APPENGINE_RUNTIME', False)
        self.url = environ.get('PATH_INFO', '')
        self.is_cached = hashlib.md5(_(self.url + '_' + self.lang)).hexdigest()
        aanvraag = self.url.split('/')[1:]
        if aanvraag:
            for i, x in enumerate(aanvraag):
                self.request.args[i] = x
        if environ.get('REQUEST_METHOD', '') in ('POST', 'PUT') \
                                 and int(environ.get('CONTENT_LENGTH', False)):
            request_body_size = int(environ.get('CONTENT_LENGTH'))
            invoer = environ['wsgi.input'].read(request_body_size)
            self.post_vars = invoer
            dpost = parse_qsl(invoer)
            self.post = True
            for (k, v) in dpost:
                self.request.post[k] = v

        dget = parse_qsl(environ.get('QUERY_STRING', ''))

        if dget:
            for (key, value) in dget:
                self.request.vars[key] = value

        zout = str(self.memory.settings.cookie_salt)
        self.cookie_salt = self.encrypt(zout, algo='sha1')
        userkey = hashlib.md5()
        userkey.update(_(self.cookie_salt))
        userkey.update(_(environ.get('SERVER_NAME', zout)))
        userkey.update(_(environ.get('HTTP_USER_AGENT', zout)))
        userkey.update(_(environ.get('HTTP_ACCEPT_LANGUAGE', self.lang)))
        userkey.update(_(environ.get('REMOTE_ADDR', zout)))

        #self.stats = httpagent.detect(environ.get('HTTP_USER_AGENT'))

        #application management
        #get the url   
        #the user key
        authkey = userkey.hexdigest()
        self.cookie = authkey[0:16]
        self.cookie_value = self.encrypt(self.cookie_salt \
                                         + authkey[16:32])
        sl = str(self.cookie + '=' + self.cookie_value)

        self.fingerprint=self.encrypt(authkey[4:12])[12:20]
        #assume sha1 is available every where
        admin = self.encrypt(authkey, algo='sha1')
        self.admin_cookie = admin[0:16]
        self.admin_cookie_value = self.encrypt(self.cookie_salt + admin)
        asl = str(self.admin_cookie + '=' + self.admin_cookie_value)
        #now lets find out if there's a session active
        if [k for k in [sl] if k in self.request.env.get('Cookie', [])]:
            self.loggedin = self.cookie
        elif [k for k in [asl] if k in self.request.env.get('Cookie', [])]:
            self.isadmin = self.admin_cookie
            self.loggedin = self.cookie
        else:
            self.loggedin = False
            self.isadmin = False


    def segment(self, wat):
        """
        Returns the request in parts
        Counts from modules

        """
        if self.request.arg(0) and self.request.arg(0) in modules:
            return self.request.arg(int(wat)+1)
        else:
            return self.request.arg(int(wat)-1)

    def get_after(self, wat):
        """
        returns the part after a segment

        """
        return self.request.args[wat]

    def get_before(self, wat):
        """
        returns the part before a segment

        """
        return self.request.args[wat]

    def user(self):
        """
        Returns an user object, if logged in
        else returns False
        """
        if self.loggedin:
            user = self.model('auth')
            return user.get_user()
        else:
            return False

    def management(self):
        """
        SimpleCMS on the console


        """
        echo('Console -program', ret=False)




    def serve(self):
        """
        Webservice Serves the request
        check if it's a media request else check the world directory
        if not then kickin the controllers

        """        
        verzoek = self.url[1:] or 'index.html'
        if self.url.startswith('/' + self.memory.settings.dbmedia_folder + '/'):
            return self.download()

        else:      
            w = self.apppath + '/world/'
            #the result
            sttc = self.getfile(w + verzoek)
            if sttc != '404':   
                data = self.alt_view(sttc)         
                return self.commit([self.status, self.headers, data])
            else:
                return self.create_page()


    def serve_file(self, req, folder=False):
        return serve_file(folder + '/' + req)

    def download(self):
        file = self.model('media')
        data = file.serve_file()
        if data:
            return [self.status, self.headers, data]
        else:
            return self.forbidden()

    def forbidden(self):
        self.status = '403 forbidden'
        output = serve_file( self.apppath + '/views/system/http/403.html')
        return output

    def getfile(self, getfile):
        return serve_file(getfile)

    def render_view(self, view='404.html', getfile=False):
        """
        In production we are caching views

        """
        if self.memory.view[str(getfile) + view] and \
                              self.memory.settings.development == 'production':
            html = self.memory.view[str(getfile) + view]
        else:
            if not getfile:
                getfile = self.apppath + '/views/' + str(view)
            else:
                getfile = getfile.replace('.', '')
                getfile = getfile + '/views/' + str(view)
            html = serve_file(getfile)
            if self.memory.settings.development == 'production':
                    self.memory.view[str(getfile) + view] = html
        return html

    def template_parser(self, pagina, path):
        if not path:
            path = self.apppath + '/views/'
        return TemplateParser(pagina, path=path)

    def view(self, view, **zargs):
        """
        returns a generated view
        environment, getfile and commit are reserved vars
        doc: https://jan-karel.nl/simplecms/views.html#view

        """
        #de view
        if not 'getfile' in zargs:
            getfile = False
        pagina = self.render_view(view=view, getfile=getfile)
        #parse the template
        if not 'getfile' in zargs:
            getfile = self.apppath
        parser = TemplateParser(pagina, path=self.apppath + '/views/')
        #render the template, added with some functionality
        if not zargs:
            zargs = {}
        if not 'environment' in zargs:
            data = parser.render(self.environment(), **zargs)
        else:
            data = parser.render(zargs['environment'], **zargs)
        #commit!
        if not 'commit' in zargs:
            return self.commit(data)
        else:
            return data

    def alt_view(self, pagina, **kwargs):
        """
        parse and returns an object to view
        environment and getfile are reserved vars
        doc: https://jan-karel.nl/simplecms/views.html#alt_view

        """

        if not 'getfile' in kwargs:
            getfile = self.apppath
        parser = self.template_parser(pagina, path=getfile + '/views/')
        if not 'environment' in kwargs:
            return parser.render(self.environment(), **kwargs)
        else:
            return parser.render(kwargs['environment'], **kwargs)

    def raw_view(self, pagina, **kwargs):
        """
        returns a view
        getfile is a reserved var
        doc: https://jan-karel.nl/simplecms/views.html#raw_view

        """
        if not 'getfile' in kwargs:
            getfile = self.apppath
        return serve_file(getfile + '/views/' + pagina)

    def commit(self, data):
        """
        cleanup database and do some garbage collection

        """
        # logic to garbage collect after exec, not always, once every 100 requests
        # taken from web2py 
        global rmeuk 
        rmeuk = ('rmeuk' in globals()) and (rmeuk + 1) % 100 or 0 
        if not rmeuk and not self.post: 
            gc.collect()
        if self.db:
            BaseAdapter.close_all_instances('commit')
        return data

    def load_class(self, module, path='controllers', blanc_env=False, func=False):
        """
        Import and loads files, classes

        """
        try:
            if not blanc_env:
                blanc_env = dict()
            ophalen = self.apppath + '/' + path + '/' + module + '.py'
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
            #get the first request
            module = self.memory.settings.modules[self.request.args[0]]
        q = self.load_class(module, blanc_env=self.environment())


        if hasattr(q, module.title()) or hasattr(q, '_run'):
            #run as class
            return q._run()
        else:
            #run as function
            segment = 1 if self.request.arg(0) and self.request.arg(0) == module else 0
            function = self.request.arg(segment) or 'index'
            functie = function.split('.')[0]
            #stripout function
            if functie in q:
                return q[functie]()
            else:
                #huf, !?
                try:
                    return q['index']()
                except:
                    #logging
                    print 'hir'
                    return q._run()


    def environment(self):
        """
        Returns functions for controllers and views
        doc: https://jan-karel.nl/simplecms/functions.html#environment

        """
        return dict(request=self.request, T=self.T, SCMS=self, db=self.db,
                    time=self.time, date=self.date, view=self.view,
                    javascript=self.javascript, prettydate = self.prettydate,
                    css=self.css, xhtml=self.xhtml, vorm = self.vorm,
                    grid = self.grid, user = self.user, segment = self.segment,
                    get_after = self.get_after, post=self.request.post,
                    model=self.model, encrypt=self.encrypt,
                    now=self.request.now, get=self.request.vars,
                    )

    def set_session(self, date=19500):
        exprires = cookiedate(date)
        return exprires

    def delete_cookie(self, duur=-95000):
        self.status = '307 Temporary Redirect'
        if self.isadmin:
            waard = self.admin_cookie + ' = 1;' + self.cookie + \
               ' = 1 ;Path = /; Expires =' + self.set_session(duur) + ';'
        else:
            duur = str(self.set_session(duur))
            waard = self.cookie + ' = 1; Path = /; Expires =' + duur + ';'
        self.headers = [('Content-type', 'text/html'),
                            ('Set-Cookie', str(waard))]

    def set_cookie(self, userlevel=1, duur=19500):
        if userlevel < 100:
            waard = self.cookie + '=' + self.cookie_value + '; Path = /;'
        else:
            waard = self.admin_cookie + '=' + self.admin_cookie_value + '; Path = /; Expires =' + self.set_session(duur) + '; HttpOnly; Session;'
        self.headers = [('Content-type', 'text/html'), ('Set-Cookie', str(waard))]

    def create_page(self):
        """
        The create page function
        prepares conditions for the main controller

        """

        if self.request.arg(0) and self.request.arg(0) == self.memory.secure:
            """
            Auth is required to load

            """
            
            
            aanvraag = self.request.arg(1)
            functie = self.request.arg(2)
            modul = self.request.arg(3)

            if not self.isadmin:
                """
                This will setup the main account
                if there are any, login will be shown

                """
                data = self.view('base/login/setup_login.html')
                return [self.status, self.headers, data]
            if aanvraag == 'logout':
                auth=self.model('auth')
                auth.user_logout(ret=True)
                return [self.status, self.headers, 'redirect']

            items = []
            for x in self.memory.settings.backend_modules:
                items.append(x[1])
            for x in self.memory.settings.backend_pages:
                items.append(x[1])
            if aanvraag and aanvraag in items:
                
                e = self.load_class(aanvraag, func=False, blanc_env=self.environment(), path='controllers/cms')
                
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
                

                e = self.load_class(self.memory.secure_controller, path='controllers/cms', blanc_env=self.environment())

                if hasattr(e, '_run'):
                    dmn = e._run()
                else:
                    try:
                        dmn = e[aanvraag]()
                    except KeyError:
                        
                        dmn = e['index']()

            return self.commit([self.status,  self.headers, dmn])
        elif self.request.arg(0) and self.request.arg(0) in self.memory.settings.modules:
            data = self.controller()
            return self.commit([self.status, self.headers, data])
        else:
            #run the default application
            uitvoer = self.controller(self.memory.settings.default_application)
            #adjust some headers
            return self.commit([self.status, self.headers, uitvoer])

    def create_password(self, email=False, password=False):
        hashed = hashlib.sha1(str(self.memory.settings.salt)).hexdigest()
        key = hashlib.new(self.memory.settings.algorithm)
        key.update(hashed)
        key.update(hashlib.md5(str(hashed + email)).hexdigest())
        key.update(hashlib.sha1(str(hashed + password)).hexdigest())
        word = hashlib.md5(key.hexdigest()).hexdigest()
        return word

    def send_email(self, email=False, subject=False, message=False, bcc=False, tls=True):
        if self.gae:
            mailserver = 'gae'
        else:
            mailserver = self.memory.settings.mailserver
        if email and subject and message:
        #build the string
            if not hasattr(self.mail, 'send'):
                self.mail = Mail(server=str(mailserver), \
                                 sender=str(self.memory.settings.mailsender), \
                                 login=str(self.memory.settings.maillogin), \
                                 tls=tls)
        return self.mail.send(email, subject, message, bcc=bcc)

    def create_ticket(self, ticket=None, data=None):
        ticket = self.model('base_tickets')
        ticket.add_ticket(refer=ticket, message=data)

    def audit_trail(self, level=None, data=None):
        audit = self.model('auth')
        audit.add_audit(level=level, bericht=data)

    def translate(self, woord, waarden=False, l=False):
        """
        Translates strings if translation is found in memory
        Default language does not get translated
        """
        lang = l if l else self.lang              
        if lang == self.memory.settings.default_lang:
            return echo(woord, waarden)
        elif woord and self.memory.language[lang]:
            try:
                find = self.memory.language[lang][hash(woord)]
                if find:
                    return echo(find.encode('utf8', 'xmlcharrefreplace'), waarden)
                else:
                    if self.memory.settings.fix_lang:
                        #self.model('language')
                        return echo(woord, waarden)

                    else:
                        return echo(woord, waarden)
            except:
                return echo(woord, waarden)
        else:
            #is there a sh
            return echo(woord, waarden)

    def cache(self, name=None, data=False):
        if name == None:
            name = self.is_cached
        if data:
            self.memory.cache[name] = [self.status, self.headers, data]
        else:
            return self.memory.cache[name]

    def encrypt(self, text, algo='md5', get='hexdigest'):
        key = hashlib.new(algo)
        key.update(_(text))
        if get == 'hexdigest':
            return key.hexdigest()
        else:
            return key

    def redirect(self, location='/'):
        self.status = '307 Temporary Redirect'
        self.headers = [('Content-type', 'text/html'),
                        ('Location', location)]
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
        app = self
        return Vorm(app, table, id)

    def grid(self, table, fields, q=False, menu=False, extra=False,
               well=False, path=False, edit=False, search=False, delete=False, new=False, view=False, smart=False):
        grid = Grid(self, table, fields, q, menu, extra, well, path, edit, search, delete, new, view, smart)
        return grid.show()

    """
    HTML helpers

    """

    def class_active(self, home, items=False, req=0):
        wat = self.request.arg(req)
        if wat:
            wat = wat.replace('.html','')
        if items:
            if wat not in items:
                return ' class="active"'
            else:
                return ''
        else:
            if wat == home:
                return ' class="active"'
            else:
                return ''

    def html_lang(self):
        #the languae ISO 639-1
        if self.lang in self.memory.settings.language:
            if self.lang == 'cn':
                return str('zh-CN')
            else:
                return str(self.lang)
        else:
            return str(self.memory.settings.default_lang)

    def xhtml(self, reqstring='body,html,div,span,a,ul,li,p,h1,h2,h3,h4'):
        """
        XHTML generator, generates html tags

        """
        for name in reqstring.split(','):
            if not name in self.html:
                self.html[name] = HTML(tag[name])
        return self.html

    def javascript(self, code=None, include=None):
        """
        javascript
        ads requested javascript to the page
        """
        e = ''
        e2 = ''
        html = self.xhtml('script')
        if code == 'show':
            for script in self.javascript_file:
                if script.startswith('js'):
                    script = '/' + str(self.memory.settings.media_folder) + '/' + str(script)
                e += str(html.script.tag('', _type="text/javascript", _src=script))
            if self.javascript_inc:
                for inc in self.javascript_inc:
                    e2 += inc + '\n'
                e += str(html.script.tag(e2, _type="text/javascript"))
            return e
        elif include:
            if include not in self.javascript_file:
                self.javascript_file.append(include)
        else:
            if include not in self.javascript_inc:
                self.javascript_inc.append(code)

    def css(self, code=None, include=None):
        """
        css
        ads requested javascript to the page
        """
        e = ''
        e2 = ''
        html = self.xhtml('link, style')
        if code == 'show':
            for script in self.css_file:
                if script.startswith('css'):
                    script = '/' + self.memory.settings.media_folder + '/' + script
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

    """
    Fetch

    """

    def fetch(self, url):
        return fetch_url(url)

    """
    geocode

    """

    def geocode(self, waarde):
        if not self.tools:
            self.tools = Tools(self)
        return self.tools.geocode(waarde)

    """
    Date and time helpers

    """

    def prettydate(self, waarde, dagen=False):
        if not self.tools:
            self.tools = Tools(self)
        return self.tools.prettydate(waarde, dagen)

    def delta(self, days=False, hours=False, seconds=False):
        """
        timedelta

        """
        return datetime.timedelta(days, hours, seconds)

    def datetime(self):
        return datetime

    def timedelta(self):
        return datetime.timedelta

    def timediff(self, datum, teruggave=False, **kwargs):
        """
        get the difference between current and givven in timedelta
        """
        return self.prettydate(datum, dagen=True)

    def date(self, datum, teruggave=False):
        return self.time(datum, teruggave, date=True)

    def now(self):
        return datetime.datetime.now()

    def utcnow(self):
        return datetime.datetime.utcnow()

    def time(self, datum, teruggave=False, **kwargs):
        """
        based on the user language, rebuilds the datetime object
        completly disregarding utc or datetime.now
        """
        wtime = 0
        timestring = False
        datestring = False
        [year, month, day, hour, seconds, millisec] = timeparts(datum)
        if self.memory.language[self.lang]:
            try:
                timestring = self.memory.language[self.lang][hash('_timestr')]
                datestring = self.memory.language[self.lang][hash('_datestr')]
                try:
                    wtime = int(self.memory.language[self.lang][hash('_diff')])
                except:
                    wtime = 0
            except:
                timestring = False
                datestring = False
                wtime = 0
        if 'date' in kwargs:
            tstr = datestring or self.memory.settings.server_datestring
        else:
            tstr = timestring or self.memory.settings.server_timestring

        server = datetime.datetime(year, month, day, hour, seconds, millisec)
        #need to adjust the time
        tijd = server + datetime.timedelta(minutes=wtime)

        if teruggave:
            return tijd
        else:
            #return the string
            #set the time
            [year, month, day, hour, seconds, millisec] = timeparts(tijd)
            if hour < 10:
                hour = str('0' + str(hour))
            if seconds < 10:
                seconds = str('0' + str(seconds))
            return echo(tstr, [year, month, day, hour, seconds, millisec])

        #our query language

        


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
    #some vars
    uri = environ['PATH_INFO']
    ext = extension(uri)
    response_headers = False
    status = '200 ok'
    output = ' '

    """
     block some bogus request
     Todo: move the views to a template
    """
    if [k for k in memory.settings.blacklist if k in uri.lower()]:
        status = '403 forbidden'
        output = serve_file(memory.folder + '/' + memory.appfolder + '/views/' + memory.base_template + '/http/403.html')
        start_response(status, [('Content-type', 'text/html'),
                                        ('Content-Length', str(len(output)))])
        return output
    else:
        try:
            #static requests
            if uri.lower() in ['/favicon.ico', '/robots.txt', '/humans.txt']:
                output = serve_file(memory.folder + '/' + 'static' + uri)

            elif uri.startswith('/' + memory.settings.media_folder + '/'):
                bst = uri.replace('/' + memory.settings.media_folder + '/', '')
                output = serve_file(memory.folder + '/static/' + str(bst))
            #output directly + cache

            else:
                app = simplecms(environ, memory)
                status, response_headers, output = app.serve()
                #del app
        except:
            if memory.settings.log:
                try:
                    fout = traceback.format_exc()
                    print fout
                    output = '404'
                    if app:
                        if not hasattr(app, 'create_ticket'):
                            app = simplecms(environ, memory)
                    app.create_ticket(ticket=app.encrypt(str(fout)),\
                                  data=fout)
                except:
                    output = '404'
            else:
                #testing
                output = '404'
    """
    if a request returns a simple 404 string we'll show an error page
    or

    """
    del app

    if output == '404':
        status = '404 not found'
        ext = 'text/html'
        output = serve_file(memory.folder + '/' + memory.appfolder + '/views/' + memory.base_template + '/http/404.html')
    elif output == 'redirect':
        output = serve_file(memory.folder + '/' + memory.appfolder + '/views/' + memory.base_template + '/http/307.html')

    if not response_headers:
        req = ext.split('/')
        if [k for k in ['image', 'css', 'javascript'] if k in req]:
            response_headers = [('Content-type', ext),
            ('Cache-Control', 'public, max-age=290304000'),
                                     ('Content-Length', str(len(str(output))))]
        else:
            response_headers = [('Content-type', ext),
                                     ('Content-Length', str(len(str(output))))]

    start_response(status, response_headers)
    return [_(output)]


def _(s, enc='utf8', err='strict'):
    """
    Fix mixed encodings, force returning bytes, ignored on 2.5

    """
    if isinstance(s, bytes):
        return s
    else:
        return bytes(s.encode(enc))


def get_folder():
    p = __file__.split('simplecms_server')
    folder = os.path.abspath(p[0])
    sys.path.append(folder)
    return folder


memory = Memory()
memory.folder = get_folder()
memory.config(serve_file(memory.folder + '/config.scms'))
#ad import path
sys.path.append(memory.folder + '/' + memory.appfolder)
#and another, the modules
sys.path.append(memory.folder + '/' + memory.appfolder + '/modules')


def start_server(port=memory.settings.port, hostname=memory.settings.hostname):
    pid = os.getpid()
    echo("SimpleCMS - v{0} - {1}", [memory.settings.version, memory.settings.release], ret=False)
    echo("A fast,stable,secure and minimalistic framework", ret=False)
    echo("Copyright Jan-Karel Visser - all rights are reserved", ret=False)
    echo("Licensed under the LGPL v3", ret=False)
    echo("Serving on port {0}...", [port], ret=False)
    echo('use "kill -SIGTERM {0}" or ^C to shutdown simplecms or panic', [pid], ret=False)
    httpd = simplecms_server((hostname, port), simplecms_handler)
    httpd.set_app(server)
    httpd.serve_forever()

if __name__ == '__main__':
    start_server()
