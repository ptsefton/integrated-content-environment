
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

from openid.store.memstore import MemoryStore
from openid.consumer.consumer import Consumer


pluginName = "ice.openid"
pluginDesc = ""
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    path = iceContext.fs.split(__file__)[0]
    pluginFunc = None
    pluginClass = OpenId
    pluginInitialized = True
    return pluginFunc


class OpenId(object):
    def __init__(self, iceContext):
        self.iceContext = iceContext
    
    def getRedirectUrlFor(self, session, openUrlId, returnUrl, realm):
        store = MemoryStore()
        session["openId_store"] = store
        consumer = Consumer(session, store)
        try:
            authRequest = consumer.begin(openUrlId)
            shouldSendRedirect = authRequest.shouldSendRedirect()
            ##print "should send redirect=%s" % shouldSendRedirect
            ##  see example code for not redirecting???  .../examples/consumer.py
            #if shouldSendRedirect==False:
            #    html = authRequest.htmlMarkup(realm, returnUrl, \
            #                            form_tag_attrs={"id":"openid_message"})
            redirectUrl = authRequest.redirectURL(realm=realm, \
                            return_to=returnUrl, immediate=False)
        except Exception, e:
            return None
        return redirectUrl
    
    def complete(self, requestData):
        session = requestData.session
        store = session.get("openId_store")
        if store is None:
            return False, {"status":"", "message":"Lost session store, try again!"}
        session["openId_store"] = None
        consumer = Consumer(session, store)
        queryDict = requestData.args
        realm = requestData.urlPath
        response = consumer.complete(queryDict, realm)
        
        result = False
        d = {}
        if response is None:
            d["status"] = None
            d["message"] = "Received no response!"
            return result, d
        displayId = response.getDisplayIdentifier()
        d["displayId"] = displayId
        d["status"] = response.status
        if hasattr(response, "message"):
            d["message"] = response.message
        else:
            d["message"] = ""
        if response.status=="success":
            canonicalId = response.endpoint.canonicalID
            if canonicalId is None:
                canonicalId = displayId
            d["canonicalId"] = canonicalId
            d["id"] = canonicalId
            d["message"] = "OK"
            result = True
        elif response.status=="failure":
            # Verification failed
            d["message"] = "Failed verification: %s" % response.message
        elif response.status=="cancel":
            d["message"] = "Cancelled"
        elif response.status=="setup_needed":
            d["message"] = "Setup needed: %s" % response.message
        else:
            d["message"] = "Failed"
        return result, d
    
    
    def test(self, requestContext, iceContext=None):
        if iceContext is None:
            iceContext = self.iceContext
        requestData = requestContext.requestData
        responseData = requestContext.responseData
        
        #
        openUrlId = requestData.value("openUrlId", "")
        completeOpenId = requestData.value("completeOpenId", "")!=""
        print "openUrlId='%s', completedOpenId='%s'" % (openUrlId, completeOpenId)
        html = "<html><head><title>%s</title></head><body>%s</body></html>"
        title = "OpenId Testing"
        form = """<form action='' method='GET'>
            <input type='hidden' name='test' value='testing'/>
            <input type='text' name='openUrlId' value='%s'/><br/>
            <input type='submit' name='login' value='login'/>
        </form>""" % openUrlId
        body = "<div><h3>OpenId Testing</h3>%s</div>" % form
        if completeOpenId:      # result from openid server
            r, d = self.complete(requestData, requestData.session)
            ##if d["message"] == "OK" and r==True then login OK
            print
            print "r='%s', d='%s'" % (r, d)
            data = "<div>Done %s - %s</div>" % (d["status"], d["message"])
            data += "<div>%s</div>" % iceContext.textToHtml(str(d))
            body += data
        elif openUrlId != "":
            # Redirect  to the openid server
            returnUrl = requestData.urlPath + "?completeOpenId=1&userUriId=%s" % openUrlId
            realm = requestData.urlPath
            redirectUrl = self.getRedirectUrlFor(requestData.session, \
                            openUrlId, returnUrl, realm)
            responseData.setRedirectLocation(redirectUrl)
            return
        else:
            pass
        html = html % (title, body)
        responseData.setResponse(html, "text/html")
        return






