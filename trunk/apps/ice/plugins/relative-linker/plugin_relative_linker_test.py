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

import sys, os
cwd = os.getcwd()
os.chdir("../..")
sys.path.append(".")
from ice_common import IceCommon
os.chdir(cwd)

from plugin_relative_linker import RelativeLinker


class MockContext(object):
    def __init__(self):
        pass
MockContext.Xml = IceCommon.Xml


class RelativeLinkerTests(IceCommon.TestCase):
    def setUp(self):
        self.baseUrl = "http://localhost:8000/"
        context = MockContext()
        self.relativeLink = RelativeLinker(context, self.baseUrl)
    
    def tearDown(self):
        pass
    
    def testInit(self):
        pass
    
    def testMakeUrlRelativeTo(self):
        relativeTo = "/one/two/three/"
        url = "/two/test.txt"
        
        relativeTo = "/packages/"
        url = "/skin/css.txt"
        result = self.relativeLink.getRelativeLink(relativeTo, url)
        self.assertEqual("../skin/css.txt", result)
        
        relativeTo = "/packages/"
        url = "skin/css.txt"
        result = self.relativeLink.getRelativeLink(relativeTo, url)
        self.assertEqual("skin/css.txt", result)
        
        relativeTo = "/"
        url = "/skin/css.txt"
        result = self.relativeLink.getRelativeLink(relativeTo, url)
        self.assertEqual("skin/css.txt", result)

    def testMakeRelative(self):
        relativeTo = "/one/two/three/"
        url = "/two/test.txt"
        result = self.relativeLink.getRelativeLink(relativeTo, url)
        self.assertEqual("../../../two/test.txt", result)
        
        relativeTo = "/"
        url = "/skin/css.txt"
        result = self.relativeLink.getRelativeLink(relativeTo, url)
        self.assertEqual("skin/css.txt", result)

    def testGetRelativeLink(self):
        relativeLink = self.relativeLink
        sourceFileName = "/packages/stf1001/"
        url = "/packages/stf1001"
        expected = "."
        actual = relativeLink.getRelativeLink(sourceFileName, url)
        self.assertEqual(expected, actual)
            
        sourceFileName = "/courseware/faculty/edu/fet/5601/2005/s2/course_content/20/Module_2_Analysis_Phase.htm"
        url = "http://localhost:8000/courseware/faculty/edu/fet/5601/2005/s2/x.htm"
        expected = "../../x.htm"
        actual = relativeLink.getRelativeLink(sourceFileName, url)
        self.assertEqual(expected, actual)
        
        url = "http://localhost:8000/courseware/faculty/edu/fet/5601/2005/s2/course_content/30/x.htm"
        expected = "../30/x.htm"
        actual = relativeLink.getRelativeLink(sourceFileName, url)
        self.assertEqual(expected, actual)
        
        sourceFileName = "/courseware/faculty/edu/fet/5601/2005/s2/course_content/20/Module_2_Analysis_Phase.htm"
        url = "http://localhost:8000/courseware/faculty/edu/fet/5601/2005/s2/course_content/20/xxx/x.htm#test"
        expected = "xxx/x.htm#test"
        actual = relativeLink.getRelativeLink(sourceFileName, url)
        self.assertEqual(expected, actual)
        
        url = "http://test.com/courseware/faculty/edu/fet/5601/2005/s2/course_content/20/xxx/x.htm"
        expected = url
        actual = relativeLink.getRelativeLink(sourceFileName, url)
        self.assertEqual(expected, actual)
        
        sourceFileName = "/courseware/faculty/edu/fet/5601/2005/s2/course_content/20/"
        url = "http://localhost:8000/courseware/faculty/edu/fet/5601/2005/s2/course_content/20/x.htm"
        expected = "x.htm"
        actual = relativeLink.getRelativeLink(sourceFileName, url)
        self.assertEqual(expected, actual)
        
        url = "http://localhost:80001/courseware/faculty/edu/fet/5601/2005/s2/course_content/20/x.htm"
        expected = url
        actual = relativeLink.getRelativeLink(sourceFileName, url)
        self.assertEqual(expected, actual)
        
        sourceFileName = "/courseware/faculty/edu/fet/5601/2005/s2/"
        url = "s2/test/x.htm"
        expected = url
        actual = relativeLink.getRelativeLink(sourceFileName, url)
        self.assertEqual(expected, actual)
        
        sourceFileName = "/courseware/faculty/edu/fet/5601/2005/s2"
        url = "s2/test/x.htm"
        expected = url
        actual = relativeLink.getRelativeLink(sourceFileName, url)
        self.assertEqual(expected, actual)
        
        sourceFileName = "/courseware/faculty/edu/fet/5601/2005/s2"
        url = "/s2/test/x.htm"
        expected = "../"*6 + "s2/test/x.htm"
        actual = relativeLink.getRelativeLink(sourceFileName, url)
        self.assertEqual(expected, actual)

        sourceFileName = "/courseware/faculty/edu/fet/5601/2005/s2/course_content/30/Module_3_Design_and_Development_of_F.odt" 
        url = "../" * 9 + "/x.htm"
        expected = url
        actual = relativeLink.getRelativeLink(sourceFileName, url)
        self.assertEqual(expected, actual)
        
        sourceFileName = "/courseware/faculty/edu/edu/5411/2005/s2/course_content/Study_Schedule.odt"
        url = "http://ezproxy.usq.edu.au/login?url=http://search.epnet.com/direct.asp?an=ED473959&amp;db=eric"
        expected = url
        actual = relativeLink.getRelativeLink(sourceFileName, url)
        self.assertEqual(expected, actual)

    def testProcessNodes(self):
        relativeTo = "/courseware/faculty/edu/fet/5601/2005/s2/"
        source = """<ul>
<li><a href='/courseware/faculty/edu/fet/5601/2005/s2/unit_resources/22/Exemplars.htm'>Exemplars</a></li>
<li><a href='/courseware/faculty/edu/fet/5601/2005/s2/course_content/Study_Schedule.htm'>Study Schedule</a></li>
<li><a href='/courseware/faculty/edu/fet/5601/2005/s2/course_content/20/Module_2_Analysis_Phase.htm'>Module 2 - Analysis Phase</a></li>
<li><a href='/courseware/faculty/edu/fet/5601/2005/s2/course_guide/assessment/Assessment.htm'>Assessment</a></li>
</ul>"""
        expected = """<ul>
<li><a href='unit_resources/22/Exemplars.htm'>Exemplars</a></li>
<li><a href='course_content/Study_Schedule.htm'>Study Schedule</a></li>
<li><a href='course_content/20/Module_2_Analysis_Phase.htm'>Module 2 - Analysis Phase</a></li>
<li><a href='course_guide/assessment/Assessment.htm'>Assessment</a></li>
</ul>"""
        actual = self.relativeLink.makeRelative(source, relativeTo)
        actual = actual.replace("'", '"')
        expected = expected.replace("'", '"')
        self.assertEqual(expected, actual)
        
        relativeTo = "/courseware/faculty/edu/fet/5601/2005/s2/unit_resources/"
        expected = """<ul>
<li><a href='22/Exemplars.htm'>Exemplars</a></li>
<li><a href='../course_content/Study_Schedule.htm'>Study Schedule</a></li>
<li><a href='../course_content/20/Module_2_Analysis_Phase.htm'>Module 2 - Analysis Phase</a></li>
<li><a href='../course_guide/assessment/Assessment.htm'>Assessment</a></li>
</ul>"""
        actual = self.relativeLink.makeRelative(source, relativeTo)    
        self.assertEqual(expected.replace("'", '"'), actual.replace("'", '"'))
    
    def testGetRelativeLinkFunction(self):
        relativeTo = "/courseware/faculty/edu/fet/5601/2005/s2/"
        url = "/courseware/faculty/edu/fet/5601/2005/s2/test1.ext"
        expected = "test1.ext"
        actual = self.relativeLink.getRelativeLink(relativeTo, url)
        self.assertEqual(expected, actual)
        
        relativeTo = "/courseware/faculty/edu/fet/5601/2005/s2/"
        url = "/courseware/faculty/edu/fet/5601/2005/s2/test/test1.ext"
        expected = "test/test1.ext"
        actual = self.relativeLink.getRelativeLink(relativeTo, url)
        self.assertEqual(expected, actual)
        
        url = "/courseware/faculty/edu/fet/5601/2005/s2/test1.ext"
        expected = "test1.ext"
        actual = self.relativeLink.getRelativeLink(relativeTo, url)
        self.assertEqual(expected, actual)


if __name__ == "__main__":
    IceCommon.runUnitTests(locals())



