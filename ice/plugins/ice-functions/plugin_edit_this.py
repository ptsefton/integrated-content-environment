
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

pluginName = "ice.function.editThis"
pluginDesc = ""
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = editThis
    pluginClass = None
    pluginInitialized = True
    return pluginFunc



def isEditable(self):
    return self.isDocView


def editThis(self):
    argPath = self.formData.value("argPath")
    if argPath:
        path = argPath
    else:
        path = self.path
    item = self.rep.getItemForUri(path)
    absPath = item._absPath
    
    if self.iceContext.isServer:
        print " ** editThis() server version **"
        return
    print "*** editThis() ***"
    
    appsExts = {}
    system = self.iceContext.system
    if system.isLinux:
        oooPath = self.iceContext.settings.get("oooPath")
        soffice = "soffice"
        if oooPath!="":
            soffice = self.iceContext.url_join(oooPath, "program", soffice)
        appsExts = {soffice:[self.iceContext.oooDefaultExt, self.iceContext.wordExt, \
                            self.iceContext.oooMasterDocExt, self.iceContext.bookExts, \
                            self.iceContext.word2007Ext, self.iceContext.wordDotExt]}
    system.startFile(absPath, appsExts=appsExts)
editThis.options={"toolBarGroup":"common", "position":4, "postRequired":True,
                    "enableIf":isEditable, "label":"_Edit", "title":"Edit this document."}









