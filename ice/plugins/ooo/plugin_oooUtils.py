
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

""" """
import os
import sys
import re
import string

pluginName = "ice.ooo.utils"
pluginDesc = "OOo Utils"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = None
    pluginClass = OOoUtils
    pluginInitialized = True
    return pluginFunc





class OOoUtils(object):
    # Constructor:
    #   __init__(iceContext)
    # Properties:
    #   
    # Methods:
    #   isOooPathOK(oooPath="")
    #   getOooPythonPath(oooPath)
    #   getBestOooPath()
    #   
    
    # fs methods used
    #   .join()
    #   .listDirectories(path) - > [dirs]
    #   .search(path, filename) -> [paths]
    #   .reSearch(path, pattern) -> [paths]
    #   .chmod(file, mode)
    #   .delete(path)
    #   .isFile(path)
    # system methods/properties used
    #   .execute(command)
    #   .isWindows
    #   .isMac
    #   .isLinux
    unoPython = "unoPython"
    
    @staticmethod
    def getOooPath():
        ooPath = [path for path in os.environ["PATH"].split(";") if path.lower().find("openoffice.org")>0]
        if len(ooPath)>0:
            return ooPath[0]
        else:
            return None
    
    
    def __init__(self, iceContext):
        self.iceContext = iceContext
        self.__fs = iceContext.fs
        self.__system = iceContext.system
        self.__output = iceContext.output
    
    
    def hasOoo3Mac(self):
        if self.__system.isMac:
            #check for openoffice 3 and use precompiled pyuno if possible
            if self.__fs.exists("/Applications/OpenOffice.org.app/Contents/program/fundamentalrc") and \
                    os.getenv('URE_BOOTSTRAP') is not None and \
                    os.getenv('DYLD_LIBRARY_PATH') is not None:
                return True
        return False
    
    def isOooPathOK(self, oooPath=""):
        if self.hasOoo3Mac():
            return True
        ooopp = self.getOooPythonPath(oooPath)
        if ooopp is not None and self.__fs.isFile(ooopp) or ooopp=="python":
            if self.__system.isWindows:
                ooopp = ooopp.replace("/", "\\")
            command = ooopp
            #command = "\"%s\" -c \"__import__('uno');print(True)\"" % ooopp
            result, msg = self.__system.execute(command, "-c", "__import__('uno');print(True)")
            #print "result='%s'" % result
            return result.startswith("True")
        else:
            return False


    def getOooPythonPath(self, oooPath):
        if self.hasOoo3Mac():
            return None
        pythonName = "python"
        if self.__system.isWindows:
            pythonName = "python.bat"
        elif self.__system.isMac:
            pythonName = "python.sh"
        elif self.__system.isLinux:
            pythonName = "python.sh"
        progPython = "program/%s" % pythonName
        if oooPath is None:
            oooPyPath = None
        elif oooPath=="":
            oooPyPath = "python"
        else:
            oooPyPath = self.__fs.join(oooPath, progPython)
        
        if oooPyPath is None:
            return None
        # check for python.exe
        if self.__system.isWindows and not self.__fs.exists(oooPyPath):
            oooPyPath = self.__fs.join(oooPath, "program/python.exe")
        
        #if self.__system.isMac and self.__fs.isFile(oooPyPath)==False:
        #    if oooPath.endswith("/"):
        #        oooPath = oooPath[:-1]
        #    pyPath = self.__getUnoPythonPath()
        #    if pyPath==oooPath:
        #        oooPyPath = pyPath
        #    else:
        #        pass
        #        self.__createUnoPythonShell(oooPath)
        #        pyPath = self.__getUnoPythonPath()
        #        if pyPath==oooPath:
        #            oooPyPath = pyPath
        #if not self.__fs.isFile(oooPath):
        #if oooPath=="":
        #    oooPyPath = "python"
        
        return oooPyPath


    def getBestOooPath(self):
        fs = self.__fs
        system = self.__system
        oooPath = None
        if self.__output is not None:
            self.__output.write("searching for the best Ooo path.\n")
        
        try:
            pass
            #import uno     # Note: may cause lockup on windows
            # OK
        except Exception, e:
            pass
        
        preferredVersion = None
        keyFilenames = ["python"]
        if system.isWindows:
            searchPaths = []
            for path in ["C:/Program Files/"]:
                searchPaths += [fs.join(path, p) for p in fs.listDirectories(path) \
                                if p.lower().startswith("openoffice")]
            keyFilenames = ["python.exe", "python.exe"]
            preferredVersion = 3
        elif system.isMac:
            searchPaths = []
            for path in ["/Applications/"]:
                searchPaths += [fs.join(path, p) for p in fs.listDirectories(path) \
                                if p.lower().startswith("openoffice") or p.startswith("NeoOffice")]
            keyFilenames.append("python.sh")
            preferredVersion = 2.0
        elif system.isLinux:
            searchPaths = []
            for path in ["/opt/", "/usr/local/", "/etc/", "/usr/lib/"]:
                searchPaths += [fs.join(path, p) for p in fs.listDirectories(path) \
                                if p.lower().startswith("openoffice")]
            keyFilenames.extend("python.sh")
        
        paths = []
        # find all openoffice.org paths
        for path in searchPaths:
            paths += fs.reSearch(path, "^(o|O)pen(o|O)ffice\\.org(.?)(\\d+(\\.\\d+)?)") + [path]
            for keyFilename in keyFilenames:
                # filter to only the one that contain a /program/python
                progPython = "/program/%s" % keyFilename
                pythonPaths = [path for path in paths if \
                                  [p for p in fs.search(path, keyFilename) if p.endswith(progPython)]!=[] \
                              ]
                versionsPaths = {}
                for path in pythonPaths:
                    match = re.search("\\/(o|O)pen(o|O)ffice\\.org(.?)(\\d+(\\.\\d+)?)", path)
                    if match:
                        ver = match.groups()[3]
                        ver = string.atof(ver)
                        if not versionsPaths.has_key(ver):
                            versionsPaths[ver] = path
                versions = versionsPaths.keys()
                versions.sort()
                if versions!=[]:
                    if preferredVersion in versions:
                        ver = preferredVersion
                    else:
                        ver = versions.pop()
                    path = versionsPaths[ver]
                    pythonPaths = [p for p in fs.search(path, keyFilename) if p.endswith(progPython)]
                    if len(paths)>0:
                        oooPath = pythonPaths[0][:-len(progPython)]
                        break
        if oooPath is None:
            # just try python
            result, msg = self.__system.execute("python", "-c", "__import__('uno');print(True)")
            if result.startswith("True"):  #result=="True\n":
                oooPath = ""
        if oooPath is None:
            oooPath = ""
        if self.__output is not None:
            if oooPath=="":
                self.__output.write("  Ooo path not found! - Warning OpenOffice conversions will not work!")
            else:
                self.__output.write("  done. oooPath='%s'\n" % oooPath)
        return oooPath


    def __getBestMacOooPath(self):
        fs = self.__fs
        for path in ["/Applications/"]:
            searchPaths += [fs.join(path, p) for p in fs.listDirectories(path) \
                            if p.lower().startswith("openoffice") or p.startswith("NeoOffice")]

        paths = []
        # find all openoffice.org paths
        for path in searchPaths:    
            paths += fs.reSearch(path, "^(o|O)pen(o|O)ffice\\.org(.?)(\\d+\\.\\d+)") + [path]
        # filter to only the one that contain a /program/uno.py
        keyFilename = "python.sh"
        progPython = "/program/" + keyFilename
        paths = [path for path in paths if \
                    [p for p in fs.search(path, "uno.py") if p.endswith(progPython)]!=[] \
                ]
        versionsPaths = {}
        for path in paths:
            match = re.search("\\/(o|O)pen(o|O)ffice\\.org(.?)(\\d+\\.\\d+)", path)
            if match:
                ver = match.groups()[3]
                ver = string.atof(ver)
                if not versionsPaths.has_key(ver):
                    versionsPaths[ver] = path
        versions = versionsPaths.keys()
        versions.sort()
        if versions!=[]:
            ver = versions.pop()
            path = versionsPaths[ver]
            paths = [p for p in fs.search(path, keyFilename) if p.endswith(progPython)]
            if len(paths)>0:
                oooPath = paths[0][:-len(progPython)]
        print "  done. oooPath = '%s'" % oooPath
        self.__createUnoPythonShell(oooPath)
        return oooPath


    def _createUnoPythonShell(self, oooPath=None):
        if oooPath is None:
            oooPath = self.getBestOooPath()
        return self.__createUnoPythonShell(oooPath)
    def __createUnoPythonShell(self, oooPath):
        #pyScript = "import uno\n"
        #test = "python -c \"%s\"" % pyScript.replace('"', '\"')
        
        pythonVersions = ["2.3", "2.4", ""]  # e.g. empty for the default version or 2.3 or 2.4 etc
        path = self.__fs.join(oooPath, "program")
        data = """export OooProgPath=%s
export PYTHONPATH=$PYTHONPATH:$OooProgPath
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$OooProgPath
export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:$OooProgPath
python%s $*
""" 
        for pythonVersion in pythonVersions:
            data = data % (path, pythonVersion)
            f = open(self.unoPython, "wb")
            f.write(data)
            f.close()
            fs.chmod(self.unoPython, 511)      # make it executable
            
            # Ok now test    Note: argument passing can not have quoted spaces
            #command = "./%s -c \"__import__('uno');print(True)\"" % self.unoPython
            command = "./" + self.unoPython
            result, msg = self.__system.execute(command, "-c", \
                    "__import__('uno');print(True)")
            print "result='%s'" % result
            print "msg='%s'" % msg
            if result=="True":
                return True
            else:
                self.__fs.delete(unoPython)
        return False
        

    def __getUnoPythonPath(self):
        path = None
        if self.__fs.isFile(self.unoPython):
            f = open(self.unoPython, "rb")
            data = f.read()
            f.close()
        m = re.search("(^|\n)export OooProgPath=(.*?)(\\|/)program", data)
        if m is not None:
            path = m.groups(1)
        return path


    class OOoStyle(object):
        # sample names - 'p', 'bq1', 'li1b'
        def __init__(self, name=None, family="", level="", type=""):
            self.__types = {"b":"bullet", "n":"number"}
                            #, "p":"paragraph", "a":"lowercaseAlpha", \
                            #"A":"uppercaseAlpha", "i":"lowercaseRoman", "I":"uppercaseRoman"}
            self.family = family
            self.level = level
            self.type = type
            if name is not None:
                self.setName(name)
            else:
                self.name = ""

        def setName(self, name):
            self.name = name
            self.family, self.level, self.type = self.__getFamilyLevelType(name)
            
        def __getFamilyLevelType(self, name):
            match = re.match(r"^([^-\d]*)(\d+|)-?(.*)$", name)
            family, level, type = match.groups(1)
            try:
                level = int(level)
            except:
                level = 0
            if family=="":
                family = "p"
            elif family=="h":
                #family += str(level)
                level = 0
            elif family=="pre" or family=="bq":
                pass
            if type in self.__types:
                type = self.__types[type]
            return family, level, type
            
        def __str__(self):
            s = "[oooStyle] family='%s', level=%s, type='%s'" % (self.family, self.level, self.type)
            return s









