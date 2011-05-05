
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
import time
import re

pluginName = "ice.extra.inlineAnnotate"
pluginDesc = "inline annotations"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method



def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = None
    pluginClass = InlineAnnotations
    pluginInitialized = True
    InlineAnnotation.dumps = staticmethod(iceContext.dumps)
    InlineAnnotation.loads = staticmethod(iceContext.loads)
    InlineAnnotation.guid = staticmethod(iceContext.guid)
    InlineAnnotation.textToHtml = staticmethod(iceContext.textToHtml)
    return pluginFunc



class InlineAnnotations(object):
    #@staticmethod
    #def annotate(prop, username, formData):   # formData -> paraID, paraHtml, comment, other(imgages etc)
    #    pass
    
    @staticmethod       # Factory
    def getInlineAnnotations(prop):
        return prop.inlineAnnotations
    
    
    def __init__(self, io):
        self.__io = io  # writeFile(), readFile(), exists() (isDirectory), listFiles(), path
        #print "InlineAnnotations.__init__(path='%s')" % io.path
        self.__rootAnnotations = None
        self.__annotations = {}
    
    
    @property 
    def rootAnnotations(self):
        if self.__rootAnnotations is None:
            self.__loadInlineAnnotations()
        return self.__rootAnnotations
    
    @property
    def hasAnnontations(self):
        return self.__io.exists()
    
    
    def removeAllAnnotations(self):
        self.rootAnnotations     # to load the annotations if needed
        for a in self.__annotations.values():
            self.__deleteAnnotation(a)
        
    
    def action(self, username, formData):
        action = formData.value("action")
        if action=="add":
            paraId = formData.value("paraId")
            text = formData.value("text")
            html = formData.value("html")
            parentId = formData.value("parentId", None)
            if not (paraId.startswith("h") or paraId=="annotateThis"):
                parentId = paraId
                paraId = None
            if parentId=="undefined":
                print "Error: received parentId is undefined!"
                return "<div style='color:red;'>Failed to annotate. Error: parentId is undefined!</div>"
            if paraId is None or paraId=="" or paraId=="undefined":
                paraId = None
                html = ""
            if paraId=="annotateThis":
                html = ""
            return self.addAnnotation(username, paraId, text, html, parentId)
        elif action=="close":
            annoId = formData.value("id", "").lower()
            return self.closeAnnotation(username, annoId)
        elif action=="delete":
            annoId = formData.value("id", "").lower()
            return self.deleteAnnotation(username, annoId)
        else:
            return "Unknown action '%s'" % action
    
    
    def addAnnotation(self, username, paraId, text, html, parentId):
        """
            username
            paraId
            text
            html
            parentId (None for rootAnnotation)
            returns anno.getDiv()
        """
        # groupId or commitId ???
        #print "addAnnotation(paraId='%s', html='%s', text='%s', parentId='%s', author='%s')" % (paraId, html, text, parentId, username)
        anno = InlineAnnotation(paraId, html, text, parentId, author=username)
        if parentId is None:
            self.rootAnnotations.append(anno)
        else:
            parent = self.__annotations.get(parentId)
            if parent is not None:
                parent.addChild(anno)
        self.__saveAnnotation(anno)
        return anno.getDiv()
    
    
    def closeAnnotation(self, username, annoId):
        print "closeAnnotation(username='%s', annoId='%s')" % (username, annoId)
        self.rootAnnotations     # to load the annotations if needed
        anno = self.__annotations.get(annoId)
        if anno is None:
            return "Not found! (Annotation with an id of '%s' not found)" % annoId
        anno.close(username, saveMethod=self.__saveAnnotation)
        #return "Closed"     # return replacement 'closed' tree (anno.getDiv())
        return anno.getDiv()
    
    
    def deleteAnnotation(self, username, annoId):
        print "deleteAnnotation(username='%s', annoId='%s')" % (username, annoId)
        self.rootAnnotations     # to load the annotations if needed
        anno = self.__annotations.get(annoId)
        if anno is None:
            #return "Not found! (Annotation with an id of '%s' not found)" % annoId
            return "Deleted"        # Already deleted
        anno.delete(username, saveMethod=self.__deleteAnnotation)
        return "Deleted"
    
    
    def getHtmlDiv(self):
        # ? including jQuery code ?
        html = "<div class='inline-annotations' style='display:none;'>%s</div>"
        html = "<div class='inline-annotations' style='display:none;border:1px solid red;'><h2>Inline comments</h2>%s</div>"
        aList = []
        for anno in self.rootAnnotations:
            div = anno.getDiv()
            aList.append(div)
        html = html % ("\n".join(aList))
        return html
    
    
    def __loadInlineAnnotations(self):
        self.__rootAnnotations = []
        if self.__io.exists():
            for file in self.__io.listFiles():
                data = self.__io.readFile(file)
                anno = InlineAnnotation.deserialize(data)
                self.__annotations[anno.id] = anno
            for anno in self.__annotations.values():
                parentId = anno.parentId
                if parentId is None:
                    self.__rootAnnotations.append(anno)
                else:
                    parent = self.__annotations.get(parentId)
                    if parent is not None:
                        parent.addChild(anno)
            # Now sort rootAnnotations based on dateTime
            def cmpAnno(anno1, anno2):
                return cmp(anno1.dateTime, anno2.dateTime)
            self.__rootAnnotations.sort(cmpAnno)
            for anno in self.__annotations.values():
                anno.children.sort(cmpAnno)
    
    
    def __saveAnnotation(self, annotation):
        data = annotation.serialize()
        name = annotation.id
        self.__io.writeFile(name, data)
    
    
    def __deleteAnnotation(self, annotation):
        name = annotation.id
        self.__io.deleteFile(name)



class InlineAnnotation(object):
    dumps = None
    loads = None
    guid = None
    textToHtml = None
    
    
    @staticmethod
    def deserialize(data):
        inlineAnnotation = InlineAnnotation.loads(data)
        return inlineAnnotation
        
    
    def __init__(self, paraId, paraHtml, text="", parentId=None, \
            author="anonymous", dateTime=None, id=None):
        if id is None:
            id = self.guid()
        self.__id = id
        self.__paraId = paraId
        self.__paraHtml = paraHtml
        self.__textContent = text
        self.__parentId = parentId
        if author is None or author=="":
            author = "anonymous"
        self.__author = author
        if dateTime is None:
            dateTime = time.time()
        self.__dateTime = dateTime
        self.__status = ""
        self.__children = []
        self.__closedBy = None
        self.__deletedBy = None
    
    
    @property
    def id(self):
        return self.__id
    
    @property
    def paraId(self):
        return self.__paraId
    
    @property
    def parentId(self):
        return self.__parentId
    
    @property
    def paraHtml(self):
        return self.__paraHtml
    
    @property
    def textContent(self):
        return self.__textContent
    
    @property
    def author(self):
        return self.__author
    
    @property
    def closedBy(self):
        return self.__closedBy
    
    @property
    def isDeleted(self):
        return self.__status=="deleted"
    
    @property
    def dateTime(self):
        return self.__dateTime
    
    @property 
    def dateTimeStr(self):
        return time.ctime(self.__dateTime)
    
    @property
    def status(self):
        return self.__status
    
    @property
    def children(self):
        return self.__children
    
    def addChild(self, inlineAnnotation):
        self.__children.append(inlineAnnotation)
    
    def close(self, closedBy, saveMethod=None):
        if closedBy is None or closedBy=="":
            closedBy = "anonymous"
        self.__closedBy = closedBy
        self.__status = "closed"
        for child in self.__children:
            child.close(closedBy, saveMethod)
        if callable(saveMethod):
            saveMethod(self)
    
    def delete(self, deletedBy, saveMethod=None):
        if deletedBy is None or deletedBy=="":
            closedBy = "anonymous"
        self.__deletedBy = deletedBy
        self.__status = "deleted"
        for child in self.__children:
            child.delete(deletedBy, saveMethod)
        if callable(saveMethod):
            saveMethod(self)
    
    def serialize(self):
        # do not serialize children data
        children = self.__children
        self.__children = []
        data = self.dumps(self)
        self.__children = children
        return data
    
    def getDiv(self):
        #  style='border:1px solid gray;padding:0.2em;margin:0.2em;'
        #  style='color:green;'
        d = """
    <div id='%s' class='inline-annotation%s'>
        <input type='hidden' name='parentId' value='%s'><!-- --></input>
        <div class='orig-content' style='display:none;'>%s</div>
        <div class='anno-info'>Comment by: <span>%s</span> &#160; <span>%s</span>%s</div>
        %s
        <div class='anno-children'><!-- -->%%s</div>
    </div>\n"""
        if self.status=="closed":
            closedBy = " &#160; &#160; Closed by: <span>%s</span>" % self.closedBy
            closed = " closed"
        else:
            closedBy = ""
            closed = ""
        if self.parentId is not None:
            color = ""
        text = self.textToHtml(self.textContent, includeSpaces=False)
        def replace(m):
            l = len(m.group())
            s = " &#160;" * (l/2)
            if l%2:
                s += " "
            return s
        text = re.sub("\s{2,}", replace, text)
        origContent = self.paraHtml.strip()
        if origContent=="":
            origContent="<!-- -->"
        #origContent = "????"
        if self.parentId is not None:
            parentId = self.parentId
        else:
            parentId = self.paraId
        d = d % (self.id.lower(), closed, parentId.lower(), origContent.replace("%", "%%"), 
                    self.author, self.dateTimeStr, closedBy, text.replace("%", "%%"))
        children = []
        for child in self.children:
            children.append(child.getDiv())
        children.reverse()
        d = d % "".join(children)
        return d

    def __str__(self):
        return "[InlineAnnotation Object]"



