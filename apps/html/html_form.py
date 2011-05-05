#
#    Copyright (C) 2006  Distance and e-Learning Centre, 
#    University of Southern Queensland
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#


import pickle
import base64
import string
import types



        
class control(object):
    def __init__(self, parent=None, label=None, text=None, submit=None, action=None, data=None, title=None,
                  klass=None, id=None, javascript=None, **kargs):
        self.parent = parent
        self.label = label
        self.includeLabel = True
        if text is not None:
            text = str(text)
        self.text = text
        self.submit = submit
        self.action = action
        self.data = data
        self.title = title
        self.klass = klass
        if id==None:
            id = self.getNextId()
        self.id = id
        self.javascript = javascript
        self.kargs = kargs
        self.onclick = None
        self.onchange = None
        self.controlType = None
        self.disabled = None

    def hasItems(self):
        return False

    def hasControls(self):
        return False
        
    def iterControls(self):
        if False:
            yield None

    def iterAllControls(self):
        if False:
            yield None

    def value(self, name=None):
        if self.parent is None:
            return None
        if name is None:
            name = self.id
        return self.parent.value(name)
        
    def values(self, name=None):
        if self.parent is None:
            return None
        if name is None:
            name = self.id
        return self.parent.values(name)

    def hasLabel(self):
        return (self.label is not None) and self.includeLabel

    def getLabelHtml(self):
        if self.label is None:
            return ""
        _for = self.getAttr("for", self.id)
        label = self.escapeHtml(self.label)
        if self.disabled==True:
            label = "<span style='color:gray;'>%s</span>" % label
        h = "<label%s> %s </label>" % (_for, label)
        return h

    def getNextId(self):
        if self.parent is not None:
            return self.parent.getNextId()
        else:
            return None
        
    def getJavascript(self):
        js = "javascript:"
        if self.action!=None:
            js += "_fx._act.value='%s';" % self.action.replace("'", "\\'")
        if self.data!=None:
            if type(self.data) is types.DictType:
                for key, value in self.data.items():
                    if key==None or key=="":
                        key = "_data"
                    js += "_fx.%s.value='%s';" % (key, str(value).replace("'", "\\'"))
            else:
                js += "_fx._data.value='%s';" % str(self.data).replace("'", "\\'")
        if self.javascript!=None:
            js += self.javascript
        if self.submit:
            js += "_fx.submit();"
        if js=="javascript:":
            js = None
        return js
        
    def getCommonAttr(self):
        #title, klass, id/name
        a = self.__attr("title", self.title)
        a += self.__attr("class", self.klass)
        a += self.__attr("id", self.id) + self.__attr("name", self.id)
        return a
    
    def getAttr(self, name, value):
        a = self.__attr(name, value)
        return a
        
    def getHtml(self):
        raise Exception("The getHtml() method must be overriden in the derived class!")
        
    def __str__(self):
        h = ""
        if self.includeLabel:
            h += self.getLabelHtml()
        h += self.getHtml()
        return h

    def escapeHtml(self, data):
        if data is None:
            return ""
        data = data.replace("&", "&amp;")
        data = data.replace("<", "&lt;").replace(">", "&gt;")
        return data

    def __attr(self, name, value):
        if value==None:
            return ""
        else:
            value = str(value)
            value = self.escapeHtml(value)
            if value.count('"')==0:
                value = '"' + value + '"'
            elif value.count("'")==0:
                value = "'" + value + "'"
            elif value.count('"')>=value.count("'"):
                value = "'" + value.replace("'", "&apos;") + "'"
            else:
                value = '"' + value.replace('"', "&quot;") + '"'
            return " %s=%s" % (name, value)


class containerControl(control):
    class mockParent(object):
        def __init__(self, id=None):
            self.__nextId = 0;
            if id is None:
                id = "xx"
            self.__Id = id
        def getNextId(self):
            self.__nextId += 1
            return str(self.__Id) + "_" + str(self.__nextId)
        def value(self, name):
            return None
        def values(self, name):
            return []
    def __init__(self, parent=None, label=None, text=None, submit=None, action=None, data=None,
                  title=None, klass=None, id=None, javascript=None, **kargs):
        if parent is None:
            parent = containerControl.mockParent(id=id)
        control.__init__(self, parent=parent, label=label, text=text, submit=submit, 
                         action=action, data=data, title=title, klass=klass, id=id,
                         javascript=javascript, **kargs)
        self.items = []

    def hasItems(self):
        return len(self.items)>0

    def hasControls(self):
        for control in self.iterControls():
            return True
        return False
        
    def iterControls(self):
        for item in self.items:
            if isinstance(item, control):
                yield item

    def iterAllControls(self):
        for control in self.iterControls():
            yield control
            for c in control.iterAllControls():
                yield c

    def addControl(self, control):
        control.parent = self
        self.items.append(control)
        
    def value(self, name=None):
        if name is None:
            name = self.id
        return self.parent.value(name)
        
    def values(self, name=None):
        if name is None:
            name = self.id
        return self.parent.values(name)

    def getHtml(self):
        h = []
        for item in self.items:
            h.append(str(item))
        return string.join(h, "")
    
    def createText(self, text):
        return htmlText(text)
    def addText(self, text):
        self.items.append(htmlText(text))
        
    def createRawText(self, text):
        return self.htmlRawText(text)
    def addRawText(self, text):
        self.items.append(htmlRawText(text))    
    
    def createSpace(self, count=1):
        return self.createRawText("&#160;" * count)
    def addSpace(self, count=1):
        self.addRawText("&#160;" * count)
    
    def createNewLine(self, count=1):
        return self.createRawText("<br />" * count)
    def addNewLine(self, count=1):
        self.addRawText("<br />" * count)
    
    def createImage(self, img, alt, title=None, klass=None, id=None):
        img = image(self, title=title, klass=klass, id=id, img=img, alt=alt)
        return img
    def addImage(self, img, alt, title=None, klass=None, id=None):
        img = image(self, title=title, klass=klass, id=id, img=img, alt=alt)
        self.addControl(img)
        return img
    
    def createTable(self, label=None, text=None, submit=None, action=None, data=None, title=None,
                 klass=None, id=None, javascript=None, **kargs):
        t = table(self, label, text, submit, action, data, title, klass, id, javascript, **kargs)
        return t
    def addTable(self, label=None, text=None, submit=None, action=None, data=None, title=None,
                 klass=None, id=None, javascript=None, **kargs):
        t = table(self, label, text, submit, action, data, title, klass, id, javascript, **kargs)
        self.addControl(t)
        return t
        
    def createFieldset(self, label=None, text=None, submit=None, action=None, data=None, title=None,
                 klass=None, id=None, javascript=None, **kargs):
        fs = fieldset(self, label, text, submit, action, data, title, klass, id, javascript, **kargs)
        return fs
    def addFieldset(self, label=None, text=None, submit=None, action=None, data=None, title=None,
                 klass=None, id=None, javascript=None, **kargs):
        fs = fieldset(self, label, text, submit, action, data, title, klass, id, javascript, **kargs)
        self.addControl(fs)
        return fs
    
    def createDiv(self, label=None, text=None, submit=None, action=None, data=None, title=None,
                 klass=None, id=None, javascript=None, **kargs):
        d = div(self, label, text, submit, action, data, title, klass, id, javascript, **kargs)
        return d
    def addDiv(self, label=None, text=None, submit=None, action=None, data=None, title=None,
                 klass=None, id=None, javascript=None, **kargs):
        d = div(self, label, text, submit, action, data, title, klass, id, javascript, **kargs)
        self.addControl(d)
        return d
        
    def createH1(self, label=None, text=None, submit=None, action=None, data=None, title=None,
                 klass=None, id=None, javascript=None, **kargs):
        h = h1(self, label, text, submit, action, data, title, klass, id, javascript, **kargs)
        return h
    def addH1(self, label=None, text=None, submit=None, action=None, data=None, title=None,
                 klass=None, id=None, javascript=None, **kargs):
        h = h1(self, label, text, submit, action, data, title, klass, id, javascript, **kargs)
        self.addControl(h)
        return h
    
    def createSpan(self, label=None, text=None, submit=None, action=None, data=None, title=None,
                 klass=None, id=None, javascript=None, **kargs):
        s = span(self, label, text, submit, action, data, title, klass, id, javascript, **kargs)
        return s
    def addSpan(self, label=None, text=None, submit=None, action=None, data=None, title=None,
                 klass=None, id=None, javascript=None, **kargs):
        s = span(self, label, text, submit, action, data, title, klass, id, javascript, **kargs)
        self.addControl(s)
        return s
    
    def createButton(self, label=None, text="Button", submit=None, action=None, data=None, title=None,
                  klass=None, id=None, javascript=None, **kargs):
        but = button(self, label, text, submit, action, data, title, klass, id, javascript, **kargs)
        return but
    def addButton(self, label=None, text="Button", submit=None, action=None, data=None, title=None,
                  klass=None, id=None, javascript=None, **kargs):
        but = button(self, label, text, submit, action, data, title, klass, id, javascript, **kargs)
        self.addControl(but)
        return but
    
    def createLink(self, label=None, text="link", submit=None, action=None, data=None, title=None,
                 klass=None, id=None, javascript=None, **kargs):
        lnk = link(self, label, text, submit, action, data, title, klass, id, javascript, **kargs)
        return lnk
    def addLink(self, label=None, text="link", submit=None, action=None, data=None, title=None,
                 klass=None, id=None, javascript=None, **kargs):
        lnk = link(self, label, text, submit, action, data, title, klass, id, javascript, **kargs)
        self.addControl(lnk)
        return lnk
        
    def createTextInput(self, label=None, text=None, submit=None, action=None, data=None, title=None,
                 klass=None, id=None, javascript=None, **kargs):
        txtInput = textInput(self, label, text, submit, action, data, title, klass, id, javascript, **kargs)
        return txtInput
    def addTextInput(self, label=None, text=None, submit=None, action=None, data=None, title=None,
                 klass=None, id=None, javascript=None, **kargs):
        txtInput = textInput(self, label, text, submit, action, data, title, klass, id, javascript, **kargs)
        self.addControl(txtInput)
        return txtInput
        
    def createCheckbox(self, label=None, text=None, submit=None, action=None, data=None, title=None,
                 klass=None, id=None, javascript=None, **kargs):
        cbox = checkbox(self, label, text, submit, action, data, title, klass, id, javascript, **kargs)
        return cbox
    def addCheckbox(self, label=None, text=None, submit=None, action=None, data=None, title=None,
                 klass=None, id=None, javascript=None, **kargs):
        cbox = checkbox(self, label, text, submit, action, data, title, klass, id, javascript, **kargs)
        self.addControl(cbox)
        return cbox
        
    def createRadioButton(self, label=None, text=None, submit=None, action=None, data=None, title=None,
                 klass=None, id=None, javascript=None, **kargs):
        r = radioButton(self, label, text, submit, action, data, title, klass, id, javascript, **kargs)
        return r
    def addRadioButton(self, label=None, text=None, submit=None, action=None, data=None, title=None,
                 klass=None, id=None, javascript=None, **kargs):
        r = radioButton(self, label, text, submit, action, data, title, klass, id, javascript, **kargs)
        self.addControl(r)
        return r
        
    def createSelectList(self, label=None, text=None, submit=None, action=None, data=None, title=None,
                 klass=None, id=None, javascript=None, **kargs):
        s = selectList(self, label, text, submit, action, data, title, klass, id, javascript, **kargs)
        return s        
    def addSelectList(self, label=None, text=None, submit=None, action=None, data=None, title=None,
                 klass=None, id=None, javascript=None, **kargs):
        s = selectList(self, label, text, submit, action, data, title, klass, id, javascript, **kargs)
        self.addControl(s)
        return s


class htmlForm(containerControl):
    def __init__(self, formData=None, method="POST", nameId="_fx_", enableFileUpload=False):
        self.__nextId = 0
        self.__formData = formData
        self.method = method
        self.nameId = nameId
        self.enableFileUpload = enableFileUpload
        self.variables = {"isPostBack":"true", "_act":"", "_data":""}
        containerControl.__init__(self, self)
        self.rawJavascript = "_fx=document.forms._fx_;\n"
    
    def processEvents(self, objectToHandleEvents=None):
        action = None
        data = None
        if self.__formData.has_key("isPostBack"):
            action = self.__formData.value("_act")
            data = self.__formData.value("_data")
        if objectToHandleEvents is None:
            return action, data
            
    def value(self, name):
        return self.__formData.value(name)
        
    def values(self, name):
        return self.__formData.values(name)
    
    def __getIsPostBack(self):
        return self.value("isPostBack") is not None
    isPostBack = property(__getIsPostBack)
    
    def addVariable(self, name, value=None):
        if value is None:
            value = self.value(name)
        self.variables[name] = value;
    
    def setValue(self, name, value):
        self.__formData.setValue(name, value)
    
    def addJavascript(self, js):
        self.rawJavascript += js + "\n"
    
    def addState(self, stateObject):
        """ serialize and encode the given object (state) """
        str = pickle.dumps(stateObject)
        value = base64.encodestring(str)
        self.addVariable("_state_", value)
        
    def getState(self):
        """ decode and recreate the state object """
        state = None
        str = self.__formData["_state_"]
        if str is not None:
            state_str = base64.decodestring(str)
            state = pickle.loads(state_str)
        return state
    
    def getNextId(self):
        self.__nextId += 1
        return "_id%s" % self.__nextId
    
    def getHtml(self):
        enctype = ""
        if self.enableFileUpload:
            enctype = "enctype='multipart/form-data' "
        html = "<form method='%s' name='%s' id='%s' %s>\n"
        html = html % (self.method, self.nameId, self.nameId, enctype)
        strlist = [html]
        for name, value in self.variables.iteritems():
            name = self.getAttr("name", name)
            value = self.getAttr("value", value)
            hidden = "<input type='hidden'%s%s />\n"
            hidden = hidden % (name, value)
            strlist.append(hidden)
        # 
        #"<script type=\"text/javascript\">_fx=document.forms._fx_;</script>\n"
        if len(self.rawJavascript)>0:
            js = self.escapeHtml(self.rawJavascript)
            js = "<script type=\"text/javascript\">%s</script>\n" % js
            strlist.append(js)
        for item in self.items:
            strlist.append(str(item))
        strlist.append("</form>\n")
        return string.join(strlist, "")


#===================
#    Controls
#===================
class table(containerControl):
    class row(object):
        def __init__(self, id=None):
            self.id = id
            self.cells = []
        def getHtmlList(self):
            s = ["<tr>\n"]
            for cell in self.cells:
                s.extend(cell.getHtmlList())
            if len(self.cells)==0:
                s.append("<td/>\n")
            s.append("</tr>\n")
            return s 
        def iterCells(self):
            for cell in self.cells:
                yield cell
    class cell(object):
        def __init__(self, colspan=None, rowspan=None):
            self.colspan = colspan
            self.rowspan = rowspan
            self.items = []
        def getHtmlList(self):
            attrs = ""
            if self.colspan is not None:
                attrs += " colspan='%s'" % self.colspan
            if self.rowspan is not None:
                attrs += " rowspan='%s'" % self.rowspan
            s = ["<td%s>" % (attrs)]
            for item in self.items:
                s.append(str(item))
            s.append("</td>\n")
            return s
            
    def __init__(self, parent=None, label=None, text=None, submit=None, action=None, data=None,
                  title=None, klass=None, id=None, javascript=None, **kargs):
    #def __init__(self, parent=None, klass=None, id=None):
        containerControl.__init__(self, parent=parent, label=label, text=text, submit=submit,
                                   action=action, data=data, title=title, klass=klass, id=id,
                                   javascript=javascript, **kargs)
        self.controlName = "table"
        self.controlType = self
        self.includeLabel = False
        self.rows = []    # a list of cells ([])

    def addRow(self):
        self.__update()
        self.rows.append(table.row())
        
    def addCell(self, colspan=None, rowspan=None):
        row = self.__update()
        cell = table.cell(colspan=colspan, rowspan=rowspan)
        row.cells.append(cell)
        
    def addToCells(self, control):
        self.addCell()
        if control.hasLabel():
            self.items.append(control.label)
        self.addCell()
        self.items.append(control.control)

    def iterRows(self):
        self.__update()
        for row in self.rows:
            yield row
    
    def hasControls(self):
        for control in self.iterControls():
            return True
        return False
    
    def iterControls(self):
        self.__update()
        for row in self.rows:
            for cell in row.cells:
                for item in cell.items:
                    if isinstance(item, control):
                        yield item
    
    def __update(self):
        if self.rows==[]:
            self.rows.append(table.row())
        # get the last row
        row = self.rows[len(self.rows)-1]
        # get the last cell
        if self.items!=[]:    # if self.items is not empty then these items must belong to the previous cell
            if row.cells==[]:    # if row has no cells then append a cell
                cell = table.cell()
                row.cells.append(cell)
                cell.items = self.items
            else:
                # get the last cell and add these items to it
                cell = row.cells[len(row.cells)-1]
                cell.items.extend(self.items)
            self.items = []
        return row

    def getHtml(self):
        self.__update()
        common = self.getCommonAttr()
        slist = []
        slist.append("<table%s>\n" % common)
        if self.label!=None:
            slist.append("<caption>%s</caption>\n" % self.escapeHtml(self.label))
        slist.append("<tbody>\n")
        for row in self.rows:
            slist.extend(row.getHtmlList())
        slist.append("</tbody>\n")
        slist.append("</table>\n")
        return string.join(slist, "")


class fieldset(containerControl):
    def __init__(self, parent=None, label=None, text=None, submit=None, action=None, data=None, title=None,
                  klass=None, id=None, javascript=None, **kargs):
        containerControl.__init__(self, parent, label, text, submit, action, data, title, klass, id, javascript, **kargs)
        self.controlName = "Fieldset"
        self.controlType = self
        self.includeLabel = False
        
    def getHtml(self):
        js = self.getJavascript()
        onclick = self.getAttr("onclick", js)
        common = self.getCommonAttr()
        legend = self.escapeHtml(self.label)
        data = ""
        if self.text is not None:
            data += self.escapeHtml(self.text)
        data += containerControl.getHtml(self)
        h = "<fieldset%s%s><legend>%s</legend>\n%s</fieldset>\n"
        h = h % (common, onclick, legend, data)
        return h
   

class blockElement(containerControl):
    def __init__(self, parent=None, label=None, text=None, submit=None, action=None, data=None, title=None,
                  klass=None, id=None, javascript=None, controlName="??", elementName="?", **kargs):
        containerControl.__init__(self, parent, label, text, submit, action, data, title, klass, id, javascript, **kargs)
        self.controlType = self
        self.controlName = controlName
        self.elementName = elementName
        self.zzzz = None
        
    def getHtml(self):
        js = self.getJavascript()
        onclick = self.getAttr("onclick", js)
        common = self.getCommonAttr()
        data = ""
        if self.text!=None:
            data += self.escapeHtml(self.text)
        data += containerControl.getHtml(self)
        h = "<%s%s%s>%s</%s>\n"
        try:
            h = h % (self.elementName, common, onclick, data, self.elementName)
        except Exception, e:
            h = ""
            print "ERROR:" + str(e)
            print dir(self)
        return h

class div(blockElement):
    def __init__(self, parent=None, label=None, text=None, submit=None, action=None, data=None, title=None,
                  klass=None, id=None, javascript=None, **kargs):
        blockElement.__init__(self, parent, label, text, submit, action, data, title, klass, id, \
            javascript, contorlName="Div", elementName="div", **kargs)

class fieldset(blockElement):
    def __init__(self, parent=None, label=None, text=None, submit=None, action=None, data=None, title=None,
                  klass=None, id=None, javascript=None, **kargs):
        blockElement.__init__(self, parent, label, text, submit, action, data, title, klass, id, \
            javascript, contorlName="Fieldset", elementName="fieldset", **kargs)
        self.includeLabel = False

    def getHtml(self):
        js = self.getJavascript()
        onclick = self.getAttr("onclick", js)
        common = self.getCommonAttr()
        data = ""
        if self.text!=None:
            data += self.escapeHtml(self.text)
        data += containerControl.getHtml(self)
        h = "<%s%s%s><legend>%s<legend>%s</%s>\n"
        try:
            h = h % (self.elementName, common, onclick, data, self.label, self.elementName)
        except Exception, e:
            h = ""
            print "ERROR:" + str(e)
            print dir(self)
        return h

class h1(blockElement):
    def __init__(self, parent=None, label=None, text=None, submit=None, action=None, data=None, title=None,
                  klass=None, id=None, javascript=None, **kargs):
        blockElement.__init__(self, parent, label, text, submit, action, data, title, klass, id, \
            javascript, contorlName="HeadingLevel1", elementName="h1", **kargs)
    

class span(containerControl):
    def __init__(self, parent=None, label=None, text=None, submit=None, action=None, data=None, title=None,
                  klass=None, id=None, javascript=None, **kargs):
        containerControl.__init__(self, parent, label, text, submit, action, data, title, klass, id, javascript, **kargs)
        self.controlName = "Span"
        self.controlType = self
    
    def addControl(self, control):
        #if isinstance(control, containerControl):
        #    raise Exception("The span control can not contain containerControls!")
        containerControl.addControl(self, control)

    def getHtml(self):
        js = self.getJavascript()
        onclick = self.getAttr("onclick", js)
        common = self.getCommonAttr()
        data = ""
        if self.text!=None:
            data += self.escapeHtml(self.text)
        data += containerControl.getHtml(self)
        h = "<span%s%s>%s</span>"
        h = h % (common, onclick, data)
        return h
    

class htmlText(object):
    def __init__(self, text=""):
        self.text = text
        self.name = "htmlText"
        self.parent = None
    def getHtml(self):
        return self.escapeHtml(self.text)
    def __str__(self):
        return self.getHtml()
    def escapeHtml(self, data):
        if data is None:
            return ""
        data = data.replace("&", "&amp;")
        data = data.replace("<", "&lt;").replace(">", "&gt;")
        return data

class htmlRawText(htmlText):
    def __init__(self, text=""):
        htmlText.__init__(self, text)
        self.name = "htmlRawText"
    def getHtml(self):
        return self.text        
        
class image(control):
    def __init__(self, parent=None, label=None, text=None, submit=None, action=None, data=None, title=None,
                  klass=None, id=None, javascript=None, img=None, alt=None, **kargs):
        control.__init__(self, parent, label, text, submit, action, data, title, klass, id, javascript, **kargs)
        self.controlName = "Image"
        self.__img = img
        if alt is None:
            self.__alt = text
        else:
            self.__alt = alt
        self.controlType = self
        
    def getHtml(self):
        js = self.getJavascript()
        onclick = self.getAttr("onclick", js)
        common = self.getCommonAttr()
        src = self.getAttr("src", self.__img)
        alt = self.getAttr("alt", self.__alt)
        h = "<img%s%s%s%s/>"% (common, src, alt, onclick)
        return h
        
    def __str__(self):
        return self.getHtml()
        
    
class button(control):
    def __init__(self, parent=None, label=None, text="Button", submit=None, action=None, data=None, title=None,
                  klass=None, id=None, javascript=None, **kargs):
        control.__init__(self, parent, label, text, submit, action, data, title, klass, id, javascript, **kargs)
        self.controlName = "Button"
        self.controlType = self
    
    def getHtml(self):
        js = self.getJavascript()
        common = self.getCommonAttr()
        onclick = self.getAttr("onclick", js)
        text = self.escapeHtml(self.text)
        h = "<button%s%s>%s</button>\n" % (onclick, common, text)
        return h


class link(control):
    def __init__(self, parent=None, label=None, text="link", submit=None, action=None, data=None, title=None,
                  klass=None, id=None, javascript=None, **kargs):
        control.__init__(self, parent, label, text, submit, action, data, title, klass, id, javascript, **kargs)
        self.controlName = "Link"
        self.controlType = self
        self.href = kargs.get("href", None)
        self.target = kargs.get("target", None)
        self.__others = ""
        if self.target is not None:
            self.__others = " target='%s'" % self.target
    
    def getHtml(self):
        js = self.getJavascript()
        if js is not None and self.submit==None:
            submit = True
        common = self.getCommonAttr()
        href = self.getAttr("href", js)
        if self.href is not None:
            href = self.getAttr("href", self.href)
        text = self.escapeHtml(self.text)
        h = "<a%s%s%s>%s</a>" % (href, common, self.__others, text)
        return h


class textInput(control):
    def __init__(self, parent=None, label=None, text=None, submit=None, action=None, data=None, title=None,
                  klass=None, id=None, javascript=None, **kargs):
        control.__init__(self, parent, label, text, submit, action, data, title, klass, id, javascript, **kargs)
        self.controlName = "Link"
        self.controlType = self
        self.size = kargs.get("size", 20)
        self.rows = kargs.get("rows", 1)
        if self.text is None:
            self.text = self.value()
            if self.text is None:
                self.text = ""
    
    def getHtml(self):
        js = self.getJavascript()
        text = self.escapeHtml(self.text)
        common = self.getCommonAttr()
        onchange = self.getAttr("onchange", js)
        h = ""
        if self.rows>1:
            rows = self.getAttr("rows", self.rows)
            cols = self.getAttr("cols", self.size)
            value = self.escapeHtml(self.text)
            h += "<textarea%s%s%s%s>%s</textarea>" % (common, onchange, rows, cols, value)
        else:
            size = self.getAttr("size", self.size)
            value = self.getAttr("value", self.text)
            h += "<input type=\"text\"%s%s%s%s />" % (common, onchange, size, value)
        return h + "\n"


class checkbox(control):
    def __init__(self, parent=None, label=None, text=None, submit=None, action=None, data=None, title=None,
                  klass=None, id=None, javascript=None, **kargs):
        control.__init__(self, parent, label, text, submit, action, data, title, klass, id, javascript, **kargs)
        self.controlName = "Checkbox"
        self.controlType = self
        self.value = kargs.get("value", None)
        self.checked = kargs.get("checked", None)
        if self.checked is None:
            if self.value is not None:
                self.checked = self.value in self.values()
            else:
                self.checked = False
        self.disabled = kargs.get("disabled", None)
        self.includeLabel = False
        
    def getHtml(self):
        js = self.getJavascript()
        common = self.getCommonAttr()
        onclick = self.getAttr("onclick", js)
        value = self.getAttr("value", self.value)
        if self.checked:
            checked = self.getAttr("checked", "checked")
        else:
            checked = ""
        h = ""
        disabled = ""
        if self.disabled==True:
            disabled=" disabled=\"disabled\""
        h += "<input type=\"checkbox\"%s%s%s%s%s />" % (common, onclick, value, checked, disabled)
        h += self.getLabelHtml()
        return h + "\n"


class radioButton(control):
    def __init__(self, parent=None, label=None, text=None, submit=None, action=None, data=None, title=None,
                  klass=None, id=None, javascript=None, **kargs):
        control.__init__(self, parent, label, text, submit, action, data, title, klass, id, javascript, **kargs)
        self.controlName = "RadioButton"
        self.controlType = self
        self.value = kargs.get("value", None)
        self.checked = kargs.get("checked", None)
        if self.checked is None:
            if self.value is not None:
                self.checked = self.value in self.values()
            else:
                self.checked = False
        self.includeLabel = False
    
    def getHtml(self):
        js = self.getJavascript()
        common = self.getCommonAttr()
        onclick = self.getAttr("onclick", js)
        value = self.getAttr("value", self.value)
        if self.checked:
            checked = self.getAttr("checked", "checked")
        else:
            checked = ""
        h = ""
        h += "<input type=\"radio\"%s%s%s%s />" % (common, onclick, value, checked)
        h += self.getLabelHtml()
        return h + "\n"


class selectList(control):
    def __init__(self, parent=None, label=None, text=None, submit=None, action=None, data=None, title=None,
                  klass=None, id=None, javascript=None, valueTextItems=None, **kargs):
        control.__init__(self, parent, label, text, submit, action, data, title, klass, id, javascript, **kargs)
        self.controlName = "SelectList"
        self.controlType = self
        self.selected = kargs.get("selected", None)
        self.valueTextItems = valueTextItems
        if isinstance(self.valueTextItems, dict):
            self.valueTextItems = self.valueTextItems.items()
        if self.selected is None:
            if self.value() in [v for v, t in self.valueTextItems]:
                self.selected = self.value()
    
    def getHtml(self):
        js = self.getJavascript()
        common = self.getCommonAttr()
        onchange = self.getAttr("onchange", js)
        h = "<select%s%s>" % (common, onchange)
        for value, text in self.valueTextItems:
            if self.selected == value:
                selected = " selected=\"selected\""
            else:
                selected = ""
            value = self.getAttr("value", value)
            text = self.escapeHtml(text)
            h += "<option%s%s>%s</option>\n" % ( value, selected, text )
        h += "</select>\n"
        return h

# __init__(self, parent=None, label=None, text=None, submit=None, action=None, data=None, title=None,
#                  klass=None, id=None, javascript=None, **kargs):

    #Label()
    #Button()
    #Link(href=None)
    #TextInput(text, size=20, rows=1)
    #CheckBox(checked=None)
    #RadioButton(checked=None)
    #SelectList(textValues=[], selected=None, dropdown=True, multiselect=False)
    #FileUpload()
        

