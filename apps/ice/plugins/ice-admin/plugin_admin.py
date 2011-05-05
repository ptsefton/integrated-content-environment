
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

pluginName = "ice.admin"
pluginDesc = "admin"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = None
    pluginClass = IceAdmin
    pluginInitialized = True
    return pluginFunc


class IceAdmin(object):
    TEMPLATE_FILE = "admin.tmpl"
    def __init__(self, iceContext):
        self.iceContext = iceContext
        self.__myPath = iceContext.fs.split(__file__)[0]
        self.TEMPLATE_FILE = iceContext.fs.join(self.__myPath, self.TEMPLATE_FILE)
    
    def processRequest(self, iceContext, requestContext):
        sessions = requestContext.requestData.__class__.sessions
        path = requestContext.path
        requestData = requestContext.requestData
        responseData = requestContext.responseData
        id = requestData.value("id")
        session = sessions.get(id, None)
        logLines = []
        if session is not None:
            logLines = session.logWriter.lines
            logFor = str(session)
        elif id=="worker":
            logLines = iceContext.workerThreadLogWriter.lines
            logFor = "Worker"
        else:
            logLines = iceContext.defaultLogWriter.lines
            logFor = "Global"
        
        ajax = requestData.value("ajax");
        if ajax is not None:
            if ajax=="test":
                #
                responseData.setResponse("OK")
                return True
            elif ajax=="reloadPlugins":     # per repoistory !!! This needs to be fixed
                iceContext.reloadPlugins()
                responseData.setResponse("OK Done.")
                return True
            #print "admin ajax request"
            #html = "Ajax testing"
            html = "</div>\n<div>".join([iceContext.textToHtml(str(l)) for l in logLines]);
            html = "<div>" + html + "</div>"
            responseData.setResponse(html)
            return True
        
        htmlTemplate = iceContext.HtmlTemplate(templateFile=self.TEMPLATE_FILE, allowMissing=True)
        sessions = sessions.values()
        def sessionSort(s1, s2):
            r = cmp(s1.username, s2.username)
            if r==0:
                r = cmp(s1.lastRequestTime, s2.lastRequestTime)
            return r
        sessions.sort(sessionSort)
        dataDict = {"logFor":logFor,
                    "id":id,
                    "session":session,
                    "sessions":sessions,
                    "logLines":[iceContext.textToHtml(str(l)) for l in logLines],
                    }
        html = htmlTemplate.transform(dataDict)
        responseData.setResponse(html)
        return True











