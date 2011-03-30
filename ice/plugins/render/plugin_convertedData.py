
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

""" """


from cPickle import dumps

pluginName = "ice.convertedData"
pluginDesc = "Converted Data Object Model"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginClass = ConvertedData
    pluginFunc = None
    pluginInitialized = True
    return pluginFunc


class ConvertedData(object):
    # Constructor:
    #   __init__(iceContext)
    # Properties:
    #   renderedTime
    #   renderedMD5
    #   errorMessage
    #   metaNames
    #   renditionNames
    #   imageNames
    #
    # Methods:
    #   setRenderedTimeAndMD5(time, md5)            # optional
    #   addErrorMessage(msg)                        #
    #   addMeta(name, data)                         # e.g. ("title", TitleStr), ("images", [ArrayOfFileImageNames]),
                                                    #   ("style.css", styleStr), ("links", [ArrayOfLinkHrefs]), & other meta info
    #   addRenditionData(name, data)                # e.g. (".xhtml.body", bodyXmlStr),
    #   addRenditionFile(name, filename)            # e.g. (".pdf", absolutePathToThePdfFile)
    #   addImageFile(name, filename)                # e.g. ("filename.ext", absolutePathToTheImageFile) NOTE: name does not contain any path info.
    #
    #   close()                                     # Cleanup
    #   debugPrint()
    #   __str__()
    #
    #   abspath(name)
    #   getMeta(name)
    #   getRendition(name)
    #   saveRenditionTo(name, toFile)
    #   getImage(name)
    #   removeImage(name)
    #   saveImageTo(name, toPath)
    #   saveTo(path)

    def __init__(self, iceContext):
        self.iceContext = iceContext
        self.__fs = iceContext.fs
        self.__tempDir = None    #file_util.tempDir()
        self.__metas = {}
        self.__renditions = {}        # name: filename
        self.__renditionsData = {}    # name: data
        self.__images = {}
        self.__imagesData = {}
        self.__errorMessage = ""
        self.error = False
        self.terminalError = False
        self.exception = None
        self.__renderedFileTime = None
        self.__renderedFileMD5 = None
        self.meta = {}


    @property
    def renderedTime(self):
        return self.__renderedFileTime


    @property
    def renderedMD5(self):
        return self.__renderedFileMD5


    @property
    def errorMessage(self):
        return self.__errorMessage


    @property
    def metaNames(self):
        return self.__metas.keys()


    @property
    def renditionNames(self):
        return self.__renditions.keys()


    @property
    def imageNames(self):
        return self.__images.keys()


    def setRenderedTimeAndMD5(self, time, md5):
        self.__renderedTime = time
        self.__renderedMD5 = md5


    def __del__(self):
        pass
        # Note: Do not call self.__tempDir.remove() from a destructor, because
        #  the destructor of self.__tempDir may have already been called by the GC
        #if self.__tempDir!=None:
        #    self.__tempDir.delete()
        if self.__tempDir!=None:
            print "Warning: ConvertedData object has not been closed!"


    def close(self):
        if self.__tempDir!=None:
            self.__tempDir.delete()
            self.__tempDir=None


    def abspath(self, name):
        if self.__tempDir is None:
            self.__tempDir = self.__fs.createTempDirectory()
        return self.__fs.join(str(self.__tempDir), name).replace("\\", "/")


    def addErrorMessage(self, msg):
        self.error = True
        self.__errorMessage += str(msg) + "\n"


    def clearError(self):
        self.error = False
        self.__errorMessage = ""
        self.terminalError = False
        self.exception = None


    def addMeta(self, name, data):
        self.__metas[name] = data


    def getMeta(self, name):
        return self.__metas[name]


    def addRenditionData(self, name, data):
        self.__renditionsData[name] = data
        self.__renditions[name] = None


    def addRenditionFile(self, name, filename):
        self.__renditions[name] = filename


    def getRendition(self, name):
        data = None
        filename = self.__renditions[name]
        if filename is None:
            data = self.__renditionsData[name]
        else:
            data = self.__fs.readFile(filename)
        return data


    def saveRenditionTo(self, name, toFile):
        data = None
        filename = self.__renditions[name]
        if filename is None:
            data = self.__renditionsData[name]
            self.__fs.writeFile(toFile, data)
        else:
            self.__fs.copy(filename, toFile)


    def addImageFile(self, name, filename):
        if filename is None or filename=="":
            return
        filename = self.abspath(filename)
        self.__images[name] = filename


    def addImageData(self, name, data):
        self.__images[name] = None
        self.__imagesData[name] = data


    def getImage(self, name):
        if self.__imagesData.has_key(name):
            return self.__imagesData[name]
        filename = self.__images[name]
        data = self.__fs.readFile(filename)
        return data


    def saveImageTo(self, name, toPath):
        filename = self.__images[name]
        if self.__fs.isDirectory(toPath):
            toPath = self.__fs.join(toPath, name)
        self.__fs.copy(filename, toPath)


    def removeImage(self, name):
        if self.__images.has_key(name):
            self.__images.pop(name)


    def saveTo(self, path):
        if not self.__fs.exists(path):
            self.__fs.makeDirectory(path)
        for key, value in self.__renditions.items():
            fromFile = value
            toFile = self.__fs.join(path, "rendition-" + key)
            self.__fs.copy(fromFile, toFile)
            self.__renditions[key] = toFile
        for key, value in self.__images.items():
            fromFile = value
            toFile = self.__fs.join(path, key)
            self.__fs.copy(fromFile, toFile)
            self.__images[key] = toFile
        self.close()
        data = dumps(self)
        self.__fs.writeFile(self.__fs.join(path, "convertedData.bin"), data)


    def debugPrint(self):
        print "RenditionFiles:"
        for key, value in self.__renditions.items():
            print " ", key, value
        print "Images:"
        for key, value in self.__images.items():
            print " ", key, value


    def __str__(self):
        s = "converterData [object]\n"
        for name in self.metaNames:
            data = self.getMeta(name)
            try:
                if len(data)>200:
                    data = "len " + str(len(data))
            except:
                pass
            s += "Meta '%s' = %s\n" % (name, data)
        for name in self.renditionNames:
            data = self.getRendition(name)
            if data is None:
                s += "Rendition '%s' = NONE!\n" % (name)
            else:
                s += "Rendition '%s' = len %s\n" % (name, len(data))
        for name in self.imageNames:
            data = self.getImage(name)
            if data is None:
                s += "Image '%s' = NONE!\n" % (name)
            else:
                s += "Image '%s' = len %s\n" % (name, len(data))
        if self.error:
            s += "ERROR: " + self.__errorMessage
        return s




