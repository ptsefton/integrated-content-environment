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

import os, sys
import unittest
from unittest import TestCase, TextTestRunner, TestLoader, TestResult, TestSuite, defaultTestLoader

sys.path.append("../../../utils")
from file_system import *
from system import *

fs = FileSystem(".")

def __getAllTestFiles(path=".", includeSubDirs=[]):
    tests = []
    if path is None:
        return tests
    if not path.endswith("/"):
        path += "/"

    #for p, dirs, files in os.walk(path):
    for p, dirs, files in fs.walk(path):
        p = p[len(path):]
        for dir in tuple(dirs):
            #if os.path.join(p, dir) not in includeSubDirs:
            if fs.join(p, dir) not in includeSubDirs:
                dirs.remove(dir)
        for file in files:
            if file.endswith("_test.py") or file.endswith("Test.py"):
                name = file[:-3]
                #Atests.append((os.path.join(path, p, file), name))
                tests.append((fs.join(path, p, file), name))
    return tests

def __getAllTestClasses(path=".", includeSubDir=[], files=[]):
    testFiles = __getAllTestFiles(path, includeSubDir)
    testFiles += files
    testClasses = []
    for filename, modName in testFiles:
        mod = __import__(modName)
        for itemName in [i for i in dir(mod) if i.startswith("test") or i.startswith("Test") or \
                                i.endswith("Test") or i.endswith("Tests")]:
            item = mod.__dict__[itemName]
            if hasattr(item, "__bases__"):
                if TestCase in item.__bases__:
                    testClasses.append([filename, itemName, item])
                elif len(item.__bases__)>0:
                    # else if a base class of the first inherited class is TestCase
                    base = item.__bases__[0]
                    if hasattr(base, "__bases__"):
                        if TestCase in base.__bases__:
                            testClasses.append([filename, itemName, item])
    return testClasses


def getAllTestClasses(path="."):
    """ Method to retrieve all TestCase classes for this directory """
    
    # Add any other TestCase classes to this list that would not other wise be found by getAllTestFiles()
    files = []    # other files that may contain TestCase classes that would not be otherwise found
    
    #files = [os.path.join(path, file) for file in files]
    files = [fs.join(path, file) for file in files]
    return __getAllTestClasses(path=path, includeSubDir=["test"], files=files)



def main(path="."):
    wasSuccessful = True
    suites = TestSuite()
    #path = os.path.abspath(path)
    path = fs.absPath(path)
    print "path='%s'" % path
    if fs.split(path)[1]=="apps":
        paths = []
        #for file in os.listdir(path):
        for file in fs.list(path):
            #p = os.path.join(path, file)
            p = fs.join(path, file)
            #if os.path.isdir(p) and not file.startswith("."):
            if fs.isDirectory(p) and not file.startswith("."):
                paths.append(p)
    else:
        paths = [path]
    for path in paths:
        #No chdir method id FileSystem
        os.chdir(path)
        print "Processing '%s'" % path
        testClasses = getAllTestClasses(path=path)
        for filename, testClassName, testClass in testClasses:
            suite = defaultTestLoader.loadTestsFromTestCase(testClass)
            print "file='%s', class='%s', test=%s" % (filename, testClassName, suite.countTestCases())
            #result = TextTestRunner(verbosity=1).run(suite)
            #if not result.wasSuccessful:
            #    wasSuccessful = False
            suites.addTest(suite)
        result = TextTestRunner(verbosity=1).run(suites)
        if result.wasSuccessful==False:
            wasSuccessful = False
    if wasSuccessful:
        print "Completed all tests OK."
        return True
    else:
        print "*** One or more tests Failed! ***"
        return result
    

if __name__ == "__main__":
    system.cls()
    print "---- Testing ----"
    print
    #unittest.main()
    main()

#suite = TestLoader().loadTestsFromTestCase(TestClass)
#suites.addTest(suite)
#TextTestRunner(verbosity=2).run(suites)

# import unittest
# unittest.main()
# class Tests(TestCase):
#    setUp()          tearDown()
#    testMethods()
#
#    assertEqual()    assertNotEqual()
#    assertTrue()     assertFalse()
#    fail()           failIf()
#    assertRaises()
#
#    suites = TestSuite()
#
#    suite = TestLoader().loadTestsFromTestCase(Tests)  
#    suites.addTest(suite)
#    #Note: defaultTestLoader is a default instance of TestLoader
#    
#    result = TextTestRunner(verbosity=1).run(suite)
#    result.errors    - are raised exceptions  -  List of tuples (TestCaseInstance, tracebackString)
#    result.failures  - are assert failures    -    "



