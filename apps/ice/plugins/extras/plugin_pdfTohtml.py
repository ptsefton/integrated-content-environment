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

""" Plugin to convert pdf to images and producing html output
supported extension: pdf

Dependencies: plugin_pdf_utils.py to do the conversion
"""

pluginName = "ice.converter.pdfTohtml"
pluginDesc = "Converting pdf to images and producing html output"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method

def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = None
    pluginClass = PdfToHtml
    pluginInitialized = True
    return pluginFunc

class PdfToHtml(object):
    exts = [".pdf"]
    
    def __init__(self, iceContext, **kwargs):
        self.iceContext = iceContext
        self.__fs = self.iceContext.fs

    def convert(self, fromToObj, toDir, options, **kwargs):
        """ converting pdf to html
            @param fromToObj: pdf full path
            @type fromToObj: String
        """
        
        if self.__fs.isFile(fromToObj):
            path, name, ext = self.__fs.splitPathFileExt(fromToObj)
            name = name.replace(" ", "_")
            #imagesFolder = self.iceContext.fs.join(path, name + "_files")
            imagesFolder = self.iceContext.fs.join(toDir, name + "_files")
            if self.iceContext.fs.isDirectory(imagesFolder):
                self.iceContext.fs.delete(imagesFolder)
            self.iceContext.fs.makeDirectory(imagesFolder)
            pdfUtilsPlugin = self.iceContext.getPlugin("ice.pdfUtils").pluginClass(self.iceContext.fs)
            imageMagickClass = pdfUtilsPlugin.imageMagickConverter(self.iceContext, imagesFolder, fromToObj)
            count, result = imageMagickClass.convertingPdfToImages()
            html="<html><head><title>%s</title></head><body><div class='body'>" % name
            #print "result= %s and count= %s" % (result, count)
            if result == "ok":
                for x in range(count):
                    html += "<h1>Page %s</h1>" % str(x+1)
                    html += "<p><img src='%s_files/%s%s.jpg' /></p>" % (name, name, str(x+1))
                #create the html page
                html += "</div></body></html>"
                return "ok", html
        else:
            return None

