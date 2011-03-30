
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

pluginName = "ice.config2-editor"
pluginDesc = "Config editor (2)"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = None
    pluginClass = ConfigEditor
    pluginInitialized = True
    path = iceContext.fs.split(__file__)[0]
    ConfigEditor.JavascriptFile = iceContext.fs.join(path,
                                ConfigEditor.EditConfigJavascriptFilename)
    ConfigEditor.TemplateFile = iceContext.fs.join(path, 
                                ConfigEditor.EditConfigTemplateFilename)
    ConfigEditor.RepTemplateFile = iceContext.fs.join(path, 
                                ConfigEditor.EditConfigRepTemplateFilename)
    ConfigEditor.SettingsTemplateFile = iceContext.fs.join(path, 
                                ConfigEditor.EditConfigSettingsTemplateFilename)
    iceContext.ajaxHandlers["config2Edit"] = ajaxCallback
    #print "*** adding config2edit ajax handler ***", iceContext.rep
    return pluginFunc


def ajaxCallback(iceContext):
    #print "config2Edit ajax callback"
    try:
        data = ""
        mimeType = "text/html"
        rdata = iceContext.requestData
        func = rdata.value("func")
        adata = rdata.args
        iceConfig = iceContext.config
        configEditor = ConfigEditor(iceContext)
        if func=="test":
            print "ajax config2Edit test function data='%s'" % str(adata)
            data = {"error":"Just testing"};
        elif func=="restart":
            iceContext._setup()    #"Restarting ICE "
            data = {"ok":"restarted"}
        elif func=="save":
            data = adata.get("data")
            data = iceContext.jsonRead(data)
            configEditor.setData(data, iceConfig)
            def saveMethod(s):
                print "--saved--"
                print s
            #iceConfig.setSaveMethod(saveMethod)
            iceConfig.save()
            print "Saved configuration changes"
            data = configEditor.getDisplayData(iceConfig)

        elif func=="getData":
            data = configEditor.getDisplayData(iceConfig)
        elif func=="getCommonSettings":
            data = configEditor.getCommonSettings()
        else:
            data = {"error":"Unknown func='%s'" % func};
    except Exception, e:
        msg = "Ajax config2Edit callback error - '%s'" % str(e)
        print msg
        data = {"error":msg};
    data = iceContext.jsonWrite(data);
    return data, mimeType


class MyDict(dict):
    def __getattr__(self, name):
        return self.get(name)


class ConfigEditor(object):
    EditConfigJavascriptFilename = "edit-config.js"
    EditConfigTemplateFilename = "edit-config.tmpl"
    EditConfigRepTemplateFilename = "edit-config-rep.tmpl"
    EditConfigSettingsTemplateFilename = "edit-settings.tmpl"
    JavascriptFile = None               # set via pluginInit
    TemplateFile = None                 # set via pluginInit
    RepTemplateFile = None              # set via pluginInit
    SettingsTemplateFile = None         # set via pluginInit
    
    def __init__(self, iceContext, **kwargs):
        self.iceContext = iceContext
        self.__system = iceContext.system
        self.__homePath = self.__system.getOsHomeDirectory()
        self.__javascript = iceContext.fs.readFile(self.JavascriptFile)
    

    def getDisplayData(self, config=None):
        if config is None:
            config = self.iceContext.config
        versionInfoSummaryHtml = self.iceContext.textToHtml(self.iceContext.versionInfoSummary)
        homePath = "?"
        try:
            system = self.iceContext.system
            homePath = system.getOsHomeDirectory();
        except: pass
        # getList()
        #  l.append( (name, str(value), desc, typeof, isDefaultValue) )
        settings = self.__settingsToDict(config.settings)
        settings["defaultRepositoryName"] = settings.get("defaultRepositoryName",
                        {"name":"defaultRepositoryName", "value":"", "type":"str", "desc":""})
        repositories = self.__repsToDict(config.repositories)
        d = {
            "port": config.port,
            "hostAddress": config.hostAddress,
            "settings": settings,                   # {"name":{"value":x, "type":x, }}
            "repositories": repositories,           # {"repName":{"settings":x, ...}}
            "homePath": homePath,
            "versionInfo": versionInfoSummaryHtml
        }
        return d  #.replace(": None", ": ''")


    def setData(self, data, config=None):
        if config is None:
            config = self.iceContext.config
        config.setPort(data.get("port"))
        config.setHostAddress(data.get("hostAddress"))
        self.__updateSettingsFromDict(config.settings, data.get("settings", {}))
        self.__updateRepsFromDict(config, data.get("repositories", {}))
        #
        #self.iceContext._setup()    #"Restarting ICE "

        

    def edit(self, requestData, iceConfig=None):
        fs = self.iceContext.fs
        self.__javascript
        html = fs.read(self.TemplateFile.replace("config.tmpl", "config2.tmpl"))
        html = html.replace("{$javascript$}", self.__javascript)
        return html


    def __settingsToDict(self, settings):
        # getList()
        #  l.append( (name, str(value), desc, typeof, isDefaultValue) )
        d = {}
        for name, value, desc, typeof, isDefaultValue in settings.getList():
            if isDefaultValue:
                continue
            d[name] = {"name":name, "value":value, "desc":desc, "type":typeof}
        return d


    def __repsToDict(self, repositories):
        d = {}
        for rep in repositories:
            d[rep.name] = {
                "name":rep.name,
                "url":rep.url,
                "path":rep.path,
                "documentTemplatesPath":rep.documentTemplatesPath,
                "exportPath":rep.exportPath,
                "settings":self.__settingsToDict(rep.settings)
                }
        return d


    def __updateSettingsFromDict(self, settings, d):
        s1 = set(settings.keys())
        s2 = set(d.keys())
        dels = s1.difference(s2)
        updates = s2.difference(dels)
        for name in dels:
            settings.delete(name)
        for name in updates:
            t = d[name].get("type")
            value = d[name].get("value")
            desc = d[name].get("desc")
            if t=="str":
                value = str(value)
                settings.set(name, value, desc)
            elif t=="bool":
                value = (value.lower()=="true")
                settings.set(name, value, desc)
            elif t=="list":
                pass
            else:
                pass

    def __updateRepsFromDict(self, config, d):
        #   name
        #   url
        #   path
        #   documentTemplatesPath
        #   exportPath
        #   settings
        #config.deleteRepository(name)
        #rep=config.createNewRepository(self, name, url, path,
        #                        documentTemplatesPath, exportPath)
        #config.addRepository(rep)
        reps = {}
        for rep in config.repositories:
            if not d.has_key(rep.name):
                config.deleteRepository(rep.name)
            else:
                reps[rep.name] = rep
        for repName, rdict in d.iteritems():
            if reps.has_key(repName):
                rep = reps[repName]
            else:
                rep=config.createNewRepository(repName, "", "", "", "")
                config.addRepository(rep)
            rep.url = rdict.get("url")
            rep.path = rdict.get("path")
            rep.exportPath = rdict.get("exportPath")
            rep.documentTemplatesPath = rdict.get("documentTemplatesPath", "")
            settings = rdict.get("settings", {})
            self.__updateSettingsFromDict(rep.settings, settings)


    def getCommonSettings(self):
        return self.__addDefaultGlobalSettings({})

    def __addDefaultGlobalSettings(self, settings):
        defaultList = (
            ("defaultExportPath", "~/ICE/export", ""),
            ("defaultDocumentTemplatesPath", "/templates", ""),
            ("asServiceOnly", False, "run as service only"),
            ("server", False, "ICE as Server"),
            ("enableExternalAccess", False, "enable external access"),
            ("displayTiming", False, ""),
            ("convertUrl", "", "Add an ICE-Service as a companion server that converts file types"),
            ("useLocalOpenOffice", True, "Set up ICE to use ICE-Service to render documents instead of using a local installation of OpenOffice"),
            ("enableTags", False, "Enable content tagging"),
            ("forceIceStyles", True, "Enable nonICE styles to be rendered with basic heading styles discovered and turned into HTML headings"),
            ("noVersionControl", False, "Add no version control option if subversion is NOT required"),
            ("enableOpenId", False, "Enable OpenID authentication"),
            ("authentication", "", "Type of authentication e.g. 'LDAP'"),
            ("ramAccessUrl", "", "RAM access URL"),
            ("ramAccessRepId", "", "RAM access repository ID"),
            ("ldapUrl", "", "The URL for the LDAP server"),
            ("ldapOU", "Staff", "LDAP OrganizationalUnit name"),
            ("ldapDC", "dc=usq,dc=edu,dc=au", "LDAP Domain context"),
            ("imageMagickPath", "", "ImageMagick path (for Windows only)"),
            ("exiftoolPath", "", "exiftool path(for Windows only)"),
            #("", False, ""),
            )
        for name, value, desc in defaultList:
            if(not settings.has_key(name)):
                t = "str"
                if type(value) is type(True):
                    t = "bool"
                settings[name] = {"name":name, "value":value, "type":t, "desc":desc}
        return settings













