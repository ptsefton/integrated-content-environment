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

import sys
if sys.path.count("../ice")==0: sys.path.append("../ice")
from ice_globals import *



class baseSite(icesite):
    def __init__(self):
        icesite.__init__(self)
        

    def traverse(self):
        title = "Ice web application"
        if self.node('home'):
            self["package-path"] = self.pathToHere
        elif self.node('packages'):
            title = "Packages"
            if self.renode('^.*$', 'code'):
                self["package-path"] = self.pathToHere
        elif self.node('public'):
            title = "Public"
            if self.node('packages'):
                title = "Public"
                if self.renode('^.*$', 'code'):
                    self["package-path"] = self.pathToHere           
        elif self.node('teams'):
            title = "Teams"
            if self.node('packages'):
                title = "Teams"
                if self.renode('^.*$', 'code'):
                    self["package-path"] = self.pathToHere
        elif self.node('courseware'):
            title = "Courseware"
            if self.renode('^.*$', 'deptname'):
                title = self["deptname"].upper()
                self["deptname"] = self["deptname"].upper()
                if self.renode('^.*$', 'coursecode'):
                    title = self["deptname"].upper() + self["coursecode"].upper() 
                    self["coursecode"] = self["coursecode"].upper()
                    if self.renode('^.*$', 'year'):
                        title = self["deptname"].upper() + self["coursecode"].upper() + " " + self["year"]
                        if self.renode('^.*$', 'semester'):
                            self["semester"] = self["semester"].upper()
                            self["package-path"] = self.pathToHere
                            self["isCourseware"] = True
        elif self.renode('^.*$', 'code'):
            if self.node('packages'):
                title = "Packages"
                if self.renode('^.*$', 'code'):
                    self["package-path"] = self.pathToHere

        if self["package-path"] and self.rep.isdir(self["package-path"])==True:
            packageNode = True
        else:
            packageNode = False
            self["package-path"] = ""
            
        self._getManifest()
        self._executeFunction()
        
        if packageNode==True and self["body"]==None:
            if self.currentNode==None or self.currentNode=="default.htm":
                self._default_htm()
            elif self.currentNode=="toc.htm":
                self._toc_htm()
        
        if self["title"]==None:
            self["title"] = title
    

# ++++ Extra ICE Function ++++

from ice_functions import *
def displayIf(self):
    return self.xhtmlTemplate != "template.xhtml"
addFunction(func=mailThis, position=15, postRequired=True, label="Email", title="Email this", displayIf=displayIf)

global refresh
refresh = getFunction("refresh")

global check_links
check_links = getFunction("check_links")


global export
def export(self, exportBaseName=None, exportCallback=None):
    import ice_export
    refresh(self)
    fileName = None
    templateName = os.path.split(self.xhtmlTemplate)[1]
    templateName = os.path.splitext(templateName)[0]
    
    toRepository = False
    deleteFirst = False
    exportHomeAlso = False
 
    print "Exporting"
    
    if self.has_key("isCourseware"):
        path = self["package-path"]
        print "Path: %s" % path
        try:
            exportBaseName = self["deptname"]
            exportBaseName += self["coursecode"]
            exportBaseName += "_" + self["year"]
            exportBaseName += self["semester"]
        except:
            pass
        if exportBaseName!=None:
            fileName = exportBaseName
        else:
            if templateName == "template":
                templateName = "Default"
        
            fileName = os.path.split(path)[1]
        fileName += "_" + templateName + ".zip"
        toRepository = True
    else:
        #path = self.path
        if self["package-path"]:
            path = self["package-path"]
            print "package-path='%s'" % path
            deleteFirst = False
        else:
            path = self.pathToHere
            if path=="":
                path = "/"
            # if exporting the root then also export the /home directory (to the root)
            #   but after exporting the root (so that /home overwrites the root content
            if path=="/":
                exportHomeAlso = True
        #print "path='%s'" % path
        fileName = os.path.join(self.rep.exportPath, self.rep.name, path.strip("/"))
    if (fileName==None) or (fileName==""):
        fileName = "export"
    
    fullFileName = os.path.join(path, fileName)

    ex = ice_export.iceExport(self)
    
    if fullFileName.endswith("/home"):
        ex.export(path, fullFileName, toRepository, exportCallback, deleteFirst)
        fullFileName = fullFileName[:-len("/home")]
 
    ex.export(path, fullFileName, toRepository, exportCallback, deleteFirst)
    if exportHomeAlso:
        #print "*** Export Home as well"
        packagePath = self["package-path"]  # Save
        self["package-path"] = "/home"
        export(self, exportBaseName=exportBaseName, exportCallback=exportCallback)
        self["package-path"] = packagePath  # Restore
    check_links(self)
    
    self["title"] = "Exported"
    self["statusbar"] = "Exported <a href='%s'>%s</a>" % (fullFileName, fileName)
    
replaceFunction(export)


# Disable 'get changes', 'sync' and 'export' when in the filemanager
global isNotFileManager
def isNotFileManager(self):
    try:
        v = self.newFormData.value("func")
        if v=="file_manager":
            return False
    except:
        return False
    return True

global workingOnLineAndNotFileManager
def workingOnLineAndNotFileManager(self):
    if self.workingOffline():
        return False
    try:
        v = self.newFormData.value("func")
        if v=="file_manager":
            return False
    except:
        return False
    return True
       
ex = getFunction("export")
ex.enableIf = isNotFileManager
up = getFunction("update")
up.enableIf = workingOnLineAndNotFileManager
sy = getFunction("sync")
sy.enableIf = workingOnLineAndNotFileManager

addFunction(func=publishThis, position=16, postRequired=True, label="Atom Pub", title="Publish this using AtomPub")








