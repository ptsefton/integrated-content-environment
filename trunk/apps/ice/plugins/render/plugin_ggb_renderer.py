
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


pluginName = "ice.render.GeoGebra"
pluginDesc = "GeoGebra renderer"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginClass = GgbConverter
    pluginFunc = None
    pluginInitialized = True
    return pluginFunc



class GgbConverter(object):
    fromToExts = {".ggb":[".htm", ".png", ".pdf"]}
    
    def __init__(self, iceContext):
        self.viewableIcon = True
        self.iceContext = iceContext
    
    
    def render(self, item, convertedData, **kwargs):
        file = item.relPath
        absPath = item._absPath
        _, name, ext = self.iceContext.fs.splitPathFileExt(absPath)
        fileData = self.iceContext.fs.readFile(absPath)
        
        GeoGebraExport = self.iceContext.getPlugin("ice.extra.geoGebraExport").pluginClass
        util = GeoGebraExport(self.iceContext, self.iceContext.settings.get('convertUrl'))
        try:
            pngData = util.createPreviewImage(fileData, 'png', '500', '500')
            convertedData.addRenditionData(".png", pngData)
            pdfData = util.createPreviewImage(fileData, 'pdf')
            convertedData.addRenditionData(".pdf", pdfData)
        except:
            pass
        
        width = util.croppedWidth
        height = util.croppedHeight
        
        if width is None:
            width = 500
        if height is None:
            height = 500
        # see if there is ggb local. 
	archive = self.iceContext.system.environment.get("GEOGEBRA_HOME", "")
        if archive == "":
	    appletHtml = GeoGebraExport.getAppletHtml(name + ext, width, height)
	else:
	    if archive.endswith("/"):
		archive = archive[:-1]
	    archive = "file://"+archive+"/geogebra.jar"
            appletHtml = GeoGebraExport.getAppletHtml(name + ext, width, height,archive)
        
        convertedData.addRenditionData(".xhtml.body", appletHtml)
        convertedData.addRenditionData(".xhtml.embed", appletHtml)
        
        return convertedData
    
