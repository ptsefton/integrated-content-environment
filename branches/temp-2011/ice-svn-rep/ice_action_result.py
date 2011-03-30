#!/usr/bin/env python
#    Copyright (C) 2008  Distance and e-Learning Centre, 
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
import traceback


class ActionResults(object):
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
    def __init__(self, mainAction, info={}):
        # info={"args":[], "kwargs":{}, "name":"ObjectClassName.MethodName"}
        self.__mainAction = mainAction
        self.__info = info
        self.__actions = []
        self.__isWarning = False
        self.__isError = False
    
    @property
    def mainAction(self):
        return self.__mainAction
    
    @property
    def info(self):
        return self.__info
    
    @property
    def actions(self):
        return self.__actions
    
    @property
    def count(self):
        return len(self.__actions)
    
    @property
    def isWarning(self):
        return self.__isWarning
    
    @property
    def isError(self):
        return self.__isError
    
    @property
    def isAllOK(self):
        return not (self.__isWarning or self.__isError)
    
    def addAction(self, action, resultMessage="", exception=None,
                isWarning=False, info={}):
        if isinstance(action, ActionResult) or isinstance(action, ActionResults):
            actionResult = action
        else:
            actionResult = ActionResult(action, resultMessage, exception,
                    isWarning, info)
        if actionResult.isWarning:
            self.__isWarning = True
        if actionResult.isError:
            self.__isError = True
        self.__actions.append(actionResult)
    
    
    def removeAction(self, action):
        self.__actions.remove(action)
        self.__isWarning = False
        self.__isError = False
        for a in self.__actions:
            self.__isWarning |= a.isWarning
            self.__isError |= a.isError
    
    
    def summary(self):
        if self.isAllOK:
            return "Completed OK"
        elif self.isError:
            return "ERROR: Unable to complete (see Details)"  # some errors encountered
        elif self.isWarning:
            return "Completed with warnings!"
    
    def message(self):
        s = "%s\n" % self.__mainAction
        for action in self.__actions:
            s += "  " + action.message()
        return s
    
    def fullInfo(self, all=True):
        s = "%s\n" % self.__mainAction
        if all:
            s = "Results for '%s'\n" % self.__mainAction
        for action in self.__actions:
            s += "  " + action.fullInfo(all).replace("\n", "\n  ")
        return s
    
    def __str__(self):
        s = "Results for '%s'\n" % self.__mainAction
        for action in self.__actions:
            s += "  " + str(action).replace("\n", "\n  ") + "\n"
        return s
    


class ActionResult(object):
    
    # Constructor
    #   __init__(action, resultMessage="", exception=None, 
    #                isWarning=False, info={})
    # Properties
    #   action
    #   resultMessage
    #   isWarning
    #   isError
    #   exceptionMessage
    #   exceptionStackTrace
    #   info
    # Methods
    #   fullInfo(all=True)
    #   __str__()
    
    def __init__(self, action, resultMessage="", exception=None, 
                isWarning=False, info={}):
        self.__action = action
        self.__message = resultMessage
        self.__isWarning = isWarning
        self.__exceptionMsg = None
        self.__exceptionStackTrace = ""
        if exception is not None:
            self.__exceptionMsg = str(exception)
            if self.__message=="":
                self.__message = self.__exceptionMsg
            if isinstance(exception, Exception):
                self.__exceptionStackTrace = self.__formattedTraceback(5) + "\n"
        if self.__message=="":
            if self.__isWarning:
                self.__message = "?"
            else:
                self.__message = "ok"
        self.__info = info
    
    @property
    def action(self):
        return self.__action
    
    @property
    def resultMessage(self):
        return self.__message
    
    @property
    def isWarning(self):
        return self.__isWarning
    
    @property
    def isError(self):
        return self.__exceptionMsg!=None
    
    @property
    def exceptionMessage(self):
        return self.__exceptionMsg
    
    @property
    def exceptionStackTrace(self):
        return self.__exceptionStackTrace
    
    @property
    def info(self):
        return self.__info
    
    def fullInfo(self, all=True):
        """ stackTrace (if any) and all info data """
        m = ""
        if all:
            m = str(self) + "\n"
        if self.__exceptionStackTrace!="":
            m += " " + self.__exceptionStackTrace
        keys = self.__info.keys()
        keys.sort()
        for key in keys:
            m += " '%s' - '%s'" % (key, self.__info[key])
        return m
    
    def message(self):
        if self.isWarning:
            s = "Warning: %s - %s" % (self.__action, self.__message)
        elif self.isError:
            s = "Error: %s - %s - %s" % (self.__action, self.__message, self.__exceptionMsg)
        else:
            s = "%s - %s" % (self.__action, self.__message)
        return s
    
    def __str__(self):
        m = ""
        if self.__info!={} and self.__message!="ok":
            m = " (has info)"
        if self.__message!="":
            m = (" -> '%s'" + m) % self.__message
        if self.__exceptionMsg is not None:
            m += "\n  Exception='%s'" % self.__exceptionMsg
        m = "%s%s" % (self.__action, m)
        if self.isError:
            m  = "Error: " + m 
        elif self.isWarning:
            m  = "Warning: " + m
        return m
    
    def __formattedTraceback(self, lines=0):
        errLines = traceback.format_tb(sys.exc_traceback)
        return "\n".join(errLines[-lines:])












