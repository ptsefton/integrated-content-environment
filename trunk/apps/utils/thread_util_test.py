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

from thread_util import *

import unittest
from unittest import TestCase, TextTestRunner, TestLoader, TestResult, defaultTestLoader as testLoader
import os
import sys
from time import sleep

from file_system import *
from system import *


captureThreadedSysStdoutAndStdErr()     # ???
workerThread = WorkerThread.getWorkerThread("workerThread1")
workerThread.captureSysIO()

class workerThreadTests(TestCase):
    def setUp(self):
        self.workerThread = WorkerThread.getWorkerThread("workerThread1")
        self.workerThread.stdout.readAndTruncate()
        self.workerThread.stderr.readAndTruncate()
    
    def tearDown(self):
        pass
    
    def jobTestMethod(self, delay=0, msg="", stderrMsg=None, exception=None, returnData=None):
        ct = currentThread()
        threadName = ct.getName()
        if stderrMsg is not None:
            sys.stderr.write(stderrMsg)
        time.sleep(delay)
        if type(msg) is types.StringType:
            print "testMethod() called on thread '%s' with msg='%s'" % (threadName, msg)
        else:
            print msg
        if exception is not None:
            raise exception
        return returnData
    
    def testRun(self):
        delay = 0
        msg = "Test"
        stderrMsg = "TestErrorMessage"
        exception = None
        returnData = "Completed OK"
        job = self.workerThread.addJob(self.jobTestMethod, msg=msg, stderrMsg=stderrMsg, \
                                        exception=exception, returnData=returnData)
        job.join()      # Wait until the job has finished
        if job.exception:
            print "**** Exception='%s'" % str(job.exception)
            raise job.exception
        self.assertEqual(job.results, returnData)
        self.assertEqual(self.workerThread.stdout.value, \
                    "testMethod() called on thread 'workerThread1' with msg='Test'\n")
        self.assertEqual(self.workerThread.stderr.value, \
                    stderrMsg)
    
    def testExceptionHandling(self):
        delay = 0
        msg = "Test"
        stderrMsg = "TestErrorMessage"
        exception = Exception("TestException")
        returnData = "Completed OK"
        job = self.workerThread.addJob(self.jobTestMethod, msg=msg, stderrMsg=stderrMsg, \
                                        exception=exception, returnData=returnData)
        job.join()      # Wait until the job has finished
        self.assertEqual(self.workerThread.stderr.value, stderrMsg)
        self.assertEqual(job.results, None)
        self.assertEqual(job.exception, exception)
        self.assertTrue(job.formatExc.startswith("Traceback "))
    
    def testJobObject(self):
        delay = 0
        msg = "Test"
        stderrMsg = "TestErrorMessage"
        exception = None
        returnData = "Completed OK"
        job = JobObject(self.jobTestMethod, msg=msg, stderrMsg=stderrMsg, \
                                        exception=exception, returnData=returnData)
        job.captureSysIO()
        self.workerThread.addJob(job)
        job.join()
        self.workerThread.stderr.readAndTruncate()
        self.workerThread.stdout.readAndTruncate()
        self.assertEqual(self.workerThread.stderr.value, "")
        self.assertEqual(self.workerThread.stdout.value, "")
        self.assertEqual(job.stderr.value, stderrMsg)
        self.assertEqual(job.stdout.value, "testMethod() called on thread 'workerThread1' with msg='Test'\n")
    
    def testJobQueue(self):
        delay = 0
        stderrMsg = None
        exception = None
        returnData = "Completed OK"
        jobs = []
        for x in range(4):
            msg = x
            returnData = x
            job = JobObject(self.jobTestMethod, msg=msg, stderrMsg=stderrMsg, \
                                        exception=exception, returnData=returnData)
            jobs.append(job)
            self.workerThread.addJob(job)
        job.join()  # wait util the last job has finished
        self.assertEqual(self.workerThread.stdout.value, "0\n1\n2\n3\n")
        x = 0
        for job in jobs:
            self.assertTrue(job.isFinished)
            self.assertFalse(job.exception)
            self.assertEqual(job.results, x)
            x += 1
    
    def testJobQueue2(self):
        delay = 0.1
        stderrMsg = None
        exception = None
        returnData = "Completed OK"
        jobs = []
        for x in range(4):
            msg = x
            returnData = x
            job = JobObject(self.jobTestMethod, msg=msg, stderrMsg=stderrMsg, \
                                        exception=exception, returnData=returnData)
            jobs.append(job)
        for job in jobs:
            self.workerThread.addJob(job)
        job = JobObject(self.jobTestMethod, msg=99, returnData=99)
        while jobs[0].isRunning==False:
            pass    # wait until the first job is started
        self.workerThread.jobQueue.insertJob(job)
        jobs[3].join()  # wait util the last job has finished
        self.assertEqual(self.workerThread.stdout.value, "0\n99\n1\n2\n3\n")
        


if __name__ == "__main__":
    system.cls()
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






