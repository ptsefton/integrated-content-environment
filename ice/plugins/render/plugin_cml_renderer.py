
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

import Image
from StringIO import StringIO


pluginName = "ice.render.CML"
pluginDesc = "Chemical Markup Language renderer"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method

CmlUtil = None


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginClass = CmlConverter
    pluginFunc = None
    pluginInitialized = True
    global CmlUtil
    CmlUtil = iceContext.getPlugin("ice.extras.cmlUtil").pluginClass
    return pluginFunc



class CmlConverter(object):
    fromToExts = {".cml":[".htm", ".pdf", ".png", ".svg"]}
    
    def __init__(self, iceContext):
        self.viewableIcon = True
        self.iceContext = iceContext
        self.__fs = iceContext.fs
    
    
    def render(self, item, convertedData, **kwargs):
        relPath = item.relPath
        path, name, _ = self.__fs.splitPathFileExt(relPath)
        fileData = item.read()
        
        appletHtml = CmlUtil.getAppletHtml(relPath, 300, 300,
                                           archive=self.__fs.join(path, "JmolApplet.jar"))
        pngHtml = CmlUtil.getPngHtml(self.__fs.join(path, name + ".png"))
        if CmlUtil.isRenderable(fileData):
            if CmlUtil.is3D(fileData):
                bodyHtml = appletHtml
            else:
                bodyHtml = pngHtml
            convertedData.addRenditionData(".xhtml.body", bodyHtml)
            convertedData.addRenditionData(".xhtml.embed", bodyHtml)
            
            util = CmlUtil(self.iceContext, self.iceContext.settings.get('convertUrl'))
            svgData = util.createPreviewImage(fileData, 'svg')
            convertedData.addRenditionData(".svg", svgData)
            
            pngData = util.createPreviewImage(fileData, 'png', '300', '300')
            convertedData.addRenditionData(".png", pngData)
            
            # convert the png to pdf
            if pngData != "":
                image = Image.open(StringIO(pngData))
                pdfFile = StringIO()
                image.save(pdfFile, "PDF")
                pdfFile.flush()
                pdfFile.seek(0)
                convertedData.addRenditionData(".pdf", pdfFile.read())
        else:
            print "Warning: '%s' is not renderable!" % file
        
        return convertedData
    