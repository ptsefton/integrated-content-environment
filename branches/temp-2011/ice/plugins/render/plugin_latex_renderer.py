
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

from glob import glob

pluginName = "ice.render.latex"
pluginDesc = "LaTeX Renderer"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginClass = TexConverter
    pluginFunc = None
    pluginInitialized = True
    return pluginFunc



class TexConverter(object):
    fromToExts = {".tex":[".htm", ".pdf"]}
    
    def __init__(self, iceContext):
        self.iceContext = iceContext
    
    
    def render(self, item, convertedData, **kwargs):
        file = item.relPath
        absPath = item._absPath
        
        tmpFs = self.iceContext.fs.createTempDirectory()
        toDir = tmpFs.absPath()
        tex4html = self.iceContext.getPlugin("ice.extra.LaTeXConverter").pluginFunc
        status, htmlFile, pdfFile = tex4html(absPath, toDir)
        
        if status == "ok":
            htmlData = tmpFs.readFile(htmlFile)
            pdfData = tmpFs.readFile(pdfFile)
            
            for srcImage in glob("%s/*.png" % toDir):
                _, filename = self.iceContext.fs.split(srcImage)
                destImage = convertedData.abspath(filename)
                self.iceContext.fs.copy(srcImage, destImage)
                convertedData.addImageFile(filename, destImage)
            
            _, name, _ = self.iceContext.fs.splitPathFileExt(absPath)
            prefix = name + "_files/"
            et = self.iceContext.ElementTree.XML(htmlData)
            for img in et.findall(".//img"):
                img.set('src', prefix + img.get('src'))
            html = self.iceContext.ElementTree.tostring(et)
            
            convertedData.addRenditionData(".xhtml.body", html)
            convertedData.addRenditionData(".pdf", pdfData)
            
            tmpFs.delete()
        else:
            logData = tmpFs.readFile(htmlFile)
            convertedData.addRenditionData(".xhtml.body", logData)
            print "Warning: LaTeX conversion failed: ", status
        
        return convertedData
