#!/usr/bn/env python
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

from svc_util import SvcUtil


# deligate most of the work to the DirInfo objects (except commit)

class SimpleVersionControl(object):
    # Constructor:
    #   __init__()
    # Properties:
    #   
    # Methods:
    #   
    def __init__(self, path):
        pass
    
    
    def add(self, recurse=False):
        pass
    
    
    def commit(self, recurse=True):
        # Fake
        pass
    
    
    def update(self, recurse=False, revNum=-1):
        # Fake  - always completes OK returning the currentRevNum
        pass
    
    
    def revert(self, recurse=False):
        pass
    
    
    def delete(self, force=True):
        pass
    
    
    def status(self, update=False):
        pass
    
    
    def info(self):
        pass

