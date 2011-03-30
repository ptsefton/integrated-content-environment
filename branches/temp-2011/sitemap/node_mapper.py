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


import re

 
class NodeMapper(object):
    def __init__(self, path="/", varDict={}):
        self.__pathArray = []
        self.__currentNode = ""
        self.__pathToHere = ""
        self.__dict = varDict
        
        self.__path = path.rstrip("/")
        self.__pathArray = self.__path.split("/")
        self.__pathArray.pop(0)     # ignore the first item
        self.__getNextNode()        # prime
    
    
    @property
    def path(self):
        return self.__path
    
    @property
    def pathToHere(self):
        return self.__pathToHere
    
    @property
    def currentNode(self):
        return self.__currentNode
    
    
##    # Used by get function name only        ## Not needed any more
#    def removeLastPathNode(self):
#        if len(self.__pathArray)==0:
#            self.__currentNode = None
#        else:
#            self.__pathArray.pop(-1)

    def __getitem__(self, name):
        return self.__dict.get(name, "")
    
    
    def __setitem__(self, name, value):
        self.__dict[name] = value
    
    
    def get(self, name):
        return self.__dict.get(name, "")
    
    
    def node(self, name):
        if self.__currentNode==None:
            return False
        if self.__currentNode==name:
            self.__getNextNode()
            return True
        else:
            return False

    
    def renode(self, pattern, varName=None):
        if self.__currentNode==None or self.__currentNode=="":
            return False
        # HACK: This hack is so that default.htm etc is not treated as a node
        if self.__currentNode.endswith(".htm"):
            return False
        if re.search(pattern, self.__currentNode):
            if varName is not None:
                self.__dict[varName] = self.__currentNode
            self.__getNextNode()
            return True
        else:
            return False

    
    def fnnode(self, f, varName=None):
        if self.__currentNode==None:
            return False
        if f(self.__currentNode):
            if varName is not None:
                self[varName] = self.__currentNode
            self.__getNextNode()
            return True
        else:
            return False

    
    def nonode(self):
        return self.__currentNode==None

    
    def __getNextNode(self):
        if self.__currentNode!="":
            self.__pathToHere += "/" + self.__currentNode
        if len(self.__pathArray) > 0:
            self.__currentNode = self.__pathArray.pop(0)
        else:
            self.__currentNode = None
    

