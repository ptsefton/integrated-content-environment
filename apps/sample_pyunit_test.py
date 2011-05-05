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

try:
    from ice_common import IceCommon
    IceCommon.setup()
except:
    import sys
    sys.path.append("../ice")
    from ice_common import IceCommon
from xml_diff import XmlTestCase        # self.assertSameXml
from unittest import TestCase


#from xxxx_sample import *


class SampleXxxxTests(TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def testName(self):
        pass

    # etc



if __name__ == "__main__":
    IceCommon.runUnitTests(locals())




