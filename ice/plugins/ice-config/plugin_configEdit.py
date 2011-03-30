
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

""" """
#from svn_rep import SvnRep #, ListItem, ItemStatus

pluginName = "ice.config-editor"
pluginDesc = "config editor"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    EditConfigXml.HtmlTemplate = iceContext.HtmlTemplate
    EditConfigXml.SvnRep = iceContext.IceRepository.SvnRep
    path = iceContext.fs.split(__file__)[0]
    EditConfigXml.myPath = path
    pluginFunc = None
    pluginClass = EditConfigXml
    pluginInitialized = True
    return pluginFunc


class EditConfigXml(object):
    myPath = ""                     # injected data
    editConfigTemplateFilename = "edit-config-template.tmpl"
    HtmlTemplate = None             # injected data
    SvnRep = None                   # injected data
    
    
    def __init__(self, iceContext):
        # fileSystem usage: split(), exists(), join()
        # system usage: getOsHomeDirectory(), isWindows
        # config usage: oooPath, settings, loadConfigValues()
        #       config.oooPath.isOooPathOK
        #       config.oooPath.getBestOooPath
        #       config.oooPath.getOooPythonPath
        #       config.settings.configFile
        self.iceContext = iceContext
        fileSystem = self.iceContext.fileSystem
        system = self.iceContext.system
        xmlParser = self.iceContext.xmlUtils.xml
        versionInfoSummaryHtml = self.iceContext.textToHtml(self.iceContext.versionInfoSummary)
        self.__fs = fileSystem
        self.__system = system
        self.__xmlParser = xmlParser
        self.__versionInfoSummaryHtml = versionInfoSummaryHtml
        self.__configFile = None
        self.__homePath = system.getOsHomeDirectory()
        self.__newRepId = None
        self.__newRepKey = None
        
        self.__settings = self.iceContext.settings
        oooUtils = iceContext.getPlugin("ice.ooo.utils").pluginClass(iceContext)
        # Default values
        self.isOooPathOK = oooUtils.isOooPathOK
        self.getBestOooPath = oooUtils.getBestOooPath
        self.getOooPythonPath = oooUtils.getOooPythonPath
        
        self.loadConfigValues = self.__settings.loadConfigValues
    
    
    def edit(self, requestData, configFile=None):
        if configFile is None:
            self.__configFile = self.__settings.configFile
        else:
            self.__configFile = configFile
        html = self.__edit(requestData)
        self.__settings = self.loadConfigValues(configFile)
        return html
    
    
    def __edit(self, requestData):
        try:
            self.__settings = self.loadConfigValues(self.__configFile)
            
            #d = self.__settings.__dict__
            d = dict(self.__settings)
            repositories = self.__settings.repositories
            d["repositories"] = repositories
            d["vars"] = self.__settings.vars
            
            d["oooPath"] = self.__settings.get("oooPath")       # property is not in the dictionary
            if self.__system.isWindows:
                d["defaultExportPath"] = "c:/ICE/exports"
            
            self.__resetFeedback(d)
            home = self.__homePath
            home = home.encode("UTF-8")
            d["homePath"] = home
            authNotRequired = False
            d["authRequired"] = False
            d["messageType"] = ""
            d["message"] = ""
            d["addVarMsg"] = ""
            
            valid = False
            if requestData.has_key("ispostback"):
                # get postback data
                d["repositories"] = {}      # only use posted data
                valid = self.__getPostbackData(requestData, d)
                repositories = d["repositories"]
                self.__settings.repositories = repositories
                self.__settings["defaultRepositoryName"] = d["defaultRepositoryName"]
            else:
                url = requestData.value("url", "")
                d["svnUrl"] = url
                if url!="":
                    requestData.setValue("addSvnUrl", "True")
                    authNotRequired = True
                d["msg"] = requestData.value("msg", "")
            
            # add this to the config template
            # added to d versionInfo
            d["versionInfo"] = self.__versionInfoSummaryHtml
            
            # Check to see if the given oooPath is a valid one or not
            result = self.__checkOooPath(d["oooPath"])
            d["oooPathFeedback"] =  result
            if result!="OK":    # if oooPath is not OK then not valid
                oooPath = self.getBestOooPath()
                if oooPath is None:
                    valid = False
                else:
                    d["oooPath"] = oooPath
                    d["oooPathFeedback"] = self.__checkOooPath(d["oooPath"])
            elif d["oooPath"]=="":
                d["oooPathFeedback"] =  result + " (not required)"
            
            # Additional settings
            keys = [key[5:] for key in requestData.keys() if key.startswith("_del_")]
            for key in keys:
                del self.__settings[key]
                self.__settings.save(reCreate=True)
            
            if requestData.has_key("addVar"):
                newVarName = requestData.value("newVarName", "")
                newVarType = requestData.value("newVarType", "")
                newVarDesc = requestData.value("newVarDesc", "")
                if newVarName != "":
                    if newVarType=="string":
                        value = ""
                    elif newVarType=="boolean":
                        value = False
                    self.__settings[newVarName] = value
                    self.__settings.vars[newVarName].desc = newVarDesc
                    self.__settings.save(reCreate=True)
                else:
                    d["addVarMsg"] = "Missing name for new setting"
            
            # Repositories
            savedData = dict(repositories)
            # Add a new repository via a SVN URL
            nameExists = False
            svnUrl = d["svnUrl"]
            if requestData.has_key("addSvnUrl") or requestData.has_key("authSubmit") or svnUrl!="":
                while True:
                    ok = False
                    svn = self.SvnRep(self.iceContext, svnUrl=svnUrl)
                    if not svn.isSvnUrlValid():
                        d["svnUrlFeedback"] = "The given URL is not a valid SVN URL or can not be accessed!"
                    else:
                        if svn.isAuthenticated() or authNotRequired:
                            # all OK
                            ok = True
                        else:
                            # needs a username and password
                            username = d["username"]
                            password = d["password"]
                            password = self.__getCachedPassword(requestData, username, password)
                            
                            if svn.login(username, password):
                                ok = True
                                self.__setCachedPassword(requestData, username, password)
                            else:
                                d["authRequired"] = True
                            if requestData.has_key("authSubmit") and ok==False:
                                d["usernamePasswordFeedback"] = "Authentication failed (wrong username or password)!"
                    if ok:
                        #if ".site/" not in svn.urlList(".") and authNotRequired==False:
                        #    d["svnUrlFeedback"] = "Warning: This does not look like a ICE repository (no .site found!)"
                        if requestData.has_key("addSvnUrl") or requestData.has_key("authSubmit"):
                            name = self.__fs.split(svnUrl.strip("/"))[1]
                            name, path = self.__getDefaultNamePath(name, repositories.keys())
                            templatePath = d["defaultDocumentTemplatesPath"]
                            exportPath = d["defaultExportPath"]
                            if svnUrl == requestData.value("url", None):
                                templatePath = requestData.value("template-path", templatePath)
                                exportPath = requestData.value("export-path", exportPath)
                                n = requestData.value("name")
                                if n is not None:
                                    # does this named repository already exists?
                                    if n in repositories.keys():
                                        # name already exists
                                        d["msg"] = "Name '%s' already exists!" % n
                                        nameExists = True
                                        break
                                    name, path = self.__getDefaultNamePath(n, repositories.keys())
                                path = requestData.value("path", path)
                                if self.__fs.exists(path):
                                    d["msg"] = "Path '%s' already exists!" % path
                            if path.startswith("~"):
                                path = d["homePath"] + path[1:]
                            repositories[name] = [path, svnUrl, exportPath, templatePath, name]
                            self.__newRepKey = name
                            d["svnUrl"] = ""
                    break
            
            # Add a blank repository section
            if requestData.has_key("add") or \
                        (repositories.keys() == []):
                repositories[""] = \
                    ["", "", d["defaultExportPath"], \
                        d["defaultDocumentTemplatesPath"], ""]
            
            class Rep(object):
                def __init__(self, id, name, url, path, docTemplatePath, exportPath, new):
                    self.id = id
                    self.name = name
                    self.url = url
                    self.path = path
                    self.docTemplatePath = docTemplatePath
                    self.exportPath = exportPath
                    self.feedback = ""
                    self.messageType = ""
                    self.message = ""
                    self.new = new
            reps = []
            newRep = None
            count = 1
            keys = repositories.keys()
            keys.sort()
            for key in keys:
                (path, url, exportPath, templatePath, key) = repositories[key]
                new = (self.__newRepKey == key) or (key == "")
                rep = Rep(count, key, url, path, templatePath, exportPath, new)
                if new:
                    newRep = rep
                count += 1
                if new:
                    reps.insert(0, rep)
                else:
                    reps.append(rep)
            #    print "name='%s'" % key
            d["reps"] = reps
            if d["defaultRepositoryName"]=="":
                d["defaultRepositoryName"] = keys[0]
            
            # Test for Saving
            if requestData.has_key("save"):
                valid = True
                requestData.setValue("OK", "quick-save")
            
            if requestData.has_key("OK"):
                if valid:
                    value = requestData.value("OK").lower()
                    self.__deletedVars = []
                    ##
                    print "--- '%s'" % d["defaultRepositoryName"]
                    print "--setting save--"
                    ##
                    self.__settings.save(reCreate=True)
                    d["messageType"] = "ok"
                    d["message"] = "Saved OK"
                    print
                    print "Saved config.xml"
                    print "Restarting ICE "
                    print
                    self.iceContext._setup()
                    redirPath = None
                    if value.find("close")!=-1:
                        if newRep is None:
                            redirPath = "/"
                        else:
                            redirPath = "/rep.%s" % newRep.name
                    elif value == "quick-save":
                        name = requestData.value("name")
                        if name is not None:
                            redirPath = "/rep.%s" % name
                    if redirPath is not None:
                        raise self.iceContext.RedirectException(redirPath)
                else:
                    # Not valid
                    d["messageType"] = "error"
                    d["message"] = "NOT SAVED! Validation failed!"
            
            # TEMPLATE
            file = self.__fs.join(self.myPath, self.editConfigTemplateFilename)
            htmlTemplate = self.HtmlTemplate(templateFile=file)
            allowMissing = True
            html = htmlTemplate.transform(d, allowMissing=allowMissing)
            if htmlTemplate.missing!=[]:
                print "----"
                print "Missing items for template='%s'" % str(htmlTemplate.missing)
                print "----"
        except self.iceContext.RedirectException, e:
            raise e
        except Exception, e:
            msg =  "Error:" + str(e)
            print msg
            return msg
        
        try:
            html = html % d
        except Exception, e:
            msg = "Unhandle error in config_edit.edit() " + \
                "(key not found in the dictionay): %s" % str(e)
            print msg
        return html
    
    
    def __resetFeedback(self, d):
        d["webPortFeedback"]=""
        d["oooPathFeedback"]=""
        d["oooPortFeedback"]=""
        d["emailFromAddressFeedback"]=""
        d["emailSmtpServerFeedback"]=""
        d["emailUsernameFeedback"]=""
        d["documentTemplatesPathFeedback"] = ""
        d["svnUrl"] = ""
        d["username"] = ""
        d["password"] = ""
        d["usernamePasswordFeedback"] = ""
        d["svnUrlFeedback"] = ""
        d["msg"] = ""
    
    
    def __getPostbackData(self, requestData, d):
        valid = True
        try:
            defaultIndex = int(requestData.value("default"))
        except:
            defaultIndex = 0
        d["iceWebPort"] = requestData.value("iceWebPort").strip()
        d["oooPath"] = requestData.value("oooPath").strip()
        d["oooPort"] = requestData.value("oooPort").strip()
        d["emailFromAddress"] = requestData.value("emailFromAddress").strip()
        d["emailSmtpServer"] = requestData.value("emailSmtpServer").strip()
        d["emailUsername"] = requestData.value("emailUsername").strip()
        d["svnUrl"] = requestData.value("svnUrl").strip()
        d["username"] = requestData.value("username", "").strip()
        d["password"] = requestData.value("password", "").strip()
        #
        if d["iceWebPort"].isdigit()==False or int(d["iceWebPort"])>65000:
            valid = False
            d["webPortFeedback"]="Invalid port number"
        #
        if d["oooPort"].isdigit()==False or int(d["oooPort"])>65000:
            valid = False
            d["oooPortFeedback"]="Invalid port number"
            
        count = 1
        defaultRepName = ""
        while requestData.has_key("_" + str(count)):
            oName = requestData.value("_" + str(count), "")
            name = requestData.value("n_" + str(count), "").strip()
            path = requestData.value("p_" + str(count), "").strip()
            url = requestData.value("u_" + str(count), "").strip()
            exportPath = requestData.value("x_" + str(count), "").strip()
            documentTemplatePath = requestData.value("d_" + str(count), "").strip()
            documentTemplatePath = documentTemplatePath.strip("/").strip("\\")
            
            if count==defaultIndex:
                defaultRepName = name
            if name=="" or name!=oName:
                # if name has been changed or deleted
                try:
                    del d["repositories"][oName]
                except:
                    pass
                if name=="":    # if deleted
                    pass
                else:           # else renamed
                    # if name has been changed then recreate
                    d["repositories"][name] = [path, url, exportPath, documentTemplatePath, name]
            else:
                # else update values
                d["repositories"][name] = [path, url, exportPath, documentTemplatePath, name]
            count += 1
        d["defaultRepositoryName"] = defaultRepName
        
        # extra settings
        for var in self.__settings.vars.values():
            name = var.name
            hasKey = requestData.has_key(name)
            if var.type == "boolean":
                self.__settings[name] = hasKey
            elif hasKey:
                value = requestData.value(name)
                self.__settings[name] = value
        
        return valid
    
    
    def __checkOooPath(self, oooPath):
        # Check to see if the given oooPath is a valid one or not
        if self.isOooPathOK(oooPath):
            result = "OK"
        else:
            oooPythonPath = self.getOooPythonPath(oooPath)
            result = "'%s' not found!" % oooPythonPath
        return result
        
    
    
    def __getDefaultNamePath(self, name, currentRepositoryNames):
        path = self.__fs.join(self.__system.getOsHomeDirectory(), "ICE")
        spath = self.__fs.join("~", "ICE")
        if self.__system.isWindows:
            path = "c:/ICE"
            spath = path
        try:
            postfix = ""
            count = 1
            while name+postfix in currentRepositoryNames or \
                    self.__fs.exists(self.__fs.join(path, name+postfix)):
                count += 1
                postfix = str(count)
            return name+postfix, self.__fs.join(spath, name+postfix)
        except Exception, e:
            print "Error: " + str(e)
            return "", ""
    
    
    cache = {}
    def __setCachedPassword(self, requestData, username, password):
        id = requestData.sessionId
        self.cache[id] = (username, password)


    def __getCachedPassword(self, requestData, username, password):
        if password!="":
            return password
        id = requestData.sessionId
        un, pw = self.cache.get(id, (None, ""))
        if un==username:
            return pw
        return ""


