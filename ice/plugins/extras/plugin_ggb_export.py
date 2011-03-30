#!/usr/bin/python
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

""" Extra Plugin to export .ggb Geogebra document
@requires: Geogebra U{http://www.geogebra.org}
@requires: os, tempfile, Image, ImageChops, StringIO
@requires: http_util    from utils/http_util.py
"""
import os, tempfile
import Image, ImageChops
from StringIO import StringIO
from http_util import Http


pluginName = "ice.extra.geoGebraExport"
pluginDesc = "geo gebra export"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    """ plugin declaration method 
    @param iceContext: IceContext type
    @param kwargs: optional list of key=value pair params
    @return: handler object
    """
    global pluginFunc, pluginClass, pluginInitialized
    ggb = GeoGebraExport(iceContext)
    pluginFunc = ggb.createPreviewImage
    pluginClass = GeoGebraExport
    pluginInitialized = True
    return pluginFunc



class GeoGebraExport(object):
    """ Base class for GeoGebraExport to export geogebra document"""
    def __init__(self, iceContext, remoteServiceUrl=None):
        """ GeoGebraExport Constructor method
        @param iceContext: Current ice context
        @type iceContext: IceContext 
        @param remoteServiceUrl: Remote ice-service site
        @type remoteServiceUrl: String
        @rtype: void
        """
        self.iceContext = iceContext
        if remoteServiceUrl == None:
            self.__remoteServiceUrl = "http://ice-service.usq.edu.au/api/convert"
        else:
            self.__remoteServiceUrl = remoteServiceUrl
        self.croppedWidth = None
        self.croppedHeight = None
    
    @staticmethod
    def getAppletHtml(ggbFile, width, height, archive="geogebra.jar"):
        """ get the applet tag element for the ggb File
        @param ggbFile: absolute path of geogebra file
        @type ggbFile: String
        @param width: width for the applet
        @type width: String
        @param height: height for the applet
        @type height: String
        @param archive: jar file to support the ggbFile
        @param archive: String 
        @rtype: String
        @return: applet tag that contains ggb File
        """
        html  = '<applet name="ggbApplet" code="geogebra.GeoGebraApplet" archive="%s" width="%s" height="%s">'
        html += '<param name="filename" value="%s" />'
        html += '<param name="framePossible" value="false" />'
        html += '<param name="showResetIcon" value="false" />'
        html += '<param name="enableRightClick" value="false" />'
        html += '<param name="showMenuBar" value="false" />'
        html += '<param name="showToolBar" value="false" />'
        html += '<param name="showToolBarHelp" value="false" />'
        html += '<param name="showAlgebraInput" value="false" />'
        html += '</applet>'
        return html % (archive, width, height, ggbFile)
    
    @staticmethod
    def cropImage(image, bgColor = (255, 255, 255)):
        """ cropping the give Image
        @param image: image file need to be cropped
        @type image: String
        @param bgColor: optional background color for the image
        @type bgColor: tuple of three
        @rtype: Image or None 
        @return: image data if successfully cropped or None if not
        """
        if image.mode != "RGB":
            image = image.convert("RGB")
        bg = Image.new("RGB", image.size, bgColor)
        diff = ImageChops.difference(image, bg)
        bbox = diff.getbbox()
        if bbox:
            return image.crop(bbox)
        return None
    
    def createPreviewImage(self, urlOrData, format, width = None, height = None):
        """ create the preview for the converted image
        @param urlOrData: url or data to be converted
        @type urlOrData: String
        @param format: format of the urlOrData
        @type format: String 
        @param width: width of the preview
        @type width: String
        @param height: height of the preview
        @type height: String
        @rType: String
        @return: Content of the preview
        """
        self.__cmdPath = self.__getLocalService(format)
	if width == None:
            width = 500
        if height == None:
            height = 500
        if self.__cmdPath != None:
            print 'Local mode using %s' % self.__cmdPath
            if self.__isUrl(urlOrData):
                data, _, errCode, msg = Http().get(urlOrData, includeExtraResults=True)
                if errCode == -1:
                    raise Exception("Failed to read data from %s, %s" % (data, msg))
            else:
                data = urlOrData
            return self.__createPreviewLocal(data, format, width, height)
        else:
            if self.__remoteServiceUrl == None:
                raise Exception('GeoGebra services unavailable')
            print 'Remote mode using: %s' % self.__remoteServiceUrl
            return self.__createPreviewRemote(urlOrData, format, width, height)
    
    def __createPreviewLocal(self, data, format, width, height):
        """ create a local preview
        @param data: data of the ggb file
        @type data: String
        @param format: format of the ggb file
        @type format: String
        @param width: width of the preview
        @type width: 
        """
        ifd, inputFile = tempfile.mkstemp(".tmp", "gg")
        os.write(ifd, data)
        os.close(ifd)
        
        ofd, outputFile = tempfile.mkstemp("." + format.lower(), "gg")
        os.close(ofd)
        self.__invokeExport(inputFile, outputFile, format, width, height)
        f = open(outputFile, "rb")
        content = f.read()
        f.close()
        
        return content
    
    def __createPreviewRemote(self, urlOrData, format, width, height):
        baseUrl = self.__remoteServiceUrl
        postData = [('format', format), ('width', width), ('height', height)]
        if self.__isUrl(urlOrData):
            postData.append(('url', urlOrData))
        else:
            postData.append(('file', ('preview.ggb', urlOrData)))
        content = Http().post(baseUrl, postData)
        if format == "png":
            cropped = self.__cropImage(StringIO(content), width, height)
            if cropped is not None:
                pngFile = StringIO()
                cropped.save(pngFile, "PNG")
                pngFile.flush()
                pngFile.seek(0)
                content = pngFile.read()
        return content
    
    def __invokeExport(self, inputFile, outputFile, format, width, height):
        try:
            exportCmd = self.__getExportCmd()
            self.iceContext.system.execute2(exportCmd, inputFile, outputFile, "all",width,height, printErr = False)
            if format == "png":
                cropped = self.__cropImage(outputFile, width, height)
                if cropped is not None:
                    cropped.save(outputFile)
        except Exception, e:
            print "Failed to create preview: %s" % str(e)
    
    def __cropImage(self, outputFile, width, height):
        srcImage = Image.open(outputFile)
        cropped = GeoGebraExport.cropImage(srcImage)
        if cropped is not None:
            self.croppedWidth = cropped.size[0] + 50
            self.croppedHeight = cropped.size[1] + 50
            if width is not None and height is not None:
                print "resizing to", width, "x", height
                cropped.thumbnail((int(width), int(height)), Image.ANTIALIAS)
            return cropped
        return None
    
    def __isUrl(self, url):
        if type(url)==str:
            return url.startswith('http://') or url.startswith('https://')
        return False
    
    def __getLocalService(self, format):
        try:
            return self.__getExportCmd()
        except Exception, e:
            print str(e)
        return None
    
    def __getExportCmd(self):
        return self.__getCmd("GEOGEBRA_HOME", "ggexport", "GeoGebra")
    
    def __getCmd(self, homeEnv, cmd, desc):
        home = self.iceContext.system.environment.get(homeEnv, "")
        if home == '':
            raise Exception("%s is not set" % homeEnv)
        else:
            cmdPath = "%s/%s" % (home, cmd)
            cmdPath = cmdPath.replace("//", "/")
        if self.iceContext.fs.exists(cmdPath):
            return cmdPath
        else:
            raise Exception("No %s installation in %s" % (desc, home))
    
    def __call__(self, urlOrData, format, width = None, height = None):
        return self.createPreviewImage(urlOrData, format, width, height)
    
