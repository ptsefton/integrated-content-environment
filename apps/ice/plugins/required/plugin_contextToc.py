
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

import string

pluginName = "ice.contextToc"
pluginDesc = "Left (context) TOC"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = contextToc
    pluginClass = None
    pluginInitialized = True
    return pluginFunc


def contextToc(iceContext, packageItem, item=None):
    if item is None:
        item = packageItem
    packageRelPath = packageItem.relPath
    isTocPage = False
    toc = ""
    if packageItem is None:
        return "<div class='contextTOC'/>"
    manifest = packageItem.getMeta("manifest")
    if manifest is None:
        return "<div class='contextTOC'/>"
    toc = "<ul style='list-style-type: none;'><li class='nav-contents'>"
    if isTocPage:
        toc += "<span class='current-url'>Contents</span>"
    else:
        toc += "<a href='%stoc.htm'>Contents</a>" % (packageItem.relPath)
    toc += "</li></ul>\n"
    
    itemGuid = item.guid
    mItem = manifest.getManifestItem(itemGuid)
    if mItem is None:
        mItem = manifest
    def getList(item, keyItem=None):
        mfToc = ""
        for child in item.children:
            if child.isHidden:
                continue
            href = iceContext.escapeXmlAttribute(child.renditionName)
            title = iceContext.escapeXmlAttribute(child.title)
            subList = ""
            if child.hasChildren and (child==keyItem):
                subList = getList(child)
            href = packageRelPath + href.encode("utf-8")
            try:
                title = title.encode("utf-8")
            except: pass
            li = "\t<li><a href='%s'>%s</a>%s</li>\n" % (href, title, subList)
            mfToc += li
        if mfToc!="":
            mfToc = "\n<ul style='list-style-type: none;'>\n%s</ul>" % mfToc
        return mfToc
    parent = manifest.getParentOf(mItem)
    if parent is not None:
        if mItem.hasChildren:
            toc += getList(parent, mItem)
        else:
            gParent = manifest.getParentOf(parent)
            if gParent is not None:
                toc += getList(gParent, parent)
            else:
                toc += getList(parent, mItem)
    else:
        toc += getList(mItem, mItem)
    return "<div class='contextTOC'>\n%s</div>\n" % toc
    









