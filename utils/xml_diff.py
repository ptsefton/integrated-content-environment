#
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

import difflib
import libxml2
import tempfile
import re
import os

from unittest import TestCase


class XmlTestCase(TestCase):
    def __init__(self, *args, **kwargs):
        self.__xmlDiff = XmlDiff()
        TestCase.__init__(self, *args, **kwargs)
    
    def assertSameXml(self, actual, expected, msg=None, printDiff=True):
        r, printData = self.__xmlDiff.assertSameXml(actual, expected, printDiff)
        if r == False:
            if printDiff:
                if msg is None:
                    msg = "Xml not the same!\n\t"
                    msg += printData
                else:
                    msg = "----------------------------------\n"
                    msg += printData
                    msg += "\n----------------------------------"
            self.fail(msg)
    
    def assertNotSameXml(self, actual, expected, msg=None, printDiff=False):
        r, printData = self.__xmlDiff.assertSameXml(actual, expected, printDiff)
        if r == True:
            if msg is None:
                msg = "Xml actual is the same as Xml expected!"
            self.fail(msg)
        else:
            if printDiff:
                msg = "----------------------------------\n"
                msg += printData
                msg += "\n----------------------------------"
                print msg



class XmlDiff(object):
    def __same(self, actual, expected, printDiff=True):
        msg = ""
        if actual==None and expected==None:
            return True, msg
        if actual==None or expected==None:
            if printDiff:
                msg += "actual = '%s'\n" % str(actual) 
                msg += "expected = '%s'" % str(expected)
            return False, msg
        if actual!=expected:
            if printDiff:
                msg += self.__stringDiff(actual, expected) + "\n"
            return False, msg
        return True, msg
    
    
    def __stringDiff(self, actual, expected):
        diff = list(difflib.ndiff(actual.splitlines(1), expected.splitlines(2)))
        return "\n".join(diff)


    def assertSameXml(self, actual, expected, printDiff=True):
        if actual==None and expected==None:
            return False, "(not XML data) actual==None and expected==None!"
        if actual is None:
            return False, "actual==None and actual!=expected!"
        if expected is None:
            return False, "expected==None and actual!=expected!"

        try:
            actual = self.normalizeXml(actual, format=True, stripWhiteOnlyText=True)
        except Exception, e:
            msg = "Actual is not well-formed XML! (or is not an xmlString or dom/node)"
            return False, msg
        try:
            expected = self.normalizeXml(expected, format=True, stripWhiteOnlyText=True)
        except:
            msg = "Expected is not well-formed XML! (or is not an xmlString or dom/node)"
            return False, msg
        
        result, msg = self.__same(actual, expected, printDiff)
        if (result==False and printDiff) and (actual is not None and expected is not None):
            msg += "\n"
            msg += "actual = '%s'\n" % str(actual)
            msg += "expected = '%s'" % str(expected)
        return result, msg

    def normalizeXml(self, xml, format=True, stripWhiteOnlyText=True):  #, stripComments=False, stripPIs=False
        if type(xml)!=type(""):
            xml = xml.serialize()
        dom = libxml2.parseDoc(xml)
        if stripWhiteOnlyText:
            textNodes = dom.xpathEval("//text()")
            #print len(textNodes)
            regex = re.compile("^\s*$")
            for node in textNodes:
                if regex.match(node.content)!=None:
                    node.unlinkNode()
                else:
                    pass
                    #print "text = '%s'" % node.content
            
        if format:
            filename = tempfile.mktemp()
            dom.saveFormatFile(filename, 1)
            dom = libxml2.parseFile(filename)
            os.remove(filename)
        result = dom.c14nMemory()
        dom.free()
        return result
    
    








