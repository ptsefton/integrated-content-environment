

#from modpywsgi import WSGIServer       # for apache
from paste.request import parse_formvars
from paste.evalexception import EvalException
import time, threading, sys, types
import Cookie

local = threading.local()

sys.path.append("../ice")
from ice_common import IceCommon
IceCommon.setup()
import ice_request

host = "localhost"
#host="139.86.38.58"
port = "8003"
#baseUrl = "http://%s:%s/" % (host, port)
iceRequest = None
requestCount = 0


class AuthMiddleWare(object):
    def __init__(self, wrapApp):
        self.__wrapApp = wrapApp
        self.__authReqired = "401 Authentication Required"
        self.__contentType = ('Content-type', 'text/html')
        self.__wwwAuth = ("WWW-Authenticate", 'Basic realm="Ice"') #Header to send
        #self.__authHeader = "Authorization"    # ("Authorization", "Basic base64Encoded_Username:Password")
        #self.__httpAuth = "HTTP_AUTHORIZATION"
        self.__html = "<html><head><title>Authentication Required</title></head><body>" + \
            "<h1>Authentication Required</h1> If you can't get in, then stay out. </body></html>"
    
    def __call__(self, environ, start_response):
        authHeader = environ.get("HTTP_AUTHORIZATION")
        if not self.authorized(authHeader):
            start_response(self.__authReqired, [self.__contentType, self.__wwwAuth])
            return [self.__html]    #Note: this is displayed only if the user
                                    #       selects the cancel button.
        # auth OK, so just pass every thing through
        environ["USERNAME"] = self.__username
        return self.__wrapApp(environ, start_response)

    def authorized(self, authHeader):
        if authHeader:
            authType, encodedData = authHeader.split(None, 1)  # split in 2 on whitespace
            if authType.lower()=='basic':
                data = encodedData.decode('base64')
                username, password = data.split(':', 1)
                self.__username = username
                return username==password   # Just for testing
        return False



def mainApp(environ, start_response):
    global requestCount
    requestCount += 1
    fields = parse_formvars(environ)
    method = environ["REQUEST_METHOD"]
    path = (environ.get("SCRIPT_NAME", "") + environ.get("PATH_INFO", ""))
    options = environ.get("options", {})
    host = environ["SERVER_NAME"]
    port = environ["SERVER_PORT"]
    #print "host='%s', port='%s'" % (host,port)
    errors = environ["wsgi.errors"]
    args = fields.mixed()
    filenames = {}
    for k, v in args.iteritems():
        if type(v) is types.InstanceType:
            filenames[k] = v
    cookies = environ.get("HTTP_COOKIE", "")
    if cookies.find("=")!=-1:
        cookies = dict([cookie.split("=") for cookie in cookies.split("; ")])
    else:
        cookies = {}
    sessionId = cookies.get("SESSION", None)
    requestData = serverRequestData(path=path, method=method, args=args, \
                    session=None, sessionId=sessionId, filenames=filenames, port=port)
    responseData = serverResponseData()
    
    threadName = threading.currentThread().getName()
    timeStr = time.strftime("%H:%M.%S")
    
    if path.startswith("/testing/"):
        getTestData(fields, environ, requestData, responseData, cookies)
    else:
        global iceRequest
        if iceRequest is None:
            baseUrl = "http://%s:%s/" % (host, port)
            iceRequest = ice_request.iceRequest(baseUrl=baseUrl)
            IceCommon.isServer = True
        gTime.setup()
        gTime.mark("Start request")
        
        iceRequest.processRequest(requestData, responseData)    #, request
        #responseData.contentType = "text/html"
        #responseData.write("TestingTwo")
        
        gTime.stopAll()
        if gTime.isHtmlPage:
            if gTime.enabled:
                print gTime
            else:
                print "Done."
        
    
    contentType = responseData.contentType
    data = responseData.data
    #contentType = "text/html"
    #data = "Testing one"
    start_response("200 OK", [("content-type", contentType), \
                                ("Set-Cookie", "SESSION=%s" % requestData.sessionId)])
    return [data]


def getTestData(fields, environ, requestData, responseData, cookies):
    threadName = threading.currentThread().getName()
    timeStr = time.strftime("%H:%M.%S")
    
    title = "Paste test"
    body = []
    
    body.append("time='%s', path='%s', requestCount=%s" % (timeStr, requestData.path, requestCount))
    body.append(getForm())
    body.append("")
    if False:
        #body.append("fields='%s'" % fields)    # a MultiDict object
        for x in fields.iteritems():
            body.append("key='%s', value='%s'" % x)
            v = x[1]
            if v.__class__.__name__=="FieldStorage":
                body.append("filename='%s'" % v.filename)
                body.append("file='%s'" % str(v.file).replace("<", "&lt;"))
                body.append("name='%s'" % v.name)
                body.append("fileData='%s'" % v.file.read().replace("\n", "<br/>"))
        body.append("fields='%s'" % str(fields))
        body.append("fields.mixed()='%s'" % str(fields.mixed()))
        #body.append("fields.getall()='%s'" % str(fields.getall()))
        body.append("")
        #body.append("dir(fields)='%s'" % str(dir(fields)))
        body.append("HTTP_COOKIE='%s'" % environ.get("HTTP_COOKIE", None))
        #for x in environ.iteritems():
        #    body.append("%s='%s'" % x)
        body.append("filenames='%s'" % str(filenames))
    else:
        body.append("requestData ='%s'" % requestData)
        body.append("requestData.keys()='%s'" % requestData.keys())
        body.append("requestData.uploadFileKeys()='%s'" % requestData.uploadFileKeys())
        filekeys = requestData.uploadFileKeys()
        for fkey in filekeys:
            body.append("requestData.uploadFilename(%s)='%s'" % (fkey, requestData.uploadFilename(fkey)))
            body.append("requestData.uploadFileData(%s)='%s'" % (fkey, requestData.uploadFileData(fkey)))
        body.append("")
        delay = requestData.value("delay")
        if delay!=None and delay!="":
            delay = int(delay)
            time.sleep(delay)
            body.append("slept for %s seconds" % delay)
        body.append("session='%s'" % requestData.session)
        if requestData.value("debug", "")!="":
            if requestCount!=debugCount:
                raise Exception("Debug requestCount='%s', debugCount='%s'" % (requestCount, debugCount))
        #body.append(kdjf)
        body.append("Username='%s'" % environ.get("USERNAME", "?"))
    body.append("")
    #body.append("HTTP_COOKIE='%s'" % environ.get("HTTP_COOKIE", ""))
    body.append("cookies='%s'" % cookies)
    
    htmlFrame = "<html><head><title>%s</title></head><body>%s</body></html>"
    data = htmlFrame % (title, "<br/>".join(body))
    responseData.setResponse(data)
    return data

def getForm():
    form = "<form method='POST' enctype='multipart/form-data'>%s</form>"
    input = "<input type='%s' name='%s' value='%s'/>"
    inputs = []
    inputs.append(input % ("text", "x", "TestingX"))
    inputs.append(input % ("text", "a", "OneX"))
    inputs.append(input % ("text", "a", "TwoX"))
    inputs.append(input % ("file", "upFile", "?"))
    inputs.append(input % ("submit", "sub", "Submit"))
    return form % ("<br/>".join(inputs))
    





class serverRequestData(object):
    #    method       - "GET" or "POST"
    #    path
    #    keys         - returns a list of all keys
    #    has_key(key) - 
    #    remove(key)  - 
    #    value(key)   - return the first value for this key  (None if key is not found)
    #    values(key)  - returns a list of values for the key (An empty list if the key is not found) 
    count = 1
    sessions = {}
    def __init__(self, path="/", method="GET", args={}, session=None, sessionId=None, \
                    filenames={}, port=None):
        if sessionId is None:
            sessionId = "%s-%s" % (int(time.time()*1000), serverRequestData.count)
            serverRequestData.count += 1
        sessions = serverRequestData.sessions
        # Check for expired sessions
        expireTime = 30     # Minutes
        delKeys = []
        for k, s in sessions.iteritems():
            if (s.time + expireTime*60)<time.time():
                delKeys.append(k)
        for k in delKeys:
            del(sessions[k])
        if session is None:
            class Session(object):
                def __init__(self):
                    self.timeCreated = time.time()
                    self.time = self.timeCreated
                    self.requests = 0
                def __str__(self):
                    return "Session: requests=%s, createdTime=%s" % \
                            (self.requests, time.ctime(self.timeCreated))
                            #time.strftime("%H:%M.%S", time.gmtime(self.timeCreated)))
            session = sessions.get(sessionId, None)
            if session is None:
                session = Session()
                sessions[sessionId] = session
            
        session.time = time.time()
        session.requests += 1
        self.__path = path
        self.__method = method
        self.__args = args
        self.__session = session
        self.__sessionId = sessionId
        self.__filenames = filenames
        self.__port = port
    
    @property
    def port(self):
        return self.__port
    
    # to be refactored out
    #@property
    #def args(self):
    #    return self.__args
    
    # to be refactored as private   # USED BY iceSession in ice_request.py
    def getSession(self):
        return self.__session
    session = property(getSession)
    
    @property
    def path(self):
        return self.__path
    
    @property
    def method(self):
        return self.__method
    
    @property
    def sessionId(self):
        return self.__sessionId
    
    
    def has_key(self, key):
        return self.__args.has_key(key)
    
    
    def remove(self, key):
        del self.__args[key]
    
    
    def keys(self):
        return self.__args.keys()
    
    
    def value(self, key, defaultValue=None):
        value = self.__args.get(key, defaultValue)
        if type(value) is types.ListType and len(value)>0:
            return value[0]
        return value
    
    
    def setValue(self, key, value):
        self.__args[key]=[value]
    
    
    def values(self, key):
        r = self.__args.get(key, [])
        if type(r) is types.StringType:
            r = [r]
        return r
    
    
    def has_uploadKey(self, key):
        return self.__filenames.has_key(key)
    
    
    def uploadFileKeys(self):
        return self.__filenames.keys()
    
    
    def uploadFilename(self, key):
        fieldStorage = self.__filenames.get(key, None)
        if fieldStorage is None:
            return None
        return fieldStorage.filename
    
    
    def uploadFileData(self, key):
        fieldStorage = self.__filenames.get(key, None)
        if fieldStorage is None:
            return None
        data = fieldStorage.file.read()
        return data
    
    
    def __str__(self):
        items = []
        for key, value in self.__args.iteritems():
            if key=="password":    # Hide the password
                items.append("'%s': %s" % (key, "'****'"))
            else:
                l = len(str(value)) 
                if l>80:
                    items.append("'%s': ...len(%s)..." % (key, l))
                else:
                    items.append("'%s': %s" % (key, value))
        username = ""
        if hasattr(self.__session, "username"):
            username = self.__session.username
        s = "%s, %s, user=%s, args={%s}" % \
                (self.__method, self.__path, username, ", ".join(items))
        return s


class serverResponseData(object):
    def __init__(self):
        self.__resultData = []
        self.__headers = dict()
    
    def getData(self):
        self.__resultData = ["".join(self.__resultData)]
        return self.__resultData[0]
    def __appendData(self, value):
        self.__resultData.append(value)
    
    @property
    def data(self):
        return self.getData()
    
    def __getContentType(self):
        return self.__headers.get("content-type", "text/html")
    def __setContentType(self, value):
        self.__headers["content-type"] = value
    contentType = property(__getContentType, __setContentType)
    
    
    def write(self, data):
        self.__appendData(data)
    
    
    def setResponse(self, data, mimeType="text/html"):
        self.contentType = mimeType
        self.__appendData(data)
    
    
    def __str__(self):
        s = "[serverResponseData object] len(data)='%s', headers='%s'" 
        s = s % (len(self.__resultData), self.__headers.keys())
        return s


class SafeEvalException(EvalException):
    def __init__(self, app):
        self.__app = app
        
    def __call__(self, environ, start_response):
        host = environ["HTTP_HOST"]
        #host = environ["SERVER_NAME"]
        #port = environ["SERVER_PORT"]
        if host=="localhost:8000":
            return EvalException(self.__app)(environ, start_response)
        return self.__app(environ, start_response)


app = mainApp
#excWrappedApp = SafeEvalException(mainApp)
#app = AuthMiddleWare(excWrappedApp)
#authWrappedApp = AuthMiddleWare


if __name__=="__main__":
    from paste import httpserver
    httpserver.serve(app, host=host, port=port)








