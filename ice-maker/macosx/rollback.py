#
#    Copyright (C) 2006  Distance and e-Learning Centre, 
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


import pysvn
import os

os.system("open /Applications/Utilities/Console.app")

client = pysvn.Client()
report = ""

print "Rolling back ICE to the previous release........ Please wait."
try:
    client.cleanup('../../../../Ice.app')
    client.cleanup('../../../../setup')   
    client.revert('../../../../Ice.app')
    client.revert('../../../../setup')
except Exception, e:
    #print "Reverting changed files first: %s" % str(e)
    report = str(e)

try:        
    result = client.update('../../../../Ice.app', revision=pysvn.Revision(pysvn.opt_revision_kind.previous), recurse=True)
    print "Rolling back Ice.app %s" % str(result)
except Exception, e:
    print "Error rolling back ICE: %s" % str(e)

try:    
    result = client.update('../../../../setup', revision=pysvn.Revision(pysvn.opt_revision_kind.previous), recurse=True)
    print "Rolling back setup %s" % str(result)
except Exception, e:
    print "Error rolling back the setup folder: %s" % str(e)

print "Completed rollback."    