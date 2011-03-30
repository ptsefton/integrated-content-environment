#
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

""" Module for ICE common constants and methods. """

import os
import sys
import string
import types
import time
import traceback
import inspect              # getmembers
from hashlib import md5
import random
from sys import path as sysPath
import gzip
from cStringIO import StringIO
Set = set
from cPickle import dumps, loads, HIGHEST_PROTOCOL
import urllib
import urlparse
from socket import gethostname, gethostbyname_ex
import threading
import copy
try:
    import Image
except Exception, e:
    print "*** %s" % str(e)
    Image = None


# Hack: to fix problem with py2exe (on windows) dll search order
zipLibFile = sys.path[-1]
sys.path.insert(0, zipLibFile)
# End of hack

# XML ElementTree
enableCElementTree = False
ElementTree = None
cElementTree = None
if ElementTree is None:
    try:
        from xml.etree import ElementTree as ElementTree
    except ImportError:
        try:
            import ElementTree as ElementTree
        except ImportError:
            try:
                from elementtree import ElementTree
            except ImportError:
                print "Error loading ElementTree! Please install and try again."
                sys.exit(1)
pyElementTree = ElementTree
try:
    from xml.etree import cElementTree as cElementTree
except ImportError:
    try:
        import cElementTree as cElementTree
    except ImportError:
        cElementTree = None
if enableCElementTree and cElementTree is not None:
    ElementTree = cElementTree
# NOTE: ElementTree.__name__ will tell you which element tree is being used.

#if len(sys.argv)>0:
#    try:
#        c = sys.argv[0]
#        path = c.rsplit("/", 1)[0]
#        if path is not None and path.startswith("/"):
#            os.chdir(path)
#    except: pass

sysPath.append("../utils")
sysPath.append("../ice-svn-rep")
sysPath.append("../sitemap")
sysPath.append("../ice")
sysPath.append("../html")
sysPath.append("../ice-template")
sysPath.append("../converter")
sysPath.append("bin")

try:
    import json     # by default try and using python's json module (2.6 & 3.0)
    jsonWrite = json.JSONEndoder().encode
    jsonRead = json.JSONDecoder().decode
except:
    # else for python 2.5 use json_py2p5.py module
    sysPath.insert(1, "../utils")
    from json_py2p5 import write as jsonWrite, read as jsonRead

from unittest import TestCase
try:
    from xml_diff import XmlTestCase        # self.assertSameXml
except Exception, e:
    print "*** xml_diff - %s" % str(e)
    XmlTestCase = None
try:
    import xml_util
except Exception, e:
    print "*** xml_util - %s" % str(e)
    class Object(object): pass
    xml_util = Object()
    xml_util.xml = None

from file_system import FileSystem, ZipString
from system import System, system
from thread_util import WorkerThread, JobObject, RLock

# Repository
from ice_reps import IceRepositories
from ice_rep2 import IceRepository
#from ice_proxy_rep import IceProxyRepository
#from svn_rep import SvnRep, ListItem, ItemStatus
#from svn_proxy_rep import SvnProxyRep
from ice_rep_indexer import DummyRepositoryIndexer  # , RepositoryIndexer
from ice_action_result import ActionResults, ActionResult

# Core
from ice_site import IceSite                    #
from node_mapper import NodeMapper
from ice_site_render import IceSiteRender
from ice_template import IceTemplateInfo
from htmlTemplate import HtmlTemplate

from ice_api import IceServices                 ###########

####
#from ice_image import IceImage
#import converted_data
#from mime_types import mimeTypes as MimeTypes
####

from html_cleanup import HtmlCleanup
from http_util import Http
    # Methods:
    #   get(url, queryString="", includeExtraResults=False)
    #       -> returns the result as a string or if includeExtraResult==True
    #           returns a tuple of (results, errCode, errMsg)
    #   post(url, formDataList)
    #          formDataList is a list/(sequence) of (formName, formData) pairs for normal form fields, or
    #          (formName, fileType) or (formName, (filename, fileData)) for a file upload form element.
    #        -> return the server response data


progName = sys.argv[0]
progPath = os.path.split(progName)[0]
workingDirectory = os.getcwd()
#if progPath!="":
#    os.chdir(progPath)
#if os.getcwd().replace("\\","/").endswith("/bin"):
#    os.chdir("..")

fileSystem = FileSystem()       # After chdir fixup
fs = fileSystem


import code_timing
#from code_timing import gTime, TimeThis
from code_timing import *
#import ice_logger



class IceException(Exception): pass

class IceCancelException(IceException): pass

class EditBookException(Exception):
    def __init__(self, msg, file, path):
        Exception.__init__(self, msg)
        self.file = file
        self.path = path

class AjaxException(Exception): pass

class UnknownMimeTypeError(Exception): pass

class NoSiteDataException(Exception): pass

class RedirectException(Exception):
    def __init__(self, redirectUrl):
        self.redirectUrl = redirectUrl


class Object(object): pass


class DictionaryObject(dict):
    def __init__(self, seqOrMapping=None, defaultValue=None, *args, **kwargs):
        self.__defaultValue = defaultValue
        if seqOrMapping is not None:
            args.insert(seqOrMapping)
        dict.__init__(self, *args, **kwargs)
    
    def __getitem__(self, name):
        return dict.get(self, name, self.__defaultValue)


class SortedDictionary(dict):
    # override the following:
    def __init__(self, *args):
        dict.__init__(self, *args)
        self.__sortedKeys = []
        self.__sorted = False
        self.__sortByValueProp = None   # default sort by keys
    
    def setSortByValueProperty(self, propertyName):
        self.__sortByValueProp = propertyName
    
    # update methods
    def __delitem__(self, key):
        dict.__delitem__(key)
        del self.__sortedKeys[key]
    
    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
        self.__sorted = False
    
    def update(self, *args):
        dict.update(self, *args)
        self.__sorted = False
    
    def popitem(self):
        self.__sorted = False
        return dict.popitem(self)
    
    def pop(self, key):
        self.__sorted = False
        return dict.pop(self)
    
    #Access methods
    def items(self):
        if not self.__sorted: self.__sort()
        items = []
        for key in self.__sortedKeys:
            items.append((key, self[key]))
        return items
    
    def keys(self):
        if not self.__sorted: self.__sort()
        return self.__sortedKeys
    
    def values(self):
        if not self.__sorted: self.__sort()
        values = []
        for key in self.__sortedKeys:
            values.append(self[key])
        return values
    
    def iteritems(self):
        if not self.__sorted: self.__sort()
        for key in self.__sortedKeys:
            yield (key, self[key])
    
    def iterkeys(self):
        if not self.__sorted: self.__sort()
        for key in self.__sortedKeys:
            yield (key)
    
    def itervalues(self):
        if not self.__sorted: self.__sort()
        for key in self.__sortedKeys:
            yield self[key]
    
    def __iter__(self):
        return self.iterkeys()
    
    def __sort(self):
        if self.__sorted: return
        if self.__sortByValueProp is None:
            # sort by keys
            self.__sortedKeys = dict.keys(self)
            self.__sortedKeys.sort()
        else:
            # sort by value.property
            # if object does not hasattr(obj, name) then not in the collection
            sortList = []
            sortProp = self.__sortByValueProp
            for key, obj in dict.items(self):
                if hasattr(obj, sortProp):
                    prop = getattr(obj, sortProp)
                    sortList.append( (prop, key) )
            sortList.sort()
            self.__sortedKeys = [i[1] for i in sortList]
        self.__sorted = True


class Tags(object):
    @staticmethod
    def getAddedDeleted(orgTags, newTags):
        orgSet = set(orgTags)
        newSet = set(newTags)
        addedTags = list(newSet.difference(orgSet))
        deletedTags = list(orgSet.difference(newSet))
        return addedTags, deletedTags
    
    @staticmethod
    def normCase(tags, normList):
        d = dict(zip([i.lower() for i in tags], tags))
        norm = dict(zip([i.lower() for i in normList], normList))
        for key in d.keys():
            if norm.has_key(key):
                d[key] = norm[key]
        tags = d.values()
        tags.sort()
        return tags
    
    @staticmethod
    def merge(tags, updateList):
        d = dict(zip([i.lower() for i in tags], tags))
        update = dict(zip([i.lower() for i in updateList], updateList))
        d.update(update)
        tags = d.values()
        tags.sort()
        return tags
    
    @staticmethod
    def remove(tags, removeTags):
        d = dict(zip([i.lower() for i in tags], tags))
        for tag in removeTags:
            tag = tag.lower()
            if d.has_key(tag):
                d.pop(tag)
        tags = d.values()
        tags.sort()
        return tags


class GetCallerInfo(object):
    def __init__(self, frame=2):
        if type(frame) is types.IntType:
            self.f = sys._getframe(frame)
        elif type(frame) is types.FrameType:
            self.f = frame
        else:
            raise Exception("The frame argument is of an invalid type!")
        self.code = self.f.f_code
        self.name = self.code.co_name
        self.filename = self.code.co_filename
        self.lineNumber = self.code.co_firstlineno
        args = inspect.getargvalues(self.f)
        # args = (listOfNamedArguments, *ArgName, **ArgName, DictionaryOfLocals)
        self._args = args
        self.args = None
        self.kwargs = None
        self.argClass = None
        self.arg1 = None
        self.arg1Name = None
        if args[1] is not None:
            self.args = args[3][args[1]]
        if args[2] is not None:
            self.kwargs = args[3][args[2]]
        if len(args[0])>0:
            self.arg1Name = args[0][0]
            self.arg1 = args[3][self.arg1Name]
            self.arg1Type = type(self.arg1)
        elif args[1] is not None:
            self.arg1Name="*" + args[1]
            if len(self.args)>0:
                self.arg1 = self.args[0]
                self.arg1Type = type(self.arg1)
    
    @property
    def callerInfo(self):
        b = self.f.f_back
        if b is not None:
            return GetCallerInfo(b)

    def __str__(self):
        args = ""
        for a in self._args[0]:
            args += ", " + a
        if self._args[1] is not None:
            args += ", *" + self._args[1]
        if self._args[2] is not None:
            args += ", **" + self._args[2]
        if len(args)>1:
            args = args[2:]
        s = "Function: %s(%s)" % (self.name, args)
        if self.arg1Name=="self" and hasattr(self.arg1, "__class__"):
            className = self.arg1.__class__.__name__
            s = "Method: %s.%s(%s)" % (className, self.name, args)
        s += "  Module: %s, LineNumber: %s" % (self.filename, self.lineNumber)
        return s


class ThreadLogWriter(object):
    sysStdout = sys.stdout
    sysStderr = sys.stderr
    def __init__(self):
        self.__threadWrites = {}
        self.defaultLogWriter = None
        #self.__rLock = RLock()
    def setThreadLogWriter(self, threadName, logWriter):
        self.__threadWrites[threadName] = logWriter
    def write(self, data):
        if data!="\n":
            threadName = threading.currentThread().getName()
            logWriter = self.__threadWrites.get(threadName, None)
            if logWriter is not None:
                logWriter.write(data)
            elif self.defaultLogWriter is not None:
                self.defaultLogWriter.write(data)
        ThreadLogWriter.sysStdout.write(data)
    def writeln(self, data, args=()):
        self.write((data % args) + "\n")
    def flush(self):
        ThreadLogWriter.sysStdout.flush()
        ThreadLogWriter.sysStderr.flush()


class LogWriter(object):
    class WData(object):
        def __init__(self, data):
            self.time = time.time()
            self.data = data
        @property
        def timeStr(self):
            uS = int(self.time % 1 * 1000000)
            t = time.strftime("%H:%M:%S ", time.localtime(self.time))
            return t + str(uS).rjust(6, "0")
        def __str__(self):
            return self.timeStr + "  " + self.data
    def __init__(self):
        self.__max = 50
        self.__pos = 0
        self.__buffer = []
    
    def write(self, data):
        l = len(self.__buffer)
        oData = self.WData(data)
        if l< self.__max:
            self.__buffer.append(oData)
        else:
            self.__buffer[self.__pos] = oData
        self.__pos += 1
        if self.__pos>=self.__max:
            self.__pos = 0
    
    @property
    def lines(self):
        return self.getLines()
    
    def getLines(self):
        l = []
        for i in self.__getRange():
            l.append(self.__buffer[i])
        return l
    
    def __getRange(self):
        l = len(self.__buffer)
        return range(self.__pos, l) + range(0, self.__pos)



# @Decorator
def tryXTimes(x=None):
    if x is None or callable(x):
        raise Exception("the @tryXTimes(num) decorator requires a number argument!")
    def tryX(func):
        def wrapper(*args, **kargs):
            for c in range(x):
                try:
                    return func(*args, **kargs)
                except:
                    if c==(x-1):
                        raise
        wrapper.__name__ = func.__name__
        wrapper.__dict__ = func.__dict__
        wrapper.__doc__ = func.__doc__
        return wrapper
    return tryX

def try3Times(func):
    return tryXTimes(3)(func)


class IceCommon(object):
    random.seed(time.time())
    
    # Constants
    OOoNS = {
                "office":"urn:oasis:names:tc:opendocument:xmlns:office:1.0",
                "style":"urn:oasis:names:tc:opendocument:xmlns:style:1.0",
                "text":"urn:oasis:names:tc:opendocument:xmlns:text:1.0",
                "table":"urn:oasis:names:tc:opendocument:xmlns:table:1.0",
                "draw":"urn:oasis:names:tc:opendocument:xmlns:drawing:1.0",
                "fo":"urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0",
                "xlink":"http://www.w3.org/1999/xlink",
                "dc":"http://purl.org/dc/elements/1.1/",
                "meta":"urn:oasis:names:tc:opendocument:xmlns:meta:1.0",
                "number":"urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0",
                "svg":"urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0",
                "chart":"urn:oasis:names:tc:opendocument:xmlns:chart:1.0",
                "dr3d":"urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0",
                "math":"http://www.w3.org/1998/Math/MathML",
                "form":"urn:oasis:names:tc:opendocument:xmlns:form:1.0",
                "script":"urn:oasis:names:tc:opendocument:xmlns:script:1.0",
                "ooo":"http://openoffice.org/2004/office",
                "ooow":"http://openoffice.org/2004/writer",
                "oooc":"http://openoffice.org/2004/calc",
                "dom":"http://www.w3.org/2001/xml-events",
                "xforms":"http://www.w3.org/2002/xforms",
                "xsd":"http://www.w3.org/2001/XMLSchema",
                "xsi":"http://www.w3.org/2001/XMLSchema-instance",
            }
    OOoNSList = OOoNS.items()
    xml_entites = {  "&lt;": u"\u003c", "&gt;": u"\u003e",
                     "&quot;": u"\u0022", "&apos;": u"\u0027", "&amp;": u"\u0026" }
    xhtml_entities = { 
                   "&zwnj;" : u"\u200c", "&aring;" : u"\u00e5",
                   "&yen;" : u"\u00a5", "&ograve;" : u"\u00f2", "&Chi;" : u"\u03a7",
                   "&delta;" : u"\u03b4", "&rang;" : u"\u232a", "&sup;" : u"\u2283",
                   "&trade;" : u"\u2122", "&Ntilde;" : u"\u00d1", "&xi;" : u"\u03be",
                   "&upsih;" : u"\u03d2", "&nbsp;" : u"\u00a0", "&Atilde;" : u"\u00c3",
                   "&radic;" : u"\u221a", "&otimes;" : u"\u2297", "&nabla;" : u"\u2207",
                   "&aelig;" : u"\u00e6", "&oelig;" : u"\u0153", "&equiv;" : u"\u2261",
                   "&lArr;" : u"\u21d0", "&infin;" : u"\u221e", "&Psi;" : u"\u03a8",
                   "&auml;" : u"\u00e4", "&circ;" : u"\u02c6", "&Epsilon;" : u"\u0395",
                   "&otilde;" : u"\u00f5", "&Icirc;" : u"\u00ce", "&Eacute;" : u"\u00c9",
                   "&ndash;" : u"\u2013", "&sbquo;" : u"\u201a", "&Prime;" : u"\u2033",
                   "&prime;" : u"\u2032", "&psi;" : u"\u03c8", "&Kappa;" : u"\u039a",
                   "&rsaquo;" : u"\u203a", "&Tau;" : u"\u03a4", "&uacute;" : u"\u00fa",
                   "&ocirc;" : u"\u00f4", "&lrm;" : u"\u200e", "&lceil;" : u"\u2308",
                   "&cedil;" : u"\u00b8", "&Alpha;" : u"\u0391", "&not;" : u"\u00ac",
                   "&Dagger;" : u"\u2021", "&AElig;" : u"\u00c6", "&ni;" : u"\u220b",
                   "&oslash;" : u"\u00f8", "&acute;" : u"\u00b4", "&zwj;" : u"\u200d",
                   "&alefsym;" : u"\u2135", "&laquo;" : u"\u00ab", "&shy;" : u"\u00ad",
                   "&rdquo;" : u"\u201d", "&ge;" : u"\u2265", "&Igrave;" : u"\u00cc",
                   "&nu;" : u"\u03bd", "&Ograve;" : u"\u00d2", "&lsaquo;" : u"\u2039",
                   "&sube;" : u"\u2286", "&rarr;" : u"\u2192", "&sdot;" : u"\u22c5",
                   "&supe;" : u"\u2287", "&Yacute;" : u"\u00dd", "&lfloor;" : u"\u230a",
                   "&rlm;" : u"\u200f", "&Auml;" : u"\u00c4", "&brvbar;" : u"\u00a6",
                   "&Otilde;" : u"\u00d5", "&szlig;" : u"\u00df", "&clubs;" : u"\u2663",
                   "&diams;" : u"\u2666", "&agrave;" : u"\u00e0", "&Ocirc;" : u"\u00d4",
                   "&Iota;" : u"\u0399", "&Theta;" : u"\u0398", "&Pi;" : u"\u03a0",
                   "&OElig;" : u"\u0152", "&Scaron;" : u"\u0160", "&frac14;" : u"\u00bc",
                   "&egrave;" : u"\u00e8", "&sub;" : u"\u2282", "&iexcl;" : u"\u00a1",
                   "&frac12;" : u"\u00bd", "&ordf;" : u"\u00aa", "&sum;" : u"\u2211",
                   "&prop;" : u"\u221d", "&Uuml;" : u"\u00dc", "&ntilde;" : u"\u00f1",
                   "&atilde;" : u"\u00e3", "&asymp;" : u"\u2248", "&uml;" : u"\u00a8",
                   "&prod;" : u"\u220f", "&nsub;" : u"\u2284", "&reg;" : u"\u00ae",
                   "&rArr;" : u"\u21d2", "&Oslash;" : u"\u00d8", "&THORN;" : u"\u00de",
                   "&yuml;" : u"\u00ff", "&aacute;" : u"\u00e1", "&Mu;" : u"\u039c",
                   "&hArr;" : u"\u21d4", "&le;" : u"\u2264", "&thinsp;" : u"\u2009",
                   "&dArr;" : u"\u21d3", "&ecirc;" : u"\u00ea", "&bdquo;" : u"\u201e",
                   "&Sigma;" : u"\u03a3", "&kappa;" : u"\u03ba", "&Aring;" : u"\u00c5",
                   "&tilde;" : u"\u02dc", "&emsp;" : u"\u2003", "&mdash;" : u"\u2014",
                   "&uarr;" : u"\u2191", "&times;" : u"\u00d7", "&Ugrave;" : u"\u00d9",
                   "&Eta;" : u"\u0397", "&Agrave;" : u"\u00c0", "&chi;" : u"\u03c7",
                   "&real;" : u"\u211c", "&eth;" : u"\u00f0", "&rceil;" : u"\u2309",
                   "&iuml;" : u"\u00ef", "&gamma;" : u"\u03b3", "&lambda;" : u"\u03bb",
                   "&harr;" : u"\u2194", "&Egrave;" : u"\u00c8", "&frac34;" : u"\u00be",
                   "&dagger;" : u"\u2020", "&divide;" : u"\u00f7", "&Ouml;" : u"\u00d6",
                   "&image;" : u"\u2111", "&hellip;" : u"\u2026", "&igrave;" : u"\u00ec",
                   "&Yuml;" : u"\u0178", "&ang;" : u"\u2220", "&alpha;" : u"\u03b1",
                   "&frasl;" : u"\u2044", "&ETH;" : u"\u00d0", "&lowast;" : u"\u2217",
                   "&Nu;" : u"\u039d", "&plusmn;" : u"\u00b1", "&bull;" : u"\u2022",
                   "&sup1;" : u"\u00b9", "&sup2;" : u"\u00b2", "&sup3;" : u"\u00b3",
                   "&Aacute;" : u"\u00c1", "&cent;" : u"\u00a2", "&oline;" : u"\u203e",
                   "&Beta;" : u"\u0392", "&perp;" : u"\u22a5", "&Delta;" : u"\u0394",
                   "&there4;" : u"\u2234", "&pi;" : u"\u03c0", "&iota;" : u"\u03b9",
                   "&scaron;" : u"\u0161", "&euml;" : u"\u00eb", "&notin;" : u"\u2209",
                   "&iacute;" : u"\u00ed", "&para;" : u"\u00b6", "&epsilon;" : u"\u03b5",
                   "&weierp;" : u"\u2118", "&uuml;" : u"\u00fc", "&larr;" : u"\u2190",
                   "&icirc;" : u"\u00ee", "&Upsilon;" : u"\u03a5", "&omicron;" : u"\u03bf",
                   "&upsilon;" : u"\u03c5", "&copy;" : u"\u00a9", "&Iuml;" : u"\u00cf",
                   "&Oacute;" : u"\u00d3", "&Xi;" : u"\u039e", "&ensp;" : u"\u2002",
                   "&ccedil;" : u"\u00e7", "&Ucirc;" : u"\u00db", "&cap;" : u"\u2229",
                   "&mu;" : u"\u03bc", "&empty;" : u"\u2205", "&lsquo;" : u"\u2018",
                   "&isin;" : u"\u2208", "&Zeta;" : u"\u0396", "&minus;" : u"\u2212",
                   "&loz;" : u"\u25ca", "&deg;" : u"\u00b0", "&and;" : u"\u2227",
                   "&tau;" : u"\u03c4", "&pound;" : u"\u00a3", "&curren;" : u"\u00a4",
                   "&int;" : u"\u222b", "&ucirc;" : u"\u00fb", "&rfloor;" : u"\u230b",
                   "&crarr;" : u"\u21b5", "&ugrave;" : u"\u00f9", "&exist;" : u"\u2203",
                   "&cong;" : u"\u2245", "&theta;" : u"\u03b8", "&oplus;" : u"\u2295",
                   "&permil;" : u"\u2030", "&Acirc;" : u"\u00c2", "&piv;" : u"\u03d6",
                   "&Euml;" : u"\u00cb", "&Phi;" : u"\u03a6", "&Iacute;" : u"\u00cd",
                   "&Uacute;" : u"\u00da", "&Omicron;" : u"\u039f", "&ne;" : u"\u2260",
                   "&iquest;" : u"\u00bf", "&eta;" : u"\u03b7", "&yacute;" : u"\u00fd",
                   "&Rho;" : u"\u03a1", "&darr;" : u"\u2193", "&Ecirc;" : u"\u00ca",
                   "&zeta;" : u"\u03b6", "&Omega;" : u"\u03a9", "&acirc;" : u"\u00e2",
                   "&sim;" : u"\u223c", "&phi;" : u"\u03c6", "&sigmaf;" : u"\u03c2",
                   "&macr;" : u"\u00af", "&thetasym;" : u"\u03d1", "&Ccedil;" : u"\u00c7",
                   "&ordm;" : u"\u00ba", "&uArr;" : u"\u21d1", "&forall;" : u"\u2200",
                   "&beta;" : u"\u03b2", "&fnof;" : u"\u0192", "&cup;" : u"\u222a",
                   "&rho;" : u"\u03c1", "&micro;" : u"\u00b5", "&eacute;" : u"\u00e9",
                   "&omega;" : u"\u03c9", "&middot;" : u"\u00b7", "&Gamma;" : u"\u0393",
                   "&euro;" : u"\u20ac", "&lang;" : u"\u2329", "&spades;" : u"\u2660",
                   "&rsquo;" : u"\u2019", "&thorn;" : u"\u00fe", "&ouml;" : u"\u00f6",
                   "&or;" : u"\u2228", "&raquo;" : u"\u00bb", "&Lambda;" : u"\u039b",
                   "&part;" : u"\u2202", "&sect;" : u"\u00a7", "&ldquo;" : u"\u201c",
                   "&hearts;" : u"\u2665", "&sigma;" : u"\u03c3", "&oacute;" : u"\u00f3" }
    crc32Table = (
        0x00000000,0x77073096,0xEE0E612C,0x990951BA,0x076DC419,0x706AF48F,0xE963A535,0x9E6495A3,
        0x0EDB8832,0x79DCB8A4,0xE0D5E91E,0x97D2D988,0x09B64C2B,0x7EB17CBD,0xE7B82D07,0x90BF1D91,
        0x1DB71064,0x6AB020F2,0xF3B97148,0x84BE41DE,0x1ADAD47D,0x6DDDE4EB,0xF4D4B551,0x83D385C7,
        0x136C9856,0x646BA8C0,0xFD62F97A,0x8A65C9EC,0x14015C4F,0x63066CD9,0xFA0F3D63,0x8D080DF5,
        0x3B6E20C8,0x4C69105E,0xD56041E4,0xA2677172,0x3C03E4D1,0x4B04D447,0xD20D85FD,0xA50AB56B,
        0x35B5A8FA,0x42B2986C,0xDBBBC9D6,0xACBCF940,0x32D86CE3,0x45DF5C75,0xDCD60DCF,0xABD13D59,
        0x26D930AC,0x51DE003A,0xC8D75180,0xBFD06116,0x21B4F4B5,0x56B3C423,0xCFBA9599,0xB8BDA50F,
        0x2802B89E,0x5F058808,0xC60CD9B2,0xB10BE924,0x2F6F7C87,0x58684C11,0xC1611DAB,0xB6662D3D,
        0x76DC4190,0x01DB7106,0x98D220BC,0xEFD5102A,0x71B18589,0x06B6B51F,0x9FBFE4A5,0xE8B8D433,
        0x7807C9A2,0x0F00F934,0x9609A88E,0xE10E9818,0x7F6A0DBB,0x086D3D2D,0x91646C97,0xE6635C01,
        0x6B6B51F4,0x1C6C6162,0x856530D8,0xF262004E,0x6C0695ED,0x1B01A57B,0x8208F4C1,0xF50FC457,
        0x65B0D9C6,0x12B7E950,0x8BBEB8EA,0xFCB9887C,0x62DD1DDF,0x15DA2D49,0x8CD37CF3,0xFBD44C65,
        0x4DB26158,0x3AB551CE,0xA3BC0074,0xD4BB30E2,0x4ADFA541,0x3DD895D7,0xA4D1C46D,0xD3D6F4FB,
        0x4369E96A,0x346ED9FC,0xAD678846,0xDA60B8D0,0x44042D73,0x33031DE5,0xAA0A4C5F,0xDD0D7CC9,
        0x5005713C,0x270241AA,0xBE0B1010,0xC90C2086,0x5768B525,0x206F85B3,0xB966D409,0xCE61E49F,
        0x5EDEF90E,0x29D9C998,0xB0D09822,0xC7D7A8B4,0x59B33D17,0x2EB40D81,0xB7BD5C3B,0xC0BA6CAD,
        0xEDB88320,0x9ABFB3B6,0x03B6E20C,0x74B1D29A,0xEAD54739,0x9DD277AF,0x04DB2615,0x73DC1683,
        0xE3630B12,0x94643B84,0x0D6D6A3E,0x7A6A5AA8,0xE40ECF0B,0x9309FF9D,0x0A00AE27,0x7D079EB1,
        0xF00F9344,0x8708A3D2,0x1E01F268,0x6906C2FE,0xF762575D,0x806567CB,0x196C3671,0x6E6B06E7,
        0xFED41B76,0x89D32BE0,0x10DA7A5A,0x67DD4ACC,0xF9B9DF6F,0x8EBEEFF9,0x17B7BE43,0x60B08ED5,
        0xD6D6A3E8,0xA1D1937E,0x38D8C2C4,0x4FDFF252,0xD1BB67F1,0xA6BC5767,0x3FB506DD,0x48B2364B,
        0xD80D2BDA,0xAF0A1B4C,0x36034AF6,0x41047A60,0xDF60EFC3,0xA867DF55,0x316E8EEF,0x4669BE79,
        0xCB61B38C,0xBC66831A,0x256FD2A0,0x5268E236,0xCC0C7795,0xBB0B4703,0x220216B9,0x5505262F,
        0xC5BA3BBE,0xB2BD0B28,0x2BB45A92,0x5CB36A04,0xC2D7FFA7,0xB5D0CF31,0x2CD99E8B,0x5BDEAE1D,
        0x9B64C2B0,0xEC63F226,0x756AA39C,0x026D930A,0x9C0906A9,0xEB0E363F,0x72076785,0x05005713,
        0x95BF4A82,0xE2B87A14,0x7BB12BAE,0x0CB61B38,0x92D28E9B,0xE5D5BE0D,0x7CDCEFB7,0x0BDBDF21,
        0x86D3D2D4,0xF1D4E242,0x68DDB3F8,0x1FDA836E,0x81BE16CD,0xF6B9265B,0x6FB077E1,0x18B74777,
        0x88085AE6,0xFF0F6A70,0x66063BCA,0x11010B5C,0x8F659EFF,0xF862AE69,0x616BFFD3,0x166CCF45,
        0xA00AE278,0xD70DD2EE,0x4E048354,0x3903B3C2,0xA7672661,0xD06016F7,0x4969474D,0x3E6E77DB,
        0xAED16A4A,0xD9D65ADC,0x40DF0B66,0x37D83BF0,0xA9BCAE53,0xDEBB9EC5,0x47B2CF7F,0x30B5FFE9,
        0xBDBDF21C,0xCABAC28A,0x53B39330,0x24B4A3A6,0xBAD03605,0xCDD70693,0x54DE5729,0x23D967BF,
        0xB3667A2E,0xC4614AB8,0x5D681B02,0x2A6F2B94,0xB40BBE37,0xC30C8EA1,0x5A05DF1B,0x2D02EF8D,
    )
    openOfficeName = "OpenOffice"
    oooDefaultExt = ".odt"
    odsExt = ".ods"
    odpExt = ".odp"
    xlsExt = ".xls"
    pptExt = ".ppt"
    oooSxwExt = ".sxw"
    oooMasterDocExt = ".odm"
    wordExt = ".doc"
    word2007Ext = ".docx"
    wordDotExt = ".dot"
    bookExts = [".book.odt"]    #, ".book.doc"
    oooConvertExtensions = [oooDefaultExt, wordExt, word2007Ext, oooMasterDocExt]        # extensions to be converted by OOo
    oooConvertExtensions.extend(bookExts)
    htmItemExtensions = [oooDefaultExt, wordExt, word2007Ext]                      # extensions to be treated as .htm items
    pdfItemExtensions = [oooDefaultExt, wordExt, word2007Ext, oooMasterDocExt]        # extensions that have a PDF rendition
    pdfItemExtensions.extend(bookExts)
    isWindows = system.isWindows
    isLinux = system.isLinux
    isMac = system.isMac

    try:
        usersProfileDir = system.getOsConfigPath("ice")
    except:
        usersProfileDir = "."
    try:
        osHomeDir = system.getOsHomeDirectory()
    except:
        osHomeDir = "."
    
    
    # variable
    oooConverter = None
    docConverter = None
    siteBaseUrl = "http://localhost:8000/"  # Default only
    relativeLinker = None               ## Changes
    getRelativeLink = None              ## Changes
    isServer = False
    cache = {}
    progName = progName
    progPath = progPath.replace("\\", "/")
    workingDirectory = workingDirectory.replace("\\", "/")
    timedTempDirectories = {}
    #
    IceContext = None
    path = "path not set!"
    repName = ""
    urlRoot = "/rep.?/"
    iceRender = None
    onceOnlyWarnings = {}
    timerThread = None
    
    
    # Objects
    reps = None
    logger = None   ########## logger   # logger setup in IceCommon.setup()
    gTime = gTime
    fileSystem = FileSystem()
    fs = fileSystem    
    system = system
    output = sys.stdout
    threadLogWriter = None
    sysStdout = sys.stdout
    sysStderr = sys.stderr
    odtBookRenderMethod = None
    versionInfoSummary = ""
    
    
    # Classes
    RelativeLinker = None
    EditBookException = EditBookException
    IceException = IceException
    IceCancelException = IceCancelException
    AjaxException = AjaxException
    UnknownMimeTypeError = UnknownMimeTypeError
    NoSiteDataException = NoSiteDataException
    RedirectException = RedirectException
    #
    NodeMapper = NodeMapper
    IceSite = IceSite
    #
    Object = Object
    DictionaryObject = DictionaryObject
    SortedDictionary = SortedDictionary
    ElementTree = ElementTree
    cElementTree = cElementTree
    pyElementTree = pyElementTree
    Tags = Tags
    WorkerThread = WorkerThread
    JobObject = JobObject
    #
    IceRepositories = IceRepositories
    #IceProxyRepository = IceProxyRepository
    IceSiteRender = IceSiteRender
    IceTemplateInfo = IceTemplateInfo
    IceRepository = IceRepository
    #SvnRep = SvnRep
    #SvnProxyRep = SvnProxyRep
    ActionResult = ActionResult
    ActionResults = ActionResults
    IceInlineAnnotations = None
    HtmlTemplate = HtmlTemplate
    #RepositoryIndexer = RepositoryIndexer
    DummyRepositoryIndexer = DummyRepositoryIndexer
    ZipString = ZipString
    Http = Http
    XmlTestCase = XmlTestCase        # self.assertSameXml
    TestCase = TestCase
    Xml = xml_util.xml
    xmlUtils = xml_util
    FileSystem = FileSystem
    GetCallerInfo = GetCallerInfo
    LogWriter = LogWriter
    HtmlCleanup = HtmlCleanup
    #is static by default
    class HtmlStr(object):
        def __init__(self, s):
            if type(s) is types.UnicodeType:
                s = s.encode("UTF-8")
            self.__s = s
        
        @property
        def html(self):
            return self.__s        
        def __str__(self):
            return self.__s
        def __len__(self):
            return len(self.__s)
    
    # Static methods
    RLock = staticmethod(RLock)
    includeForTiming = staticmethod(includeForTiming)
    timeClass = staticmethod(timeClass)
    jsonRead = staticmethod(jsonRead)
    jsonWrite = staticmethod(jsonWrite)

    @staticmethod
    def setupTimerThread():
        interval = 60
        def target():
            def tic():
                print "--tic--"
                reps = IceCommon.reps
                for rep in reps:
                    if rep.name.startswith("?"):
                        continue
                    iceContext = rep.iceContext
                    if bool(iceContext.settings.get("autoSync"))==False:
                        continue
                    print "  %s,  %s  %s" % \
                        (rep.name, rep.getItem("")._absPath, iceContext.settings.get("autoSync"))
                    def updateCallback(item, **kwargs):
                        if item.isFile:
                            print "  * updated '%s'" % item.relPath
                    if iceContext.iceSite:
                        rootItem = rep.getItem("/")
                        rootItem._update(True, updateCallback)
                        print "  rendered %s" % rootItem.render(force=False, skipBooks=False)
                    else:
                        print "No ice site loaded"
            time.sleep(5)       # startup delay
            while True:
                try:
                    tic()
                except Exception, e:
                    print "Exception in tic() - %s" % str(e)
                time.sleep(60)
        if False:
            t = threading.Thread(target=target, name="WorkTimer")
            t.daemon = True
            t.start()
            IceCommon.timerThread = t

    
    @staticmethod
    def getImageImport():
        return Image


    @staticmethod
    def outputWriter(data):
        if IceCommon.output is not None:
            IceCommon.output.write(data)
    
    
    @staticmethod
    def writeln(data, args=()):
        IceCommon.outputWriter((data % args) + "\n")
    

    @staticmethod
    def wget(uri, queryString=None, headers={}):
        data = ""
        try:
            http = IceCommon.Http()
            r, data, headers = http.get2(uri, queryString=queryString, headers=headers)
            if r==False:
                print "Warning: Failed to retrieve data from '%s'\n%s" % (uri, data)
                data = None
        except Exception, e:
            print "Warning: Failed to retrieve data from '%s'\n%s" % (uri, str(e))
        return data

    
    @staticmethod
    def getTimedTempDirectory(hours=0, minutes=0, seconds=0):
        #IceCommon.timedTempDirectories = {}
        minutes += hours * 60
        seconds += minutes * 60
        tempDir = IceCommon.fs.createTempDirectory()
        def getRemover(item):
            def remove():
                IceCommon.timedTempDirectories[item].delete()
                del IceCommon.timedTempDirectories[item]
            return remove
        t = threading.Timer(seconds, getRemover(tempDir))
        IceCommon.timedTempDirectories[tempDir] = t
        t.start()
        return tempDir
    
    
    @staticmethod
    def getcwd():
        return os.getcwd()
    
    
    @staticmethod
    def chdir(path):
        os.chdir(path)
    
    
    @staticmethod
    def getArgv():
        return list(sys.argv)
    
    
    @staticmethod
    def now():
        return time.time()
    
    
    @staticmethod
    def localtime(t=None):
        if t is None:
            t = time.time()
        return time.localtime(t)
    
    
    @staticmethod
    def urlparse(url):
        """ <scheme>://<netloc>/<path>;<params>?<query>#<fragment> 
            returns a tuple of (scheme, netloc, path, params, query, frament) """
        return urlparse.urlparse(url)
    
    
    @staticmethod
    def urlunparse(urlParts):
        return urlparse.urlunparse(urlParts)
    
    
    @staticmethod
    def md5Hex(data):
        return md5(data).hexdigest()
    
    
    @staticmethod
    def urlJoin(*args):
        result = os.path.join(*args).replace("\\", "/")
        return result
    url_join = urlJoin
    
    
    @staticmethod
    def normalizePath(path):
        path = os.path.normpath(path)
        return path.replace("\\", "/")
    
    
    @staticmethod
    def strToInteger(strNum):
        return string.atoi(strNum)
    
    @staticmethod
    def cleanUpString(text):
        """
            To fix the endash error in title "mix encoded strings with Unicode strings". 
        """
        if text is None or text == '':
            return text
        try:
            text = text.encode("utf-8")
        except:
            newText = ""
            t = text.decode("utf-8")
            for c in t:
                newC = c
                if ord(c)>127:
                    newC = "&#%s;" % ord(c)
                if ord(c)==8211:
                    #change to this otherwise the toc has &#8211; value instead of endash
                    newC = chr(45)
                if ord(c)==160:
                    #&nbsp;
                    newC = " "
                newText += newC
                text = newText
        text = str(text)
        return text
        
    @staticmethod
    def iceSplitExt(file):
        base, ext = os.path.splitext(file)
        base2, ext2 = os.path.splitext(base)
        if ext2==".book":
            ext = ext2 + ext
            base = base2
        return base, ext
    
    
    @staticmethod
    def urlQuote(s):
        return urllib.quote(s)
    
    
    @staticmethod
    def dumps(obj):
        data = dumps(obj, HIGHEST_PROTOCOL)
        return data
    
    
    @staticmethod
    def loads(dataStr):
        obj = loads(dataStr)
        return obj
    
    
    @staticmethod
    def crc32(data):
        crc32Table = IceCommon.crc32Table
        crc = 0xffffffff
        for c in data:
            crc = crc32Table[(crc^ord(c))&0xff]^((crc>>8)&0xffffff)
        return crc ^ 0xffffffff;
    
    
    @staticmethod
    def crc32Hex(data):
        s = hex(IceCommon.crc32(data))[2:]
        if s.endswith("L"):
            s = s[:-1]
        return s.lower()
    

    @staticmethod
    def getHtmlFormattedErrorMessage(e, msg=""):
        errorMessage = IceCommon.textToHtml(str(e))
        html = "<div class='iceException' style='border:1px solid black;padding:0.5em;'>"
        html += msg
        html += "<div style='color:red;'>Error Message: %s</div>" % errorMessage
        html += "<hr/><div><i>Stack trace</i></div>"
        errText = IceCommon.formattedTraceback()
        html += "<div style='color:blue;'>%s</div>" % IceCommon.textToHtml(errText)
        html += "<i>Error: %s</i>" % errorMessage
        html += "</div>"
        if False:
            print "\n------------------------------"
            print msg
            print "Error: %s" % str(e)
            print "------------------------------\n"
        return html
    
    
    
    @staticmethod
    def textToHtml(text, includeSpaces=True):
    	if text is None: text = ""
        html = text.replace("&", "&amp;")
        html = html.replace("<", "&lt;")
        html = html.replace(">", "&gt;")
        html = html.replace("\n", "<br/>")
        html = html.replace("'", "&apos;")
        html = html.replace('"', "&quot;")
        if includeSpaces:
            html = html.replace(" ", "&#160;")
            html = html.replace("\t", "&#160;&#160;&#160;&#160;")
        else:
            html = html.replace("\t", "    ")
        return html
    
    
    @staticmethod
    def xmlEscape(str):
        if str is None:
            return None
        str = str.replace("&", "&amp;")
        str = str.replace("'", "&apos;").replace('"', "&quot;")
        str = str.replace("<", "&lt;").replace(">", "&gt;")
        return str
    
    
    @staticmethod
    def escapeXmlAttribute(s):
        if s is None:
            return ""
        s = s.replace("&", "&amp;")
        s = s.replace("<", "&lt;").replace(">", "&gt;")
        s = s.replace("'", "&apos;").replace('"', "&quot;")
        return s
    
    
    @staticmethod
    def httpTimeFormat(t=None, plusSeconds=0):
        if t is None:
            t = time.time()
        #tz = " " + ("+" + str(time.timezone/-36))[-5:]
        #return time.strftime("%a, %d %b %Y %H:%M:%S " + tz, time.localtime(t+plusSeonds))
        tz = " GMT"
        return time.strftime("%a, %d %b %Y %H:%M:%S "+tz, time.gmtime(t+plusSeconds))
    
    
    @staticmethod
    def gzip(data, filename=""):
        s = StringIO()
        gz = gzip.GzipFile(filename, "wb", 9, s)
        gz.write(data)
        gz.close()
        data = s.getvalue()
        s.close()
        return data
    
    
    @staticmethod
    def ungzip(gzData):
        s = StringIO(gzData)
        gz = gzip.GzipFile(None, "rb", 9, s)
        data = gz.read()
        gz.close()
        s.close()
        return data
    
    
    @staticmethod
    def httpCache(t, maxAge=None):
        if maxAge is None:
            maxAge = 300 * 24 * 60 * 60    # 300 Days
        lastModified = "Last-Modified", IceCommon.httpTimeFormat(t)
        eTag = "ETag", '"' + hex(int(t))[2:] + '"'
        expires = "Expires", IceCommon.httpTimeFormat(t, maxAge)
        cc = "must-revalidate, proxy-revalidate, max-age=%s, s-maxage=%s" % (maxAge, maxAge)
        #cc = "public, " + cc   # data is public (and cachable)
        #cc = "no-cache, no-store, " + cc   # no-cache check first, no-store do not store at all
        cacheControl = "Cache-Control", cc
        #header( "HTTP/1.1 304 Not Modified" )
        return (lastModified, expires, eTag, cacheControl)
        #Last-Modified header, with an If-Modified-Since request  - respond with header( "HTTP/1.1 304 Not Modified" )
        #ETag, with a If-None-Match request   - respond with header( "HTTP/1.1 304 Not Modified" )
    
    
    @staticmethod
    def formattedTraceback(lines=0):
        tb = sys.exc_info()[2]
        if tb is None:
            return "No traceback infomation available!"
        else:
            errLines = traceback.format_tb(tb)
            return "\n".join(errLines[-lines:])
    
    
    @staticmethod
    def getCallers(depth=1):
        callers = []
        for x in range(depth):
            # callerInfo = (file, line, method, code)
            callerInfo = traceback.extract_stack(limit=3+x)[0]
            callers.append(callerInfo)
        return callers
    
    
    @staticmethod
    def printCallers(depth=1, output=None):
        if output is None:
            output = IceCommon.output
        callers = IceCommon.getCallers(depth+1)
        callers.pop(0)
        x = 0
        for callerInfo in callers:
            file, line, method, code = callerInfo
            output.write("%s#%s %s '%s' %s\n" % (" " * x, line, method, file, code))
            x += 1
    
    
    @staticmethod
    def getStackList(f=None, limit=None):
        return traceback.format_stack(f=f, limit=limit)
        
    
    
    @staticmethod
    def guid():
        global __guidCount
        try:
            __guidCount += 1
        except:
            __guidCount = 0
        if __guidCount > 65535:
            __guidCount = 0
        gcs = hex(__guidCount)[2:].rjust(4, "0")
        t = int(time.time() * 1000000)
        st = hex(t)[2:-1]
        st = st.rjust(14, "0") + gcs
        st = st.lower()
        
        data = repr(random.random())
        
        rid = md5(data).hexdigest()
        uid = st + rid[len(st):]
        return uid.lower()
    
    
    @staticmethod
    def guidNum(hex=None):
        if hex is None:
            hex = IceCommon.guid()
        else:
            hex = hex.replace("-", "").replace("{", "").replace("}", "")
        return string.atol(hex, 16)
    
    
    @staticmethod
    def getOptions(args, shortOptionNames={"h":"help"}, flags=[""], defaultArgs=[] ):
        # flags (e.g. ["flag"] will make sure that a flag will not consume the next non -argument
        #   Note: flags are also converted to True|False
        # defaultArgs is a list of default option names for un-named arguments
        #   e.g. defaultArgs=["input", "output"] will assign 'input' to the
        #       first non (- or --) argument input and 'output' to the second
        # NOTE: "-nflag xxx"  'xxx' will be a value of 'nflag' and not a default argument!
        #       so if 'nflag' is going to be used only as a flag this add it to the flags list
        options = {}
        if True:        # add support of +flag  (converts +flag into -flag:1)
            tArgs = []
            for arg in args:
                if arg.startswith("+") and arg[1:].lower() in flags:
                    args = "-%s:1" % args[1:]
                tArgs.append(arg)
            args = tArgs
        else:
            args = list(args)
        args.append("")
        rList = []
        numArgs = zip(range(len(args)), args)
        for x, option in [(x, i.lstrip("-").lower()) for x, i in numArgs if i.startswith("-")]:
            rList.append(x)
            value = None
            equalIndex = option.find("=")
            colonIndex = option.find(":")
            if equalIndex>0 and ((colonIndex==-1) or (equalIndex<colonIndex)):
                option, value = numArgs[x][1].split("=", 1)
                option = option.lstrip("-").lower()
            elif colonIndex>0:
                option, value = numArgs[x][1].split(":", 1)
                option = option.lstrip("-").lower()
            option = shortOptionNames.get(option, option)
            if option in flags:
                if value == None:
                    value = True
                value = bool(value)
            if value is None and options!="" and option not in flags:
                value = numArgs[x+1][1]
                if value.startswith("-") or value=="":
                    value = None
                else:
                    rList.append(x+1)
            #if value is not None and (value.lower()=="false" or value=="0"):
            #    value = False
            options[option] = value
        args.pop()
        rList.reverse()
        for i in rList:
            del args[i]
        for option in options.keys():
            if option in defaultArgs:
                defaultArgs.remove(option)      # already used
        x = range(min(len(args), len(defaultArgs)))
        for i in x:
            options[defaultArgs[i]] = args[i]
        for i in x:
            del args[0]
        options[None] = args    # a list of unprocessed input arguments
        return options
    
    
    @staticmethod
    def getMembers(moduleName):
        return inspect.getmembers(moduleName)
    
    
    @staticmethod
    def sleep(seconds):
        time.sleep(seconds)
    
    @staticmethod
    def exit(num=0):
        sys.exit(num)
    
    
    @staticmethod
    def runUnitTests(locals):
        from unittest import TestCase, main
        try:
            from xml_diff import XmlTestCase        # self.assertSameXml
        except:
            XmlTestCase = None
        system.cls()
        print "---- Testing ----"
        print
        
        # Run only the selected tests
        #  Test Attribute testXxxx.slowTest = True
        #  fastOnly (do not run any slow tests)
        args = list(sys.argv)
        sys.argv = sys.argv[:1]
        args.pop(0)
        #runTests = ["Add", "testAddGetRemoveImage"]
        runTests = args
        runTests = [ i.lower().strip(", ") for i in runTests]
        runTests = ["test"+i for i in runTests if not i.startswith("test")] + \
                    [i for i in runTests if i.startswith("test")]
        if runTests!=[]:
            testClasses = [i for i in locals.values() \
                            if hasattr(i, "__bases__") and \
                                (TestCase in i.__bases__ or XmlTestCase in i.__bases__)]
            testing = []
            for x in testClasses:
                l = dir(x)
                l = [ i for i in l if i.startswith("test") and callable(getattr(x, i))]
                for i in l:
                    if i.lower() not in runTests:
                        #print "Removing '%s'" % i
                        delattr(x, i)
                    else:
                        #print "Testing '%s'" % i
                        testing.append(i)
            x = None
            num = len(testing)
            if num<1:
                print "No selected tests found! - %s" % str(args)[1:-1]
            elif num==1:
                print "Running selected test - %s" % (str(testing)[1:-1])
            else:
                print "Running %s selected tests - %s" % (num, str(testing)[1:-1])
        
        main()
    
    
    @staticmethod
    def mergeTags(myTags, newTags, oldTags):
        tags = []
        mySet = set(myTags)
        newSet = set(newTags)
        oldSet = set(oldTags)
        # find my deleted tags
        myDelSet = oldSet.difference(mySet)
        # find my added tags
        myAddedSet = mySet.difference(oldSet)
        # Add my added tags
        newSet.update(myAddedSet)
        # Remove my delete tags (if they still exists)
        newSet = newSet.difference(myDelSet)
        return list(newSite)
    
    
    @staticmethod
    def mergeConflictingTags(file, myFile, newFile, oldFile, fs):
        # myTags
        data = fs.readFile(myFile)
        if data is None: data = ""
        myTags = data.split()
        myTags.sort()
        # newTags
        data = fs.readFile(newFile)
        if data is None: data = ""
        newTags = data.split()
        newTags.sort()
        # oldTags
        data = fs.readFile(oldFile)
        if data is None: data = ""
        oldTags = data.split()
        oldTags.sort()
        #MergeTags
        tags = IceCommon.mergeTags(myTags, newTags, oldTags)
        # save the merged data
        data = "\n".join(tags)
        fs.writeFile(file, data)
IceCommon.setupTimerThread()




class CommonBaseDict(dict):
    __DICT = dict()
    def __init__(self, *args):
        dict.__init__(self, *args)
    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
        if not self.__DICT.has_key(key):
            self.__DICT[key] = value
    def __getitem__(self, key):
        return self.get(key)
    def get(self, key, default=None):
        if dict.has_key(self, key):
            return dict.__getitem__(self, key)
        return self.__DICT.get(key, default)
    def has_key(self, key):
        return dict.has_key(self, key) or self.__DICT.has_key(key)
    def keys(self):
        keys = set(self.__DICT.keys())
        keys.update(dict.keys(self))
        return list(keys)
    def copy(self):
        return CommonBaseDict(dict.items(self))


from ice_content_request import execSiteData
class IceContext(IceCommon):
    def __init__(self, pluginsPath="plugins", loadRepositories=False, \
                loadConfig=True, loadPlugin=True, options={}):         # pluginsPath="../../ice/plugins"
        # setup stdout and stderr
        IceCommon.threadLogWriter = ThreadLogWriter()
        IceCommon.defaultLogWriter = self.LogWriter()
        IceCommon.threadLogWriter.defaultLogWriter = IceCommon.defaultLogWriter
        sys.stdout = IceCommon.threadLogWriter
        sys.stderr = IceCommon.threadLogWriter
        IceCommon.output = sys.stdout
        self.__pluginsPath = pluginsPath
        self.__iceSite = None
        self.iceFunctions = None
        self.__path = list(sys.path)
        self.__plugins = {}
        self.__pluginSingletonObjects = {}
        self.ajaxHandlers = CommonBaseDict()        # Hack: a work around, so that a handler is shared between contexts for now
        self.rep = None
        self.config = None
        self.__settings = {}
        self.__objectCache = {}
        self.__rLock = RLock()
        
        #############
        self.workerThread = WorkerThread.getWorkerThread("workerThread")
        self.workerThreadLogWriter = self.LogWriter()
        self.threadLogWriter.setThreadLogWriter("workerThread", self.workerThreadLogWriter)
        def workerThreadTest():
            print "Testing worker thread jobID='%s'" % self.workerThread.currentJob.id
            for x in range(5):
                time.sleep(2)
                print "Tic %s" % x
        def test2():
            print "Second job JobID='%s'" % self.workerThread.currentJob.id
            sys.stdout.write("stdout write")
            sys.stdout.write("123")
            sys.stderr.write("stderr test\n")
        workerThread = self.workerThread
        class WData(object):
            def __init__(self, data):
                self.time = time.time()
                self.id = workerThread.currentJob.id
                self.data = data
            @property
            def timeStr(self):
                uS = int(self.time % 1 * 1000000)
                t = time.strftime("%H:%M:%S ", time.localtime(self.time))
                return t + str(uS).rjust(6, "0")
            def __str__(self):
                return "%s-%s  %s" % (self.timeStr, self.id, self.data)
        self.workerThreadLogWriter.WData = WData
        #self.workerThread.addJob(workerThreadTest, "testID")
        #self.workerThread.addJob(test2, "testID2")
        
        self.asyncJobs = {}
        self._setup(loadRepositories, loadConfig, loadPlugin, options)
    
    
    @property
    def settings(self):
        return self.__settings

    @property
    def reps(self):     # ReadOnly
        return IceCommon.reps
    
    def clone(self, deep=False, settings=None):
        # settings will be the repository's own settings
        #print "******* iceContext.clone() *************"
        c = copy.copy(self)      # keep it cheap
        if deep:
            c.__path = list(self.__path)
            c.__plugins = self.__plugins.copy()
            c.ajaxHandlers = self.ajaxHandlers.copy()
        if settings is not None:
            c.__settings = settings
            c.isServer = settings.get("server", self.isServer)
        return c
        # copy.beepcopy(self)
    
    
    def __getIceSite(self):
        r = self.__iceSite
        return r
    def __setIceSite(self, value):
        self.__iceSite = value
    iceSite = property(__getIceSite, __setIceSite)
    
    
    def _setup(self, loadRepositories=True, loadConfig=True, loadPlugin=True, options={}):
        #print "_setup()"
        if self.__pluginsPath is not None and loadPlugin:
            self._loadPlugins(self.__pluginsPath, loadConfig)

        self.__iceHostName, _, self.__iceHostAddr = gethostbyname_ex(gethostname())

        if loadRepositories:
            self.loadRepositories()

    def loadRepositories(self):
        # if we have settings information
        if self.settings is not None and self.settings!={}:
            IceCommon.reps = self.IceRepositories(self,
                            execSiteDataCallback=execSiteData)
            return IceCommon.reps

    def _loadPlugins(self, pluginsPath, loadConfig):
        #print " _loadPlugins()"
        ## Load Plugins ##
        self.loadPlugins(pluginsPath)
        # Plugins
        self.IceInlineAnnotations = self.getPlugin("ice.extra.inlineAnnotate").pluginClass
        
        if loadConfig:
            ## load config
            self.__settings = self.__getConfigSettings()
        
        self.IceRender = self.getPlugin("ice.render").pluginClass

        try:
            usersProfileDir = system.getOsConfigPath("ice", create=True)
        except:
            usersProfileDir = "."
        logPath = usersProfileDir
        logLevel = self.__settings.get("logLevel", 22)
        sLogPath = self.__settings.get("logPath")
        if sLogPath is not None:
            if self.fs.isDirectory(sLogPath):
                logPath = sLogPath
            else:
                print "Warning: logPath='%s' is not valid, using default log path" % sLogPath

        # Required plugins
        versionInfo = self.getPluginClass("ice.info")(self)
        self.versionInfoSummary = versionInfo.getSummary()
        # Logger
        try:
            self.logger = self.getPluginClass("ice.logger")(self).getLogger(logPath, logLevel)
        except:
            self.logger = MockLogger()
        # MimeTypes
        self.MimeTypes = self.getPluginClass("ice.mimeTypes")(self)
        # ConvertedData
        self._ConvertedData = self.getPluginClass("ice.convertedData")
        
        gTime.enabled = self.__settings.get("displayTiming", False)
        
        ## Load ice function plugins   ## Note: this is repository dependent
        self.loadIceFunctionsPlugins()
        
        #############
        self.__loadServicesPlugins()
        
        self.FileManager = self.getPlugin("ice.fileManager").pluginClass
    
    
    def __getConfigSettings(self):
        data = self.fs.readFile("config2.xml")
        #data = None
        if data is not None:
            Config = self.getPluginClass("ice.config2")
            self.config = Config(self)
            version = self.config.process(data)
            print "loaded config (version='%s')" % version
            settings = self.config.settings
            def saveMethod(xmlStr):
                self.fs.writeFile("config2.xml", xmlStr)
            self.config.setSaveMethod(saveMethod)
        else:
            Config = self.getPluginClass("ice.config-xml")
            if Config is None:
                raise Exception("'ice.config-xml' plugin not found and is required!")
            self.config = Config(self)
            print "loaded config"
            settings = self.config.loadConfigValues()
        
        port = self.config.port
        host = self.config.hostAddress
        self.siteBaseUrl = "http://%s:%s/" % (host, port)
        self.isServer = settings.get("server", False)
        
        pythonPath = settings.get("oooPythonPath")
        if pythonPath is None:
            if settings.get("hasOoo3Mac")==False:
                print "No OpenOffice python found!"
        else:
            if not os.path.isdir(pythonPath):
                pythonPath = os.path.split(pythonPath)[0]
            #
            syspath = sys.path          # save sys.path
            sys.path = self.__path
            try:
                sys.path.append(pythonPath)
                syspath.append(pythonPath)      ## ????
            finally:
                sys.path = syspath      # restore sys.path
            #
        return settings
    
    
    def addAsyncJob(self, function, id=None, message=""):
        try:
            self.__rLock.acquire()
            if id is None:
                id = self.guid()
            status = self.Object()
            status.message = message
            status.resultSummary = ""
            status.resultDetails = ""
            status.resultError = ""
            job = self.workerThread.addJob(_function=function, _id=id)
            job.status = status
            self.asyncJobs[id] = job
            return job
        finally:
            self.__rLock.release()

    def getAsyncJob(self, id):
        try:
            self.__rLock.acquire()
            job = self.asyncJobs.get(id, None)
            return job
        finally:
            self.__rLock.release()
    
    def removeAsyncJob(self, id):
        try:
            self.__rLock.acquire()
            if self.asyncJobs.has_key(id):
                del self.asyncJobs[id]
        finally:
            self.__rLock.release()
    
    
    def ConvertedData(self):
        return self._ConvertedData(self)
    
    
    def outputWriter(self, data):
        if self.output is not None:
            self.output.write(data)
    
    
    def writeln(self, data, args=()):
        self.outputWriter((data % args) + "\n")
    
    
    def __loadServicesPlugins(self):
        self.iceServices = IceServices(self)

        # add plugin services
        for servicePlugin in self.getPluginsOfType("ice.service."):
            service = servicePlugin.pluginInit(self)
            service.name = servicePlugin.pluginName
            service.description = servicePlugin.pluginDesc
            for ext in service.exts:
                self.iceServices.addServicePlugin(ext, service)
    
    
    def getPluginsOfType(self, pluginNS):
        return [p for p in self.__plugins.values() if p.pluginName.startswith(pluginNS)]
    
    
    def reloadIceFunctions(self):
        #print "reloadIceFunctions()"
        syspath = sys.path              # save sys.path
        sys.path = self.__path
        try:
            iceFunctionsPlugin = self.getPlugin("ice.functions")
            if iceFunctionsPlugin is not None:
                reload(iceFunctionsPlugin)
            for plugin in self.getPluginsOfType("ice.function."):
                reload(plugin)
        finally:
            sys.path = syspath         # restore sys.path
        self.loadIceFunctionsPlugins()
    
    
    def loadIceFunctionsPlugins(self):
        iceFunctionsPlugin = self.getPlugin("ice.functions")
        if iceFunctionsPlugin is None:
            return
        #print "** loadIceFunctionsPlugins **"
        self.iceFunctions = iceFunctionsPlugin.pluginClass(self)
        
        for plugin in self.getPluginsOfType("ice.function."):
            func = plugin.pluginInit(self)
            options = func.__dict__
            options.update(options.get("options", {}))
            if options.get("group") is None:
                options["group"] = "toolbar_%s" % options.get("toolBarGroup", "")
            self.iceFunctions.add(func, **options)
    
    
    #============ PLUGINS ================
    def loadPlugins(self, pluginsPath="./plugins"):
        #print "*** loadPlugins(pluginsPath='%s')" % pluginsPath
        fs = self.fs
        syspath = sys.path          # save sys.path
        sys.path = self.__path
        def importPlugin(file):
            try:
                plugin = __import__(file[:-3])
                if not hasattr(plugin, "pluginProperties"):
                    plugin.pluginProperties = {}
                pluginProperties = plugin.pluginProperties
                if pluginProperties.has_key("name"):
                    plugin.pluginName = pluginProperties.get("name")
                name = plugin.pluginName
                if pluginProperties.get("loadError") is None:
                    self.__plugins[name] = plugin
                else:
                    loadErrorMsg = pluginProperties.get("loadError")
                    if pluginProperties.get("required", False):
                        print "* failed to load a required plugin name '%s' - '%s'" % (name, loadErrorMsg)
                    else:
                        if pluginProperties.get("optional", False):
                            print "optional plugin name '%s' failed to load - '%s'" % (name, loadErrorMsg)
                        else:
                            print "plugin name '%s' failed to load - '%s'" % (name, loadErrorMsg)
            except Exception, e:
                print "* failed to load plugin '%s' - '%s'" % (file, str(e))
        try:
            if fs.isDirectory(pluginsPath):
                for path, dirs, files in fs.walk(pluginsPath):
                    # Windows doesn't like adding paths to the PYTHONPATH with
                    # slash at the end
                    while path.endswith("/"):
                        path = path[:-1]
                    ffiles = [f for f in files \
                        if f.startswith("plugin_") and f.endswith(".py") and not f.endswith("_test.py")]
                    if ffiles!=[]:
                        if path in sys.path:
                            sys.path.remove(path)
                        sys.path.insert(0, path)
                    for file in ffiles:
                        importPlugin(file)
#                        try:
#                            plugin = __import__(file[:-3])
#                            if not hasattr(plugin, "pluginProperties"):
#                                plugin.pluginProperties = {}
#                            pluginProperties = plugin.pluginProperties
#                            if pluginProperties.has_key("name"):
#                                plugin.pluginName = pluginProperties.get("name")
#                            name = plugin.pluginName
#                            if pluginProperties.get("loadError") is None:
#                                self.__plugins[name] = plugin
#                            else:
#                                loadErrorMsg = pluginProperties.get("loadError")
#                                if pluginProperties.get("required", False):
#                                    print "* failed to load a required plugin name '%s' - '%s'" % (name, loadErrorMsg)
#                                else:
#                                    if pluginProperties.get("optional", False):
#                                        print "optional plugin name '%s' failed to load - '%s'" % (name, loadErrorMsg)
#                                    else:
#                                        print "plugin name '%s' failed to load - '%s'" % (name, loadErrorMsg)
#                        except Exception, e:
#                            print "* failed to load plugin '%s' - '%s'" % (file, str(e))
            elif fs.isFile(pluginsPath):
                path, file = self.fs.split(pluginsPath)
                sys.path.insert(0, path)
                importPlugin(file)
                sys.path.pop(0)
        finally:
            sys.path = syspath      # restore sys.path
    
    
    def loadSitePlugins(self, pluginsPath="/.site"):
        pPath = self.rep.getAbsPath(pluginsPath)
        self.loadPlugins(pPath)
    
    
    def reloadPlugin(self, plugin):
        if type(plugin) in types.StringTypes:
            plugin = self.__plugins.get(plugin)
        if plugin is None:
            return False
        syspath = sys.path
        sys.path = self.__path
        try:
            if self.__plugins.has_key(plugin.pluginName):
                self.__plugins.pop(plugin.pluginName)
            reload(plugin)
            plugin.pluginInitialized = False
            name = plugin.pluginName
            self.__plugins[name] = plugin
            return True
        finally:
            sys.path = syspath
        return False
    
    
    def reloadPlugins(self):
        syspath = sys.path
        sys.path = self.__path
        try:
            for plugin in self.__plugins.values():
                reload(plugin)          # python reload module
                plugin.pluginInitialized = False
        finally:
            sys.path = syspath
    
    
    def getPlugin(self, name, reInit=False):
        plugin = self.__plugins.get(name)
        if plugin is not None:
            if reInit or not plugin.pluginInitialized:
                plugin.pluginInit(self)
        else:
            msg = "Warning: can not find plugin '%s'!" % name
            #raise Exception(msg)
            if not IceCommon.onceOnlyWarnings.has_key(msg):
                IceCommon.onceOnlyWarnings[msg] = msg
                self.writeln(msg)
        return plugin
    
    
    def getPluginClass(self, name, reInit=False):
        plugin = self.getPlugin(name, reInit)
        if plugin is not None:
            return plugin.pluginClass
        return None

    def getPluginObject(self, name, **kwargs):
        pluginObj = None
        pluginClass = self.getPluginClass(name)
        if pluginClass is not None:
            pluginObj = pluginClass(self, **kwargs)
        return pluginObj


    def getPluginSingletonObject(self, name):
        pluginObj = self.__pluginSingletonObjects.get(name)
        if pluginObj is None:
            pluginObj = self.getPluginObject(name)
            self.__pluginSingletonObjects[name] = pluginObj
        return pluginObj

    #######################
    def IceImage(self, imageData, imageExt=None):
        return self.getPluginClass("ice.image")(imageData, imageExt)

    #######################
    def getOooConverter(self):
        if self.oooConverter is None:
            OpenOfficeConverterPlugin = self.getPlugin("ice.ooo.OpenOfficeConverter")
            self.oooConverter = OpenOfficeConverterPlugin.pluginClass(self)
        return self.oooConverter
    
    
    def getDocConverter(self):
        if self.docConverter is None:
            docConverterPlugin = self.getPlugin("ice.render.docConverter")
            self.docConverter = docConverterPlugin.pluginClass(self)
        return self.docConverter

    
    def getObjectFromCache(self, name, createFunc=None):
        if not self.__objectCache.has_key(name):
            if callable(createFunc):
                self.__objectCache[name] = createFunc()
        return self.__objectCache.get(name)

    
    def getImsManifest(self, mfItem, includeSource=False, forceCreate=False):
        imsManifest = None
        if mfItem.isDirectory:
            mfItem = mfItem.getChildItem("manifest.xml")
        plugin = self.getPlugin("ice.ims.manifest")
        imsManifest = plugin.pluginClass.getManifest(self, \
                        mfItem, includeSource, forceCreate)
        return imsManifest
    
    
    def getRepositoryIndexer(self, indexPath):
#        try:
#            indexer = self.RepositoryIndexer(self, indexPath)
#        except Exception, e:
#            self.writeln("Warning: Using DummyRepositoryIndexer \n\t%s" % str(e))
#            indexer = self.DummyRepositoryIndexer(self, indexPath)
#        return indexer
        return self.DummyRepositoryIndexer(self, indexPath)
    
    
    def getIceTemplateInfo(self, xhtmlTemplateFilename, isSlidePage, packagePath):
            return self.IceTemplateInfo.getIceTemplateInfo(self, \
                            xhtmlTemplateFilename, isSlidePage, packagePath)
    
    
    def getIceSiteRender(self):
        return self.IceSiteRender(self)
    
    
    def getPackagePathFor(self, path):
        if self.iceSite is None:
            return False
        return self.iceSite.getPackagePathFor(path)


    def isLocalUrl(self, url):
        #print "** isLocalUrl(url='%s')" % url
        r = False
        protocol, netloc, path, param, query, fid = IceCommon.urlparse(url)
        if protocol=="http" or protocol=="https":
            r = self.isNetlocLocal(netloc)
            if False:
                #dont' know why. This never start with rep.name so it keep returning the wrong data.
                r = path.startswith(self.urlRoot)
                ## for testing only
                if self.urlRoot=="/rep.TestContent/" and path.startswith("/rep.TempTest-"):
                    r = True
                ##
        if protocol=="" and netloc=="":
            r = True
        return r
    
    
    def isNetlocLocal(self, netloc):
        result = False
        if netloc=="":
            return True
        iceHostPort = self.config.port
        if netloc.find(':') == -1:
            locHost = netloc
            locPort = iceHostPort
        else:
            if netloc.find("//") != -1:
                #if there is http://
                url = netloc.split("/")[2]
            else:
                url = netloc
            if url.find(":") == -1 and url.find("/") == -1:
                # if it is e.g. ice-one.usq.edu.au 
                #purely address
                locHost= url
                locPort = 8000
            else:
                locHost, locPort = url.split(':')[:2]
            #get http: findout a way to remove it
        localAddrs = ['', 'localhost', '127.0.0.1', self.config.hostAddress, self.__iceHostName]
        altHostNames = self.settings.get("altHostNames", [])
       
        
        if type(altHostNames) is types.ListType:
            localAddrs.extend(altHostNames)
        localAddrs.extend(self.__iceHostAddr)
        if locHost in localAddrs and int(locPort) in [int(iceHostPort), 8000]:
            result = True
        #print "isNetlocLocal(netloc='%s') %s" % (netloc, result)
        return result


    def getMimeTypeFor(self, name):
        return self.MimeTypes.get(self.fs.splitExt(name)[1].lower())

    def getMimeTypeForExt(self, ext):
        return self.MimeTypes.get(ext.lower())



IceCommon.IceContext = IceContext


# Time these classes
IceCommon.timeClass(IceSite)
IceCommon.timeClass(IceSiteRender, True)
IceCommon.timeClass(IceTemplateInfo)




class MockLogger(object):
    def __init__(self):
        print ("*** WARNING: Using MockLogger ***")
    def iceInfo(self, msg, *args):
        msg = msg % args
        print ("INFO: " + msg)
    def iceWarning(self, msg, *args):
        msg = msg % args
        print ("WARNING: " + msg)
    def iceError(self, msg, *args):
        msg = msg % args
        print ("ERROR: " + msg)
    def flush(self):
        pass
    def log(self, level, message, *args, **kwargs):
        print "LOG(%s): %s" % (level, message)



##############################################
#######  Imports needed for Image (PIL) ######
#import Image   # done above
import codecs
from encodings import *
from encodings import aliases
from encodings import ascii
from encodings import cp437
from encodings import cp850
from encodings import cp1252
from encodings import string_escape
from encodings import unicode_escape
from encodings import utf_8
from encodings import utf_16_le
try:
    from encodings import mbcs
except:
    pass

try:        # for Image
    import BmpImagePlugin
    import DcxImagePlugin
    import EpsImagePlugin
    import GifImagePlugin
    try:
        import IcnsImagePlugin
    except:
        pass
    import IcoImagePlugin
    import JpegImagePlugin
    import MpegImagePlugin
    import PdfImagePlugin
    import PcxImagePlugin
    import PngImagePlugin
    import TiffImagePlugin
    import TgaImagePlugin
    try:
        import WbmpImagePlugin
    except:
        pass
except:
    pass
##############################################



