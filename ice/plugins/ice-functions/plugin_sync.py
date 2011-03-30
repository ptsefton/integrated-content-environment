
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

pluginName = "ice.function.sync"
pluginDesc = ""
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method

## Not used any more!

def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = sync
    pluginClass = None
    pluginInitialized = True
    return pluginFunc



def isLoggedIn(self):
    return self.session.loggedIn


def sync(self):
    print "plugin sync"
    if self.isInPackage:
        path = self.packagePath
        item = self.rep.getItemForUri(path)
        print "Sync package-path = ", path
        msg = "Sync package completed."
    else:
        path = self["argPath"]
        item = self.rep.getItemForUri(path)
        print "Sync path=", item.relPath
        msg = "Sync '%s' completed." % item.relPath
    
    item.asyncSync(force=False, skipBooks=False)
    
    self["title"] = "Sync"
    #self["body"] = report.getAsHtml(all=True)
## Not used any more!
sync.options = {"toolBarGroup":"common", "position":3, "postRequired":False,
                "enableIf":isLoggedIn, 
                "label":"_Sync", "title":"Synchronize content with the server and other users"}









