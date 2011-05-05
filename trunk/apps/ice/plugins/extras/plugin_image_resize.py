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

import json

""" Plugin to resize image files 
supported extension: png, jpg, gif, bmp and saved as jpg

Images can be processed by:
 * Resized based on Ratio provided
 * Resized based on fixed width
 * Cropped based on provided cropping coordinates
"""

pluginName = "ice.converter.imageResize"
pluginDesc = "Resizing images"
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
    pluginFunc = None
    pluginClass = ImageResize
    pluginInitialized = True
    return pluginFunc

class ImageResize(object):
    """ Base class for ImageResize 
    @ivar exts: Supported extension list 
    """ 
    exts = [".png", ".jpg", ".jpeg", ".gif", ".bmp"]
    
    def __init__(self, iceContext, **kwargs):
        """ Image Resize Constructor method 
        @param iceContext: Current ice context
        @type iceContext: IceContext 
        @rtype: void
        """
        self.iceContext = iceContext
        self.__fs = self.iceContext.fs

    def convert(self, fromToObj, options, toDir, **kwargs):
        """ converting image to sample size
            @param fromToObj: image full path
            @type fromToObj: String
            
            Image Resize variables:
            @var resizeTo: Ratio in percentage of resized image
                Calculation of new Image width and height:
                  New Image width = Current Image width *(100+resizeTo)/100)
                  New Image height = Current Image height *(100+resizeTo)/100)
            @var fixedWidth: Fixed Width of the resized image
                Calculation of new Image height:
                  New Image Height = (Current Image height * fixedWidth)/ Current Image width
                  
            Image cropping variables:
            @var left: left bottom coordinates
            @var upper: upper left coordinates
            @var right: right upper coordinates
            @var lower: lower right coordinates
                Calculation of new Image width and height:
                   New Image Width = right coordinates - left coordinates
                   New Image Height = lower coordinates - upper coordinates
            
            @var resizing: Set to true if it's resizing process, otherwise false 
            
            @rtype: String
            @return: outputFile name
        """

        if self.__fs.isFile(fromToObj):
            path, name, ext = self.__fs.splitPathFileExt(fromToObj)
            data = self.__fs.readFile(fromToObj)
            self.__imgObj = self.iceContext.IceImage(data)
            width, height = self.__imgObj.size

            multipleImageOptions = {}
            if options.has_key("multipleImageOptions"):
                multipleImageOptions = json.loads(options["multipleImageOptions"])
                
            imageOptions = {}
            if multipleImageOptions:
                #do multiple conversion here...
                for optionName in multipleImageOptions:
                    imageOptions = multipleImageOptions[optionName]
                    self.__resizing(fromToObj, imageOptions, toDir, optionName)
                return toDir
            else:
                #do normal conversion
                outputFile = self.__resizing(fromToObj, options, toDir)
                return outputFile
        else:
            return None
        
        
    def __resizing(self, fromToObj, imageOptions, toDir, optionName=""):
        #Setting default variable
        resizeTo = -50
        fixedWidth = 100
        left = 100
        upper = 100
        right = 400
        lower = 400
        resizing = True
        enlargeImage = True
        imgObj = None
        resizeOptions = imageOptions["option"]
        if resizeOptions == "ratio":
            if imageOptions["ratio"] != "": 
                resizeTo = int(imageOptions["ratio"])
        if resizeOptions == "fixedWidth":
            if imageOptions["fixedWidth"] != "":
                fixedWidth = int(imageOptions["fixedWidth"])
            if imageOptions["enlarge"] == "false":
                enlargeImage = False
        if resizeOptions == "crop":
            resizing = False
            if imageOptions["cropLeft"] != "":
                left = int(imageOptions["cropLeft"])
            if imageOptions["cropUpper"] != "":
                upper = int(imageOptions["cropUpper"])
            if imageOptions["cropRight"] != "":
                right = int(imageOptions["cropRight"])
            if imageOptions["cropLower"] != "":
                lower = int(imageOptions["cropLower"])
        
        if self.__fs.isFile(fromToObj):
            path, name, ext = self.__fs.splitPathFileExt(fromToObj)
            data = self.__fs.readFile(fromToObj)
            imgObj = self.iceContext.IceImage(data)
            width, height = imgObj.size
            
            if resizeOptions == "ratio":
                newWidth = int(width*(100+resizeTo)/100)
                newHeight = int(height*(100+resizeTo)/100)
            elif resizeOptions == "fixedWidth":
                newWidth = int(fixedWidth)
                newHeight = int((height*fixedWidth)/width)
                if not enlargeImage:
                    if width<newWidth: #keep the image size if the enlargeImage option is set to false
                        newWidth = width
                        newHeight = height
            if resizing:
                # Perform resizing
                imgObj.resizeImage2((newWidth, newHeight))
            else:
                # Perform cropping
                newWidth = right-left
                newHeight = lower-upper
                imgObj.cropImage((newWidth, newHeight))
            if optionName:
                try:
                    outputFile = self.__fs.join(toDir, name + "_%s.jpg" % (optionName))
                except:
                    outputFile = "%s/%s_%s.jpg" % (toDir, name, optionName)
                imgObj.save(outputFile)
            else:
                try:
                    outputFile = self.__fs.join(toDir, name + "_%sx%s.jpg" % (newWidth, newHeight))
                except:
                    outputFile = "%s/%s_%sx%s.jpg" % (toDir, name, newWidth, newHeight)
                imgObj.save(outputFile)
                return outputFile

