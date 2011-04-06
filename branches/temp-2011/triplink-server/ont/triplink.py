

# Server mode:
#           href, [referer] -> referer/subject, predicate, object
# Format html mode:
#           change a elements into rdfa via template & other metadata

from urlparse import urlsplit, parse_qs, urlunsplit
from urllib import urlencode
import types, json
import re, os

class Triple (object):
    def __init__(self, params, urlParts, content="", referer="."):
        self.__params = params
        self.__urlParts = urlParts
        self.__referer = referer
        self.__content = content
        self.__text = re.sub("<.*?>","", content)
       

    @property
    def content(self):
        return self.__content

    @property
    def text(self):
        return self.__text

    @property
    def subject(self):
        return self.getParam("tl_s", self.__referer)
    
    @property
    def predicate(self):
        return self.getParam("tl_p", None)
    
    @property
    def object(self):
        obj = self.getParam("tl_o", None)
        if obj is None:
            params = self.__params.copy()
            if params.has_key("tl_p"):
                params.pop("tl_p")
            if params.has_key("tl_s"):
                params.pop("tl_s")
            params.pop("triplink")
            query = urlencode(params)
            obj = urlunsplit((self.__urlParts.scheme, self.__urlParts.netloc, 
                    self.__urlParts.path, query, self.__urlParts.fragment))
        return obj
    
    @property
    def isValid(self):
        return self.getParam("triplink", "").startswith("http://purl.org/triplink/v/0.1")
    
    def getParam(self, name, default=None):
        p = self.__params.get(name, [])
        if(len(p)>0):
            return p[0]
        return default



class TripLink(object):
    def __init__(self, iceContext=None, defaultTemplatePath=None):
        self.iceContext = iceContext
        self.tripLinkTemplate = None
        
        if defaultTemplatePath is None:
            defaultTemplatePath = os.path.abspath("triplinkTemplate.json")
      
        self.setTemplate(defaultTemplatePath)
    
    def setTemplate(self, defaultTemplatePath):
        if defaultTemplatePath:
            f = None
            try:
                f = open(defaultTemplatePath, "rb")
                self.tripLinkTemplate = json.loads(f.read())
            finally:
                if f is not None:
                    f.close()

  

    def process(self, link, content="", referer="."):
        urlParts = urlsplit(link)
        query = urlParts.query
        params = parse_qs(query)
        triple = Triple (params, urlParts, content=content, referer=referer)
        
        if triple.isValid:
            tempData = self.tripLinkTemplate.get(triple.predicate, \
                        self.tripLinkTemplate.get("default", {}))
            if tempData:
                tempData = dict(tempData)       # create a working copy
                for key, value in tempData.iteritems():
                    if type(value) is types.ListType:
                        tempData[key] = [self.render(i, triple, link) for i in value]
                    else:
                        tempData[key] = self.render(value, triple, link)
            return tempData
        else:
            return {}
        
    def render(self, temp, triple, link):
        return temp.replace("$predicate", triple.predicate). \
                    replace("$object", triple.object). \
                    replace("$content", triple.content). \
                    replace("$text", triple.text). \
                    replace("$subject", triple.subject). \
                    replace("$url", link)



