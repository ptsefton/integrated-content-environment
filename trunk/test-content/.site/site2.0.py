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

#from ice_functions import *
print "*** Using the Default site file! ***"

class baseSite(icesite):
    def __init__(self):
        icesite.__init__(self)
        

    def traverse(self):
        title = "Ice web application"
        self["parent"] = ""
        # while it is not 'package', 'Package', 'packages' or 'Packages' - skip  
        while self.renode("^(?!(P|p)ackages?$).*$", "parent"): pass
        if self.node('packages') or self.node('Packages'):
            title = "Packages"
            if self.renode('^.*$', 'code'):
                self["package-path"] = self.pathToHere
        elif self.node('package') or self.node('Package'):
            title = "Package"
            self["code"] = self["parent"]
            self["package-path"] = self.pathToHere
        
        ##
        if self["package-path"] and self.rep.isdir(self["package-path"])==True:
            packageNode = True
        else:
            packageNode = False
            self["package-path"] = ""
        
        ##
        self._getManifest()             ##
        self._executeFunction()         ##
        
        if packageNode==True and self["body"]==None:
            if self.currentNode==None or self.currentNode=="default.htm":
                self._default_htm()     ##
            elif self.currentNode=="toc.htm":
                self._toc_htm()         ##
        
        if self["title"]==None:
            self["title"] = title
    

# ++++ Extra ICE Function ++++
if True:
    def displayIf(self):
        return self.xhtmlTemplate != "template.xhtml"
    addFunction(func=mailThis, position=15, postRequired=True, label="Email", title="Email this", displayIf=displayIf)
    
    addFunction(func=publishThis, position=31, postRequired=True, label="Atom Pub", title="Publish this using AtomPub")





