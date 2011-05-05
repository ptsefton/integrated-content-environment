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
""" """

from http_util import Http
from lame_wrapper import lame_available, lame

pluginName = "ice.extra.lameEncoder"
pluginDesc = "lame encoder"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = None
    pluginClass = LameEncoder
    pluginInitialized = True
    return pluginFunc


class LameEncoder(object):
    def __init__(self, iceContext):
        self.iceContext = iceContext
    
    def convert(self, wavFile, mp3File = None):
        return self.__wav2mp3(wavFile, mp3File)
    
    def __wav2mp3(self, wavFile, mp3File = None):
        lameAvailable = lame_available()
        error = False
        if lameAvailable:
            outFile = lame(wavFile, mp3File) 
            if outFile.find("unsupported audio format")>-1:
                error = True
            else:
                return outFile
        if not lameAvailable or error:
            convertUrl = self.iceContext.settings.get("convertUrl")
            if convertUrl == None:
                raise Exception("Lame encoding service not available")
            else:
                if self.iceContext.system.isMac:
                    convertUrl += "/aiff"
                else:
                    convertUrl+="/wav"
                print "Lame is not available, converting using convertUrl: ", convertUrl
                fd = open(wavFile)
                options = {}
                options.update({"sessionid": ""})
                postData = [(k, v) for k, v in options.iteritems()]
                wavData = fd.read()
                fd.close()
                postData.append(("file",  ("%s" % wavFile, wavData)))
                data, headers, _, _ = self.iceContext.Http().post(convertUrl, postData,
                                                                includeExtraResults=True)
                if mp3File is None:
                    path, name, _ = self.iceContext.fs.splitPathFileExt(wavFile)
                    mp3File = self.iceContext.fs.join(path, name + ".mp3")
                self.iceContext.fs.writeFile(mp3File, data)
                fd.close()
                return mp3File
    

