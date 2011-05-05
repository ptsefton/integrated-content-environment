
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

""" Plugin to convert .wav file to .mp3 files """


pluginName = "ice.converter.waveToMp3"
pluginDesc = "Convert Wave (or '.aiff') to MP3"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method



def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = None
    pluginClass = WaveToMp3
    pluginInitialized = True
    return pluginFunc



class WaveToMp3(object):
    exts = [".wav", ".aiff"]
    SERVERPATH = "/wav"

    
    def __init__(self, iceContext, **kwargs):
        self.iceContext = iceContext
        self.__lameWrapper = LameWrapper(iceContext)
        self.__isAvailable = self.__lameWrapper.isAvailable
        self.__convertServer = None
        if self.__isAvailable==False:
            self.__convertServer = iceContext.getPlugClass("ice.extra.convertServer")



    @property
    def isAvailable(self):
        return self.__isAvailable


    def convert(self, fromToObj, **kwargs):
        """
            fromToObj must support the following methods:
                getFromFile(), getToFile(), getData(), putData(data=data [, name=None])
        """
        if self.__isAvailable==False:
            raise Exception("No lame encoding or WaveToMp3 server found!")
        if self.__lameWrapper.isAvailable:
            fromFile = fromToObj.getFromFile()
            toFile = fromToObj.getToFile()
            self.__lameWrapper.lame(fromFile, toFile)
        elif self.__convertServer is not None:
            postData = [("file", fromToOjb.getData())]
            data = self.__convertServer.post(path=self.SERVERPATH, postData=postData)
            fromToObj.putData(data)
        else:
            raise Exception("Unexpected error - no lameWrapper or convertServer!")
    

    def __call__(self, data):       # short-hand method
        class FromToObj(object):
            def __init__(self, iceContext, data):
                self.__fs = iceContext.fs
                self.__data = data
                self.__result = None
                self.__tempDir = None
            @property
            def result(self):
                if self.__result is None and self.__tempDir is not None:
                    self.__result = self.__tempDir.read("toFile")
                return self.__result
            def getData(self):
                return data
            def putData(self, data):
                self.__result = data
            def getFromFile(self):
                if self.__tempDir is None:
                    self.__tempDir = self.__fs.createTempDirectory()
                self.__tempDir.write("fromFile", self.__data)
                return self.__tempDir.absPath("fromFile")
            def getToFile(self):
                if self.__tempDir is None:
                    self.__tempDir = self.__fs.createTempDirectory()
                return self.__tempDir.absPath("toFile")
            def close(self):
                if self.__tempDir is not None:
                    self.__tempDir.delete()
                    self.__tempDir = None
            def __del__(self):
                self.close()
        fromToObj = FromToObj(data)
        self.convert(fromToObj)
        return fromToObj.result
    

############################


class LameWrapper(object):
    def __init__(self, iceContext):
        self.iceContext = iceContext
        self.__fs = iceContext.fs
        self.__system = iceContext.system
        self.__lameAvailable = None

    
    @property
    def isAvailable(self):
        if self.__lameAvailable is None:
            self.__lameAvailable = self.__lameAvailableCheck()
        return self.__lameAvailable


    def lame(self, inputFile, outputFile = None):
        """ run lame to convert .mp3 to .wav
        @param inputFile: absolute path of .mp3 file
        @type inputFile: String
        @param outputFile: absolute path of the converted .wav file
        @type outputFile: String

        @rtype: String
        @return: outputFile path
        """
        if outputFile is None:
            path, name, _ = self.__fs.splitPathFileExt(inputFile)
            outputFile = self.__fs.join(path, name + ".mp3")
        out, err = self.__system.executeNew("lame", inputFile, outputFile)
        if len(err) > 0 and not err.startswith("LAME") and not err.startswith("Sound"):
            raise Exception(err)
        return outputFile


    def __lameAvailableCheck(self):
        """ check if lame is install locally
        @rtype: boolean
        @return: true if lame is installed locally
        """
        out, err = self.__system.executeNew("lame", "--version")
        return out.startswith("LAME")

    

