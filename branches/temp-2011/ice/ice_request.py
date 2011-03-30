#!/usr/bin/python
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

""" Module to handle the serving of an IceSite. """

from ice_ajax_request import processAjaxRequest
from ice_api_request import processApiRequest
from ice_binary_request import processBinaryRequest
from ice_content_request import processContentRequest, execSiteData


#  Note: Change config screen to a config/setup screen that does any
#           setup, creating and checking out of repositories
#           e.g. more this away for ice_rep etc.


class IceRequest(object):
    """ IceRequest class. """
    # Constructor:
    #   __init__(iceContext)
    # Properties:
    #   
    # Methods:
    #   processRequest(requestContext)   # return True if processed OK
    #   
    # NOTES:
    #   processRequest(requestContext)
    #       check Authorization, Authentication, logging in and out, editConfig etc.
    #       
    #       
    
    def __init__(self, iceContext):
        self.iceContext = iceContext
        
        self.iceContext.logger.iceInfo("Init IceRequest (handler)")
        self.__iceSpecialFiles = {"/ice.js":(None, None), 
                                    "/jquery.js":(None, None),
                                    "/favicon.ico":(None, None)}
        fs = self.iceContext.FileSystem()
        if fs.isDirectory("fake.skin"):
            d = {}
            skin = "skin/"
            def walkerFunc(path, dirs, files):
                if ".svn" in dirs:
                    dirs.remove(".svn")
                dir = path[path.find("/")+1:]
                for file in files:
                    d[skin + dir + file] = fs.readFile(path + file)
            fs.walker("fake.skin", walkerFunc)
            fs.updateFakeFiles(d)
        self.__fs = fs
    
    
    # render ICE HTTP Request
    def processRequest(self, requestContext):
        requestData = requestContext.requestData
        responseData = requestContext.responseData
        session = requestData.session
        path = requestContext.path          # == requestData.unquotedPath    
        method = requestData.method
        #

        try:
            # Hack for jmol
            if path.find("/META-INF/")!=-1 or \
                path.find("/org/openscience/jmol/")!=-1 or \
                path.find("/geogebra/")!=-1:
                #print "** jmol/geo hack '%s' 404 Not found" % path
                responseData.notFound = True
                return self.iceContext
            requestData.isAjax = requestData.value("ajax")!=None
            requestData.isApi = path.startswith("/api/")
            
            # Test for ice special files and just serve them. e.g. jquery.js & ice.js
            if self.__iceSpecialFiles.has_key(path):
                self.__serveIceSpecialFile(requestContext)
                return self.iceContext
            
            # Test for any REAL root access
            if (self.iceContext.isServer and (path=="/" or path=="")) or \
                    (path=="/options") or (path=="/list"):
                names = self.iceContext.reps.names
                if len(names)>1:
                    html = "<html><head><title>Select repository</title>  <link rel='stylesheet' href='/skin/default.css' /></head><body>%s</body></html>"
                    body = "<h1>ICE Server</h1><h2>Select an ICE repository</h2><ul style='color: navy; list-style-type: square'>%s</ul>"
                    items = []
                    names.sort()
                    for name in names:
                        rep = self.iceContext.reps.getRepository(name)
                        msg = ""
                        if name.startswith("?"):
                            href = "/ice.config/?repId=%s&checkout=1&returnPath=/"
                            href = href % (name[1:])
                            msg = "(not yet checked out) "
                        else:
                            href = "/rep.%s/" % name
                        item = "<a href='%s'>%s</a> %s" % (href, rep.configName, msg)
                        if self.iceContext.reps.defaultName==name:
                            item = "<b>%s</b>" % item
                            items.insert(0, "<li>%s</li>" % item)
                        else:
                            items.append("<li>%s</li>" % item)
                    body = body % "\n".join(items)
                    html = html % body
                    responseData.write(html)
                    return self.iceContext
            
            ##
            # Test for edit-config
            func = requestData.value("func")
            if func is not None:
                func = func.lower().replace("-", "").replace("_", "")
            if (path.endswith("/edit-config") or func=="editconfig"):
                if not self.iceContext.isServer:
                    try:
                        self.__editConfig(requestContext)
                    except self.iceContext.RedirectException, e:
                        responseData.setRedirectLocation(e.redirectUrl)
                    return self.iceContext
            #
            
            # Test for API/Atom Feed
            if requestData.isApi:
                processApiRequest(self.iceContext, requestContext)
                return self.iceContext
            
            #
            # Test for ice.admin or ice.config etc
            if path.startswith("/ice."):
                if path.startswith("/ice.admin/"):
                    adminPlugin = self.iceContext.getPlugin("ice.admin")
                    if adminPlugin is not None:
                        admin = adminPlugin.pluginClass(self.iceContext)
                        admin.processRequest(self.iceContext, requestContext)
                        return self.iceContext
                elif path.startswith("/ice.config/"):
                    configPlugin = self.iceContext.getPlugin("ice.config")
                    if configPlugin is not None:
                        config = configPlugin.pluginClass(self.iceContext)
                        config.processRequest(self.iceContext, requestContext)
                        return self.iceContext
            ####  Get the correct repository  ####
            try:
                rIceContext = self.iceContext.reps.getRequestRepositoryContext(requestContext)
            except self.iceContext.RedirectException, e:
                if requestData.isAjax:
                    iceContext = self.iceContext.clone()
                    iceContext.requestData = requestContext.requestData
                    iceContext.responseData = requestContext.responseData
                    iceContext.session = None
                    iceContext.item = None
                    processAjaxRequest(iceContext)
                    return iceContext
                if path.startswith("/skin/"):
                    data = self.__fs.readFile(path.strip("/"))
                    if data is not None: # do not redirect for skin data if it can be found
                        ext = self.iceContext.fs.splitExt(path)[1]
                        mimeType = self.iceContext.getMimeTypeForExt(ext)
                        responseData.setResponse(data, mimeType)
                        return self.iceContext
                responseData.setRedirectLocation(e.redirectUrl)
                return self.iceContext
            if rIceContext is None:
                if requestContext.isServer:
                    raise Exception("Failed to rIceContext!")
                else:
                    self.__editConfig(requestContext)
                return self.iceContext
            path = rIceContext.path
            rep = rIceContext.rep
            requestData.isApi = path.startswith("/api/")        # test again (after rep.name processed)
            
            ##
            #print "isServer='%s' %s" % (rIceContext.isServer, rIceContext.settings.get("server"))
            ##

            item = rep.getItemForUri(path)
            rIceContext.item = item
            
            # Test for API/Atom Feed
            if requestData.isApi:
                processApiRequest(rIceContext, requestContext)
                return self.iceContext
            
            # No authentication or authorization required
            if path.startswith("/skin/"):
                processBinaryRequest(rIceContext)
                return rIceContext

            loginPage = rIceContext.getPlugin("ice.loginPage").pluginClass(rIceContext)
            
            if rIceContext.isServer:
                auth = rIceContext.getPlugin("ice.auth.server").pluginClass(rIceContext)
            else:
                auth = rIceContext.getPlugin("ice.auth.local").pluginClass(rIceContext)
            if requestData.has_key("logout"):
                auth.logout(rIceContext)
            if auth.checkForLogin(rIceContext):
                username = requestData.getHeader("username")
                password = requestData.getHeader("password")
                if password is not None:
                    #print "username='%s', password='%s'" % (username, password)
                    r, userMsg = auth.login(rIceContext, username, password)
                    if r==False:
                        password = None
                if password is None:
                    r = loginPage.login(rIceContext, auth.login)
                    if r==True:
                        if requestData.value("login")=="oidResult":     # login=oidResult
                            print "OpenID authenticated OK\n"
                            responseData.setRedirectLocation(requestData.path)
                            return rIceContext
                    else:
                        if r is None:       # OpenID redirect
                            pass
                        else:
                            html = responseData.addNoCacheMeta(r, rIceContext.ElementTree)
                            responseData.setNoCacheHeaders()
                            responseData.setResponse(r)
                        return rIceContext
            if auth.hasReadAccess(session, path)==False:
                msg = "forbidden access (path='%s')" % path
                print msg
                responseData.write(msg)
                responseData.forbidden = True
                return rIceContext
            
            #### Authentication required ####
            if requestData.isAjax:
                processAjaxRequest(rIceContext)
                return rIceContext

            self.__processRequest(rIceContext)
            return rIceContext
        except self.iceContext.IceException, ie:
            msg = str(ie)
            msg = self.iceContext.textToHtml(msg)
            html = "<div style='color:red;padding:1em;'>ICE Exception: '%s'</div>" % msg
            html += "<div style='padding:1em;'>Try changing the configuration file. <a href='edit-config'>Edit-config</a></div>"
            html = "<div>%s</div>" % html
            responseData.setResponse(html)
            self.iceContext.logger.flush()
            return self.iceContext
        except Exception, e:
            self.iceContext.logger.exception("Unhandled exception in iceRequest.processRequest()")
            errMsg = str(e)
            errTrace = self.iceContext.formattedTraceback(lines=3)
            html = """<div style='color:red;padding:1em;'>
                    ERROR: Unhandled exception in iceRequest.processRequest() - %s</div>
                    <br/><hr/>Stack trace<hr/>%s<br/>
                    """ % (self.iceContext.textToHtml(str(e)), self.iceContext.textToHtml(str(errTrace)))
            responseData.setResponse(html)
            self.iceContext.logger.flush()
            return self.iceContext
    
    
    # ================
    # Private Methods
    # ================
    
    
    def __iceServerRequest(self, iceContext):
        pass
    
    
    def __iceLocalRequest(self, iceContext):
        pass
    
    
    def __serveIceSpecialFile(self, requestContext):
        #self.__iceSpecialFiles = {"/ice.js":(None, None), 
        #                            "/jquery.js":(None, None),
        #                            "/jquery-ui.js":(None, None),
        #                            "/favicon.ico":(None, None)}
        path = requestContext.path
        responseData = requestContext.responseData
        data, mimeType = self.__iceSpecialFiles.get(path, (None, None))
        if data is None:
            ext = self.iceContext.fs.splitExt(path)[1]
            mimeType = self.iceContext.getMimeTypeForExt(ext)
            filePath = path.lstrip("/")
            if filePath.startswith("jquery"):
                data = self.iceContext.fs.readFile(filePath)
                # only cache jquery.js at this stage
                self.__iceSpecialFiles[path] = (data, mimeType)
            else:
                data = self.iceContext.fs.readFile(filePath)
        if path.startswith("/jquery") and requestContext.requestData.acceptGzip:
            data = self.iceContext.gzip(data)
            responseData.setHeader("Content-Encoding", "gzip") #"gzip")
        responseData.setResponse(data, mimeType)
        return True
    
    
    # process a non ajax request
    def __processRequest(self, rIceContext):
        #iceContext.writeln("ice_request.__processRequest()")
        #gTime.mark("ice_request.processRequest()")
        
        rep = rIceContext.rep
        path = rIceContext.path
        item = rIceContext.item
        
        # Is this a ICE content request or an ICE binary request?
        if item.isBinaryContent:
            # OK is binary content
            if item.needsUpdating:
                print "Updating requested '%s' binary contents first. Please wait." % item.uri
                item.render(skipBooks=False)
            return processBinaryRequest(rIceContext)
        
        return processContentRequest(rIceContext)
    
    
    def __testForEditConfig(self, requestContext):
        # if using default settings (or the current rep is not valid)
        #    or the path endswith /edit-config then
        #    edit the config (return True)
        try:
            path = requestContext.path
            ext = self.iceContext.fs.splitExt(path)[1]
            func = requestContext.requestData.value("func", "")
            func = func.lower().replace("-", "").replace("_", "")
            if path.endswith("/edit-config") or func=="editconfig":
                return self.__editConfig(requestContext)
            #
            return False
        except Exception, e:
            self.iceContext.writeln(self.iceContext.formattedTraceback())
            msg = "Exception in ice_request.__testForEditConfig(): Error - '%s'\n" % str(e)
            if self.iceContext.output is not None:
                self.iceContext.output.write(msg)
            self.iceContext.responseData.setResponse(self.iceContext.textToHtml(msg))
            return True
    
    
    def __editConfig(self, requestContext, msg=""):
        requestData = requestContext.requestData
        requestData.setValue("msg", msg)
        configEditorPluginName = self.iceContext.settings.configEditorPluginName
        #print "ice_request.__editConfig() configEditorPluginName='%s'" % configEditorPluginName
        EditConfigXml = self.iceContext.getPlugin(configEditorPluginName).pluginClass
        if EditConfigXml is None:
            html = "<div style='color:red;'>Error: Can not load or find config-editor plugin!<br/><a href='.'>back</a></div>"
            requestContext.responseData.setResponse(html)
            return True
        editConfigXml = EditConfigXml(self.iceContext)
        html = editConfigXml.edit(requestData)
        requestContext.responseData.setResponse(html)
        # restart may be required (a reloading of self.iceContext.reps)
        # Re-load all repositories
        #iceContext.reps = self.IceRepositories(iceContext, \
        #                                    iceRender=iceContext.iceRender, \
        #                                    execSiteDataCallback=execSiteData)
        return True
    
    
    
    
    #if path.endswith(".png") or path.endswith(".gif") or path.endswith(".css"):
    #    secs = 60
    #    responseData.setHeader('Cache-Control', 'must-revalidate, proxy-revalidate, max-age=%s, s-maxage=%s' % (secs, secs))
    #    #responseData.setHeader('Expires', 'Thu, 04 Dec 2008 01:24:52 +0000')
    #    #responseData.setHeader('ETag', '"47abaf64"')
    #    #responseData.setHeader('Last-Modified', 'Fri, 08 Feb 2008 01:24:52 +0000')
    #    pass
    
    
