#
#    Copyright (C) 2005  Distance and e-Learning Centre, 
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

import copy
import sys, time, types
import traceback, inspect
from cStringIO import StringIO

import threading
from threading import Thread
from threading import currentThread, RLock, local, Event

# change sys.stdout and sys.stderr so that it is thread safe (or can be used in a thread safe way)???

def test(d=1):
    time.sleep(d)
    print currentThread().getName()

# WorkerThread(name='newName') creates a named workerThread object that will then execute JobObjects
#   that are placed in its JobQueue
# JobObject(_function, *args, **kwargs) creates a job (function with arguments) that is to be executed
#   by a WorkerThread later-on at some time.


class WorkerThread(object):
    # Constructor:
    #   __init__(name="worker")
    # Properties:
    #   name
    #   isAlive     # normaly True
    #   isWorking   # currently doing work
    #   currentJob  # current (or last) job executing
    #   jobQueue    # the queue of jobs to be executed
    # Methods:
    #   # short-cut method for adding jobs to the jobQueue
    #   addJob(_function, _id, *args, **kwargs) or addJob(jobObject)
    #   close()     # stop this workerThread once all jobs have been completed.
    #   captureSysIO()  # self.stdout and self.stderr will capture all sys.stdout and sys.stderr output
    #                   #   that is not captured by the jobObject
    
    @staticmethod
    def getWorkerThread(name):
        for thread in threading.enumerate():
            if thread.getName()==name and hasattr(thread, "workerThread"):
                return thread.workerThread
        # else create a new workerThread
        return WorkerThread(name)
    
    def __init__(self, name="worker"):
        self.__name = name
        self.__event = Event()
        self.__thread = Thread(target=self.__run, name=name)
        self.__thread.workerThread = self
        self.__thread.setDaemon(True)          # is a daemon thread (this thread will not stop python from closing)
        self.__isWorking = False
        self.__thread.start()
        self.__jobQueue = JobQueue(self.__onAddJobCallback)
        self.__currentJob = None
        self.__rLock = RLock()
        self.__close = False
        self.__stdout = None
        self.__stderr = None
    
    @property
    def name(self):
        return self.__name
    
    @property
    def isAlive(self):
        return self.__thread.isAlive()
    
    @property
    def isWorking(self):
        self.__rLock.acquire()
        try:
            return self.__isWorking
        finally:
            self.__rLock.release()
    
    @property
    def currentJob(self):
        """ The current running job or the last job that was ran. """
        self.__rLock.acquire()
        try:
            return self.__currentJob
        finally:
            self.__rLock.release()
    
    @property
    def jobQueue(self):
        return self.__jobQueue
    
    ##
    def __getStdout(self):
        self.__rLock.acquire()
        try:
            return self.__stdout
        finally:
            self.__rLock.release()
    def __setStdout(self, io):
        self.__rLock.acquire()
        try:
            self.__stdout = io
        finally:
            self.__rLock.release()
    stdout = property(__getStdout, __setStdout)
    
    def __getStderr(self):
        self.__rLock.acquire()
        try:
            return self.__stderr
        finally:
            self.__rLock.release()
    def __setStderr(self, io):
        self.__rLock.acquire()
        try:
            self.__stderr = io
        finally:
            self.__rLock.release()
    stderr = property(__getStderr, __setStderr)
    ##

    def close(self):
        self.__rLock.acquire()
        try:
            self.__close = True
            self.__event.set()
        finally:
            self.__rLock.release()
    
    def __del__(self):
        pass
    
    def addJob(self, _function, _id, *args, **kwargs):       # short-cut method
        """
            usage: addJob(jobObject) 
               or: addJob(function, _id, *args, **kwargs)
            returns the add jobObject
        """
        if isinstance(_function, JobObject):
            jobObject = _function
        else:
            jobObject = JobObject(_function, _id, *args, **kwargs)
        self.__jobQueue.addJob(jobObject)
        return jobObject
    
    def captureSysIO(self):
        self.stdout = ThreadSafeStringIO()
        self.stderr = ThreadSafeStringIO()
    
    def __onAddJobCallback(self, jobQueue):
        self.__rLock.acquire()
        try:
            self.__event.set()
        finally:
            self.__rLock.release()
    
    def __run(self):
        while True:
            self.__event.wait()         # wait for a new job to run
            # while there are jobs, run them
            while self.__jobQueue.size>0:
                self.__rLock.acquire()
                try:
                    self.__event.clear()
                    job = self.__jobQueue.getJob()
                    self.__currentJob = job
                    self.__isWorking = True
                finally:
                    self.__rLock.release()
                if job is not None:
                    try:
                        job.start()
                    except:
                        pass
            self.__rLock.acquire()
            try:
                self.__isWorking = False
                if self.__close:
                    break
            finally:
                self.__rLock.release()


class JobObject(object):
    # Constructor:
    #   __init__()
    # Properties:
    #   isRunning           # This jobObject is currently being executed
    #   isFinished          # This jobObject has been executed (and now the results can be read)
    #   results             # The returned results from the function
    #   exception           # The exception if one was thrown
    #   formatExc           # Stack trace information (if exception was thrown)
    #   stdout
    #   stderr
    # Methods:
    #   getFunctionAndArgs()    # returns a tuple of (function, args, kwargs) 
    #   setOnFinishedCallback(callback) 
    #           # callback(this_jobObject) 
    #           # Note: that this callback will run in the worker thread that runs the code.
    #           # Returns true if the callback will be called, else False if it has already finished.
    #   start()                 # starts executing this jobObject on the currentThread. NOTE: normally called by the WorkerThread
    #   join(timeout=None)      # stops the calling thread until timeout or this jobObject has been executed
    #   captureSysIO()  # self.stdout and self.stderr will capture all sys.stdout and sys.stderr output

    def __init__(self, _function, _id, *args, **kwargs):
        self.__rLock = RLock()
        self.__isRunning = False
        self.__isFinished = False
        self.__function = _function
        self.__id = _id
        self.__args = args
        self.__kwargs = kwargs
        self.__event = Event()
        self.__onFinishedCallback = None
        self.__results = None
        self.__exception = None
        self.__formatExc = None
        self.__stdout = None
        self.__stderr = None
    
    @property
    def id(self):
        # is readonly should be safe
        return self.__id
    
    @property
    def isRunning(self):
        self.__rLock.acquire()
        try:
            return self.__isRunning
        finally:
            self.__rLock.release()
    
    @property
    def isFinished(self):
        self.__rLock.acquire()
        try:
            return self.__isFinished
        finally:
            self.__rLock.release()
    
    @property
    def results(self):
        return self.__results
    
    @property
    def exception(self):
        return self.__exception
    
    @property
    def formatExc(self):
        return self.__formatExc
    
    def __getStdout(self):
        self.__rLock.acquire()
        try:
            return self.__stdout
        finally:
            self.__rLock.release()
    def __setStdout(self, io):
        self.__rLock.acquire()
        try:
            self.__stdout = io
        finally:
            self.__rLock.release()
    stdout = property(__getStdout, __setStdout)
    
    def __getStderr(self):
        self.__rLock.acquire()
        try:
            return self.__stderr
        finally:
            self.__rLock.release()
    def __setStderr(self, io):
        self.__rLock.acquire()
        try:
            self.__stderr = io
        finally:
            self.__rLock.release()
    stderr = property(__getStderr, __setStderr)
    
    def getFunctionAndArgs(self):
        """ returns a tuple of (function, args, kwargs) """
        return self.__function, self.__args, self.__kwargs
    
    def setOnFinishedCallback(self, callback):
        """ callback(this_jobObject) 
            Note: that this callback will run in the worker thread that runs the code.
            Returns true if the callback will be called, else False if it has already finished.
        """
        self.__rLock.acquire()
        try:
            self.__onFinishedCallback = callback
            return not self.__isFinished
        finally:
            self.__rLock.release()
    
    def captureSysIO(self):
        self.stdout = ThreadSafeStringIO()
        self.stderr = ThreadSafeStringIO()
    
    def start(self):
        self.__rLock.acquire()
        try:
            self.__isRunning = True
        finally:
            self.__rLock.release()
        try:
            self.__results = self.__function(*self.__args, **self.__kwargs)
        except Exception, e:
            self.__exception = e
            self.__formatExc = traceback.format_exc()
        except:
            self.__exception = Exception("unexception of a non-exception type!")
            #tracebackObj = sys.exc_traceback
            #self.__formatExc = traceback.format_tb(tracebackObj)
            self.__formatExc = traceback.format_exc()
        try:
            self.__isRunning = False
            self.__isFinished = True
            self.__event.set()
            callback = self.__onFinishedCallback
        finally:
            self.__rLock.release()
        if callable(callback):
            try:
                callback(self)
            except:
                pass
    
    def join(self, timeout=None):
        self.__rLock.acquire()
        try:
            #if self.__isRunning:
            if self.__isFinished==False:
                self.__event.clear()
            else:
                return
        finally:
            self.__rLock.release()
        self.__event.wait(timeout)



class JobQueue(object):
    # Constructor:
    #   __init__(onAddJobCallback=None)
    # Properties:
    #   size        # the current size of the queue
    # Methods:
    #   addJob(jobObject)
    #   insertJob(jobObject, index=0)
    #   getJob()                        # returns the next jobObject to be executed or None
    #   peekJob(index=0)
    #   remove(jobObject)               # returns True if jobObject was removed from the queue
    #   deQueue()                       # removes ALL jobObjects from the queue and returns them (as a list)
    def __init__(self, onAddJobCallback=None):
        self.__rLock = RLock()
        self.__jobs = []
        self.__onAddJobCallback = onAddJobCallback
    
    @property
    def size(self):
        self.__rLock.acquire()
        try:
            return len(self.__jobs)
        finally:
            self.__rLock.release()
    
    def addJob(self, jobObject):
        self.__rLock.acquire()
        try:
            self.__jobs.append(jobObject)
        finally:
            self.__rLock.release()
        if callable(self.__onAddJobCallback):
            self.__onAddJobCallback(self)
    
    def insertJob(self, jobObject, index=0):
        self.__rLock.acquire()
        try:
            self.__jobs.insert(index, jobObject)
        finally:
            self.__rLock.release()
        if callable(self.__onAddJobCallback):
            self.__onAddJobCallback(self)
    
    def getJob(self):
        self.__rLock.acquire()
        try:
            if len(self.__jobs)>0:
                return self.__jobs.pop(0)
            else:
                return None
        finally:
            self.__rLock.release()
    
    def peekJob(self, index=0):
        self.__rLock.acquire()
        try:
            if len(self.__jobs)>index:
                return self.__jobs[index]
            else:
                return None
        finally:
            self.__rLock.release()
    
    def removeJob(self, job):
        """ Return True if job was removed OK, else False
        """
        self.__rLock.acquire()
        try:
            try:
                self.__jobs.remove(job)
                return True
            except:
                return False
        finally:
            self.__rLock.release()
    
    def deQueue(self):
        self.__rLock.acquire()
        try:
            queue = self.__jobs
            self.__jobs = []
            return queue
        finally:
            self.__rLock.release()




class ThreadSafeStringIO(object):
    # Constructor:
    #   __init__()
    # Properties:
    #   value                   # all the data that has been writen (after a readAndTruncate())
    # Methods:
    #   readAndTruncate()       # removes the data that has been written and returns it
    #   write(data)
    def __init__(self):
        self.__io = None
        self.__rLock = RLock()
    
    @property
    def value(self):
        self.__rLock.acquire()
        try:
            if self.__io is None:
                return None
            return self.__io.getvalue()
        finally:
            self.__rLock.release()
    
    def readAndTruncate(self):
        self.__rLock.acquire()
        try:
            if self.__io is None:
                self.__io = StringIO()
            data = self.__io.getvalue()
            self.__io.truncate(0)
        finally:
            self.__rLock.release()
        return data
    
    def write(self, data):
        self.__rLock.acquire()
        try:
            if self.__io is None:
                self.__io = StringIO()
            self.__io.write(data)
        finally:
            self.__rLock.release()


class ThreadedStdout(object):
    # Constructor:
    #   __init__()
    # Properties:
    #   
    # Methods:
    #   close()         # restore the captured io
    #   write(data)
    
    def __init__(self, x):
        #sysStdout.write("ThreadStdout __init__\n")
        if isinstance(x, ThreadedStdout):
            raise Exception("argument x is also a ThreadedStdout")
        self.__stdout = x.stdout
        self.__x = x
        x.stdout = self
    
    def close(self):
        self.__x.stdout = self.__stdout
    
    def write(self, data):
        ct = currentThread()
        if hasattr(ct, "workerThread"):
            wt = ct.workerThread
            currentJob = wt.currentJob
            if currentJob is not None:
                stdout = currentJob.stdout
            if stdout is None:
                stdout = wt.stdout
            if stdout is not None:
                stdout.write(data)
                return
        self.__stdout.write(data)
    
    def __del__(self):
        self.close()
    
    def __call__(self, data):
        self.write(data)


class ThreadedStderr(object):
    # Constructor:
    #   __init__()
    # Properties:
    #   
    # Methods:
    #   close()         # restore the captured io
    #   write(data)
    
    def __init__(self, x):
        self.__stderr = x.stderr
        self.__x = x
        x.stderr = self
    
    def close(self):
        self.__x.stderr = self.__stderr
    
    def write(self, data):
        ct = currentThread()
        if hasattr(ct, "workerThread"):
            wt = ct.workerThread
            currentJob = wt.currentJob
            if currentJob is not None:
                stderr = currentJob.stderr
            if stderr is None:
                stderr = wt.stderr
            if stderr is not None:
                stderr.write(data)
                return
        self.__stderr.write(data)
    
    def __del__(self):
        self.close()
    
    def __call__(self, data):
        self.write(data)


sysStdout = sys.stdout
def captureThreadedSysStdoutAndStdErr():
    ThreadedStdout(sys)
    ThreadedStderr(sys)




# @synchronized - Decorator - will lock to the object (instance)
def synchronized(func):
    """
     synchronize wrapper decorator 
     Note: this can only be applied to methods (instance and class methods, not static methods)
            - Methods that require a self argument!
    """
    def wrapper(self, *args, **kargs):
        # Note: A try except block if is generally faster than a if test then block WHEN there is no exception
        try:        
            rlock = self._sync_lock
        except AttributeError:
            # Note: the use of the atomic setdefault method is very important, so that two threads do not
            #    create and use two different RLock objects at the same time!
            #  Using the setdefault method, insures that no matter how many threads simultaneously try 
            #     and create a new RLock, they will all get the same RLock object.
            rlock = self.__dict__.setdefault('_sync_lock', RLock())
        rlock.acquire()
        try:
            return func(self, *args, **kargs)
        finally:
            rlock.release()
    wrapper.__name__ = func.__name__
    wrapper.__dict__ = func.__dict__
    wrapper.__doc__ = func.__doc__
    return wrapper



