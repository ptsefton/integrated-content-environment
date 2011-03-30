 #!/usr/bin/python
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

from sys import path as sysPath
sysPath.append("../../utils")

import sys
import string, types
from cPickle import loads, dumps
from file_system import FileSystem
from system import system as _system

from mockSvn import *



class MockSimpleClient(object):
    __fs = FileSystem()
    def __init__(self, path=None, fs=None, create=False):
        if fs is not None:
            self.__fs = fs
        else:
            self.__fs = self.__fs.clone()
        if path is None:
            path = self.__fs.absolutePath(".")
        self.__path = path
        self.__infosObjs = {}
        
    
    # file = file|path list
    def add(self, file, recurse=True):
        pass
    
    def commit(self, file, recurse=True):
        pass
    
    def delete(self, file, recurse=True):
        pass
    
    #def info(self, file, recurse=False):
    #    pass
    
    def list(self, file, recurse=False):
        pass
    
    def status(self, file, recurse=False):
        pass
    
    #def mkdir(self, file):
    #    pass
    
    def revert(self, file, recurse=True):
        pass
    
    def update(self, file, recurse=True):
        pass
    
    #def export(self, file, recurse=True):
    #    # copy - but do not copy the .mockSvn directories
    #    pass
    
    def log(self, file, limit=10):    # can give log for only one item
        pass
    
    #def copy(self, src, dest):
    #    pass
    
    #def move(self, src, dest):
    #    self.copy(src, dest)
    #    self.delete([src])
    
    def flush(self):
        
    
    def __getNameAndPath(self, file):
        path, name = self.__fs.split(file)
        return path, name
    
    def __getInfosObject(self, path):
        absPath = self.__fs.absolutePath(path)
        infos = self.__infosObjs.get(absPath, None)
        if infos is None:
            infos = MockSvnInfos.load(path=absPath, fs=self.__fs)
            self.__infosObjs[absPath] = infos
        return infos
    


if __name__=="__main__":
    args = list(sys.argv)
    args.pop(0)
    print "args = '%s'" % str(args)
    #client = MockSimpleClient()



