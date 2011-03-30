
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

""" Plugin to convert text to MP3 """


pluginName = "ice.converter.textToSpeech"
pluginDesc = "Convert text to MP3"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method



def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = None
    pluginClass = TextToSpeech
    pluginInitialized = True
    return pluginFunc



class TextToSpeech(object):
    exts = [".txt"]
    

    # Constructor:
    #   __init__(iceContext, engine="native")
    # Properties:
    #   isTextToSpeechAvailable
    # Methods:
    #   textToSpeech(text)
    #   textToWave(text)        # Note: setup in the constructor
    @staticmethod
    def getHtml(iceContext, txtFile, format = "mp3"):
        _, name, _ = iceContext.fs.splitPathFileExt(txtFile)
        return '<object type="%s" data="%s.%s" />' \
               % (iceContext.MimeTypes["." + format], name, format)


    def __init__(self, iceContext, engine="native", **kwargs):
        self.iceContext = iceContext
        self.__engine = engine

        self.__lameEncoder = None
        self.__convertUrl = None

        LameEncoder = self.iceContext.getPluginClass("ice.extra.lameEncoder")
        if LameEncoder is not None:
            self.__lameEncoder = LameEncoder(self.iceContext)

        self.textToWave = self.__textToWaveNotAvailable
        if tts_available(engine):
            self.textToWave = self.__textToWave
        else:
            self.__convertUrl = self.iceContext.settings.get("convertUrl")
            if self.__convertUrl=="":
                self.__convertUrl = None
            if self.__convertUrl is not None:
                self.__convertUrl += "/txt"
                self.textToWave = self.__textToWaveService
        self.__isTextToSpeechAvailable = (self.__lameEncoder is not None) and \
                self.textToWave!=self.__textToWaveNotAvailable


    @property
    def isAvailable(self):
        return self.__isTextToSpeechAvailable


    def convert(self, fromToObj, **kwargs):
        """

        """
        pass


    def textToSpeech(self, text):
        if self.__lameEncoder is None:
            raise Exception("Text to speech service not available. Failed to load MP3 encoder plugin!")
        if self.textToWave==self.__textToWaveNotAvailable:
            raise Exception("Text to speech service not available.")
        # OK
        tmpFs = self.iceContext.fs.createTempDirectory()
        try:
            inputFile = tmpFs.absPath("data.txt")
            tmpFs.writeFile(inputFile, text)
            outputFile = self.textToWave(inputFile)
            try:
                outputFile = self.__lameEncoder.convert(outputFile)
            except Exception, e:
                raise Exception("Text to speech service not available. (%s)" % str(e))
            content = tmpFs.readFile(outputFile)
        finally:
            tmpFs.delete()
        return content


    def __textToWaveNotAvailable(self, txtFile, outFile=None):
        raise Exception("Text to speech service not available")


    def __textToWave(self, txtFile, outFile=None):
        return text_to_speech(txtFile, outFile, self.__engine)


    def __textToWaveService(self, txtFile, outFile=None):
        print "Using text to speech service at %s" % self.__convertUrl
        options = {"format":"wav", "engine":self.__engine}

        fd = open(txtFile)
        postData = [(k, v) for k, v in options.iteritems()]
        postData.append(("file", fd))
        http = self.iceContext.Http()
        data = http.post(self.__convertUrl, postData)
        if outFile is None:
            path, name, _ = self.iceContext.fs.splitPathFileExt(txtFile)
            outFile = self.iceContext.fs.join(path, name + ".wav")
        self.iceContext.fs.writeFile(outFile, data)
        fd.close()
        return outFile


    def __call__(self, text):
        return self.textToSpeech(text)




################################################################################
################################################################################
import os

class TTSWrapper(object):
    def __init__(self, iceContext):
        self.iceContext = iceContext
        self.__fs = iceContext.fs
        self.__system = iceContext.system


    def isAvailable(self, engine="native"):
        nativeAvailable = False
        if engine=="native":
            nativeAvailable = self.__macosxSayAvailable()
        # fallback to festival if possible
        if nativeAvailable:
            return True
        else:
            return self.__festivalAvailable()


    def textToSpeech(self, inputFile, outputFile=None, engine="native"):
        ttsFunc = None
        canUseFestival = self.__festivalAvailable()
        if engine == "native":
            # check for native TTS engines
            if self.__macosxSayAvailable():
                ttsFunc = macosx_say
        elif engine == "other" and canUseFestival:
            ttsFunc = self.__festivalClient
        else:
            raise Exception("Unknown speech engine: %s" % engine)

        # fallback on festival if possible
        if ttsFunc is None and canUseFestival:
            ttsFunc = self.__festivalClient
        if callable(ttsFunc):
            return ttsFunc(inputFile, outputFile)
        return None


    def __macosxSayAvailable(self):
        if self.__system.isMac:
            tmpFs = self.__fs.createTempDirectory()
            tmpFile = tmpFs.absPath("test.aiff")
            retval = os.system("say -o %s test" % tmpFile)      ###########
            tmpFs.delete()
            return retval == 0
        else:
            return False


    def __macosxSay(self, inputFile, outputFile = None):
        if outputFile is None:
            path, name, _ = self.__fs.splitPathFileExt(inputFile)
            outputFile = self.__fs.join(path, name + ".aiff")
        _, stderr = self.__execute3("say", "-o", outputFile, "-f", inputFile)
        if len(stderr) > 0:
            raise Exception(stderr)
        return outputFile


    def __festivalAvailable(self):          # linux
        stdout, _ = self.__execute3("festival_client", "--version", readout = True)
        return stdout.startswith("festival_client")


    def __festivalClient(self, inputFile, outputFile = None):
        if outputFile is None:
            path, name, _ = self.__fs.splitPathFileExt(inputFile)
            outputFile = self.__fs.join(path, name + ".wav")
        if self.__system.isMac:
            _, stderr = self.__execute3("festival_client",
                                   "--output", outputFile,
                                   "--ttw", inputFile)
        else:
            stdout, stderr = self.__execute3("text2wave",
                                    "-f", 8000, "-o", outputFile, inputFile)
        return outputFile


    def __execute3(self, cmd, *args, **kwargs):
        out = ""
        err = ""
        readout = kwargs.get("readout", False)
        readerr = kwargs.get("readout", True)
        try:
            _, stdout, stderr = system.execute3(cmd, *args)
            if readout:
                out = stdout.read()
                stdout.close()
            if readerr:
                err = stderr.read()
                stderr.close()
        except Exception, e:
            print "Warning: %s: %s" % (cmd, str(e))
        return out, err




