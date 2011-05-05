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


pluginName = "ice.render.SVG"
pluginDesc = "Scalable Vector Graphics renderer"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginClass = SvgConverter
    pluginFunc = None
    pluginInitialized = True
    return pluginFunc



class SvgConverter(object):
    fromToExts = {".svg":[".htm", ".pdf", ".png"]}
    
    def __init__(self, iceContext):
        self.viewableIcon = True
        self.iceContext = iceContext
    
    
    def render(self, item, convertedData, **kwargs):
        absPath = item._absPath
        
        SVGConverter = self.iceContext.getPlugin("ice.extra.SVGConverter").pluginClass
        converter = SVGConverter(self.iceContext)
        html = converter.getHtml(absPath)
        convertedData.addRenditionData(".xhtml.body", html)
        
        try:
            pdfData = converter.convert(absPath, {"format": "pdf"})
            pngData = converter.convert(absPath, {"format": "png"})
            convertedData.addRenditionData(".pdf", pdfData)
            convertedData.addRenditionData(".png", pngData)
        except Exception, e:
            convertedData.exception = e
            convertedData.addErrorMessage(str(e))
        
        return convertedData
    
