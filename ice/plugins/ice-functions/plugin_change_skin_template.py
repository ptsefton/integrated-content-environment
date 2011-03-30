
#    Copyright (C) 2008  Distance and e-Learning Centre, 
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

""" """

pluginName = "ice.function.changeSkinTemplate"
pluginDesc = ""
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method



def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = changeTemplate
    pluginClass = None
    pluginInitialized = True
    return pluginFunc



# Change Template Toolbar
def __selectTemplateToolbar(self):
    selected = "selected='selected'"
    s = "\n<form style='display:inline;' method='POST'>\n"
    s += "<input type='hidden' name='func' value='changeTemplate'/>\n"
    s += "<input type='hidden' name='argPath' value='%(argPath)s'/>\n"
    s += "&#160;Template:"
    s += "<select name='template' onchange='submit()' title='Change Template'>\n"
    default = self.defaultXhtmlTemplateFilename
    current = self.session.get("xhtmlTemplateFilename", default)
    r = ""
    if default==current:
        r = selected
    s += "<option value='%s' %s>Default</option>" % (default, r)
    try:
        files = self.rep.getSkinTemplates(["/", self.packagePath])
        for file in files:
            value = "templates/" + file + ".xhtml"
            r = ""
            if value==current:
                r = selected
            name = self.iceContext.fs.splitExt(file)[0]
            s += "<option value='%s' %s>%s</option>\n" % (value, r, name)
    except:
        pass
    s += "</select>\n"
    s += "</form>\n"
    return s 


# Change template
def changeTemplate(self):
    self['statusbar'] = "changeTemplate"
    if self.formData.has_key("template") and self.formData.value("template")!='':
        data = self.formData.value("template")
        #self.setXhtmlTemplate(data)
        self.session["xhtmlTemplateFilename"] = data
        self['statusbar'] = "Changed template to %s." % data
#@IceFunction2.toolbar(toolBarGroup="publish", position=54, postRequired=True,
#                label="changeTemplate", title="changeTemplate",
#                toolbarHtml=__selectTemplateToolbar)
changeTemplate.options={"toolBarGroup":"publish", "position":36, "postRequired":True,
                    "label":"changeTemplate", "title":"changeTemplate",
                    "toolbarHtml":__selectTemplateToolbar}







