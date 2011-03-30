
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

from config_settings import Settings


class IceRepConfig(object):
    # Constructor:
    #   IceRepConfig(ElementTree, defaultSettings)
    # Properties:
    #   settings
    #   url
    #   path
    #   documentTemplatesPath
    #   name
    #   exportPath
    #   repName
    # Methods:
    #   processRepElement(repNode)      -> None
    #   getRepElement()                 -> element
    def __init__(self, ElementTree, defaultSettings, homePath=""):
        self.__et = ElementTree
        self.name = ""
        self.url = ""
        self._path = ""
        self._documentTemplatesPath = "templates"
        self._exportPath = ""
        self.repName = ""
        self._settings = Settings(self.__et, defaultSettings)
        self._homePath = homePath
    
    
    @property
    def settings(self):
        return self._settings


    def __getPath(self):
        return self._path
    def __setPath(self, value):
        if value.startswith("~"):
            value = self._homePath + value[1:]
        self._path = value
    path = property(__getPath, __setPath)


    def __getExportPath(self):
        return self._exportPath
    def __setExportPath(self, value):
        if value.startswith("~"):
            value = self._homePath + value[1:]
        self._exportPath = value
    exportPath = property(__getExportPath, __setExportPath)


    def __getDocumentTemplatesPath(self):
        return self._documentTemplatesPath
    def __setDocumentTemplatesPath(self, value):
        if value.startswith("~"):
            value = self._homePath + value[1:]
        self._documentTemplatesPath = value
        pass
    documentTemplatesPath = property(__getDocumentTemplatesPath, __setDocumentTemplatesPath)
    
    def processRepElement(self, repNode):
        if repNode.tag!="repository":
            raise Exception("not a repository element")
        self.url = repNode.get("url") or ""
        self.path = repNode.get("path") or ""
        self.documentTemplatesPath = repNode.get("documentTemplatesPath") or "templates"
        self.name = repNode.get("name") or ""
        self.exportPath = repNode.get("exportPath") or ""
        e = repNode.find("settings")
        self._settings.processSettingsElement(e)
    
    
    def getRepElement(self):                    #
        et = self.__et
        element = et.Element("repository")
        element.set("url", self.url)                  # @url
        element.set("path", self.path)                # @path
        element.set("documentTemplatesPath", self.documentTemplatesPath) # @documentTemplatesPath
        element.set("name", self.name)                # @name
        element.set("exportPath", self.exportPath)    # @exportPath
        # settings
        settings = self._settings.getSettingsElement()
        element.append(settings)
        return element
    
    
    def __cmp__(self, other):
        return cmp(self.name, other.name)











