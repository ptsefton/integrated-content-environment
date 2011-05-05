
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

pluginName = "ice.navButtons"
pluginDesc = "Context navigation buttons"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = getNavButtons
    pluginClass = None
    pluginInitialized = True
    return pluginFunc


def getNavButtons(iceContext, manifest, currentItemGuid, isTocPage, packagePath):
    # get manifest item for current path
    urlJoin = iceContext.urlJoin
    mItem = None
    nextMItem = None
    previousMItem = None
    parentMItem = None
    html = ""
    countl = [0]

    def getNextVisibleItem(mItem, depthFirst=True):
        nextMItem = None
        if mItem.hasChildren and depthFirst:
            nextMItem = mItem.children[0]
        else:
            p = manifest.getParentOf(mItem)
            if p is not None:
                children = p.children
                i = children.index(mItem)+1
                if len(children)>i:
                    nextMItem = children[i]
                    # This is to solve a stack-overflow (recursion-depth) 
                    #  when there are thousands of hidden item  
                    while nextMItem.isHidden and len(children)>(i+1):
                        i += 1
                        nextMItem = children[i]
                    #
                else:   # else my parent next sibling
                    nextMItem = getNextVisibleItem(p, False)
        if nextMItem is not None:
            if nextMItem.isHidden or not nextMItem.renditionName.endswith(".htm"):
                #print "renditionName='%s' %s" % (nextMItem.renditionName, countl[0])
                nextMItem = getNextVisibleItem(nextMItem, False)
        return nextMItem
    
    def getPreviousVisibleItem(mItem):
        #print "*** getPreviousVisibleItem(%s)" % mItem
        done = False
        currentMItem = mItem
        previousMItem = None
        while not done:
            p = manifest.getParentOf(currentMItem)
            if p is not None:
                children = p.children
                i = children.index(currentMItem)
                if i==0:
                    previousMItem = p
                else:
                    previousMItem = children[i-1]
                #print previousMItem
                if previousMItem is not None and previousMItem.isHidden \
                        or not previousMItem.renditionName.endswith(".htm"):
                    currentMItem = previousMItem
                else:
                    done = True
            else:
                done = True
        return previousMItem

#        if p is not None:
#            children = p.children
#            i = children.index(mItem)
#            if i==0:
#                previousMItem = p
#            else:
#                previousMItem = children[i-1]
#        if previousMItem is not None:
#            if previousMItem.isHidden or not previousMItem.renditionName.endswith(".htm"):
#                previousMItem = getPreviousVisibleItem(previousMItem)
#        return previousMItem
    
    mItem = manifest.getManifestItem(currentItemGuid)
    
    if mItem is None:
        if isTocPage and manifest.children!=[]:
            nextMItem = manifest.children[0]
            if nextMItem.isHidden:
                nextMItem = getNextVisibleItem(nextMItem)
    else:
        nextMItem = getNextVisibleItem(mItem)
        previousMItem = getPreviousVisibleItem(mItem)
        parentMItem = manifest.getParentOf(mItem)
        if (nextMItem is None) and (parentMItem is not None):       # Next = TOC
            nextMItem = parentMItem
        if (previousMItem is None) and (parentMItem is not None):   # Previous = TOC
            previousMItem = parentMItem
    
    def getImage(mItem, name):
        def getImageLink(path, href, imageName, title):
            " Note: the imageName is the image name without the '.gif' extension "
            html = "<a href='%s' title='%s'><img style='border:0px' src='%s.gif' alt='%s'/></a>"
            html = html % (href, title, urlJoin(path, "skin/" + imageName), imageName)
            html += "&#160;"
            return html
        
        def getInactiveImage(path, imageName):
            html = "<img style='border:0px' src='%s.gif' alt='inactive %s'/>"
            html = html % (urlJoin(path, "skin/inactive_" + imageName), imageName)
            html += "&#160;"
            return html
        
        if mItem is None:
            html = getInactiveImage(packagePath, name)
        else:
            if mItem.relPath=="":
                html = getImageLink(packagePath, 
                        urlJoin(packagePath, "toc.htm"), name, "Contents")
            else:
                href = mItem.renditionName
                title = mItem.title
                try:
                    href = href.encode("utf-8")
                except: pass
                try:
                    title=title.encode("utf-8")
                except: pass
                title = iceContext.textToHtml(title)
                html = getImageLink(packagePath, 
                        urlJoin(packagePath, href), name, title)
        return html
    html += getImage(previousMItem, "previous")
    html += getImage(parentMItem, "up")
    html += getImage(nextMItem, "next")
    if False:
        print "   mItem='%s'" % str(mItem)
        print "   nextMItem '%s'" % nextMItem
        print "   previousMItem '%s'" % previousMItem
        print "   parentMItem '%s'" % parentMItem
    
    if html!="":
        html = "<div>\n" + html + "\n</div>\n"
    return html
    









