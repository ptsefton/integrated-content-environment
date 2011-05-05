
#    Copyright (C) 2010  Distance and e-Learning Centre,
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

""" """

from threading import Thread
from threading import RLock
from time import sleep
import types 


pluginName = "ice.delay.cleanup"
pluginDesc = ""
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = DelayCleanup.getDelayCleanup
    pluginClass = DelayCleanup
    pluginInitialized = True
    return pluginFunc


class DelayCleanup(object):
    SLEEPTIME = 3
    _delayCleanup = None

    @staticmethod
    def getDelayCleanup(iceContext):
        if DelayCleanup._delayCleanup is None:
            DelayCleanup._delayCleanup = DelayCleanup(iceContext)
        return DelayCleanup._delayCleanup

    @staticmethod
    def curry(func, *args, **kwargs):
        def cfunc():
            func(*args, **kwargs)
        return cfunc;

    
    def __init__(self, iceContext, **kwargs):
        self.iceContext = iceContext
        self.__fs = iceContext.fs
        self._running = True
        self.__delPaths = {}
        self._functions = {}
        self._rLock = RLock()       # self._rLock.acquire() & self._rLock.release()
        self._thread = Thread(target=self.__waitLoop, name="delayCleanup thread")
        self._thread.daemon = True
        self._thread.start()



    def delPath(self, absPath, secs):
        if type(absPath) not in types.StringTypes:
            raise Exception("absPath must be a string argument!")
        try:
            self._rLock.acquire()
            self.__delPaths[absPath] = secs
            #print "__delPaths.keys='%s'" % self.__delPaths.keys()
        finally:
            self._rLock.release()

    
    def cancelDel(self, absPath):
        try:
            self._rLock.acquire()
            if self.__delPaths.has_key(absPath):
                del self.__delPaths[absPath]
        finally:
            self._rLock.release()

    def doFunc(self, func, secs):
        try:
            self._rLock.acquire()
            self._functions[func] = secs
        finally:
            self._rLock.release()

    def _safe(self, func, *args, **kwargs):
        try:
            self._rLock.acquire()
            return func(*args, **kwargs)
        finally:
            self._rLock.release()


    def __ticWork(self):
        try:
          try:
            self._rLock.acquire()
            secs = self.SLEEPTIME
            dels = []
            for absPath in self.__delPaths.iterkeys():
                try:
                    self.__delPaths[absPath] -= secs
                    if self.__delPaths[absPath]<0:
                        #print "delay deleting '%s'" % absPath
                        dels.append(absPath)
                        self.__fs.delete(absPath)
                except Exception, e:
                    pass
                    #print "(absPath) error %s" % str(e)
            for absPath in dels: del self.__delPaths[absPath]

            dels = []
            for func in self._functions.iterkeys():
                try:
                    self._functions[func] -= secs
                    #print func, self._functions[func]
                    if self._functions[func]<0:
                        dels.append(func)
                        func()
                except Exception, e:
                    pass
                    #print "(func) error %s" % str(e)
            for func in dels: del self._functions[func]
          except Exception, e:
              pass
              #print str(e)
        finally:
            self._rLock.release()


    def __waitLoop(self):
        while self._running:
            sleep(self.SLEEPTIME)
            try:
                self.__ticWork()
            except:
                pass

    def __del__(self):
        try:
            for key in self.__delPaths:
                dels.append(absPath)
            self.__delPaths.clear()
        except:
            pass
        self._running = False
        self._thread = None
