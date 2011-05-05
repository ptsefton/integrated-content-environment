
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

import textile

pluginName = "ice.render.textile"
pluginDesc = "Textile rendere"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginClass = TextConverter
    pluginFunc = None
    pluginInitialized = True
    return pluginFunc



class TextConverter(object):
    fromToExts = {".textile":(".htm",), ".txtl":(".htm",)}
    
    def __init__(self, iceContext):
        self.iceContext = iceContext
    
    
    def render(self, item, convertedData, **kwargs):
        absFile = item._absPath
        text = self.iceContext.fs.readFile(absFile)
       
        html = textile.textile(text)
        #print "HTML: " + html
        #html = "<div>%s</div>" % html
        convertedData.addMeta("title", "A text document")
        convertedData.addRenditionData(".xhtml.body", html)
        return convertedData


