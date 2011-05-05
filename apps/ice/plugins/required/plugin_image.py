
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

"""
Image plugin to support image manipulation used in ICE
@requires: Image, ImageChops library from python PIL library
@requires: StringIO
"""

import Image, ImageChops
from cStringIO import StringIO

pluginName = "ice.image"
pluginDesc = ""
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
    IceImage._Image = iceContext.getImageImport()
    pluginFunc = None
    IceImage._Image = Image
    IceImage.StringIO = StringIO
    pluginClass = IceImage
    pluginInitialized = True
    return pluginFunc

class IceImage:
    """
    Base class for IceImage Class
    @ivar _Image
    @ivar StringIO 
    """
    _Image = None
    StringIO = None
    # Constructor:
    #   __init__(imageData, imageExt=None)
    # Properties:
    #   size
    #   info
    # Methods:
    #   getSize()
    #   getInfo()
    #   getType()
    #   getPixel(pixel)
    #   getPalette()
    #   needsResizing(newSize)
    #   isAnim()
    #   hasTransparency()
    #   showImage
    #   convertbwGifToPng(size)
    #   bwResizeImage(newSize)
    #   removeTransparency()
    #   resizeImage(newSize)
    #   resizeImage2(size=None)
    #   save(toFile, compress=75)


    class __dataStream:
        """
        private dataStream class
        """
        def __init__(self, data, _Image):
            """ dataStream constructor method
            @param data:
            @type data:   
            
            @param _Image:
            @type _Image: PIL image object
            
            @var count:
            """
            self.data = data
            self.count = 0
            self._Image = _Image
        def read(self, amount):
            """ read method
            @param amount:
            @type amount: integer
            
            @return: Image data
            @rtype: PIL image object 
            """
            data = self.data[self.count:self.count+amount]
            self.count+=amount
            return data
        def seek(self, offset):
            """ seek method
            @param offset:
            @type offset: integer 
            """
            self.count=offset
        def tell(self):
            """ tell method
            @return: count value
            @rtype: integer
            """
            return self.count
        def image(self):
            """ get image method
            @return: image data
            @rtype: PIL image object
            """
            return self._Image.open(self)


    def __init__(self, imageData, imageExt=None):
        """ Constructor of IceImage to create a Image object from
        imageData
        @param imageData:
        @type imageData:
        @param imageExt: image extension
        @type imageExt: String 
        """
        try:
            self.__im = self.__dataStream(imageData, self._Image).image()
        except Exception, e:
            raise Exception("Error creating the 'Image' object - " + str(e))
        if imageExt!=None:
            self.__imageExt = self._Image.EXTENSION[imageExt]
        else:
            self.__imageExt = self.__im.format

    def getSize(self):
        """ Image size property
        @return: Image size in tuple (width, height)
        @rtype: tuple
        """
        return self.__im.size
    size = property(getSize)

    def getInfo(self):
        """ Image information property
        @return: Image information
        @rtype: Dictionary
        """
        return self.__im.info
    info = property(getInfo)

    def getType(self):
        """ get Image extension 
        @return: image extension
        @rtype: String
        """
        return self.__imageExt

    def getPixel(self, pixel):
        """ get Image based on the provided pixel value
        @param pixel: pixel position in the the image in tuple (x,y)
        @type pixel: tuple
        @return: requested pixel
        @rtype: Integer
        """
        return self.__im.getpixel(pixel)

    def getpalette(self):
        """ get Image palette
        @return: Image palette
        @rtype: PIL palette object
        """
        return self.__im.getpalette()

    def needsResizing(self, newSize):
        """ check if Image need to be resized
        @param newSize: new size of the image
        @type newSize: tuple (width, height)
        
        @return: True or False depend on the current image size and the new size
        @rtype: Boolean   
        """
        if self.__im.mode=="CMYK":
            return True
        return self.__getSizeDiff(self.__im.size, newSize) > 0.1

    def isAnim(self):
        """ Check if the Image is an animation
            #duration is sometimes 0, thus not a true animation.
            
        @return: True or False depend on the duration of the image
        @rtype: Boolean
        """
        try: 
            return self.__im.info['duration'] and self.__im.info['loop']!=2 #not 1 or 0
        except:
            return False

    def hasTransparency(self):
        """ Check if image has transparency
        @return: True or False depend on the transparency information of the image
        @rtype: Boolean
        """
        try:
            return self.__im.info['transparency']!=-1 #not 0-255
        except:
            return False

    def showImage(self):
        """ Show the image
        This method is supported in PIL to have image preview
        """
        self.__im.show()

    def convertbwGifToPng(self, size):
        """ This convert black and white gif to PNG method is used
        to support mathtype object. 
        All Mathtype objects will be resized and converted to PNG.
        @param size: the size of the new image
        @param type: tuple (width, height) 
        """
        img = self.__im
        if size is None:
            size = img.size

        if self.hasTransparency():
            self.removeTransparency()

        if img.mode != "P" and img.mode != "L":
            img = img.resize(size, self._Image.ANTIALIAS)
        else:
            img = img.convert('L')
            img = img.resize(size, self._Image.ANTIALIAS)
            img = img.convert('P')
            p = img.getpalette()
            p.reverse()
            img.putpalette(p)

            img = img.convert('L')
            new = self._Image.new('L', img.size, 0)
            img = self._Image.merge('RGBA', (new, new, new, img))

            self.__im = img

    def bwResizeImage(self, newSize):
        """ This convert black and white and resized image is used to
        support mathtype object.
        All Mathtype objects will be resized and save to the same
        file extension.
        NOTE: current support for Mathtype objects use the above convertbwGifToPng
        method
        @param size: the size of the new image
        @param type: tuple (width, height) 
        
        @return: image data
        @rtype: 
        """
        img = self.__im
        if img.mode != "P":
            img = img.resize(newSize, self._Image.ANTIALIAS)
        else:
            p = self.__paletteHack(img)
            if p is not None:
                img.putpalette(p)
            img = img.convert("L")
            img = img.resize(newSize, self._Image.ANTIALIAS)
            img = img.convert("P")
#            for x in range(newSize[0]):
#                for y in range(newSize[1]):
#                    loc = (x,y)
#                    px = img.getpixel(loc)
#                    if px > 223:
#                        img.putpixel(loc, 255)
#                    else:
#                        px = int(px * 1.33)
#                        img.putpixel(loc, px)
        s = self.StringIO()
        img.save(s, self.__imageExt, transparency=2)
        data = s.getvalue()
        return data

    def removeTransparency(self):
        """ Changes the transparency and background colour to pure white
        so that when converted to jpg, it will look good """
        if self.hasTransparency():
            alphaIndex = 3*self.__im.info['transparency']
            p = self.__im.getpalette()
            p[alphaIndex] = 255
            p[alphaIndex+1] = 255
            p[alphaIndex+2] = 255
            self.__im.putpalette(p)
            del self.__im.info['transparency']


    def resizeImage(self, newSize):
        """ Resize Image method resize the provided image AND
        IF the image mode is "P" (palette e.g. gif) AND has transparent 
        background, do palette hack to replace the transparent 'pink'
        color to 'white'. This hacking is used to support
        GIF87a format which does not have transparency information of the image
        @param size: the size of the new image
        @param type: tuple (width, height) 
        
        @return: image data
        @rtype: 
        """
        data = None
        try:
            #Test to see if the image needs resizing
            #if self.__getSizeDiff(self.__im.size, newSize)>0.1:
            #if self.needsResizing(newSize):
            if self.__im.mode=="CMYK":
                self.__im = self.__im.convert("RGBA")
            if True:
                resizedImage = self.__im.resize(newSize, self._Image.ANTIALIAS)
                s = self.StringIO()
                resizedImage.save(s, self.__imageExt)
                data = s.getvalue()
                # try data hack to restore a gif's transparent background color
                hackData = self.__gifDataHack(data)
                if hackData!=None:
                    data = hackData
                elif resizedImage.mode=="P":
                    # OK try just replacing the transparent 'pink' color to 'white'.  Do palette hack
                    hackPalette = self.__paletteHack(resizedImage)
                    if hackPalette != None:
                        resizedImage.putpalette(hackPalette)
                        resizedImage.save(s, self.__imageExt)
                        data = s.getvalue()
                    data = s.getvalue()
            else:
                s = self.StringIO()
                self.__im.save(s, self.__imageExt)
                data = s.getvalue()
        except IOError, e:
            raise Exception("IOError resizing image - " + str(e))
        except Exception, e:
            raise Exception("Error resizing image - " + str(e))
        return data


    def resizeImage2(self, size=None):
        """ Resize image2 method will resize the provided image with
        a new size. Limitation on this method:
        When running in Linux such as Ubuntu, transparent PNG will
        have black background
        @param size: the size of the new image
        @param type: tuple (width, height) 
        """
        if size is None:
            size = self.__im.size
        if self.__im.mode=="CMYK":
            self.__im = self.__im.convert("RGBA")
        if self.__im.mode == "P":
            self.__im = self.__im.convert()
        self.__im = self.__im.resize(size, self._Image.ANTIALIAS)

    def cropImage(self, size):
        """ Cropping image method will crop image based on the provided new size
        @param size: the size of the new image
        @param type: tuple (width, height) 
        """
        if self.__im.mode == "P":
            self.__im = self.__im.convert("RGB")
        
        bgColor = (255, 255, 255)
        bg = Image.new("RGB", size, bgColor)
        diff = ImageChops.difference(self.__im, bg)
        bbox = diff.getbbox()
        if bbox:
            self.__im = self.__im.crop(bbox)
        

    def save(self, toFile, compress=75):
        """ Save image to specified file
        @param toFile: outputFile name
        @type toFile: String
        @param compress: image compression quality
        @type compress: Integer   
        """
        self.__im.save(toFile, quality=compress)


    def __paletteHack(self, image):
        """ Perform palette hack on the image
        to replace the "pink" background to "white" color.
        This is mainly used to support png/gif images
        that has transparent background and need to be resized
        @param image: Image that need to be process
        @type image: PIL image object
        
        @return: New hacked image data
        @rtype: PIL image object          
        """
        alphaColor = (252, 3, 251)
        p = image.getpalette()
        for x in range(0, 767, 3):
            rgb = (p[x], p[x+1], p[x+2])
            if rgb == alphaColor:
                p[x] = 255
                p[x+1] = 255
                p[x+2] = 255
                return p
        return None

    def __getPinkIndex(self, p):
        """ Get the Pink color index from the image
        @param p: palette
        @type p: String   
        @return: None if color index is not found 
        @rtype: integer
        """
        alphaColor = "\xfc\x03\xfb"
        for x in range(0, 255):
            rgb = p[x*3:x*3+3]
            if rgb == alphaColor:
                return x
        return None

    def __gifDataHack(self, data):
        """ This method will try and add transparency information to the
        gif image.
        CHECKING is done to check if image is a GIF89a or GIF87a
        @param data: Image data
        @type data: String
        
        @return: new hacked gif data
        @rtype: String 
        """
        s = data[:6]
        if s=="GIF89a" or s=="GIF87a":
            flag = data[10]
            if True:
            #if (flag & 0x87) ==0x87:
                header = data[:13+256*3]
                idata = data[13+256*3:]
                if idata[0]=="\x21" and idata[1]=="\xf9":
                    return None
                else:
                    palette = data[13:13+256*3]
                    index = self.__getPinkIndex(palette)
                    if index!=None:
                        #print "applying gif data hack", index
                        block = "\x21\xf9\x04\x01\x00\x00" + chr(index) + "\x00"
                        return header + block + idata
        return None

    def __getSizeDiff(self, size1, size2):
        """ Get the size difference between two image sizes
        @param size1: first image size
        @type size1: tuple (width, height)
        @param size2: second image size
        @type size2: tuple (width, height)
        
        @return: the difference between two image
        @rtype: integer  
        """
        xDiff = abs(size1[0]*1.0/size2[0])
        yDiff = abs(size1[1]*1.0/size2[1])
        diff = abs(max(xDiff, yDiff)-1)
        return diff

















