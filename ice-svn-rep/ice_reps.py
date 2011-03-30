#
#    Copyright (C) 2006  Distance and e-Learning Centre, 
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

import types


class IceRepositories(object):
    # Constructor:
    #   __init__(iceRender, defaultRepositoryName=None, \
    #                repositoryInfos=None, execSiteDataCallback=None)
    # Properties:
    #   names       # a list of all the repository name's
    #   
    # Methods:
    #   getRepository(repName=None)     # returns the IceRepository with the given name
    #   
    def __init__(self, iceContext, execSiteDataCallback=None):
        self.iceContext = iceContext

        self.IceRepository = self.iceContext.IceRepository
        
        self.__defaultConfigName = self.iceContext.config.defaultRepositoryName
        self.__defaultRepositoryName = None
        self.__repositoryInfos = self.iceContext.config.repositories
        self.__reps = {}
        self.__fs = self.iceContext.fs
        self.__output = iceContext.output
        count = 0
        for i in self.__repositoryInfos:
            # need to load reps to get the names...
            try:
                if type(i) is types.StringType:           # old config
                    info = self.__repositoryInfos[i]
                    name = i
                    rep = self.__getRepository(name)
                else:                                       # new config2
                    info = i
                    name = i.name
                    rep = self.__getRepository2(info)
                if rep is not None:
                    rName = rep.name
                    if rName=="?":
                        count += 1
                        rName = "?%s" % count
                        rep.setName(rName)
                    if self.__reps.has_key(rName):
                        msg = "Warning: The previous repository '%s' ('%s') is being replaced!"
                        msg = msg % (self.__reps[rName].configName, rName)
                        self.iceContext.logger.iceInfo(msg)
                    self.__reps[rName] = rep
                    if rep.configName==self.__defaultConfigName:
                        self.__defaultRepositoryName = rName
                else:
                    print "No repository is available in config"
            except Exception, e:
                print " Error reps.__init__ - '%s'" % str(e)
    
    
    @property
    def names(self):
        return self.__reps.keys()
    
    
    @property
    def defaultName(self):
        return self.__defaultRepositoryName
    

    def __iter__(self):
        for rep in self.__reps.itervalues():
            yield rep


    def getRequestRepositoryContext(self, requestContext):
        repName = self.__getRepName(requestContext)
        requestData = requestContext.requestData
        session = requestContext.session
        session.repositoryName = repName
        
        if requestData.has_key("loginSubmit"):
            responseData = requestContext.responseData
            session.username = requestData.value("username")
            session.password = requestData.value("password")
            responseData.setCookie("username", session.username)
            responseData.setCookie("repName", repName)
        
        rep = self.__reps.get(repName, None)
        if rep is None:
            return None
        
        iceContext = rep.iceContext.clone(deep=False)
        iceContext.requestData = requestContext.requestData
        iceContext.responseData = requestContext.responseData
        iceContext.session = requestContext.session
        iceContext.path = requestContext.path
        iceContext.threadName = requestContext.threadName
        iceContext.repName = repName
        iceContext.urlRoot = "/rep.%s/" % repName
        return iceContext
    
    
    def getRepository(self, name):
        return self.__reps.get(name, None)
    
    
    def changeRepositoryName(self, oldName, newName):
        try:
            rep = self.__reps.pop(oldName)
            self.__reps[newName] = rep
        except:
            pass
    
    
    def __getRepository2(self, repInfo):
        repIceContext = self.iceContext.clone(deep=True, settings=repInfo.settings)        # create a new context for each repository
        #
        repIceContext.RelativeLinker = repIceContext.getPlugin("ice.relativeLinker").pluginClass
        repIceContext.relativeLinker = repIceContext.RelativeLinker(repIceContext, repIceContext.siteBaseUrl)
        repIceContext.getRelativeLink = repIceContext.relativeLinker.getRelativeLink
        #
        repIceContext.iceRender = repIceContext.IceRender(repIceContext)
        
        try:
            repPath = self.__fs.absPath(repInfo.path)
            repUrl = repInfo.url
            exportPath = repInfo.exportPath
            documentTemplatesPath = repInfo.documentTemplatesPath
            name = repInfo.name
            # Load Repository
            try:
                rep = self.IceRepository(repIceContext, basePath=repPath, 
                                        repUrl=repUrl, name=name, 
                                        iceRender=repIceContext.iceRender)
                if self.iceContext.isServer and False:    ## Turn on proxy access
                    proxyRep = self.iceContext.IceProxyRepository(rep)
                    repIceContext.rep = proxyRep
                else:
                    repIceContext.rep = rep
                repIceContext.loadSitePlugins()
                repIceContext.logger.iceInfo("Loaded Repository '%s' ('%s'), repPath='%s'" % \
                                    (name, rep.name, rep.getAbsPath("/")))
            except Exception, e:
                ##
                print
                print "---"
                print self.IceRepository
                print str(e)
                print self.iceContext.formattedTraceback()
                print "===="
                ##
                repIceContext.writeln("Exception e='%s'" % str(e))
                rep = None
                raise e
            
            if rep.isAuthRequired and self.__output is not None:
                self.__output.write("  Authentication required first!\n")
            rep.exportPath = exportPath
            rep.documentTemplatesPath = documentTemplatesPath
        except Exception, e:
            msg = str(e)
            if msg.startswith("Not a valid"):
                raise self.iceContext.IceException("Repository '%s' has an invalid SVN repository URL set in the configuration file." % name)
            elif msg.find(" repository path is not valid")>-1:
                if self.__fs.exists(repPath):
                    raise self.iceContext.IceException("The repository path '%s' already exists and is not a local repository path!" % repPath)
                else:
                    raise self.iceContext.IceException("The repository path '%s' is invalid!" % repPath)
            else:
                raise self.iceContext.IceException("Error load repository '%s':\n\t %s" % (name, msg))
            rep = None
        return rep
    
    
    def __getRepository(self, name):
        ##
        #print 
        #print "__getRepository(name='%s')" % name
        # Note: iceContext is currently not used - but can be updated or for updating etc.
        if name=='':
            return None
        rep = None
        info = self.__repositoryInfos.get(name, None)
        if info is None:
            return None
        repIceContext = self.iceContext.clone(deep=True)        # create a new context for each repository
        #
        repIceContext.RelativeLinker = repIceContext.getPlugin("ice.relativeLinker").pluginClass
        repIceContext.relativeLinker = repIceContext.RelativeLinker(repIceContext, repIceContext.siteBaseUrl)
        repIceContext.getRelativeLink = repIceContext.relativeLinker.getRelativeLink
        #
        repIceContext.iceRender = repIceContext.IceRender(repIceContext)
        try:
            repPath = self.__fs.absPath(info[0])
            repUrl = info[1]
            exportPath = info[2]
            documentTemplatesPath = info[3]
            # Load Repository
            try:
                rep = self.IceRepository(repIceContext, basePath=repPath, 
                                        repUrl=repUrl, name=name, 
                                        iceRender=repIceContext.iceRender)
                if self.iceContext.isServer and False:    ## Turn on proxy access
                    proxyRep = self.iceContext.IceProxyRepository(rep)
                    repIceContext.rep = proxyRep
                else:
                    repIceContext.rep = rep
                repIceContext.loadSitePlugins()
                repIceContext.logger.iceInfo("Loaded Repository '%s' ('%s'), repPath='%s'" % \
                                    (name, rep.name, rep.getAbsPath("/")))
            except Exception, e:
                ##
                print
                print "---"
                print self.IceRepository
                print str(e)
                print self.iceContext.formattedTraceback()
                print "===="
                ##
                repIceContext.writeln("Exception e='%s'" % str(e))
                rep = None
                raise e
            
            if rep.isAuthRequired and self.__output is not None:
                self.__output.write("  Authentication required first!\n")
            rep.exportPath = exportPath
            rep.documentTemplatesPath = documentTemplatesPath
        except Exception, e:
            msg = str(e)
            if msg.startswith("Not a valid"):
                raise self.iceContext.IceException("Repository '%s' has an invalid SVN repository URL set in the configuration file." % name)
            elif msg.find(" repository path is not valid")>-1:
                if self.__fs.exists(repPath):
                    raise self.iceContext.IceException("The repository path '%s' already exists and is not a local repository path!" % repPath)
                else:
                    raise self.iceContext.IceException("The repository path '%s' is invalid!" % repPath)
            else:
                raise self.iceContext.IceException("Error load repository '%s':\n\t %s" % (name, msg))
            rep = None
        return rep
    
    
    def __getRepName(self, requestContext):
        """ return repName
            or may raise an RedirectException
        """
        # check path for repository name
        repName = None
        path = requestContext.path
        if path.startswith("/rep."):
            parts = path[1:].split("/", 1)
            repName = parts[0][len("rep."):]
            if len(parts)<2:
                # Redirect to the root
                raise self.iceContext.RedirectException(redirectUrl="/rep.%s/" % repName)
            path = "/" + parts[1]
            requestContext.path = path
            
            # now check that the repository name is known
            #   otherwise redirect to the default repository name
            if self.__reps.has_key(repName):
                # OK   (return repName)
                pass
            else:
                repName = requestContext.session.repositoryName
                if repName is None or repName=="":
                    repName = self.__defaultRepositoryName
                if repName is None or repName=="":
                    raise self.iceContext.RedirectException(redirectUrl="/edit-config")
                #check if rep is still exist
                try:
                    rep = self.__getRepository(requestContext)
                except:
                    rep = None
                if rep is not None: 
                    print "redirect to /rep.%s/" % repName
                    raise self.iceContext.RedirectException(redirectUrl="/rep.%s/" % repName)
                else:
                    if self.__defaultRepositoryName != requestContext.session.repositoryName and self.__defaultRepositoryName is not None:
                        print "redirect to default rep: /rep.%s/" % self.__defaultRepositoryName
                        raise self.iceContext.RedirectException(redirectUrl="/rep.%s/" % self.__defaultRepositoryName)
                    else: 
                        raise self.iceContext.RedirectException(redirectUrl="/edit-config")
        else:
            repName = requestContext.session.repositoryName
            if repName is not None and repName!="":
                ## HACK: for now - do not redirect for /skin/ files
                if path.find("/.skin/")!=-1 or path.find("/skin/")!=-1:
                    return repName
                ##
                # redirect to the session's repName
                queryString = requestContext.requestData.queryString
                if queryString:
                    queryString = "?" + queryString
                if not path.startswith("/"):
                    path = "/" + path
                redirectUrl = "/rep.%s%s%s" % (repName, path, queryString)
            else:
                if self.__defaultRepositoryName is None or self.__defaultRepositoryName=="":
                    raise self.iceContext.RedirectException(redirectUrl="/edit-config")
                redirectUrl = "/rep.%s/" % self.__defaultRepositoryName
                if self.__defaultRepositoryName.startswith("?"):
                    repId = self.__defaultRepositoryName.split("?", 1)[-1]
                    redirectUrl = "/ice.config/?repId=%s&checkout=1&returnPath=/" % repId
            raise self.iceContext.RedirectException(redirectUrl=redirectUrl)
        return repName
    







