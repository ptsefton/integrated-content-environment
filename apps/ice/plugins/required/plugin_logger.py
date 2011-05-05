
#    Copyright (C) 2009  Distance and e-Learning Centre,
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

from logging import setLoggerClass, getLogger, shutdown, addLevelName
from logging import Handler, DEBUG, Logger, Formatter

import os
import re

pluginName = "ice.logger"
pluginDesc = "Logger"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = getIceLogger
    pluginClass = PLogger
    pluginInitialized = True
    return pluginFunc


class PLogger(object):
    def __init__(self, iceContext):
        self.iceContext = iceContext

    def getLogger(self, logPath, logLevel):
        return getIceLogger(logPath, logLevel)



class IcePrintHandler(Handler):
    def __init__(self):
        Handler.__init__(self)
        self.setFormatter(Formatter("%(levelname)s -  \t%(message)s"))
        self.setLevel(2)

    def emit(self, record):
        print self.format(record)


class IceRotatingFileHandler(Handler):
    def __init__(self, fileName, maxBytes=60*1024, level=DEBUG):
        Handler.__init__(self, level)
        path, fileName = os.path.split(fileName)
        if path=="":
            path = "."
        self.path = path
        self.maxBytes = maxBytes
        # Default formatter for this handler. NOTE: can be overriden!
        self.setFormatter(Formatter("%(asctime)s %(levelname)s -  \t%(message)s"))

        self.name, self.ext = os.path.splitext(fileName)
        self.re = re.compile("^" + re.escape(self.name) + "(\d+)" + re.escape(self.ext) + "$")
        self.fileName = self.getCurrentFileName()
        self.__openFile()


    def getCurrentFileName(self):
        n = self.__getCurrentHighestNumber()
        return self.name + str(n) + self.ext

    def getNextFileName(self):
        n = self.__getCurrentHighestNumber()
        return self.name + str(n+1) + self.ext

    def __openFile(self):
        self.f = open(os.path.join(self.path, self.fileName), "a")

    def __getCurrentHighestNumber(self):
        l = os.listdir(self.path)
        l = [self.__getNumber(item) for item in l]
        l.append(1)
        return max(l)


    def __getNumber(self, fileName):
        m = self.re.match(fileName)
        if m==None:
            return 0
        else:
            return int(m.group(1))

    def doRollover(self):
        try:
            self.f.close()
            self.fileName = self.getNextFileName()
            self.__openFile()
        except:
            pass

    def close(self):
        try:
            self.f.close()
        except:
            pass

    def flush(self):
        try:
            self.f.flush()
        except:
            pass

    def emit(self, record):
        s = self.format(record)
        try:
            self.f.write(s + "\n")
            if self.f.tell()>self.maxBytes:
                self.doRollover()
        except:
            pass

    # Note: call order (in Handler)
    #  handle(record)
    #  filter(record) - if returns None - then processing stops here
    #  acquire()
    #  emit(record) -> write(format(record))
    #  release()

    # LogRecord object properties
    # 'args', 'created', 'exc_info', 'filename', 'getMessage', 'levelname', 'levelno', 'lineno', 'module',
    #    'msecs', 'msg', 'name', 'pathname', 'process', 'relativeCreated', 'thread'


class IceLogger(Logger):
    def iceInfo(self, msg, *args):
        self.log(25, msg % args)
    def iceWarning(self, msg, *args):
        self.log(50, msg % args)
    def iceError(self, msg, *args):
        self.log(100, msg % agrs)
    def flush(self):
        for h in self.handlers:
            h.flush()
setLoggerClass(IceLogger)


def getIceLogger(usersProfileDir, logLevel):
    logger = getLogger("ice")

    # logger methods
    #  debug(msg), info(msg). warning(msg), error(msg), critical(msg)
    #  exception(msg) - ERROR level
    #  log(levelNum, msg)
    #  addFilter(filter), removeFilter(filter)
    #  makeRecord(name, lvl, fn, lno, msg, args, exc_info)
    #  NOTE: to add a custom filter simple create a class that implements a filter(self, record) method and
    #    return record or None for filtered out records

    # logging methods
    #  shutdown()
    #  addLevelName(levelno, name)

    if logger.handlers==[]:
        #logHandler = RotatingFileHandler("./ice.log", "a", maxBytes=100*1024, backupCount=99) #Not in version 2.3.5!
        path = "."
        path = usersProfileDir
        logHandler = IceRotatingFileHandler(os.path.join(path, "ice.log"))
        logFormatter = Formatter("%(asctime)s %(levelname)s -  \t%(message)s")
        logHandler.setFormatter(logFormatter)
        logger.addHandler(logHandler)
        logger.addHandler(IcePrintHandler())

        logger.setLevel(int(logLevel))
        #logger.setLevel(DEBUG)
        logger.shutdown = shutdown
        addLevelName(25, "IceInfo")
        addLevelName(50, "IceWarning")
        addLevelName(100, "IceError")

    return logger


# Usage:
#    logger.log(levelno, msg)
#    logger.debug(msg)
#    logger.iceInfo(msg)
#



