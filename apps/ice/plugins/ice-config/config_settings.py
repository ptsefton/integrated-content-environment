
#    Copyright (C) 2009  Distance and e-Learning Centre, 
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

from config_var import Var


class Settings(object):
    # Constructor:
    #   Settings(ElementTree, defaultSettings=None)
    # Properties:
    #   configEditorPluginName
    #   ooo_port
    #   ooo_host
    #   ooo_python_path
    #   [key]       # Read and Write
    #   delete key
    # Methods:
    #   get(name, default=None)
    #   getList()
    #   keys()
    #   getDescriptionFor(name)
    #   setDescriptionFor(name, description)
    #   set(name, value, description=None)
    #   processSettingsElement(settingsNode)
    #   getSettingsElement()

    def __init__(self, ElementTree, defaultSettings=None):
        self.__et = ElementTree
        self._defaultSettings = defaultSettings
        self.__settings = {}
        self.__descriptions = {}
        self.__var = Var(self.__et)

    @property
    def configEditorPluginName(self):
        return "ice.config2-editor"

    # for old code only
    @property
    def ooo_port(self):
        return self.get("oooPort", "2002")
    @property
    def ooo_host(self):
        return self.get("oooHost", "localhost")
    @property
    def ooo_python_path(self):
        return self.get("oooPythonPath")


    def __getitem__(self, name):
        return self.get(name)
    
    
    def __delitem__(self, name):
        if self.__settings.has_key(name):
            self.__settings.pop(name)
        if self.__descriptions.has_key(name):
            self.__descriptions.pop(name)
    
    
    def __setitem__(self, name, value):
        #print "__setitem__(name='%s', value='%s')" % (name, value)
        self.set(name, value)

    def has_key(self, name):
        return self.__settings.has_key(name)
    
    def get(self, name, default=None):
        if self.__settings.has_key(name):
            return self.__settings.get(name)
        elif self._defaultSettings is not None:
            return self._defaultSettings.get(name, default)
        return default
    
    
    def getList(self):
        l = []
        names = self.keys()
        for name in names:
            isDefaultValue = not self.__settings.has_key(name)
            value = self.get(name, "")
            try:
                desc = self.getDescriptionFor(name)
            except:
                desc = None
            typeof = str(type(value)).split("'")[1]
            l.append( (name, str(value), desc, typeof, isDefaultValue) )
        return l
    
    
    def keys(self):
        if self._defaultSettings is None:
            names = set()
        else:
            names = set(self._defaultSettings.keys())
        names.update(self.__settings.keys())
        l = list(names)
        l.sort()
        return l
    
    
    def getDescriptionFor(self, name):
        desc = self.__descriptions.get(name)
        if desc is None and self._defaultSettings is not None:
            desc = self._defaultSettings.getDescriptionFor(name)
        return desc
    
    
    def setDescriptionFor(self, name, description):
        self.__descriptions[name] = description
    
    
    def set(self, name, value, description=None):
        self.__settings[name] = value
        self.__descriptions[name] = description


    def delete(self, name):
        self.__delitem__(name)


    def processSettingsElement(self, settingsNode):
        if settingsNode is None:
            return
        if settingsNode.tag!="settings":
            raise Exception("not a settings element!")
        varNodes = settingsNode.findall("var")
        for varNode in varNodes:
            name, value, desc = self.__var.processVarElement(varNode)
            self.set(name, value, desc)
    
    
    def getSettingsElement(self):
        settings = self.__et.Element("settings")
        names = self.__settings.keys()
        names.sort()
        for name in names:
            value = self.__settings[name]
            desc = self.__descriptions.get(name)
            v = self.__var.getVarElement(name, value, desc)
            settings.append(v)
        return settings
    
    def __str__(self):
        #l.append( (name, str(value), desc, typeof, isDefaultValue) )
        #return "*settings*"
        formatStr = "  %s=%s(%s) desc='%s' isDefault=%s"
        items = [(formatStr % (n,v,t,d,dv)) for n,v,d,t,dv  in self.getList()]
        return "[Settings]\n" + "\n".join(items)









