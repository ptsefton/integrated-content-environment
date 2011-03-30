#
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

print "=== Using the Default site2.1.py file! ==="
# iceContext is only in scope at this level (Note: not global)


class IceSiteMap(IceSite):
    def __init__(self, iceContext, *args, **kwargs):
        IceSite.__init__(self, iceContext, *args, **kwargs)
    
    
    def mapPath(self, nodeMapper):
        # returns (title, packagePath)
        title = "Ice web application"
        packagePath = ""
        
        # while it is not 'package', 'Package', 'packages' or 'Packages' - skip  
        while nodeMapper.renode("^(?!(P|p)ackages?$).*$", "parent"): pass
        if nodeMapper.node('packages') or nodeMapper.node('Packages'):
            title = "Packages"
            if nodeMapper.renode('^.*$', 'code'):
                packagePath = nodeMapper.pathToHere
        elif nodeMapper.node('package') or nodeMapper.node('Package'):
            title = "Package"
            packagePath = nodeMapper.pathToHere
        
        return (title, packagePath)
    
    
    def custom(self, *args, **kwargs):
        pass





