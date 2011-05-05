
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

pluginName = "ice.loginPage"
pluginDesc = "login page"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method

LOGIN_TEMPLATE_FILE = "login.tmpl"


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    path = iceContext.fs.split(__file__)[0]
    LoginPage.TEMPLATE_FILE = iceContext.fs.join(path, LOGIN_TEMPLATE_FILE)
    pluginFunc = None
    pluginClass = LoginPage
    pluginInitialized = True
    return pluginFunc


class LoginPage(object):
    TEMPLATE_FILE = None
    
    def __init__(self, iceContext):
        #htmlTemplate = self.HtmlTemplate(templateFile=self.TEMPLATE_FILE, allowMissing=True)
        #dataDict = {}
        #html = htmlTemplate.transform(dataDict)
        #if htmlTemplate.missing!=[]:
        #    print "----"
        #    print "Missing items from template='%s'" % str(htmlTemplate.missing)
        #    print "----"
        self.iceContext = iceContext
        self.isServer = iceContext.isServer
        self.systemUsername = iceContext.system.username
    

    def login(self, iceContext, authLogin):
        """ returns True if logged in OK, else returns the HTML login page. """
        html = None
        session = iceContext.session
        requestData = iceContext.requestData

        if requestData.value("workOffline"):
            session.workingOffline = True
            return True
        
        username = ""
        openIdUri = ""
        if session.usingOpenId:
            openIdUri = session.username
        else:
            username = session.username
        username = requestData.value("username", username).strip()
        password = requestData.value("password", "").strip()
        openIdUri = requestData.value("openIdUri", openIdUri).strip()
        session.usingOpenId = (openIdUri!="")
        if session.usingOpenId:
            username = ""
            password = ""
            session.username = openIdUri
        else:
            session.username = username
        if requestData.value("login", None) is not None:            
            x = authLogin(iceContext, \
                        username=username, password=password, openIdUri=openIdUri)
            if x is None:       # OpenID redirect
                return None
            (r, msgUsername) = x
            if r:
                session.username = msgUsername
                session.password = password
                session.usingOpenId = (openIdUri!="")
                session.loggedIn = True
                return True
        enableOpenId = self.iceContext.settings.get("enableOpenId", False)
        if enableOpenId:
            html = self.__openIdLogin(iceContext)
        else:
            html = self.__login(iceContext)
        return html
    
    
    def __login(self, iceContext):
        html = None
        try:
            html = iceContext.rep.getItem("/skin/template-login.xhtml").read()
            if html==None:
                raise Exception()
            #print "/skin/template-login.xhtml"
        except:
            try:
                f = open("template-login.xhtml", "rb")
                html = f.read()
                f.close()
            except:
                html = None
        if html==None:
            raise Exception("ERROR: template-login.xhtml not found!")
        
        # for server version disable workOffline elements
        if self.isServer:
            xml = self.iceContext.Xml(html)
            nodes = xml.getNodes("//*[local-name()='input' and @name='workOffline']")
            for node in nodes:
                node.delete()
            html = str(xml)
            xml.close()
        
        return html
    
    
    def __openIdLogin(self, iceContext):
        rep = iceContext.rep
        responseData = iceContext.responseData
        session = iceContext.requestData.session
        html = None
        try:
            html = rep.getItem("/skin/template-ologin.xhtml").read()
            if html==None:
                raise Exception()
            if self.isServer:
                try:
                    et = iceContext.ElementTree
                    xml = et.XML(html)
                    inputs = xml.findall(".//input")
                    offlineButton = [i for i in inputs if i.get("name")=="workOffline"][0]
                    offlineButton.set("type", "hidden")
                    offlineButton.set("name", "_")
                    offlineButton.set("value", "")
                    if session.usingOpenId:
                        openIdUriInput = [i for i in inputs if i.get("name")=="openIdUri"][0]
                        openIdUriInput.set("value", session.username)
                    else:
                        usernameInput = [i for i in inputs if i.get("name")=="username"][0]
                        usernameInput.set("value", session.username)
                    for n in xml.findall(".//*"):
                        if n.text is None:
                            n.text = " "
                    html = et.tostring(xml)
                except Exception, e:
                    print "error - '%s'" % str(e)
        except:
            try:
                loginPlugin = iceContext.getPlugin("ice.login")
                if loginPlugin is None:
                    raise Exception("No login plugin found!")
                html = loginPlugin.pluginFunc(iceContext, self.systemUsername)
            except:
                html = None
        if html==None:
            raise Exception("ERROR: template-login.xhtml not found!")
        return html

    



