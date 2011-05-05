#!/usr/bin/env python
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

try:
    from ice_common import IceCommon
    IceCommon.setup()
except:
    import sys, os
    sys.path.append(os.getcwd())
    sys.path.append(".")
    os.chdir("../../")
    from ice_common import IceCommon
# XmlTestCase        # self.assertSameXml


from plugin_check_links import *

class MockRep(object):
    def __init__(self, iceContext, contents={}, linksMeta={}, manifest={}):
        # Note: linksMeta is a dictionary of dictionaries e.g. {"one.htm":{links}}
        self.fs = iceContext.fs
        self.iceContext = iceContext
        self.iceContext.rep = self
        self.contents = contents
        self.linksMeta = linksMeta
        self.manifest = manifest
    
    def read(self, file):
        if file.endswith("/manifest.xml"):
            dom = IceCommon.Xml("<dummy xmlns='http://www.imsglobal.org/xsd/imscp_v1p1'/>", \
                    [("x", "http://www.imsglobal.org/xsd/imscp_v1p1")])
            #hrefs = dom.getContents("//x:resource/x:file/@href")
            
            rNode = dom.getRootNode()
            resNode = dom.createElement("resource")
            rNode.addChild(resNode)
            for name in self.contents.keys():
                fNode = dom.createElement("file", href=name)
                resNode.addChild(fNode)
            
            data = str(dom)
            #print data
            dom.close()
            return data
        else:
            return self.contents.get(file)
    
    def getItemNameFor(self, file):
        return file
    
    def getMeta(self, file, name):
        file = file.rstrip("/")
        if name!="links":
            raise Exception("mockRep.prop.getMeta() only supports name='links'")
        return self.linksMeta.get(file)
    
    def itemExists(self, path):
        # is valid if itemExists and itemHidden==False
        return self.contents.has_key(path)
    
    def itemHidden(self, path):
        return not self.contents.has_key(path)

    def getItem(self, relPath):
        item = MockIceItem(self.iceContext, relPath, self.contents, self.linksMeta, manifest=self.manifest)
        return item
    
    def getItemForUri(self, uriPath):
        MockItem = MockIceItem(self.iceContext, uriPath, self.contents, self.linksMeta, manifest=self.manifest)
        item = MockItem.getIceItemForUri(self.iceContext, uriPath, self.contents, self.linksMeta)
        return item
    
    def getAbsPath(self, relPath="/"):
        path = self.iceContext.url_join("/", relPath)
        path = self.iceContext.normalizePath(path)
        return path
    
class MockIceItem(object):
    def __init__(self, iceContext, relPath, contents={}, linksMeta={}, manifest=None):
        self.contents = contents
        self.linkMeta = linksMeta
        self.iceContext = iceContext
        self.fs = self.iceContext.fs
        self.relPath = relPath
        self.name = iceContext.fs.split(relPath)[1]
        self.meta = {}
        self.manifest = manifest
        self.__setLinkMeta(linksMeta)
        
    def __setLinkMeta(self, linksMeta):
        if linksMeta.has_key(self.relPath):
            self.meta["links"] = linksMeta[self.relPath]
        
    def read(self):
        file = self.relPath
        data = None
        if file.endswith("/manifest.xml"):
            dom = IceCommon.Xml("<dummy xmlns='http://www.imsglobal.org/xsd/imscp_v1p1'/>", \
                    [("x", "http://www.imsglobal.org/xsd/imscp_v1p1")])
            rNode = dom.getRootNode()
            resNode = dom.createElement("resource")
            rNode.addChild(resNode)
            for name in self.contents.keys():
                fNode = dom.createElement("file", href=name)
                resNode.addChild(fNode)
            data = str(dom)
            dom.close()
        return data
    
    def getIceItemForUri(self, iceContext, uri, contents, linksMeta):
        if uri.find("/skin/")>0:
            absPath = iceContext.rep.getAbsPath(uri)
            if not iceContext.fs.isFile(absPath):
                uri = uri[uri.find("/skin/"):]
        item = MockIceItem(iceContext, uri, contents, linksMeta, manifest=self.manifest)
        return item
    
    def getMeta(self, name, value=None):
        if name=="toc":
            value = self.meta.get(name, "")
        elif name=="manifest":
            manifest = MockManifest(manifest=self.manifest)
            return manifest
        else:
            value = self.meta.get(name, value)
        return value
    
    @property
    def exists(self):
        if self.contents.has_key(self.relPath):
            return True
        return False
    
    @property
    def uriNotFound(self):
        return False
    
class MockManifest(object):
    def __init__ (self, manifest=None):    
        self.title = manifest["/"][0]
        self.children = manifest["/"][1]
        self.noOfItems = manifest["/"][2]
        self.__manifestItem = None
        self.__allManifestItems = []
        for relPath in manifest:
            if relPath!="/":
                self.__manifestItem = MockManifestItem(relPath, manifest[relPath][0], manifest[relPath][1], manifest[relPath][2])
                self.__allManifestItems.append(self.__manifestItem)
    
    @property
    def allManifestItems(self):
        mItems = self.__allManifestItems
        return mItems
        
        
class MockManifestItem(object):
    def __init__ (self, relPath=None, title="", children=0, renditionName=""):
        self.relPath = relPath
        self.title = title
        self.children = children
        self.renditionName = renditionName
        
    

class CourseLinkCheckTests(IceCommon.TestCase):
    def setUp(self):
        self.iceContext = IceCommon.IceContext
        self.stdout = sys.stdout
        #sys.stdout = StringIO()
    
    def tearDown(self):
        sys.stdout = self.stdout
    
    def testInit(self):
        rep = MockRep(self.iceContext)
        checker = CourseLinkCheck(self.iceContext)

    def xtestEmptyReport(self):
        rep = MockRep(self.iceContext)
        checker = CourseLinkCheck(self.iceContext)
        report = checker.report("/")
        
        dom = IceCommon.Xml(report)
        try:
            h1 = dom.getNode("//h1[1]")
            h1msg = h1.getNextSibling().content
            #print h1msg
            self.assertEqual(h1msg, "\nNo invalid internal links\n")
            
            h1 = dom.getNode("//h1[2]")
            h1msg = h1.getNextSibling().content
            #print h1msg
            self.assertEqual(h1msg, "\nNo external links found\n")
        finally:
            dom.close()

    def xtestExternalLinkReport(self):
        manifestItem = {"/": ["Package Title", 1, 0], "one.odt": ["One Title", 0, "one.htm"]}
        rep = MockRep(self.iceContext, {"/one.htm":""}, {"/one.htm":{"http://www.python.org":"linkText"}}, manifest=manifestItem)
        checker = CourseLinkCheck(self.iceContext)
        report = checker.report("/")
#        print report
#        print "----"
        dom = IceCommon.Xml(report)
        try:
            h1 = dom.getNode("//h1[1]")
            h1msg = h1.getNextSibling().content
            self.assertEqual(h1msg, "\nNo invalid internal links\n")
            
            h1 = dom.getNode("//h1[2]")
            #print str(h1)
            nextSibling = h1.getNextSibling()
            if nextSibling.getType()=="text":
                nextSibling = nextSibling.getNextSibling()
            listItem = nextSibling.getNode("li[1]")
            #print str(listItem)
            self.assertEqual(len(listItem.getNodes("a")), 1)
            self.assertEqual(listItem.getNode("a/@href").content, "/one.htm")
            #print h1msg
            #self.assertEqual(h1msg, "No external links found")
        finally:
            dom.close()

    def testLinkReport(self):
        #             contents          links
        manifestItem = {"/": ["Package Title", 1, 0], 
                        "one.odt": ["One Title", 0, "one.htm"]
                        }
        rep = MockRep(self.iceContext, {"/one.htm":""}, {"/one.htm":
                    {   "/one.htm":"localOK",
                        "/bad.htm":"localBad",          # Bad
                        "one.htm":"relativeLocalOK",
                        "bad.htm":"relativeLocalBad",   # Bad
                        "news://somewhere.com":"newLink",       #External
                        "mailto:ice.testing@iceTesting.xxx":"mailtoLink",   #External
                        "http://www.python.org":"pythonLink",     #External
                    }
                    }, manifest=manifestItem)
        checker = CourseLinkCheck(self.iceContext)
        report = checker.report("/")
#        print "report='%s'" % report
        dom = IceCommon.Xml(report)
        try:
            h1 = dom.getNode("//h1[1]")
            nextSibling = h1.getNextSibling()
            if nextSibling.getType()=="text":
                nextSibling = nextSibling.getNextSibling()
            listItems = nextSibling.getNodes("li")
            #print str(h1)
            #print str(nextSibling)
            #print nextSibling.content
            #for listItem in listItems:
            #    print "-"
            #    print str(listItem)
            #print "---\n"
            self.assertEqual(h1.content, "Invalid internal links")
            self.assertEqual(len(listItems), 2)
            self.assertEqual(listItems[0].content, 
                    '/bad.htm in these pages: one.htm with the link text "relativeLocalBad". ')
            self.assertEqual(listItems[1].content, 
                    '/bad.htm in these pages: one.htm with the link text "localBad". ')
            
            h1 = dom.getNode("//h1[2]")
            nextSibling = h1.getNextSibling()
            if nextSibling.getType()=="text":
                nextSibling = nextSibling.getNextSibling()
            listItems = nextSibling.getNodes("li")
            #print str(h1)
            #print str(nextSibling)
            #print nextSibling.content
            #for listItem in listItems:
            #    print "-"
            #    print str(listItem)
            #print "---\n"
            self.assertEqual(h1.content, "External links")
            self.assertEqual(len(listItems), 3)
            self.assertEqual(listItems[0].content, 
                'news://somewhere.com in these pages: one.htm with the link text "newLink". ')
            self.assertEqual(listItems[1].content, 
                'mailto:ice.testing@iceTesting.xxx in these pages: one.htm with the link text "mailtoLink". ')
            self.assertEqual(listItems[2].content, 
                '/one.htm in these pages: one.htm with the link text "pythonLink". ')

        finally:
            dom.close()



if __name__ == "__main__":
    IceCommon.runUnitTests(locals())






