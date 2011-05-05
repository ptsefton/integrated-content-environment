
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

from config_settings import Settings        # for defaultSettings
from config_rep import IceRepConfig


pluginName = "ice.config2"
pluginDesc = ""
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = None
    pluginClass = IceConfig
    pluginInitialized = True
    return pluginFunc



class IceConfig(object):
    # Constructor:
    #   IceConfig(iceContext, **kwargs)
    #                   iceContext.ElementTree  # plug more if converting from old format
    # Properties:
    #   settings
    #   defaultRepositoryName
    #   port
    #   hostAddress
    #   repositories
    # Methods:
    #   setDefaultRepositoryName(name)
    #   serialize()
    #   process(xmlStr)
    #   save()
    #   
    #   createNewRepository(name, url, path, documentTemplatesPath, exportPath) -> rep
    #   addRepository(rep)
    #   deleteRepository(name)
    #   getRepNames()
    #   getRep(name)
    def __init__(self, iceContext, **kwargs):
        self.iceContext = iceContext
        self.__et = iceContext.ElementTree
        self.__host = "localhost"
        self.__port = "8000"
        self.__settings = Settings(self.__et)
        self.__repositories = {}
        self.__saveMethod = kwargs.get("saveMethod", None)
        self.__homePath = "";
        try:
            self.__homePath = self.iceContext.system.getOsHomeDirectory()
        except: pass
    
    
    @property
    def hostAddress(self):
        return self.__host
    
    
    @property
    def port(self):
        return self.__port
    
    
    @property
    def settings(self):
        return self.__settings
    
    
    @property
    def defaultRepositoryName(self):
        return self.__settings.get("defaultRepositoryName", "")


    @property
    def repositories(self):
        reps = self.__repositories.values()
        reps.sort()
        # reps[0].name(& repName), reps[0].settings
        return reps
    
    
    def setDefaultRepositoryName(self, name):
        self.__settings.set("defaultRepositoryName", name)
    
    
    def setPort(self, port):
        self.__port = port


    def setHostAddress(self, host):
        self.__host = host


    def getRepNames(self):
        names = self.__repositories.keys()
        names.sort()
        return names
    
    
    def getRep(self, name):
        return self.__repositories.get(name)
    
    
    def createNewRepository(self, name, url, path,
                                documentTemplatesPath, exportPath):
        rep = IceRepConfig(self.__et, self.__settings, homePath=self.__homePath)
        rep.url = url
        rep.path = path
        rep.documentTemplatesPath = documentTemplatesPath
        rep.name = name
        rep.exportPath = exportPath
        return rep
    
    
    def addRepository(self, rep):
        self.__repositories[rep.name] = rep
    
    
    def deleteRepository(self, name):
        if self.__repositories.has_key(name):
            self.__repositories.pop(name)
    
    
    def serialize(self):
        et = self.__et
        xml = et.XML("<iceConfig version='2.0'/>")
        host = et.Element("iceWebHost")
        host.text = self.__host
        xml.append(host)
        port = et.Element("iceWebPort")
        port.text = str(self.__port)
        xml.append(port)
        # Settings
        settings = self.__settings.getSettingsElement()
        xml.append(settings)
        # Repositories
        reps = et.Element("repositories")
        if self.defaultRepositoryName is not None:
            reps.set("default", self.defaultRepositoryName)
        repNames = self.__repositories.keys()
        repNames.sort()
        for repName in repNames:
            rep = self.__repositories[repName]
            reps.append(rep.getRepElement())
        #
        xml.append(reps)
        self.__formatXml(xml)
        xmlStr = et.tostring(xml)
        return xmlStr
    
    
    def process(self, xmlStr):
        # xml.find(element
        if xmlStr==None or xmlStr.strip()=="":
            xmlStr = "<iceConfig version='2.0'/>"
        xml = self.__et.XML(xmlStr)
        if xml.tag!="iceConfig":
            raise Exception("Not a valid ICE Config XML file!")
        version = xml.get("version")

        if version is None or version=="1": #### OLD VERSION support
            return self._processVersion1(xmlStr)

        if version=="2" or version=="2.0":
            pass # OK
        else:
            raise Exception("Unsupported version of ICE-Config XML file!")
        # iceWebHost        self.__host         String
        e = xml.find("iceWebHost")
        if e is not None: self.__host = e.text
        # iceWebPort        self.__port         String
        e = xml.find("iceWebPort")
        if e is not None: self.__port = e.text
        # settings
        e = xml.find("settings")
        if e is not None:
            self.__settings.processSettingsElement(e)
        # repositories"
        e = xml.find("repositories")
        if e is not None:
            repNodes = e.findall("repository")
            for repNode in repNodes:
                rep = IceRepConfig(self.__et, self.__settings, homePath=self.__homePath)
                rep.processRepElement(repNode)
                self.__repositories[rep.name] = rep
        #
        if(not self.__settings.has_key("oooHost")):
            self.__settings["oooHost"] = "localhost"
        if(not self.__settings.has_key("oooPath")):
            self.__settings["oooPath"] = ""
        if(not self.__settings.has_key("oooPythonPath")):
            self.__settings["oooPythonPath"] = "python"
        if(not self.__settings.has_key("oooPort")):
            self.__settings["oooPort"] = "2002"
        return version


    def _processVersion1(self, xmlStr):
        #
        # Support for older config version (1.0)
        #
        Config = self.iceContext.getPluginClass("ice.config-xml")
        if Config is None:
            raise Exception("'ice.config-xml' plugin not found and is required!")
        config = Config(self.iceContext)
        settings = config.loadConfigValues(configXmlStr=xmlStr)
        self.__port = settings.get("iceWebPort")
        self.__host = settings.get("host", "localhost")
        self.__settings.set("defaultRepositoryName", settings.defaultRepositoryName)
        self.__settings.set("oooPath", settings.get("oooPath"), "The path to OpenOffice.org")
        self.__settings.set("oooPythonPath", settings.get("oooPythonPath"), "")
        self.__settings.set("oooPort", settings.get("oooPort"), "OOo port")
        self.__settings.set("oooHost", settings.get("oooHost"), "OOo host address")
        self.__settings.set("emailFromAddress", settings.get("emailFromAddress"), "")
        self.__settings.set("emailSmtpServer", settings.get("emailSmtpServer"), "")
        self.__settings.set("emailUsername", settings.get("emailUsername"), "")
        keys = settings.keys()
        if "host" in keys:
            keys.remove("host")
        if "iceWebPort" in keys:
            keys.remove("iceWebPort")
        for key in keys:
            self.__settings.set(key, settings.get(key))
        #"Name" : [path, url, exportPath, documentTemplatesPath, realName]
        for name, value in settings.repositories.iteritems():
            path, url, exportPath, documentTemplatesPath, _ = value
            rep = self.createNewRepository(name, url, path, documentTemplatesPath, exportPath)
            self.addRepository(rep)
        return "1"      # Version 1.0
        # convert from version 1
    
    def save(self, saveMethod=None):
        r = False
        if not callable(saveMethod):
            saveMethod = self.__saveMethod
        if callable(saveMethod):
            xmlStr = self.serialize()
            saveMethod(xmlStr)
            r = True
        return r
    
    
    def setSaveMethod(self, saveMethod):
        self.__saveMethod = saveMethod
    
    
    def __formatXml(self, xml, level=1):
        if xml.tag=="var":
            return
        children = xml.getchildren()
        if children!=[]:
            xml.text = "\n" + "\t" * level
            for child in children:
                child.tail = "\n" + "\t" * level
                self.__formatXml(child, level+1)
            child.tail = "\n" + "\t" * (level-1)











