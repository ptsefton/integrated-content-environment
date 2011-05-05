
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

import types

pluginName = "ice.createToolbar"
pluginDesc = ""
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method

TOOLBAR_TEMPLATE_FILE = None


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized, TOOLBAR_TEMPLATE_FILE
    path = iceContext.fs.split(__file__)[0]
    TOOLBAR_TEMPLATE_FILE = iceContext.fs.join(path, "toolbar.tmpl")
    pluginFunc = createToolbar
    pluginClass = None
    pluginInitialized = True
    return pluginFunc



def createToolbar(iceContext, item, iceSite):
    # Toolbar
    enableTags = iceContext.settings.get("enableTags", False)
    iceSite["app-css"] = "/skin/app.css"
    iceSite["path"] = iceSite.uri
    path = iceSite.uri
    # Hack: fixup argPath
    iceSite["argPath"] = iceContext.escapeXmlAttribute(iceSite["argPath"])
    if path.endswith("/"):
        path = path[:-1]
    session = iceSite.session
    packagePath = iceSite.packagePath
    isInPackage = iceSite.isInPackage
    fileManager = iceSite.fileManager
    
    # TEMPLATE
    htmlTemplate = iceContext.HtmlTemplate(templateFile=TOOLBAR_TEMPLATE_FILE, allowMissing=True)
    urlPath = iceContext.urlJoin(iceContext.urlRoot, item.relDirectoryPath[1:])
    itemPath = iceContext.urlJoin(iceContext.urlRoot, item.relPath[1:])
    uri = iceContext.urlJoin(iceContext.urlRoot, item.uri[1:])
    itemIdPath = ""
    if item.isFile:
        itemIdPath = urlPath + item.getIdUrl()
    # setup dataDict
    
    refreshPath = iceContext.urlQuote(uri)
    if iceContext.urlRoot == uri:
        refreshPath = "." 
    
    dataDict = {"htmlStr":iceContext.HtmlStr, 
        "context":iceSite, 
        "isServer":iceContext.isServer, 
        "itemPath":iceContext.urlQuote(itemPath),
        "itemIdPath":iceContext.urlQuote(itemIdPath),
        "uri": iceContext.urlQuote(uri),
        "refreshPath": refreshPath,
        "path":urlPath,
        "enableTags":enableTags,
        }
    #"path":urlPath,
    dataDict["directory"] = iceContext.escapeXmlAttribute(item.relDirectoryPath)
    
    if packagePath is None:
        packagePath = ""
    actionPath = packagePath
    if actionPath.startswith("/"):
        actionPath = actionPath[1:]  
    if not actionPath.endswith("/") and actionPath!="":
        actionPath = actionPath + "/"
    actionPath = iceContext.urlJoin(iceContext.urlRoot, actionPath)
    dataDict["actionPath"] = actionPath
       
    groups = iceContext.iceFunctions.groups
    #for g in groups.itervalues():
    #    print g.keys()
    
    def getToolbarGroup(toolbarGroupName, names=None):
        groupName = "toolbar_%s" % toolbarGroupName
        if names is None:
            values = groups.get(groupName, {}).values()
        elif type(names)==types.ListType:
            values = []
            for name in names:
                item = groups.get(groupName, {}).get(name)
                if item is not None:
                    values.append(item)
        else:
            name = str(names)
            values = groups.get(groupName, {}).get(name)
        return values
    dataDict["getToolbarGroup"] = getToolbarGroup
    if fileManager is not None:
        dataDict["Add"] = {"addTemplates":fileManager.getAddTemplates()}
        dataDict["enablePaste"] = fileManager.enablePaste
        dataDict["odtTemplates"], dataDict["currentTemplate"] = fileManager.getOdtTemplates()
    else:
        #print "*** fileManager is None"
        addTemplates = iceContext.FileManager.GetAddTemplates(iceContext, 
                                            iceContext.rep, iceContext.fs)
        dataDict["Add"] = {"addTemplates":addTemplates}
        dataDict["enablePaste"] = False
        dataDict["odtTemplates"], dataDict["currentTemplate"] = [], ""
    username = session.username
    #iceContext.system.username
    #print "session -> .username='%s', .workingOffline='%s', .loggedIn='%s'" % (session.username, session.workingOffline, session.loggedIn)
    dataDict["username"] = username
    #
    dataDict["workingOffline"] = session.workingOffline
    dataDict["loggedIn"] = session.loggedIn
    if session.loggedIn:
        dataDict["loginDisable"] = ""
    else:
        dataDict["loginDisable"] = "disabled='disabled'"
    dataDict["isPackage"] = isInPackage
    toolbarGroupNames = [i for i in groups.keys() if i.startswith("toolbar_")]
    dataDict["toolbarGroupNames"] = [i[8:] for i in toolbarGroupNames]
    for groupName in toolbarGroupNames:
        for func in groups.get(groupName, {}).values():
            func._update(iceSite)
    
    # Working status
    dataDict["workingStatus"] = ""
    dataDict["workingStatusUpdate"] = ""
    job = session.asyncJob
    if job is not None and job.isFinished==False:
        dataDict["workingStatusUpdate"] = "update"
        dataDict["workingStatus"] = "Status: " + job.status.message

    rep = iceContext.rep
    if rep._svnRep is None and rep.isAuthRequired==False:
        dataDict["loginLogout"] = False
    else:
        dataDict["loginLogout"] = True
    
    # -- Apply TEMPLATE --
    html = htmlTemplate.transform(dataDict)
    iceSite["appStyleCss"] = htmlTemplate.includeStyle + iceSite["appStyleCss"]
    if htmlTemplate.missing!=[]:
        print "----"
        print "Missing items from template='%s'" % str(htmlTemplate.missing)
        print "----"
    iceSite["toolbar"] = html








