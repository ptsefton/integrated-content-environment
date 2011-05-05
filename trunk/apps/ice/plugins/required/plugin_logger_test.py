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

#import sys
#if sys.path.count("../ice")==0: sys.path.append("../ice")
#from ixe_globals import *
from ice_common import IceCommon
IceCommon.setup()

from plugin_logger import *

import unittest
import os


class TestHandler(Handler):
    def __init__(self):
        Handler.__init__(self)
        self.records = []

    def emit(self, record):
        self.records.append(record)


class IceLoggerTests(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testIceLogger(self):
        logger = getLogger("test")
        testHandler = TestHandler()
        logger.addHandler(testHandler)
        self.assertEqual(logger.handlers, [testHandler])
        logger.setLevel(10)
        logger.log(2, "TestLevel2")
        logger.log(12, "TestLevel12")
        error = None
        try:
            raise Exception("TestException")
        except Exception, e:
            error = e
            logger.log(11, "exceptionTest", exc_info=True)
        logger.iceInfo("iceInfoMsg")
        loggedRecords = testHandler.records
        if False:
            for record in loggedRecords:
                print "levelno=%s, msg='%s'" % (record.levelno, record.msg)
                if record.exc_info is not None:
                    e = record.exc_info[1]
                    print " Exception message='%s'" % e
        self.assertEqual(loggedRecords[0].levelno, 12)
        self.assertEqual(loggedRecords[0].msg, "TestLevel12")
        self.assertEqual(loggedRecords[1].msg, "exceptionTest")
        self.assertEqual(loggedRecords[1].exc_info[1], error)
        self.assertEqual(loggedRecords[2].levelno, 25)
        self.assertEqual(loggedRecords[2].msg, "iceInfoMsg")



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




