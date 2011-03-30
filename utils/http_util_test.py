#!/usr/local/bin/python
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

from http_util import *

import unittest
from unittest import TestCase, TextTestRunner, TestLoader, TestResult, defaultTestLoader as testLoader
import os
import sys



class HttpTests(TestCase):
    def setUp(self):
        self.http = Http(dummyHTTP=MockHTTP)
    
    def tearDown(self):
        pass
    
    def testBasicPost(self):
        url = "http://localhost"
        formData = [("one", "dataOne"), ("two", "dataTwo")]
        data = self.http.post(url, formData)
        self.assertEqual("OK", data)
        


class MockHTTP(object):
    def __init__(self, host):
        pass
    
    @property
    def file(self):
        return self

    def read(self):
        return "OK"
    
    def putrequest(self, name, data):
        pass
    
    def putheader(self, htype, data):
        pass
    
    def endheaders(self):
        pass
    
    def send(self, data):
        pass
    
    def getreply(self):
        return None, None, None
    

if __name__ == "__main__":
    try:
        os.system("reset")
    except:
        try:
            os.system("cls")
        except:
            print
            print
    print "---- Testing ----"
    print
    unittest.main()





