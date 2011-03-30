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

import sys
sys.path.append("../ice")
from ice_common import IceCommon

from ice_action_result import *


class ActionResultsTests(IceCommon.TestCase):
    #ActionResults
    # Constructor
    #   __init__(mainAction, info={})
    # Properties
    #   mainAction
    #   info
    #   actions
    #   isWarning
    #   isError
    #   isAllOK
    # Methods
    #   addAction(action, resultMessage="", exception=None, isWarning=False, info={})
    #   summary()
    #   message()
    #   fullInfo(all=True)
    #   __str__()
    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def testInit(self):
        actionResults = ActionResults("Test")
        self.assertEqual("Test", actionResults.mainAction)
        self.assertFalse(actionResults.isWarning)
        self.assertFalse(actionResults.isError)
        self.assertTrue(actionResults.isAllOK)
        self.assertEqual(actionResults.actions, [])
        self.assertEqual("Completed OK", actionResults.summary())
        self.assertEqual("Test\n", actionResults.message())
        self.assertEqual("Results for 'Test'\n", actionResults.fullInfo())
        self.assertEqual("Results for 'Test'\n", str(actionResults))
    
    def testAddAction(self):
        actionResults = ActionResults("Test")
        actionResults.addAction("Step1")
        actionResults.addAction("Step2", "-ok-")
        self.assertEqual(len(actionResults.actions), 2)
        self.assertFalse(actionResults.isWarning)
        self.assertFalse(actionResults.isError)
        self.assertTrue(actionResults.isAllOK)
        actionResults.addAction("Step3", "-warning-", isWarning=True)
        self.assertTrue(actionResults.isWarning)
        self.assertFalse(actionResults.isError)
        self.assertFalse(actionResults.isAllOK)
        self.assertTrue(str(actionResults).find("Warning:")>-1)
        try:
            raise Exception("TestError")
        except Exception, e:
            actionResults.addAction("Step4", exception=e)
        self.assertTrue(actionResults.isWarning)
        self.assertTrue(actionResults.isError)
        self.assertFalse(actionResults.isAllOK)
        self.assertTrue(str(actionResults).find("Error:")>-1)
        #print actionResults
        #print "---"
        #print actionResults.fullInfo()


if __name__ == "__main__":
    IceCommon.runUnitTests(locals())



