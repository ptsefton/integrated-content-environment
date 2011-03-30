
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

pluginName = "ice.config"
pluginDesc = "Configuration and setup"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = None
    pluginClass = IceConfig
    pluginInitialized = True
    IceConfig.PATH = iceContext.fs.split(__file__)[0]
    return pluginFunc


class IceConfig(object):
    PATH = None
    TEMPLATE_FILE = "config.tmpl"
    
    def __init__(self, iceContext, **kwargs):
        self.iceContext = iceContext
    
    
    def processRequest(self, iceContext, requestContext):
        path = requestContext.path
        requestData = requestContext.requestData
        responseData = requestContext.responseData
        
        checkout = requestData.value("checkout", "0")!="0"
        if checkout:
            html = self.__repositoryCheckout(iceContext, requestData)
        else:
            html = "not found"
        
        responseData.setResponse(html)
        return True
    
    
    def __repositoryCheckout(self, iceContext, requestData):
        session = requestData.session
        checkout = requestData.value("checkout", "")
        repId = requestData.value("repId")
        returnPath = requestData.value("returnPath")
        user = requestData.value("user", "")
        password = requestData.value("password")
        #doCheckout = requestData.value("doCheckout")=="1"
        dataDict = {
                    "error":False, 
                    "repId":repId,
                    "checkout":checkout,
                    "user":user,
                    "returnPath":returnPath, 
                    "title":"Repository checkout",
                    }
        reps = iceContext.reps
        rep = reps.getRepository("?%s" % repId)
        ajax = requestData.value("ajax", "")
        if ajax!="":
            #print "AJAX - '%s'" % ajax
            if ajax=="doCheckout":
                data = {}
                data["msg"] = "checkout!"
                rep.logout()
                authRequired = not rep.isAuthenticated
                if authRequired:
                    r = rep.login(user, password)
                    if r==False:
                        data["text"] = "authFailed"
                        return iceContext.jsonWrite(data)
                    session.username = user
                    session.password = password
                    session.workingOffline = False
                    session.loggedIn = True
                # OK - create a worker thread
                #session
                jobId = self.iceContext.guid()
                def worker():
                    job = session.asyncJob
                    job.status.messages = ["checking out..."]
                    oldName = rep.name
                    job.status.rep = rep
                    def messageWriter(msg):
                        iceContext.writeln(msg)
                        job.status.messages.append(msg)
                    rep._setup(messageWriter)
                    if rep.isSetup:
                        job.status.messages.append("Checkout completed OK")
                        reps = self.iceContext.loadRepositories()   # reload repositories
                        #reps.changeRepositoryName(oldName, rep.name)
                        username = session.username
                        password = session.password
                        usingOpenId = session.usingOpenId
                        session.repositoryName = rep.name
                        session.username = username
                        session.password = password
                        session.usingOpenId = usingOpenId
                        session.loggedIn = True
                        session.workingOffline = False
                        try:
                            r = reps.getRepository(rep.name)
                            r.login(username,password)
                        except Exception,e:
                            print "Error in getRepository - '%s'" % str(e)
                    else:
                        job.status.messages.append("Checkout failed!")
                    iceContext.removeAsyncJob(job.id)
                job = iceContext.addAsyncJob(worker, jobId)
                job.status.messages = ["checkout."]
                session.asyncJob = job
            elif ajax=="statusUpdate":
                data = {}
                try:
                    job = session.asyncJob
                    if job is None:
                        data["done"] = True
                    else:
                        msg = "\n".join(job.status.messages)
                        data["msg"] = iceContext.textToHtml(msg)
                        data["msg"] = data["msg"].replace("&apos;", "&#39;") # for IE
                        if job.isFinished:
                            data["done"] = True
                            data["cmd"] = "goto"
                            data["data"] = "/rep.%s/" % job.status.rep.name
                            session.asyncJob = None
                except Exception, e:
                    # rep may be None or ?
                    data["err"] = iceContext.getHtmlFormattedErrorMessage(e)
                    data["err"] = data["err"].replace("&apos;", "&#39;")
                    data["done"] = True
            return iceContext.jsonWrite(data)
        if rep is not None:
            repConfigName = rep.configName
            repUrl = rep.repUrl
            dataDict["repConfigName"] = rep.configName
            dataDict["repUrl"] = rep.repUrl
            dataDict["basePath"] = rep.getAbsPath("/")
            repBasePath = rep.getAbsPath("/")
            authRequired = not rep.isAuthenticated
            dataDict["authRequired"] = authRequired
            if rep.isSetup:
                # ? is already setup
                dataDict["error"] = "Repository is already setup? (unexpected!)"
            else:
                if iceContext.fs.exists(repBasePath):
                    msg = "The repository path '%s' already exists! Can not checkout." % repBasePath
                    dataDict["error"] = msg
                else:
                    x = "configName='%s', isSetup=%s, isAuthenticated=%s" 
                    x = x % (repConfigName, rep.isSetup, rep.isAuthenticated)
                    #print x
                    #print repBasePath, iceContext.fs.exists(repBasePath)
        else:
            dataDict["error"] = "Can not get repository info for '%s'" % repId
        
        templateFile = self.iceContext.urlJoin(self.PATH, self.TEMPLATE_FILE)
        htmlTemplate = iceContext.HtmlTemplate(templateFile, allowMissing=True)
        html = htmlTemplate.transform(dataDict)
        return html
    






