
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

pluginName = "ice.function.changeRepository"
pluginDesc = ""
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = changeRepository
    pluginClass = None
    pluginInitialized = True
    return pluginFunc


# Change Repository Toolbar
def __selectRepositoryToolbar(self):
    names = self.iceContext.reps.names
    if len(names)<2:
        return ""
    selected = "selected='selected'"
    s = "\n<form style='display:inline;' action='' method='POST' name='changeRep'>"
    s += "<input type='hidden' name='func' value='changeRepository'/>\n"
    s += "<input type='hidden' name='argPath' value='%(argPath)s'/>\n"
    s += "<span class='toolbar-label'>Rep:</span>"
    js = "document.forms.changeRep.action=document.forms.changeRep.repName.value"
    s += "<select name='repName' onchange='%s; document.forms.changeRep.submit();'>\n" % js
    default = "Default"
    current = self.rep.configName
    r = ""
    try:
        reps = {}
        for name in names:
            rep = self.iceContext.reps.getRepository(name)
            reps[rep.configName] = rep
        configNames = reps.keys()
        configNames.sort()
        for configName in configNames:
            rep = reps[configName]
            rName = rep.name
            r = ""
            if configName==current:
                r = selected
            if configName!=rName:
                if rName.startswith("?"):
                    rName = "not checked out"
                label = "%s (%s)" % (configName, rName)
            else:
                label = configName
            if rep.name.startswith("?"):
                value = "/ice.config/?repId=%s&checkout=1&returnPath=%s"
                value = self.iceContext.xmlEscape(value)
                value = value % (rep.name[1:], self.iceContext.requestData.path)
            else:
                value = "/rep.%s/" % rep.name
            s += "<option value='%s' %s>%s</option>\n" % (value, r, label)
    except:
        pass
    s += "</select>\n"
    s += "</form>\n"
    return s 


# Change repository
def changeRepository(self):
    path = self.formData.value("argPath")
    if path is None:
        path = ""
    if path.startswith("/"):
        path = path[1:]
    while (path!="") and (not self.rep.getItem(path).exists):
        path = self.fs.split(path)[0]
    if path!="":
        redirectUrl = self.fs.join(self.iceContext.urlRoot, path)
        self.iceContext.responseData.setRedirectLocation(redirectUrl)
changeRepository.options={"toolBarGroup":"common", "position":56, "postRequired":True,
                        "label":"changeRepository", "title":"changeRepository",
                        "toolbarHtml":__selectRepositoryToolbar}











