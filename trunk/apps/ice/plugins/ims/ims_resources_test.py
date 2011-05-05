 #!/usr/bin/env python
#    Copyright (C) 2007  Distance and e-Learning Centre, 
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

from ims_resources import *

import unittest
from unittest import TestCase, TextTestRunner, TestLoader, TestResult, defaultTestLoader as testLoader
from xml_diff import XmlTestCase    # assertSameXml(actual, expected, msg=None, printDiff=True)
                                    # assertNotSameXml(actual, expected, msg=None, printDiff=False)
                                    # 

imsNSList = [ \
            ("ims", "http://www.imsglobal.org/xsd/imscp_v1p1"), \
            ("imsmd", "http://www.imsglobal.org/xsd/imsmd_v1p2"), \
            ("xsi", "http://www.w3.org/2001/XMLSchema-instance"), \
         ]

resourcesXmlStr = """<resources>
    <resource identifier="1d8994d66d3f5774b5d92b143bfd2daa" type="webcontent"
            href="intro/assessment.htm">
        <file href="intro/assessment.htm"/>
    </resource>
</resources>
"""

# Use (setup) the mockResource for testing        
ImsResources.ImsResource = mockResource


# ImsResources   (keyed by resource.identifier)
#  Constructor:
#    ImsResources(parent, includeSource=False)
#  Properties:
#    rep (ReadOnly)
#    startPath (ReadOnly)
#    files (ReadOnly) [] array of files (hrefs)
#    [resourceIdentifier]
#  Methods:
#    createResource(href)
#    addResource(resource)
#    removeResource(resource)
#    getResourceByHref(href)
#    containsResource(href)
#    load(resourcesNode)
#    serialize(xml)
class ImsResourcesTests(XmlTestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def test(self):
        pass
##def test_init_AndProperties():
##    rep = mockRepository()
##    parent = mockParent(rep)
##    ress = ImsResources(parent)
##    
##    assert ress.rep is rep
##    assert ress.startPath == parent.startPath
##    assert str(ress) == "<resources/>"
##    
##
##def test_load_serialize():
##    parent = mockParent()
##    ress = ImsResources(parent)
##
##    xml = IceCommon.Xml(resourcesXmlStr)
##    ress.load(xml.getRootNode())
##    
##    href = "intro/assessment.htm"
##    id = "1d8994d66d3f5774b5d92b143bfd2daa"
##    assert ress.containsResource(href)
##    assert ress.getResourceByHref(href) is not None
##    assert ress[id] is not None
##    
##    ressXmlStr = """<resources><resource href="intro/assessment.htm" identifier="1d8994d66d3f5774b5d92b143bfd2daa" mock="True"/></resources>"""
##    assert str(ress) == ressXmlStr
##    ressNode = ress.serialize(xml)
##    assertSameXml(ressNode, ressXmlStr)
##    
##    xml.close()
##
##
##def test_otherResourceMethods():
##    # Test the following ImsResources 'resource' methods
##    #    removeResource(resource)
##    #    getResourceByHref(href)
##    #    containsResource(href)
##    parent = mockParent()
##    ress = ImsResources(parent)
##    href1 = "one.htm"
##    id1 = "ID+one.htm"
##    href2 = "dir/two.htm"
##    id2 = "ID+dir/two.htm"
##
##    # addFileResource() tests
##    res1 = ress.createResource(href1)
##    ress.addResource(res1)
##    res2 = ress.createResource(href2)
##    ress.addResource(res2)
##    assert res1.includeSource == False
##    
##    assert str(ress) == """<resources><resource href="dir/two.htm" identifier="ID+dir/two.htm" mock="True"/><resource href="one.htm" identifier="ID+one.htm" mock="True"/></resources>"""
##    
##    # containsResource() tests
##    assert ress.containsResource(href1)
##    assert ress.containsResource(href2)
##    assert ress.containsResource("x")==False
##    
##    # getResourceByHref() tests
##    assert ress.getResourceByHref(href1) is res1
##    assert ress.getResourceByHref(href2) is res2
##    assert ress.getResourceByHref("x") is None
##        
##    # [] tests
##    assert ress[id1] is res1
##    assert ress[id2] is res2
##    assert ress["x"] is None
##
##    # removeResource() tests
##    assert ress.removeResource(res1) is res1
##    assert ress.getResourceByHref(href1) is None
##    assert ress.getResourceByHref(href2) is res2
##    assert ress.removeResource(res2) is res2
##    assert ress.getResourceByHref(href1) is None
##    assert ress.getResourceByHref(href2) is None
##    assert ress.removeResource(res1) is None
##    
##    assert str(ress) == "<resources/>"
##
##def test_includeSource():
##    parent = mockParent()
##    ress = ImsResources(parent, includeSource=True)
##    href1 = "one.htm"
##    res1 = ress.createResource(href1)
##    ress.addResource(res1)
##    
##    assert res1.includeSource



class mockRepository(object):
    pass


class mockParent(object):
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


class mockResource(object):
    def __init__(self, parent, href=None, resNode=None, includeSource=False):
        self.parent = parent
        self.href = href
        self.resNode = str(resNode)
        self.includeSource = includeSource
        self.exists = True
        if resNode!=None:
            self.href = resNode.getAttribute("href")
            self.identifier = resNode.getAttribute("identifier")
        elif href==None:
            raise Exception("Either 'href' or 'resNode' parameter must be set!")
        else:
            self.identifier = "ID+%s" % href
        
    def serialize(self, xml):
        node = xml.createElement("resource", identifier=self.identifier, href=self.href, mock=True)
        return node



if __name__ == "__main__":
    import sys
    IceCommon.system.cls()
    print "---- Testing ----"
    print
    
    # Run only the selected tests
    #  Test Attribute testXxxx.slowTest = True
    #  fastOnly (do not run any slow tests)
    args = list(sys.argv)
    sys.argv = sys.argv[:1]
    args.pop(0)
    runTests = ["Add", "testAddGetRemoveImage"]
    runTests = args
    runTests = [ i.lower().strip(", ") for i in runTests]
    runTests = ["test"+i for i in runTests if not i.startswith("test")] + \
                [i for i in runTests if i.startswith("test")]
    if runTests!=[]:
        testClasses = [i for i in locals().values() \
                        if hasattr(i, "__bases__") and TestCase in i.__bases__]
        for x in testClasses:
            l = dir(x)
            l = [ i for i in l if i.startswith("test") and callable(getattr(x, i))]
            testing = []
            for i in l:
                if i.lower() not in runTests:
                    #print "Removing '%s'" % i
                    delattr(x, i)
                else:
                    #print "Testing '%s'" % i
                    testing.append(i)
        x = None
        print "Running %s selected tests - %s" % (len(testing), str(testing)[1:-1])
    
    unittest.main()





