#!/bin/env python
# -*- coding: utf-8 -*-

"""
 Grid
 A simple crud tool for SimpleCMS

 Copyright Jan-Karel Visser - all rights are reserved
 Licensed under the LGPLv3 (http://www.gnu.org/licenses/lgpl.html)

 This program is distributed in the hope that it will be useful, but
 WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

"""


edit_link = '<div class="btn-group pull-right">[1][extra][2][3]</div>'
btn = 'btn'
table_layout = '<table>{head}<tbody>{rows}</tbody></table>'
smartsearch = ['=','contains', '>=', '<=', '!=']


class Grid:

    def __init__(self, SCMS, table, fields, q=False, menu=False, extra=False, well=False, path=False, edit=False, search=False, delete=False, new=False, view=False, smart=False):
        self.app = SCMS
        self.auth = self.app.model('base_auth')
        self.table = self.app.db[table]
        self.taf = table
        self.fields = fields
        self.user = self.app.user()
        self.html = self.app.xhtml(
                'table,div,h2,p,a,ul,li,thead,th,tr,td,span,form,input,button')
        self.y = 20
        self.q = q if q else False
        self.xmenu = menu if menu else ''
        self.extra = extra if extra else False
        self.path = path if path else self.app.apppath + '/views/'+ self.app.m.base_template   
        self.well = well
        self.tot = False
        self.get_roles(edit, delete, view, new, search, smart)

    def get_roles(self, edit, delete, view, new, search, smart):
        self.canedit = edit if edit else False
        self.candelete = delete if delete else False
        self.canview = view if view else False
        self.cannew = new if new else False
        self.cansearch = search if search else False
        self.smart = smart if smart else False


    def user_rights(self, role=False):
        if int(self.user.userlevel) >= 200:
            return  dict(edit=1, view=1, delete=1, new=1, search=1, smart=1)
        if role:
            role='ok'
            return  dict(edit=1, view=1, delete=1, new=1, search=1, smart=1)
        else:
            return  dict(edit=0, view=0, delete=0, new=0, search=0, smart=0)





    def query_fields(self):
        collected_fields = []
        if not 'id' in self.fields:
            collected_fields.append(self.table['id'])
        for item in self.table:
            if item.name in self.fields:
                collected_fields.append(self.table[item.name])
        #create the headers

        return collected_fields

    def select_q(self):
        try:
            if self.q[3]:
                return self.table((self.table[q[0]]== self.q[1]) & (self.table[q[2]] == self.q[3]))
        except:
            return self.table[self.q[0]] == self.q[1]

    def query(self):
        #var limit set?
        if self.app.r.vars.pagina:
            a = (int(self.app.r.vars.pagina) * self.y) - self.y
            b = (int(self.app.r.vars.pagina) * self.y)
        else:
            a = (self.y - self.y)
            b = self.y
        if self.app.r.vars.zoeken and self.cansearch:
            zoek = self.app.r.vars.zoeken.replace('%20', ' ')
            if [k for k in smartsearch if k in zoek.lower()] and self.smart: 
                try:
                    if self.q:
                        res = self.app.db.smart_query(self.select_q(), zoek).select(
                                                                limitby=(a, b))
                    else:
                        res = self.app.db.smart_query([self.table], zoek).select(
                                                                limitby=(a, b))
                    self.tot = len(res)
                except:
                    res = False
            else:
                #try search at given strings
                zoekbaar = self.query_fields()
                xzoek = ''
                for x in zoekbaar:

                    x = str(x).replace(str(self.table)+'.', '')
                    if x != 'id' :
                        xzoek = str(xzoek) + str(x) + ' contains \'' + str(zoek.replace(' ','')) + '\' or '
                term = str(xzoek[:-4])
                
                try:
                    if self.q:
                        res = self.app.db.smart_query(self.select_q(), term).select(
                                                                limitby=(a, b))

                    else:
                        res = self.app.db.smart_query([self.table], term).select(
                                                                limitby=(a, b))

                    self.tot = len(res)
                except:
                    res = False
            return res
        if self.q:

            return self.app.db(self.select_q()).select(*self.query_fields(), limitby=(a, b))
        else:
            return self.app.db().select(*self.query_fields(), limitby=(a, b))

    def totaal(self):
        if self.q:
            return self.app.db(self.select_q()).count()
        else:
            return self.app.db(self.table.id > 0).count()

    def message(self, text, classname='danger'):
        self.html.span.add('&times;', _class='closer close_gridxid')
        self.html.div.add(self.html.span.xml() + ' '+self.app.T(text, l='nl'),
                                               _class=classname, _id='gridxid')
        return self.html.div.xml()

    def search_form(self):
        if not self.cansearch:
            return ''
        javascrip = "$('.submit_search').click(submit_search);function submit_search()\
{if($('#gridsearchval').val()){location.replace('" + self.app.url + "?zoeken=' + $('#gridsearchval').val());}}"

        self.app.javascript(code=javascrip)
        if self.smart:
            javascrip = "$('.smart_search').click(smart_search);function smart_search()\
{alert(this);}"
            self.app.javascript(code=javascrip)
            #build query from fields

        self.html.span.add('&times;', _class='closer close_gridsrchf')
        self.html.input.add('', _type='search', name='search', _value='',
                                   _id='gridsearchval', _placeholder=self.app.T('Zoeken...'))
        self.html.div.add(self.html.input.xml(), _class='span8')
        if self.smart:
            self.html.button.add(self.app.T('query'), _class='btn smart_search',_type='button')
        self.html.button.add(self.app.T('Zoeken', l='nl'), _class='btn',_type='button')
   
        self.html.div.add(self.html.button.xml(), _class='span2')
        self.html.form.add(self.html.span.xml() + self.html.div.xml(),
                            _method='get', _action='#', _class='well row hide',
                                                               _id='gridsrchf')
        return self.html.form.xml()

    def menu(self, message=False, classname='error'):
        newl = self.app.T('{0}?bewerk=nieuw&pagina={1}', [self.app.url,\
                                         self.app.r.vars.get('pagina', 1)])
        bl = self.app.T('{0}?pagina={1}', [self.app.url,\
                                         self.app.r.vars.get('pagina', 1)])

        btnnew = btn + ' icon-pencil btn-success pull-right'
        btnb = btn + ' icon-arrow-circle-left btn-warning pull-right'
        btnsearch = btn + ' icon-search pull-right t_function_show_gridsrchf '
        veld = ''
        if self.app.r.vars.bekijken or self.app.r.vars.bewerk:
                    self.html.a.add(' ' + self.app.T('Terug', l='nl'), _href=bl,
                                                                   _class=btnb)
        if not self.app.r.vars.bewerk == 'nieuw' and self.cannew:
            self.html.a.add(' ' + self.app.T('Nieuw',l='nl'), _href=newl, _class=btnnew)
        if self.app.r.vars.show and self.canedit:
            editl = self.app.T('{0}?bewerk={1}&pagina={2}', [self.app.url,\
             self.app.r.vars.show, self.app.r.vars.get('pagina', 1)])
            self.html.a.add(' ' + self.app.T('Bewerk'), _href=editl,
                                                                 _class=btnnew)
        if not self.app.r.vars.bewerk and self.cansearch:
            self.html.a.add(' ' + self.app.T('Zoeken'), _class=btnsearch)
        self.html.div.add(self.xmenu + self.html.a.xml(), _class='btngroup')
        if message:
                veld = self.message(message, classname)
        if self.well:
            #build the well
            self.html.h2.add(' ' + self.app.T(self.well[0]), _class=self.well[2] if self.well[2] else 'icon-pencil')
            self.html.p.add(self.well[1])
            te = self.html.h2.xml() + self.html.p.xml() + self.html.div.xml()
            self.html.div.add(te, _class="well")
            return self.html.div.xml() + veld + self.search_form()
        else:
            return self.html.div.xml() + veld + self.search_form()

    def show(self):
        if self.app.r.vars.bewerk:
            return self.edit(self.app.r.vars.bewerk)
        elif self.app.r.vars.weergeven:
            return self.show_row()
        elif self.app.r.vars.xsearch:
            return self.show_results()
        elif self.app.r.vars.verwijder:
            del self.table[self.app.r.vars.verwijder]
            menu = self.menu('Item verwijderd')
            return menu + self.gridtable()
        else:
            return self.menu() + self.gridtable()

    def show_results(self):
        res = self.app.db.smart_query([self.table],
                                         self.app.r.vars.zoeken).select()
        return str(res)

    def show_row(self):
        #use template?
        rij = self.table[self.app.r.vars.weergeven]
        path = self.path + '/grid/view_' + str(self.table) + '.html'
        template = self.app.raw_view('view_' + str(self.table) + '.html', getfile=self.path + '/grid/')
        #template = self.app.getfile(getfile=path)
        if template == '404':
            for v in rij:
                if rij[str(v)] and str(v) not in ['update_record','delete_record']:
                    self.html.li.add('<em>' + str(v) + '</em><br />' + \
           (str(rij[str(v)]) if rij[str(v)] else str(rij[str(v)])[0, 255]))
            self.html.ul.add(self.html.li.xml(), _class='unbullet')
            return self.menu() + self.html.ul.xml()
        else:
            template = self.app.alt_view(template, row=rij)
            return self.menu() + template

    def gridtable(self):

        javascrip = "$('.del_item').click(delete_item);function delete_item(e)\
{var item=m(this.id).getAttribute('data-del');m('delete_ok').href=item;$('#deleter').fadeIn();}"
        self.app.javascript(code=javascrip)
        #use template?
        #path = self.path + '/grid/table_' + str(self.table) + '.html'

        template = self.app.raw_view('table_' + str(self.table) + '.html', getfile=self.path + '/grid/')
        if template == '404':
            veld = ''
            aantal = 0
            rijen = self.query()
            if rijen:
                for x in self.fields:
                    self.html.th.add(self.app.T(self.table[x].label))
                    aantal = aantal + 1
                self.html.th.add(' ', _colspan='2')
                self.html.thead.add(self.html.th.xml())
                header = self.html.thead.xml()
                for x in rijen:
                    for g in self.fields:
                        self.html.td.add(x[g])
                        if not self.canedit:
                            self.ppencil = ''
                        else:
                            self.ppencil ='<a href="{0}?bewerk={1}&pagina={2}" class="icon-pencil btn smalltext"> </a>'
                        if not self.canview:
                            self.psearch = ''
                        else:
                            self.psearch = '<a href="{0}?weergeven={1}&pagina={2}" class="icon-search btn smalltext"> </a>'
                        if not self.candelete:
                            self.pdelete = ''
                        else:
                            self.pdelete='<span id="del_{1}" data-del="{0}?verwijder={1}&pagina={2}" class="icon-trash btn smalltext del_item"> </span>'
                        if self.extra:
                            ex = self.extra
                            vervang =  ex.replace('[id]', str(x['id']))
                            if 'username' in x:
                                vervang =  vervang.replace('[username]', str(x['username']))
                            d = edit_link.replace('[extra]', vervang)
                        else:
                            d = edit_link.replace('[extra]', '')
                    #delete is x
                    d = d.replace('[1]', self.ppencil)
                    d = d.replace('[2]', self.psearch)
                    d = d.replace('[3]',self.pdelete)
                    self.html.td.add(self.app.T(d, [self.app.url,
                               x['id'], self.app.r.vars.get('pagina', 1)]))
                    self.html.tr.add(self.html.td.xml())
                    veld = veld + self.html.tr.xml()
                x = table_layout.replace('{head}', header)
                veld = x.replace('{rows}', veld)
                #bladeren
                delen = (self.tot if self.tot else self.totaal()) / self.y + 1
                return veld + self.pagination(delen)
            else:
                return self.message('Geen gegevens beschikbaar', classname='error icon-exclamation-triangle')
        else:
            rijen = self.query()
            delen = (self.tot if self.tot else self.totaal()) / self.y + 1
            template = self.app.alt_view(template, rows=rijen, pagination=self.pagination(delen))
            return template
            

    def pagination(self, delen):
        if delen > 1:
                loc = self.app.r.vars.get('pagina', 1)
                deelteller = 0

                deler = delen
                
                """
                if loc >=5:

                elif loc <=10:

                elif loc 
                """
                if int(loc) >= 3:
                    self.html.a.add(' <<', _href=self.app.url + '?pagina=1')
                    self.html.li.add(self.html.a.xml(), _class='')    

                for x in range(delen):



                    classname = ("active" if loc == str(x + 1) else "")
                    href = self.app.url + '?pagina=' + str(x + 1)
                    if self.app.r.vars.search:
                        href = href + '&zoeken=' + self.app.r.vars.search

                    if x >= (int(loc) - 5) and x <= (int(loc) + 4):    

                        self.html.a.add(str(x + 1), _href=href)
                        self.html.li.add(self.html.a.xml(), _class=classname)

                if int(loc) < (delen-3):
                    self.html.a.add(' >>', _href=href)
                    self.html.li.add(self.html.a.xml())

                self.html.ul.add(self.html.li.xml())

                self.html.div.add(self.html.ul.xml(),
                                                _class='pagination pull-right')
                p =  self.html.div.xml()
                d =  p.replace('<li><li ','<li ')
                return d
        else:
            return ''

    def delete(self, id):
        formulier = self.app.vorm(self.table, id=id)
        return formulier.delete()

    def edit(self, id=0):
        message = False
        classname = False
        if id != 'nieuw':
            f = self.app.vorm(self.table, id=id)
        else:
            f = self.app.vorm(self.table)
        if self.app.post:
            #presave
            ee = f.save(post=self.app.r.post)
            if ee:
                message = self.app.T('item opgeslagen')
                classname = 'success'
            else:
                message = self.app.T('Formulier niet opgeslagen. Er is een fout opgetreden')
                classname = 'error'

        #use template?

        template = self.app.raw_view('edit_' + str(self.table) + '.html', getfile=self.path + '/grid/')

        if template == '404':
            form = f.show() + '<button type="submit" class="btn btn-success bigger pull-right icon-check"> '+self.app.T('Opslaan',l='nl')+'</button>'  
            self.html.form.add(form, _method="post", _autocomple="off", action=self.app.url)
            return self.menu(message, classname) + self.html.form.xml()
        else:
            template = self.app.alt_view(template, form=f)
            return self.menu(message, classname) + template
