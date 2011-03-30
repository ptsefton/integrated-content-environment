
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

pluginName = "ice.dirNav"
pluginDesc = "dirNav"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = dirNav
    pluginClass = None
    pluginInitialized = True
    return pluginFunc


# Directory navigation for exportVersion and when in a none-package-directory
def dirNav(iceContext, item):
    excludeFiles = ["imscp_rootv1p1.dtd", "favicon.ico"]
    ## Not Found 
    ## make all links relative to item.uri (and not item.relPath as is currently)
    if item.isDir:
        html = "<ul>"
        if item.relPath=="/":
            html += "<li class='app-parent-inactive'><span class='app-parent-inactive' "
            html +=   "title='Parent folder'><span>..</span></span></li>" 
        else:
            href = "../default.htm"
            html += "<li class='app-parent'><a href='%s' class='app-parent' " % href
            html +=   "title='Parent folder'><span>../</span></a></li>"
        for i in item.listItems():
            if i.name in excludeFiles:
                continue
            rawFile, ext = iceContext.fs.splitExt(i.relPath)
            itemName = i.getMeta('title')
            if itemName is None:
                itemName = i.name
            #else:
            #    itemName += " (" + i.name + ")"
            if ext == iceContext.oooDefaultExt:
                ext = '.htm'
                itemPath = rawFile + ext
                i = iceContext.rep.getItem(itemPath)
            if i.hasHtml:
                itemPath = iceContext.fs.splitExt(i.relPath)[0] + ".htm"
            if i.isDir:
                html += "<li><a href='%sdefault.htm'>%s</a></li>" % (i.relPath, itemName)
            elif iceContext.rep.mimeTypes.has_key(ext):
                html += "<li><a href='%s'>%s</a></li>" % (i.relPath, itemName)
            else:
                html += "<li>%s</li>" % i
        html += "</ul>"
        title = " : - %s" % item.relPath
        body = html
    return title, body

#        if self.body is not None:
#            self.body += body
#        else:
#            self.body = body
#        if self.title is not None:
#            self.title += title








