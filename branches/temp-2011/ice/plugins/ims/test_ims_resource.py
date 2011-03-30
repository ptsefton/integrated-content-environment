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

from ims_resource import ImsResource

from hashlib import md5
from diff_util import *


imsNSList = [ \
            ("ims", "http://www.imsglobal.org/xsd/imscp_v1p1"), \
            ("imsmd", "http://www.imsglobal.org/xsd/imsmd_v1p2"), \
            ("xsi", "http://www.w3.org/2001/XMLSchema-instance"), \
         ]
# Test Data
resXmlStr = """<resource identifier="1d8994d66d3f5774b5d92b143bfd2daa"
                 type="webcontent" href="intro/assessment.htm">
    <file href="intro/assessment.htm"/>
    <file href="intro/assessment.pdf"/>
</resource>"""


# Mock objects
class mockResources(object):
    def __init__(self, rep=None):
        if rep==None:
            rep = mockRepository()
        self.__rep = rep
        self.__startPath = "/test/"
    
    def __getStartPath(self):
        return self.__startPath
    startPath = property(__getStartPath)
    
    def __getRep(self):
        return self.__rep
    rep = property(__getRep)

    def getIdFor(self, href):
        s = IceCommon.url_join(self.startPath, href)
        name, ext = IceCommon.fs.splitExt(s)
        hash = md5(name)
        return hash.hexdigest()    


class mockRepository(object):
    def __init__(self):
        self.__files = {}
        item = {"name": "/test/intro/assessment.odt", "html": True, "pdf": True, \
                "rendition": {".pdf": True}, \
                "meta": {"images": [], "isSlide": False}
               }
        self.__files["/test/intro/assessment"] = item
        
        item = {"name": "/test/one.odt", "html": True, "pdf": True, \
                "rendition": {".pdf": True}, \
                "meta": {"images": ["one.gif", "two.jpg"], "isSlide": True}
               }
        self.__files["/test/one"] = item
        
        item = {"name": "/test/two.doc", "html": True, "pdf": True, \
                "rendition": {".pdf": True}, \
                "meta": {"images": [], "isSlide": False}
               }
        self.__files["/test/two"] = item
    
    
    def __getItem(self, file, key, default=None):
        name, ext = IceCommon.fs.splitExt(file)
        item = self.__files.get(name, None)
        if item==None:
            return default
        return item[key]
    
    def getItemNameFor(self, file):
        return self.__getItem(file, "name")
    
    def isHtmlItem(self, file):
        return self.__getItem(file, "html", False)
    
    def isPdfItem(self, file):
        return self.__getItem(file, "pdf", False)
    
    def hasRendition(self, file, renditionType):
        rendition = self.__getItem(file, "rendition")
        if rendition==None:
            return False
        return rendition[renditionType]
    
    def getMeta(self, file, metaName):
        if metaName=="images":
            pass
        elif metaName=="isSide":
            pass
        else:
            raise Exception("mockRepository.getMeta('%s', '%s') does not support metaName '%s'!" % (file, metaName, metaName))
        meta = self.__getItem(file, "meta")
        return meta[metaName]


# ImsResource
#  Constructor:
#    ImsResource(parent, href=None, resNode=None, includeSource=False)
#  Properties:
#    startPath (ReadOnly)
#    identifier (ReadOnly)
#    href (ReadOnly)
#    repPath (ReadOnly)
#    isWordDoc (ReadOnly)
#    
#  Methods:
#    serialize(xml)
#    

def test_init_fromResNode():
    mockRess = mockResources()
    xml = IceCommon.Xml(resXmlStr)
    resNode = xml.getRootNode()
    
    res = imsResource(mockRess, resNode=resNode)
    # Test all (ReadOnly) properties
    assert res.startPath == "/test/"
    assert res.identifier == "1d8994d66d3f5774b5d92b143bfd2daa"
    assert res.href == "intro/assessment.htm"
    assert res.repPath == "/test/intro/assessment.odt"
    assert res.exists == True
    assert res.isWordDoc == False
    print str(res)
    # Test the serialize() method
    newResNode = res.serialize(xml)
    assertSameXml( newResNode, resNode)
    xml.close()


def test_init_fromHref():
    mockRess = mockResources()
    
    res = imsResource(mockRess, href="one.htm")
    # Test all (ReadOnly) properties
    assert res.startPath == "/test/"
    assert res.identifier == "8c7586325a75fb6d03e7041f48a8226e"
    assert res.href == "one.htm"
    assert res.repPath == "/test/one.odt"
    assert res.exists == True
    assert res.isWordDoc == False
    assert str(res) == """<resource href="one.htm" identifier="8c7586325a75fb6d03e7041f48a8226e" type="webcontent"><file href="one.htm"/><file href="one.pdf"/><file href="one_files/one.gif"/><file href="one_files/two.jpg"/></resource>"""

    res = imsResource(mockRess, href="two.htm", includeSource=True)
    # Test all (ReadOnly) properties
    assert res.startPath == "/test/"
    assert res.identifier == "16b00cb17125b8add43cdc8567551fae"
    assert res.href == "two.htm"
    assert res.exists == True
    assert res.repPath == "/test/two.doc"
    assert res.isWordDoc == True
    #print str(res)
    assert str(res) == """<resource href="two.htm" identifier="16b00cb17125b8add43cdc8567551fae" type="webcontent"><file href="two.doc"/><file href="two.htm"/><file href="two.pdf"/></resource>"""


def test_doesNotExist():
    mockRess = mockResources()
    
    res = imsResource(mockRess, href="doesNotExist.htm")
    assert res.exists == False
    assert res.startPath == "/test/"
    
    assert res.identifier == "c3d63b860718032cd432bccc27f4f6d1"
    assert res.href == "doesNotExist.htm"
    assert res.repPath == None
    assert res.isWordDoc == False


    


