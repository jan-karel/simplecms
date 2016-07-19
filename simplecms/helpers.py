#!/bin/env python
# -*- coding: utf-8 -*-

"""
 SimpleCMS helpers
 some basic functions

 Copyright Jan-Karel Visser - all rights are reserved
 Licensed under the LGPLv3 (http://www.gnu.org/licenses/lgpl.html)

 This program is distributed in the hope that it will be useful, but
 WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.


"""


import re
import datetime
import uuid
from time import gmtime, time

try:
    import urllib2
except ImportError:
    import urllib.request

try:
    import cStringIO as StringIO

except:
    from io import StringIO


io = StringIO


_week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
_month = [None, 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep',\
          'Oct', 'Nov', 'Dec']


regex_geocode = \
    re.compile(r"""<geometry>[\W]*?<location>[\W]*?<lat>(?P<la>[^<]*)</lat>[\W]
*?<lng>(?P<lo>[^<]*)</lng>[\W]*?</location>""")

sleutel = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(uuid.getnode()) ))

EXT_TYPE = {
    '.load': 'text/html',
    '.nessus': 'text/xml',
     '.7z': 'application/x-7z-compressed',
    '.atom': 'application/atom+xml',
     '.bmp': 'image/bmp',
    '.bz': 'application/x-bzip',
    '.bz2': 'application/x-bzip',
    '.cer': 'application/x-x509-ca-cert',
    '.cert': 'application/x-x509-ca-cert',
    '.css': 'text/css',
    '.csv': 'text/csv',
    '.deb': 'application/x-deb',
    '.der': 'application/x-x509-ca-cert',
    '.doc': 'application/msword',
    '.docbook': 'application/docbook+xml',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.dtd': 'application/xml-dtd',
    '.epub': 'application/epub+zip',
    '.flv': 'video/x-flv',
    '.gpg': 'application/pgp-encrypted',
    '.htm': 'text/html',
    '.html': 'text/html',
    '.ico': 'image/vnd.microsoft.icon',
    '.jpe': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.jpg': 'image/jpeg',
    '.js': 'application/javascript',
    '.json': 'application/json',
    '.jsonp': 'application/jsonp',
    '.pdf': 'application/pdf',
    '.pem': 'application/x-x509-ca-cert',
    '.pgp': 'application/pgp-encrypted',
    '.png': 'image/png',
    '.pps': 'application/vnd.ms-powerpoint',
    '.ppt': 'application/vnd.ms-powerpoint',
    '.ppz': 'application/vnd.ms-powerpoint',
    '.qif': 'image/x-quicktime',
    '.rar': 'application/x-rar',
    '.rdf': 'application/rdf+xml',
    '.rss': 'application/rss+xml',
    '.svg': 'image/svg+xml',
    '.svgz': 'image/svg+xml-compressed',
    '.swf': 'application/x-shockwave-flash',
    '.tar': 'application/x-tar',
    '.tar.bz': 'application/x-bzip-compressed-tar',
    '.tar.bz2': 'application/x-bzip-compressed-tar',
    '.tar.gz': 'application/x-compressed-tar',
    '.tar.lzma': 'application/x-lzma-compressed-tar',
    '.tar.lzo': 'application/x-tzo',
    '.tar.xz': 'application/x-xz-compressed-tar',
    '.tar.z': 'application/x-tarz',
    '.tbz': 'application/x-bzip-compressed-tar',
    '.tbz2': 'application/x-bzip-compressed-tar',
    '.tif': 'image/tiff',
    '.tiff': 'image/tiff',
    '.torrent': 'application/x-bittorrent',
    '.txt': 'text/plain',
    '.zip': 'application/zip'
    }

config = {
    'version': '1.0',
    'release': 'preview',
    'hostname': '',
    'port': 8888,
    'log' : True,
    'company_name' : 'SimpleCMS',
    'default_application' : 'website',
    'app_folder' : 'application',
    'base_template': 'base',
    'layout':'',
    'data_model': 'website',
    'development': 'dev',
    'worldfolders': {},
    'cdn_string': 'sqlite://database.db',
    'migrate': True, 
    'fake_migrate': True, 
    'gae_cdn_string': 'gae',
    'secure': 'management',
    'secure_controller': 'cms',
    'algorithm': 'sha512',
    'salt': sleutel,
    'cookie_salt': sleutel.split('-')[0],
    'media_folder': 'static',
    'dbmedia_folder': 'media',
    'mailserver': 'smtp.gmail.com:587',
    'mailsender': 'user@gmail.com',
    'maillogin': 'user@gmail.com:wachtwoord',
    'blacklist': ['@','*', '(',')','[',']', '}', '{', '<', '>', \
              '.ini','php','asp','jsp','jar', '~','*','.bak', 'wp', ':', '%',';', ',', '__',\
              'sql', 'cgi','csv','mysql','ftp','_vt','.hta','.bak','pwd'\
              'w00t', 'pma', 'admin', 'git', 'svn' ],
    'modules': {},
    'backend_pages':[('Website','pagina','globe'),('Bestanden','verkenner','picture-o')],
    'backend_modules': [('Beheer','beheer','cogs')],
    'language': {'en':'English', 'nl':'Nederlands'},
    'default_lang': 'en',
    'sql_lang': True,
    'server_timestring': '{0}-{1}-{2} {3}:{4}',
    'server_datestring': '{0}-{1}-{2}',

}


def default_config():
    return config

def extension(filename, default='text/html'):
    """
    Returns the Content-Type string matching extension of the given filename.
    """
    bestand = filename.rfind('.')
    if bestand >= 0:
        default = EXT_TYPE.get(filename[bestand:].lower(), default)
        ext = filename.rfind('.', 0, bestand)
        if ext >= 0:
            default = EXT_TYPE.get(filename[ext:].lower(), default)
            if default.startswith('text/'):
                default += '; charset=utf-8'
    return default


def cookiedate(future=0, weekdayname=_week, monthname=_month):
    now = time()
    year, month, day, hh, mm, ss, wd, y, z = gmtime(now + future)
    return "%s, %02d %3s %4d %02d:%02d:%02d GMT" % \
           (weekdayname[wd], day, monthname[month], year, hh, mm, ss)


def fetch_url(url):
    try:
        req = urllib2.urlopen(url)
        html = req.read()
    except:
        try:
            from google.appengine.api import urlfetch
            html = urlfetch.fetch(url=url)
        except:
            req = urllib.request.urlopen(url)
            html = req.read()
    return html


def literal_evil(st):
    """
    Eval could be evil. ast.literal_eval

    """
    return eval(st)


def execute(code):
    exec_buffer = io.StringIO()
    sys.stdout = exec_buffer
    try:
        exec(code)
        sys.stdout = sys.__stdout__
        last_output = exec_buffer.getvalue()
        exec_buffer.close()
        return last_output
    except:
        return '404'


def timeparts(datum):
    if hasattr(datum, 'year'):
        year = datum.year
        month = datum.month
        day = datum.day
        try:
            hour = datum.hour
            seconds = datum.minute
            millisec = datum.second
        except:
            hour = 00
            seconds = 00
            millisec = 0000
    else:
        datum = str(datum)
        parse_date = datum.split('-')
        rest = parse_date[2].split(' ')
        year = int(parse_date[0])
        month = int(parse_date[1])
        day = int(rest[0])
        #break it appart - time
        try:
            parse_time = rest[1].split(':')
            hour = int(parse_time[0])
            seconds = int(parse_time[1])
            millisec = int(float(parse_time[2]))
        except:
            hour = 00
            seconds = 00
            millisec = 0000
    return [year, month, day, hour, seconds, millisec]


def echo(message, replacements=False, ret=True):
    """
    For cross compatibility between 2 and 3

    """
    b = int('-1')
    if replacements:
        for x in replacements:
            f = b = b + 1
            k = '{' + str(f) + '}'
            message = message.replace(k, str(x))
    if ret:
        return str(message)
    else:
        print (str(message))


def serve_file(e):
    if isinstance(e, list):
        for x in e:
            print x
            d = get_file(x)
            print d
            if d != '404':
                print 'niet 404'
                return d
        return '404'        
    else:
        return get_file(e)

def get_file(e):        
    e = e.replace('//', '/')
    e = e.replace(';', '')
    e = e.replace('|', '') 
    e = e.replace(':', '')
    e = e.replace('..', '')
    print 'link is:'+e
    try:
        file = open(e, 'rb')
        item = file.read()
        file.close()
    except:
        item = '404'
    return item


class HTML:
    """
    returns string for views
    raw tag accessible via html.x.tag
    """

    def __init__(self, tag):
        self.tag = tag
        self.uitvoer = ''
        self.collect = []
        self.t = 0

    def add(self, tex, **arge):
        tag = str(self.tag(tex, **arge))
        self.uitvoer = self.uitvoer + tag
        self.collect += [tag]
        self.t = self.t + 1
        return tag

    def len(self):
        return self.t

    def clear(self):
        self.uitvoer = ''
        self.collect = []
        self.t = 0

    def items(self):
        if self.t >= 1:
            return self.collect
        else:
            return []

    def xml(self):
        e = str(self.uitvoer)
        self.clear()
        return e


# urlparse contains a duplicate of this method to avoid a circular import.  If
# you update this method, also update the copy in urlparse.  This code
# duplication does not exist in Python3. Thus we included here

_hd = '0123456789ABCDEFabcdef'
_ht = dict((a + b, chr(int(a + b, 16))) for a in _hd for b in _hd)


def unquote(s):
    """unquote('abc%20def') -> 'abc def'."""
    res = s.split('%')
    # fastpath
    if len(res) == 1:
        return s
    s = res[0]
    for item in res[1:]:
        try:
            s += _ht[item[:2]] + item[2:]
        except KeyError:
            s += '%' + item
        except UnicodeDecodeError:
            s += unichr(int(item[:2], 16)) + item[2:]
    return s


"""RFC 3986 is considered the current standard and any future changes to
urlparse module should conform with it.  The urlparse module is
currently not entirely compliant with this RFC due to defacto
scenarios for parsing, and for backward compatibility purposes, some
parsing quirks from older RFCs are retained. The testcases in
test_urlparse.py provides a good indicator of parsing behavior. """


def parse_qs(qs, keep_blank_values=0, strict_parsing=0):
    """Parse a query given as a string argument.

        Arguments:

        qs: percent-encoded query string to be parsed

        keep_blank_values: flag indicating whether blank values in
            percent-encoded queries should be treated as blank strings.
            A true value indicates that blanks should be retained as
            blank strings.  The default false value indicates that
            blank values are to be ignored and treated as if they were
            not included.

        strict_parsing: flag indicating what to do with parsing errors.
            If false (the default), errors are silently ignored.
            If true, errors raise a ValueError exception.
    """
    dict = {}
    for name, value in parse_qsl(qs, keep_blank_values, strict_parsing):
        if name in dict:
            dict[name].append(value)
        else:
            dict[name] = [value]
    return dict


def parse_qsl(qs, keep_blank_values=0, strict_parsing=0):
    """Parse a query given as a string argument.

    Arguments:

    qs: percent-encoded query string to be parsed

    keep_blank_values: flag indicating whether blank values in
        percent-encoded queries should be treated as blank strings.  A
        true value indicates that blanks should be retained as blank
        strings.  The default false value indicates that blank values
        are to be ignored and treated as if they were  not included.

    strict_parsing: flag indicating what to do with parsing errors. If
        false (the default), errors are silently ignored. If true,
        errors raise a ValueError exception.

    Returns a list, as G-d intended.
    """
    pairs = [s2 for s1 in qs.split('&') for s2 in s1.split(';')]
    r = []
    for name_value in pairs:
        if not name_value and not strict_parsing:
            continue
        nv = name_value.split('=', 1)
        if len(nv) != 2:
            if strict_parsing:
                raise echo("bad query field: {0}", name_value)
            # Handle case of a control-name with no equal sign
            if keep_blank_values:
                nv.append('')
            else:
                continue
        if len(nv[1]) or keep_blank_values:
            name = unquote(nv[0].replace('+', ' '))
            value = unquote(nv[1].replace('+', ' '))
            r.append((name, value))
    return r


class Tools:

    def __init__(self, SCMS):
        self.app = SCMS

    def geocode(self, address):
        try:
            a = urllib.quote(address)
        except:
            a = urllib2.quote(address)
        txt = fetch_url('http://maps.googleapis.com/maps/api/geocode/json?sensor=false&address='+a)
        return txt

    def prettydate(self, d, dagen=False):
        """
        calculates the time difference
        """
        if isinstance(d, datetime.datetime):
            dt = datetime.datetime.now() - d
        elif isinstance(d, datetime.date):
            dt = datetime.date.today() - d
        elif isinstance(d, str):
            s = timeparts(d)
            d = datetime.datetime(s[0], s[1], s[2], s[3], s[4], s[5])
            dt = datetime.datetime.now() - d
        elif not d:
            return ''
        else:
            return '[invalid date]'
        if dagen:
            terug = True
            if dt.days < 0:
                terug = False
                dt = -dt
            return [terug, dt]
        if dt.days < 0:
            suffix = ' from now'
            dt = -dt
        else:
            suffix = self.app.T(' ago')
        if dt.days >= 2 * 365:
            return self.app.T('{0} years', [int(dt.days / 365)]) + suffix
        elif dt.days >= 365:
            return self.app.T('{0} year', [int(1)]) + suffix
        elif dt.days >= 60:
            return self.app.T('{0} months', [int(dt.days / 30)]) + suffix
        elif dt.days > 21:
            return self.app.T('{0} month', [int(1)]) + suffix
        elif dt.days >= 14:
            return self.app.T('{0} weeks', [int(dt.days / 7)]) + suffix
        elif dt.days >= 7:
            return self.app.T('{0} week', [int(1)]) + suffix
        elif dt.days > 1:
            return self.app.T('{0} days', [dt.days]) + suffix
        elif dt.days == 1:
            return self.app.T('{0} day', [int(1)]) + suffix
        elif dt.seconds >= 2 * 60 * 60:
            return self.app.T('{0} hours', [int(dt.seconds / 3600)]) + suffix
        elif dt.seconds >= 60 * 60:
            return self.app.T('{0} hour', [int(1)]) + suffix
        elif dt.seconds >= 2 * 60:
            return self.app.T('{0} minutes', [int(dt.seconds / 60)]) + suffix
        elif dt.seconds >= 60:
            return self.app.T('{0} minute', [int(1)]) + suffix
        elif dt.seconds > 1:
            return self.app.T('{0} seconds', [dt.seconds]) + suffix
        elif dt.seconds == 1:
            return self.app.T('{0} second', [int(1)]) + suffix
        else:
            return self.app.T('now')


def xmlescape(s, quote=True):
    """
    returns an escaped string of the provided text s
    s: the text to be escaped
    quote: optional (default True)
    """
    # first try the xml function
    # otherwise, make it a string
    if not isinstance(s, (str, unicode)):
        s = str(s)
    elif isinstance(s, unicode):
        s = s.encode('utf8', 'xmlcharrefreplace')
    #s = s.replace("&", "&amp;")
    #s = s.replace("<", "&lt;")
    #s = s.replace(">", "&gt;")
    if quote:
        s = s.replace("'", "&#x27;")
        #s = s.replace('"', "&quot;")
    return s


class TAG(object):

    rules = {'ul': ['li'],
             'ol': ['li'],
             'thead': ['tr'],
             'tbody': ['tr'],
             'select': ['option', 'optgroup'],
             'optgroup': ['optionp']}

    def __init__(self, name):
        self.safe = safe
        self.name = name
        self.parent = None
        self.components = []
        self.attributes = {}

    @staticmethod
    def wrap(component, rules):
        if not rules:
            return component
        if not isinstance(component, TAG) or not component.name in rules:
            return TAG(rules[0])(component)

    def __call__(self, *components, **attributes):
        rules = self.rules.get(self.name, [])
        self.components = [self.wrap(comp, rules) for comp in components]
        self.attributes = attributes
        for component in self.components:
            if isinstance(component, TAG):
                component.parent = self
        return self

    def append(self, component):
        self.components.append(component)

    def insert(self, i, component):
        self.components.insert(i, component)

    def remove(self, component):
        self.components.remove(component)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.components[key]
        else:
            return self.attributes.get(key)

    def __setitem__(self, key, value):
        if isinstance(key, int):
            self.components.insert(key, value)
        else:
            self.attributes[key] = value

    def __iter__(self):
        for item in self.components:
            yield item

    def __str__(self):
        return self.xml()

    def __add__(self, other):
        return cat(self, other)

    def add_class(self, name):
        """ add a class to _class attribute """
        c = self['_class']
        classes = (set(c.split()) if c else set()) | set(name.split())
        self['_class'] = ' '.join(classes) if classes else None
        return self

    def remove_class(self, name):
        """ remove a class from _class attribute """
        c = self['_class']
        classes = (set(c.split()) if c else set()) - set(name.split())
        self['_class'] = ' '.join(classes) if classes else None
        return self

    regex_tag = re.compile('^([\w\-\:]+)')
    regex_id = re.compile('#([\w\-]+)')
    regex_class = re.compile('\.([\w\-]+)')
    regex_attr = re.compile('\[([\w\-\:]+)=(.*?)\]')

    def find(self, expr):
        union = lambda a, b: a.union(b)
        if ',' in expr:
            tags = reduce(union, [self.find(x.strip())
                                  for x in expr.split(',')], set())
        elif ' ' in expr:
            tags = [self]
            for k, item in enumerate(expr.split()):
                if k > 0:
                    children = [set([c for c in tag if isinstance(c, TAG)])
                                for tag in tags]
                    tags = reduce(union, children)
                tags = reduce(union, [tag.find(item) for tag in tags], set())
        else:
            tags = reduce(union, [c.find(expr)
                                 for c in self if isinstance(c, TAG)], set())
            tag = TAG.regex_tag.match(expr)
            id = TAG.regex_id.match(expr)
            _class = TAG.regex_class.match(expr)
            attr = TAG.regex_attr.match(expr)
            if (tag is None or self.name == tag.group(1)) and \
               (id is None or self['_id'] == id.group(1)) and \
               (_class is None or _class.group(1) in \
                    (self['_class'] or '').split()) and \
               (attr is None or self['_' + attr.group(1)] == attr.group(2)):
                tags.add(self)
        return tags

    def xml(self):
        name = self.name
        if name == 'script' or name == 'li':
            #allow raw input here
            co = ''.join(v for v in self.components)
        else:
            co = ''.join(xmlescape(v) for v in self.components)
        ca = ' '.join('%s="%s"' % (k[1:], k[1:] if v == True else xmlescape(v))
             for (k, v) in sorted(self.attributes.items())
             if k.startswith('_') and v is not None)
        ca = ' ' + ca if ca else ''
        if not self.components:
            return '<%s%s />' % (name, ca)
        else:
            return '<%s%s>%s</%s>' % (name, ca, co, name)

    __repr__ = __str__


class METATAG(object):

    def __getattr__(self, name):
        return TAG(name)

    def __getitem__(self, name):
        return TAG(name)

tag = METATAG()


class cat(TAG):

    def __init__(self, *components):
        self.components = components

    def xml(self):
        return ''.join(xmlescape(v) for v in self.components)


class safe(TAG):

    default_allowed_tags = {
        'a': ['href', 'title', 'target'], 'b': [], 'blockquote': ['type'],
        'br': [], 'i': [], 'li': [], 'ol': [], 'ul': [], 'p': [], 'cite': [],
        'code': [], 'pre': [], 'img': ['src', 'alt'], 'strong': [],
        'h1': [], 'h2': [], 'h3': [], 'h4': [], 'h5': [], 'h6': [],
        'table': [], 'tr': [], 'td': ['colspan'], 'div': [],
        }

    def __init__(self, text, sanitize=False, allowed_tags=None):
        self.text = text
        self.allowed_tags = allowed_tags or safe.default_allowed_tags

    def xml(self):
        return self.text