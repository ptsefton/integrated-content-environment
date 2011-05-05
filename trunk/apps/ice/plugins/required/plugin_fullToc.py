
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
import types

pluginName = "ice.fullToc"
pluginDesc = "Full TOC"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = fullToc
    pluginClass = None
    pluginInitialized = True
    return pluginFunc


def fullToc(iceContext, packageItem):
    # results = title, body, pdfRenditionLink
    manifest = packageItem.getMeta("manifest")
    #manifest.updateItems(packageItem)
    if manifest is None:
        raise Exception("manifest is NONE for packageItem")
    else:
        title = manifest.title
    if title is None:
        title = "Untitled!"
    def getHtmlList(item):
        htmlList = ""
        lItems = []
        for child in item.children:
            if child.isHidden:
                continue
            subList = getHtmlList(child)
            href = child.renditionName
            href = iceContext.urlQuote(href)
            title = iceContext.escapeXmlAttribute(child.title)
            if type(title) is types.UnicodeType:
                title = title.encode("utf-8")
            li = "<li><a href='%s'>%s</a>%s</li>" % (href, title, subList)
            lItems.append(li)
        if lItems!=[]:
            htmlList = "<ul style='list-style-type: none;'>%s</ul>" % ("\n".join(lItems))
        return htmlList
    body = getHtmlList(manifest)
    return title, body
    

## IMS Manifest TOC
def fullImsToc(iceContext, mf, uri, packagePath):
    # results = title, body, pdfRenditionLink
    title = mf.defaultOrganization.title
    mainToc = mf.defaultOrganization.getHtmlList(recurse=True)
    body = mainToc
    if mainToc=="":
        msg =  "*** toc.htm in package(manifest ok) but defaultOrganization failed to get HTML list!"
        iceContext.writeln(msg)
        body = "<div>Manifest defaultOrganization failed to get HTML list!</div>"
        raise Exception("Manifest defaultOrganization failed to get HTML list!")
    return title, body
fullImsToc.toc = fullToc

fullToc.fullImsToc = fullImsToc









