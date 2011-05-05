#
#    Copyright (C) 2006  Distance and e-Learning Centre, 
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

import inspect
import time
import traceback



class GTime(object):
    def __init__(self):
        self.ddata = {}     # used outside of this object
        self.enabled = True
        self.displayAsMs = True
        self.setup()
    
    def setup(self):
        self.startTiming()
    def startTiming(self):
        """ start timing """
        self.__stack = []
        self.__sections = dict()
        self.__marks = []
        self.__startTime = time.time()
        self.__lastMark = self.__startTime
        self.__totalTime = 0.0
        self.__stoppedAll = False
        self.isHtmlPage = False
    
    @property
    def totalTime(self):
        return self.__totalTime
    
    @property
    def marks(self):
        """ returns a list of (name, timeFromStart, timeFromPreviousMark) tuples """
        return self.__marks
    
    def mark(self, name):
        """ place a named time mark in the timing sequence """
        ti = time.time()
        t = ti-self.__startTime
        d = ti-self.__lastMark
        self.__lastMark = ti
        self.__marks.append( (name, t, d) )
        return ti, t, d
    
    # @includeForTiming - decorator -
    def includeForTiming(self, func):
        func.timeThis = True
        return func
    
    # @excludeFromTiming - decorator -
    def excludeForTiming(self, func):
        return self.excludeFromTiming(func)
    def excludeFromTiming(self, func):
        func.timeThis = False
        return func
    
    # @timeThis - decorator - 
    def timeThis(self, func):
        """ Usage: apply the @TimeThis decorator to any function or method that needs to be timed. """
        __func = func
        __name = func.__name__ + "()"
        if hasattr(func, "im_class"):
            __className = func.im_class.__name__
        else:
            __className = func.__module__
        __callCount = 0
        
        
        def wrapper(*args, **kargs):
            if self.enabled:
                self.start(__className, __name)
                try:
                    return __func(*args, **kargs)
                finally:
                    self.stop(__className, __name)
            else:
                return __func(*args, **kargs)
        # change the __call's function name to match the orginal
        # copy all attributes of the orginal function to this function
        wrapper.__name__ = func.__name__
        wrapper.__dict__ = func.__dict__
        wrapper.__doc__ = func.__doc__
        
        return wrapper

    #def time(self, _method, *args, **kargs):
    #    section = _method.im_self.__class__.__name__
    #    subSection = _method.im_func.__name__
    #    self.start(section, subSection)
    #    try:
    #        _method(*args, **kargs)
    #    finally:
    #        self.stop(section, subSection)
    
    class TimingData(object):
        def __init__(self, name, parent, push, pop, strTime=None):
            self.__push = push
            self.__pop = pop
            self.__startTime = 0.0
            self.__in = False
            self.name = name
            self.parent = parent
            self.dict = {}
            self.totalTime = 0.0            # time from staring to returning(finishing)
            self.totalWorkingTime = 0.0     # time working in this routine (excuting other timed routines)
            self.recursionCount = 0
            self.calledCount = 0
            if parent is not None:
                parent.dict[name] = self
            if strTime is not None:
                self.__strTime = strTime
        
        @property
        def timing(self):
            return self.__in
        
        def start(self):
            self.calledCount += 1
            self.__push()
            if self.__in == False:
                self.__startTime = time.time()
                self.__in = True
            else:
                self.recursionCount += 1
        
        def stop(self, all=False):
            if self.__in:
                t = self.__pop()
                self.totalWorkingTime += t
                if self.recursionCount>0:
                    self.recursionCount -= 1
                    if all:
                        self.stop(all)
                else:
                    t = time.time()
                    self.totalTime += t - self.__startTime
                    self.__in = False
            else:
                # already stopped
                pass
        
        def __strTime(self, t):
            return str(round(t, 4))
        
        def info(self, level=0):
            lines = []
            totalWorkingTime = self.totalWorkingTime
            s = "    " * level
            if self.dict!={}:
                for item in self.dict.itervalues():
                    workingTime, ls = item.info(level+1)
                    totalWorkingTime += workingTime
                    lines.extend(ls)
            if self.__in:
                s = "Currently timing... "
            #totalTime, totalWorkingTime, (calledCount)
            s += "%s - " % self.name
            s += "%s, %s (%s)" % (self.__strTime(self.totalTime), \
                    self.__strTime(totalWorkingTime), self.calledCount)
            lines.insert(0, s)
            return totalWorkingTime, lines
        
        def __str__(self):
            totalWorkingTime, lines = self.info()
            return "\n".join(lines)
    
    def __getNewTimingData(self, name, parent=None):
        return self.TimingData(name, parent, self.__push, self.__pop, self.__strTime)
    
    # protected?
    def start(self, section, subSection=""):
        """ start timing a section and optional subSection """
        subSection = str(subSection)
        #sec, sectionTimingData = self.__sections.setdefault(section, (dict(), 
        #                        self.__getNewTimingData(section)) )
        #subSec = sec.setdefault(subSection, 
        #                        self.__getNewTimingData(subSection, sectionTimingData))
        sectionTimingData = self.__sections.get(section, None)
        if sectionTimingData is None:
            sectionTimingData = self.__getNewTimingData(section)
            self.__sections[section] = sectionTimingData
        sec = sectionTimingData.dict
        subSec = sec.get(subSection, None)
        if subSec is None:
            subSec = self.__getNewTimingData(subSection, sectionTimingData)
            sec[subSection] = subSec
        sectionTimingData.start()
        subSec.start()
    
    # protected?
    def stop(self, section, subSection=""):
        """ stop timing a section and optional subSection """
        subSection = str(subSection)
        timingData = self.__sections.get(section, None)
        if timingData is None:
            raise Exception("section '%s' not found!" % section)
        sec = timingData.dict
        subSec = sec.get(subSection)
        if subSec is None:
            raise Exception("section '%s', subSection '%s' not found!" % (section, subSection))
        subSec.stop()
        timingData.stop()
    
    def stopAll(self):
        """ stop all timing
            including any and all unstopped section-subsection timings.
        """
        messages = []
        if self.__stoppedAll == False:
            self.__stoppedAll = True
            stopTime, x, y = self.mark("END")
            self.__totalTime = stopTime - self.__startTime
            for section in self.__sections.keys():
                sectionTimingData = self.__sections[section]
                sec = sectionTimingData.dict
                keys = sec.keys()
                keys.sort()
                for subSection in keys:
                    timingData = sec[subSection]
                    if timingData.timing:
                        msg = "section '%s', subSection '%s' was not stopped! recursionCount=%s"
                        msg = msg % (section, subSection, timingData.recursionCount)
                        messages.append(msg)
                        timingData.stop(all=True)
                if sectionTimingData.timing:
                    sectionTimingData.stop(all=True)
                    raise Exception("section '%s' was not stopped???" % section)
        return messages
    
    #
    def __push(self, id=None):
        now = time.time()
        self.__stack.append((id, now, 0))
    
    # get the time that this has been on the top of the stack
    def __pop(self, id=None):
        now = time.time()
        pid, pt, neg = self.__stack.pop()
        assert(id==pid)
        t = now - pt - neg
        neg += t
        l = len(self.__stack)
        if l>0:
            l -= 1
            pid, pt, tneg = self.__stack[l]
            self.__stack[l] = pid, pt, tneg + neg
        return t
    
    def getSectionNames(self):
        """ returns a list of all section names """
        names = self.__sections.keys()
        names.sort()
        return names
    
    def getSectionData(self, section):
        """ return a section timingData """
        sectionTimingData = self.__sections.get(section, None)
        if sectionTimingData is None:
            raise Exception("section '%s' not found!" % section)
        return sectionTimingData
    
    def getSectionsData(self):
        """ returns a dict of sectionNames: timingData """
        keys = self.__sections.keys()
        keys.sort()
        d = {}
        for key in keys:
            d[key] = self.getSectionData(key)
        return d
    
    def __getMarks(self):
        l = []
        for name, t, d in self.__marks:
            l.append( (name, self.__strTime(t), self.__strTime(d)) )
        return l
    
    def __strTime(self, t):
        if self.displayAsMs:
            s = str(round(t*1000,3)) + "mS"
        else:
            s = str(round(t, 4))
        return s

    def getDisplayLines(self):
        """ """
        lines = []
        lines.append(" ---  Timing Results  ----")
        for mark in self.__getMarks():
            lines.append("Mark '%s', %s, (%s)" % mark)
        lines.append("")
        for sectionName, timingData in self.getSectionsData().iteritems():
            tmp, xlines = timingData.info()
            lines.extend(xlines)
        lines.append(" --- --- \n")
        return lines
    
    def getDisplayString(self):
        """ """
        return "\n".join(self.getDisplayLines())

    def __str__(self):
        self.stopAll()
        return self.getDisplayString()

    #======================================================
    def getCaller(self):
        # (filename, line#, methodName, lineStr)
        return traceback.extract_stack(limit=3)[0]
        
    def printCallers(self, depth=1):
        for x in range(depth):
            file, line, method, code = traceback.extract_stack(limit=3+x)[0]
            print "%s#%s %s '%s' %s" % (" " * x, line, method, file, code)
    
    # @whosCallingMe - decorator -
    def whosCallingMe(self, func):
        # levels=1, print=True, record=False
        def wrapper(*args, **kargs):
            printCallers()
            func(*args, **kargs)
        # change the __call's function name to match the orginal
        # copy all attributes of the orginal function to this function
        wrapper.__name__ = func.__name__
        wrapper.__dict__ = func.__dict__
        wrapper.__doc__ = func.__doc__
        return wrapper
        
# @includeForTiming - decorator -
def includeForTiming(func):
    func.timeThis = True
    return func

# @excludeFromTiming - decorator -
def excludeForTiming(func):
    return excludeFromTiming(func)
def excludeFromTiming(func):
    func.timeThis = False
    return func


class NullGTime(object):
    def __init__(self):
        self.setup()
        self.ddata = {}
        
    def setup(self):
        self.__marks = []
        self.__startTime = time.time()
        self.__lastMark = self.__startTime
        self.isHtmlPage = False
    
    def __get_marks(self):
        return self.__marks
    marks = property(__get_marks)
    
    def mark(self, name):
        ti = time.time()
        t = ti-self.__startTime
        d = ti-self.__lastMark
        self.__lastMark = ti
        self.__marks.append( (name, t, d) )
        return ti, t, d
    
    def start(self, section, subSection=None):
        pass
    
    def stop(self, section, subSection=None):
        pass
    
    def stopAll(self):
        pass
    
    def getMarks(self):
        return []
    
    def getSections(self):
        return []
    
    def getSection(self, section):
        return []
        
    def getSectionsData(self):
        return {}
        
    def getSectionData(self, section):
        return {}, 0.0

# Note: this type of decorator can not be stacked because it returns a class instance object instead 
#        of a function that the next decorator will be expecting!
#class TimeThis(object):
#    """ Usage: apply the @TimeThis decorator to any function or method that needs to be timed. """
#    level = 0
#    def __init__(self, func):
#        self.__func = func
#        self.__name = func.__name__ + "()"
#        if hasattr(func, "im_class"):
#            self.__className = func.im_class.__name__
#        else:
#            self.__className = func.__module__
#        self.__callCount = 0
#    
#    def __call__(self, *args, **kargs):
#        gTime.start(self.__className, self.__name)
#        try:
#            return self.__func(*args, **kargs)
#        finally:
#            gTime.stop(self.__className, self.__name)


global gTime
gTime = NullGTime()
gTime = GTime()

class DecorateAllPublicMethods(object):
    def __init__(self, klass, decorator, methodFilter=None):
        if not inspect.isclass(klass):
            raise Exception("the klass argument must be set to a class!")
        self.klass = klass
        self.klassName = klass.__name__
        #print "className='%s'" % self.klassName
        #for name, x in self.publicMethods:
        #    print "  " + name
        self.decorator = decorator
        if methodFilter is None:
            self.__methodFilter = self.__isPublic
        else:
            self.__methodFilter = methodFilter
        self.publicMethods = self.__getAllPublicMethods()
        self.__decorateMethods()
    
    def __getAllPublicMethods(self):
        members = inspect.getmembers(self.klass)
        # inspect.ismethod() will accept methods and classmethods only
        methods = [m for m in members if inspect.ismethod(m[1])]
        publicMethods = [m for m in methods if self.__methodFilter(m[0], m[1])]
        return publicMethods
    
    def __isPublic(self, methodName, method):
        return methodName=="__init__" or not methodName.startswith("_")
    
    def __decorateMethods(self):
        for name, method in self.publicMethods:
            try:
                decorator = self.decorator(method)
            except Exception, e:
                print "-ERROR: methodName='%s' - %s" % (name, str(e))
            try:
                #print method.__name__
                self.klass.__dict__[name] = decorator
            except:
                # Properties
                #print "??? name='%s'" % (name)
                s = "self.klass.%s = decorator" % name
                exec s
                


def timeClass(klass, includePrivateMethods=False):
    #print "*** timeClass('%s') ***" % klass.__name__
    test = False
    if klass.__name__=="svnRep":
        test = True
    def methodFilter(methodName, method):
        r = methodName=="__init__" or not methodName.startswith("_")
        if hasattr(method, "timeThis"):
            r = bool(method.timeThis)
        #if r==True and test==True:
        #    print "  ", methodName
        return r
    def methodFilterIncludePrivate(methodName, method):
        return True
    if includePrivateMethods:
        methodFilter = methodFilterIncludePrivate
    klass._TimedClass_ = True
    x = DecorateAllPublicMethods(klass, gTime.timeThis, methodFilter)
    return x





