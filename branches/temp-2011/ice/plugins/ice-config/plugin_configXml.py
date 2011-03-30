#
#    Copyright (C) 2005  Distance and e-Learning Centre, 
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


""" Module to read configuration parameters from config.xml """

import types

pluginName = "ice.config-xml"
pluginDesc = "config"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method



def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = None
    pluginClass = Config
    pluginInitialized = True
    return pluginFunc



class Config(dict):
    # Constructor:
    #   __init__(configFile=None, system=None)
    # Methods:
    #   load()
    #   serialize(reCreate=False)
    #   save(reCreate=False, saveTo=None)
    # Properties:
    #    using_defaults = True
    #    defaultRepositoryName
    #    repositories = {}
    
    settings = None
    TYPE_MAP = {types.StringType: "string", types.BooleanType: "boolean", types.ListType: "list", types.IntType: "integer"}
    
    class Var(object):
        def __init__(self, name, desc, type, value):
            self.name = name
            self.update(desc, type, value)
        def update(self, desc, type, value):
            if desc is None or desc=="":
                self.desc = self.name
            else:
                self.desc = desc
            self.type = type
            self.value = value
    
    
    
    def __init__(self, iceContext, configFile=None):
        self.__system = iceContext.system
        self.__fs = iceContext.fs
        self.__xmlUtils = iceContext.xmlUtils
        if configFile is None:
            configFile = self.getConfigFileLocation()
        oooUtils = iceContext.getPlugin("ice.ooo.utils").pluginClass(iceContext)
        # Default values
        self.isOooPathOK = oooUtils.isOooPathOK
        self.getBestOooPath = oooUtils.getBestOooPath
        self.getOooPythonPath = oooUtils.getOooPythonPath
        
        self.__nonVarList = ["hasOoo3Mac", "iceWebPort", "oooPath", "oooPythonPath",
                            "oooPort", "oooHost", "emailFromAddress", 
                            "emailSmtpServer", "emailUsername", "logLevel",
                            "defaultExportPath", "defaultDocumentTemplatesPath", "defaultRepositoryName"]
        
        self.using_defaults = True
        self["hasOoo3Mac"] = oooUtils.hasOoo3Mac()
        self["iceWebPort"] = "8000"
        self["oooPath"] = ""
        self["oooPythonPath"] = ""
        self["oooPort"] = "2002"
        self["oooHost"] = "localhost"
        self["emailFromAddress"] = ""
        self["emailSmtpServer"] = ""
        self["emailUsername"] = ""
        self["logLevel"] = "22"
        self["defaultRepositoryName"] = ""
        
        self["defaultExportPath"] = "~/ICE/exports"
        self["defaultDocumentTemplatesPath"] = "/templates"
        
        self.configFile = configFile
        
        # repositories = { "Name" : [path, url, exportPath, documentTemplatesPath, realName] }
        self.repositories = {}
        
        self.vars = dict()
        self.__home = self.__system.getOsHomeDirectory()
    
    @property
    def configEditorPluginName(self):
        return "ice.config-editor"


    @property
    def hostAddress(self):
        return self.get("host", "localhost")
    
    
    @property
    def port(self):
        return self.get("iceWebPort", "8000")
    
    
    @property
    def defaultRepositoryName(self):
        return self.get("defaultRepositoryName")
    
    
    def setPort(self, port):
        self["iceWebPort"] = port
    
    
    def loadConfigValues(self, configFile=None, configXmlStr=None):
        ## FIXME the caching of Config.settings somehow loses repositories
        ## when reloading the config, so disable it for now
        #if Config.settings is not None and configFile is None:
        #    return Config.settings
        if configFile is not None:
            self.configFile = configFile
        self.load(configXmlStr)
        Config.settings = self
        return self
    
    
    def get(self, key, default=None):
        return dict.get(self, key, default)
    
    def __getitem__(self, key):    # over
        return self.get(key)
    
    
    def __setitem__(self, key, value):
        if type(key) is not types.StringType:
            raise Exception("Only string keys are allowed")
        if key=="oooPath":
            try:
                self["oooPythonPath"] = self.getOooPythonPath(value)
            except: pass
        # mac oooPath returns None which causes the test to fail
        if not (self.__system.isMac and key in ["oooPath", "oooPythonPath"]):
            self.__testValue(value)
        #
        if key not in self.__nonVarList:
            self.vars[key] = self.Var(key, None, self.TYPE_MAP[type(value)], value)
        dict.__setitem__(self, key, value)
    
    
    def __delitem__(self, key):
        if self.vars.has_key(key):
            del self.vars[key]
        dict.__delitem__(self, key)
    
    
    def getConfigFileLocation(self):
        configFilename = "config.xml"
        #if hasattr(os, "iceTesting") and os.iceTesting==True:
        #    configFilename = "testConfig.xml"
        if self.__fs.isFile(configFilename):
            return self.__fs.absPath(configFilename)
        path = self.__system.getOsConfigPath("ice", create=True)
        fullPath = self.__fs.join(path, configFilename)
        return fullPath
    
    
    def load(self, configXmlStr=None):
        xml = self.__getConfigXml(configXmlStr)
        if xml==None:
            if not self.isOooPathOK(self.get("oooPath")):
                self["oooPath"] = self.getBestOooPath()
            return False
        
        self.using_defaults = False
        rootNode = xml.getRootNode()
        
        # iceWebPort
        x = self.__getValue(rootNode, "iceWebPort", self)
        # oooPath
        self.__getValue(rootNode, "oooPath", self)
        # oooPort
        self.__getValue(rootNode, "oooPort", self)
        # oooHost
        self.__getValue(rootNode, "oooHost", self)
        # emailFromAddress
        self.__getValue(rootNode, "emailFromAddress", self)
        # emailSmtpServer
        self.__getValue(rootNode, "emailSmtpServer", self)
        # emailSsername
        self.__getValue(rootNode, "emailUsername", self)
        # logLevel
        self.__getValue(rootNode, "logLevel", self)
        
        # repositories    
        self.repositories = dict()
        self["defaultRepositoryName"] = ""
        nodes = rootNode.getNodes("//repository")
        for node in nodes:
            name, path, url, exportPath, documentTemplatesPath = self.__getRepositoryData(node)
            if name is None:
                continue
            self.repositories[name] = [path, url, exportPath, documentTemplatesPath, name]
            if self.get("defaultRepositoryName") == "":
                self["defaultRepositoryName"] = name
                
        node = rootNode.getNode("//repositories")
        if node!=None:
            attName = node.getAttribute("default")
            if attName!=None:
                name = attName.strip()
                if self.repositories.has_key(name):
                    self["defaultRepositoryName"] = name
        
        #NOTE: The following line of code does not work when compiled under MAC OSX
        #        use a two step process instead
        #nodes = rootNode.getNodes("//settings/var")  
        settingsNode = rootNode.getNode("//settings")
        if settingsNode is not None:
            nodes = settingsNode.getNodes("var")
            for node in nodes:
                name, value = self.__getVarNameValue(node)
                self[name] = value
                desc = node.getAttribute("desc")
                type = node.getAttribute("type")
                if self.vars.get(name) is None:
                    self.vars[name] = self.Var(name, desc, type, value)
                else:
                    self.vars[name].update(desc, type, value)
        
        xml.close()
        
        if not self.isOooPathOK(self.get("oooPath")):
            self["oooPath"] = self.getBestOooPath()
        self["oooPythonPath"] = self.getOooPythonPath(self.get("oooPath"))
        
        self.__fixupHomeRelativePaths()
        
        return True
    
    
    def __getRepositoryData(self, repNode):
        attName = repNode.getAttribute("name")
        name = "Default"
        if attName!=None:
            name = attName.strip()
        
        attName = repNode.getAttribute("path")
        if attName==None:
            path = None
            name = None
        else:
            path = attName.strip()
        
        url = ""
        attName = repNode.getAttribute("url")
        if attName!=None:
            url = attName.strip().rstrip("/")
        
        exportPath = self.get("defaultExportPath")
        attName = repNode.getAttribute("exportPath")
        if attName!=None:
            exportPath = attName.strip()
        
        documentTemplatesPath = self.get("defaultDocumentTemplatesPath")
        attName = repNode.getAttribute("documentTemplatesPath")
        if attName!=None:
            documentTemplatesPath = attName.strip()
        if not documentTemplatesPath.startswith("/") and \
                not documentTemplatesPath.startswith("\\"):
            documentTemplatesPath = "/" + documentTemplatesPath
        
        return name, path, url, exportPath, documentTemplatesPath
    
    
    def __fixupHomeRelativePaths(self, homePath=None):
        if homePath is None:
            homePath = self.__home
        for rep in self.repositories.values():
            # repPath - 0
            # exportPath -  2
            if rep[0].startswith("~"):
                rep[0] = homePath + rep[0][1:]
            if rep[2].startswith("~"):
                rep[2] = homePath + rep[2][1:]
    
    
    def serialize(self, reCreate=False):
        if reCreate==True:
            self.__fixupHomeRelativePaths()
            xml = self.__xmlUtils.xml("<iceConfig/>")
            xml.addComment(" ice web server port ")
            xml.addElement("iceWebPort").addContent(str(self.get("iceWebPort")))
            
            xml.addComment(" OOo listen port\n  NOTE if you change this value, \n  " + \
                    "you will need to RESTART OOo (and the OOo QuickStart) for this to take effect!\n")
            xml.addElement("oooPort").addContent(str(self.get("oooPort")))
            
            xml.addComment(" The path to where OpenOffice.org is installed ")
            xml.addElement("oooPath").addContent(self.get("oooPath"))
            
            xml.addComment(" Email From Address ")
            xml.addElement("emailFromAddress").addContent(self.get("emailFromAddress"))
            
            xml.addComment(" Email SMTP Server ")
            xml.addElement("emailSmtpServer").addContent(self.get("emailSmtpServer"))
            
            xml.addComment(" Email username ")
            xml.addElement("emailUsername").addContent(self.get("emailUsername"))
            
            xml.addComment(" Repositories names, paths [, urls, exportPath, documentTemplatesPath] ")
            # repositories = { repName, [path, url, exportPath] }
            repNames = self.repositories.keys()
            repNames.sort()
            reps = xml.addElement("repositories")
            if self.get("defaultRepositoryName") in repNames:
                reps.setAttribute("default", self.get("defaultRepositoryName"))
            for repName in repNames:
                path, url, exportPath, documentTemplatesPath = self.repositories[repName][0:4]
                repNode = xml.createElement("repository", name=repName, path=path, url=url, \
                        exportPath=exportPath, documentTemplatesPath=documentTemplatesPath)
                reps.addChild(repNode)
            
            xml.addComment(" Settings ")
            settingsNode = xml.addElement("settings")
            for name, value in dict.iteritems(self):
                var = self.vars.get(name)
                if var is not None:
                    desc = name
                    if var.desc is not None:
                        desc = var.desc
                    node = self.__createVarNode(xml, name, value, desc)
                    settingsNode.addChild(node)
            xmlStr = xml.serialize()
            xml.close()
        else:
            raise Exception("reCreate=False option not supported yet!")
            xml = self.__getConfigXml()
            rootNode = xml.getRootNode()
            # iceWebPort
            node = rootNode.getNode("iceWebPort")
            if node!=None:
                node.setContent(self.get("iceWebPort"))
            # oooPath
            node = rootNode.getNode("oooPath")
            if node!=None:
                node.setContent(self.get("oooPath"))
            # oooPort
            node = rootNode.getNode("oooPort")
            if node!=None:
                node.setContent(self.get("oooPort"))
            # logLevel
            node = rootNode.getNode("logLevel")
            if node!=None:
                node.setContent(self.get("logLevel"))
            
            xmlStr = str(xml)
            xml.close()
        return xmlStr


    def save(self, reCreate=False, saveTo=None):
        if saveTo is None:
            file = self.configFile
        else:
            file = saveTo
        xmlStr = self.serialize(reCreate)
        f = open(file, "wb")
        f.write(xmlStr)
        f.close()
    

    def __getConfigXml(self, configXmlStr=None):
        xml = None
        if configXmlStr is None:
            configFile = self.configFile
            
            #Should change to self.__fs.isFile(config)
            if (not self.__fs.isFile(configFile)) and (not configFile.startswith("<")):
                print "Config xml file '%s' not found!" % configFile
                print "  using default config values!"
                return None
            try:
                xml = self.__xmlUtils.xml(configFile)
                if xml.isHtml:
                    xml.close()
                    xml = None
                    raise Exception("isHtml and not XML")
            except Exception, e:
                #print str(e)
                print "Failed to parse config xml file '%s' - not well-formed XML!" % configFile
                print " using default config values"
                self["oooPath"] = self.getBestOooPath()
                self["oooPythonPath"] = self.getOooPythonPath(self.get("oooPath"))
                return None
        else:
            xml = self.__xmlUtils.xml(configXmlStr)
        return xml
    
    
    def __getValue(self, node, eName, defaultValue):
        if defaultValue==self:
            defaultValue = self[eName]        # get the defaultValue from self using the elementName
        value = defaultValue
        valueType = type(defaultValue)
        content = node.getContent(eName)
        if content is not None:
            content = content.strip()
        if valueType is types.StringType:
            if content is not None:
                value = content
        elif valueType is types.IntType:
            try:
                value = int(content)
            except:
                pass
        elif valueType is types.BooleanType:
            if content is not None:
                tmp = content.upper()
                value = (tmp=="YES" or tmp=="TRUE")
        else:
            raise Exception("type '%s' is not supported!" % str(valueType))
        self[eName] = value
        return value


    def __getVarNameValue(self, node):
        name = node.getAttribute("name")
        value = None
        
        type = node.getAttribute("type")
        if type is None:
            type = "string"
        type = type.lower()
        
        if type=="string" or type=="str":
            value = node.getAttribute("value")
            if value==None:
                value = node.getContent()
        elif type=="int" or type=="integer":
            value = self.__getInteger(node)
        elif type=="bool" or type=="boolean":
            value = self.__getBoolean(node)
        elif type=="array" or type=="list":
            value = self.__getArrayList(node)
        elif type=="dict" or type=="dictionary":
            value = self.__getDictionaryValue(node)
        elif type=="xml":
            xmlNode = node.getNode("*")
            value = str(xmlNode)
        else:
            print "Error: type='%s' is unsupported"
        return name, value

    def __getInteger(self, node):
        value = node.getAttribute("value")
        if value==None:
            value = node.getContent()
        try:
            value = int(value)
        except:
            value = None
        return value
    
    def __getBoolean(self, node):
        value = node.getAttribute("value")
        if value==None:
            value = node.getContent()
        try:
            value = value.strip().lower()
            if value=="0" or value=="false" or value=="":
                value = False
            else:
                value = True
        except:
            value = True
        return value

    def __getArrayList(self, node):
        sep = node.getAttribute("sep")
        data = node.getAttribute("value")
        if data==None:
            data = ""
        value = []
        if sep==None:
            try:
                value = eval("[" + data + "]")
            except:
                pass
        elif data!="":
            value = data.split(sep)
        for n in node.getNodes("*|text()"):
            if n.getType()=="text":
                if sep==None:
                    try:
                        v = eval("[" + n.getContent() + "]")
                        value.extend(v)
                    except:
                        pass
                else:
                    v = n.getContent().split(sep)
                    value.extend(v)
            else:
                tmpName, v = self.__getVarNameValue(n)
                value.append(v)
        return value

    def __getDictionaryValue(self, node):
        data = node.getAttribute("value")
        if data==None:
            data = ""
        value = {}
        try:
            value = eval("{" + data + "}")
        except:
            pass
        atts = node.getAttributes()
        try:
            atts.pop("type")
            atts.pop("name")
        except:
            pass
        value.update(atts)
        for n in node.getNodes("var|text()"):
            if n.getType()=="text":
                try:
                    v = eval("{" + n.getContent() + "}")
                    value.update(v)
                except:
                    pass
            else:
                xName, xValue = self.__getVarNameValue(n)
                value[xName] = xValue
        return value

    def __testValue(self, value):
        valueType = type(value)
        if valueType is types.StringType:
            # OK
            return True
        elif valueType is types.IntType:
            # OK
            return True
        elif valueType is types.BooleanType:
            # OK
            return True
        elif valueType is types.ListType:
            # Then test its items
            for item in value:
                if self.__testValue(item)==False:
                    raise Exception("List item value may be out of context! (is not string, bool, int, list or dict type)")
                    return False
            return True
        elif valueType is types.DictType:
            # Then test its keys and values
            for key, value in value.iteritems():
                if type(key) is not types.StringType:
                    raise Exception("Only string dictionary keys are allowed")
                    return False
                self.__testValue(value)
        else:
            raise Exception("Value may be out of context! ('%s' is not string, bool, int, list or dict type)" % valueType)
            return False
            
    
    def __createVarNode(self, xml, name, value, desc=None):
        valueType = type(value)
        node = xml.createElement("var", name=name)
        if desc is not None:
            node.setAttribute("desc", desc)
        try:
            if valueType is types.StringType:
                node.setAttribute("type", "string")
                node.setAttribute("value", value)
            elif valueType is types.BooleanType:
                node.setAttribute("type", "boolean")
                node.setAttribute("value", str(value))
            elif valueType is types.IntType:
                node.setAttribute("type", "integer")
                node.setAttribute("value", str(value))
            elif valueType is types.ListType:
                node.setAttribute("type", "list")
                s = str(value)[1:-1]
                node.setContent(s)
            elif valueType is types.DictType:
                node.setAttribute("type", "dict")
                s = str(value)[1:-1]
                node.setContent(s)
            else:
                raise Exception("Invalid value type")
        except:
            node.delete()
            node = None
        return node


    def createConfigXml(self, iceWebPort=8000, oooPort="2002", oooPath="", exportPath="/export", \
            defaultRepName="Default", repositories={}, saveAs=None):
        xml = self.__xmlUtils.CreateXml("iceConfig", formatted=True)
        xml.addComment(" ice web server port ")
        xml.addElement("iceWebPort").addContent(str(iceWebPort))

        xml.addComment(" OOo listen port\n  NOTE if you change this value, \n  " + \
                "you will need to RESTART OOo (and the OOo QuickStart) for this to take effect!\n")
        xml.addElement("oooPort").addContent(str(oooPort))

        xml.addComment(" The path to where OpenOffice.org is installed ")
        xml.addElement("oooPath").addContent(oooPath)

        xml.addComment(" Email From Address ")
        xml.addElement("emailFromAddress").addContent("")

        xml.addComment(" Email SMTP Server ")
        xml.addElement("emailSmtpServer").addContent("")
        
        xml.addComment(" Email Username ")
        xml.addElement("emailUsername").addContent("")
        
        xml.addComment(" Export Path ")
        xml.addElement("exportPath").addContent(exportPath)
        
        xml.addComment(" Repositories names, paths [, urls] ")
        # repositories = { repName, [path, url, None] }
        repNames = repositories.keys()
        repNames.sort()
        reps = xml.addElement("repositories")
        if defaultRepName in repNames:
            reps.addAttribute("default", defaultRepName)
        for repName in repNames:
            path, url = repositories[repName][0:2]
            reps.addElement("repository", name=repName, path=path, url=url)
        
        if saveAs!=None:
            xml.saveFile(saveAs)
        
        xmlStr = str(xml)
        xml.close()
        
        return xmlStr
    






