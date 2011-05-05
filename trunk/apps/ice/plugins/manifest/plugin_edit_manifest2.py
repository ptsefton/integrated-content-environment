
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
import time
import copy

#from ims_organizer import ImsOrganizer


pluginName = "ice.function.editManifest"
pluginDesc = "Manifest editor"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method
path = None


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized, path
    path = iceContext.fs.split(__file__)[0]
    #ImsOrganizer.myPath = path
    pluginFunc = editManifest
    pluginClass = None
    pluginInitialized = True
    iceContext.ajaxHandlers["manifest"] = ajaxCallback
    return pluginFunc


def ajaxCallback(iceContext):
    #print "manifest ajaxCallback"
    mimeType = "text/html"
    data = "<div>&#160;</div>"
    path = iceContext.path
    requestData = iceContext.requestData
    cmd = requestData.value("cmd", "")
    arg1 = requestData.value("arg1", "")
    arg2 = requestData.value("arg2", "")
    packageItem = iceContext.rep.getItem(path)
    manifest = packageItem.getMeta("manifest")
    if manifest is None:
        packageItem = packageItem.parentItem
        manifest = packageItem.getMeta("manifest")
    if manifest is not None:
        #print "*Ajax - loaded manifest ok"
        srcId = arg1.split("_")[-1]
        mItem = manifest.getManifestItem(srcId)
        destId = arg2.split("_")[-1]
        if srcId=="root":
            if cmd=="home" or cmd=="updateTitle":
                mItem = manifest
        if destId=="":
            destId = None
        if mItem is not None:
            if cmd=="home":
                if arg2.lower()=="true":
                    manifest.homePageItem = mItem
                else:
                    manifest.homePageItem = None
            elif cmd=="hide":
                mItem.isHidden = (arg2.lower()=="true")
            elif cmd=="dropBefore":
                manifest.insertBefore(destId, srcId)
            elif cmd=="dropInto":
                manifest.addTo(destId, srcId)
            elif cmd=="dropAdd":
                manifest.addTo(destId, srcId)
            elif cmd=="updateTitle":
                title = arg2.strip()
                if arg2=="":
                    arg2 = None
                arg2 = iceContext.cleanUpString(arg2)
                mItem.manifestTitle = arg2
        packageItem.setMeta("manifest", manifest)
        packageItem.flush(True)
        #
        plugin = iceContext.getPlugin("ice.contextToc")
        data = plugin.pluginFunc(iceContext, packageItem)
        #
    #print "*** manifest ajax callback cmd='%s', arg1='%s', arg2='%s', path='%s'" % (cmd, arg1, arg2, path)
    return data, mimeType



def isPackage(self):
    return self.isPackage    


# Organize (manifest)
def editManifest(self):
    templatePath = self.iceContext.fs.join(path, "manifest.tmpl")
    #__refresh(self)
    print "editManifest() path='%s', packagePath='%s'" % (self.path, self.packagePath)
    plugin = self.iceContext.getPlugin("ice.manifest")
    if plugin is None:
        print "Failed to find 'ice.manifest' plugin!"
        return
    packageItem = self.packageItem
    if packageItem is None:
        print "*** packageItem is None!"
        return
    manifest = packageItem.getMeta("manifest")
    if manifest is None:
        manifest = plugin.pluginClass(self.iceContext)
        packageItem.setMeta("manifest", manifest)
    st = time.time()
    manifest.updateItems(packageItem)
    packageItem.flush(True)
    print "updated manifest in '%s'" % (time.time()-st)
    
    #for child in manifest.children:
    #    print "%s - title='%s', isHidden=%s, %s" % (child.relPath, child.title, child.isHidden, child.itemGuid)
    self['title'] = "Package Organizer"
    
    # AJAX methods
    # manifest.addTo(addToItemGuid, itemGuid)
    # manifest.insertBefore(beforeItemGuid, itemGuid)
    #  manifestItem.title = setValue        manifest.setTitle(itemGuid, title)
    #  manifestItem.isHidden = setValue     manifest.setHidden(itemGuid, hidden)
    htmlTemplate = self.iceContext.HtmlTemplate(templatePath)
    manifest = copy.copy(manifest)
    
    children = manifest.children
    mediaChildren = [child for child in children if child.relPath.find("media/")!=-1]
    for child in mediaChildren:
        manifest._children.remove(child)
    def htmlSafe(s):
        s = self.iceContext.escapeXmlAttribute(s)
        s = self.iceContext.cleanUpString(s)
        return s
    d = {
            "manifest":manifest,
            "mItems":manifest.children,
            "asHtml":htmlSafe,
        }

    html= htmlTemplate.transform(d, allowMissing=True)
    self["body"]=html
    self["appStyleCss"] += htmlTemplate.includeStyle

editManifest.options={"toolBarGroup":"common", "position":14, "postRequired":False,
                    "enableIf":isPackage, "label":"_Organizer",
                    "title":"Organize content and edit titles",
                    "destPath":"%(package-path)s"+"editManifest"
                    }
    







