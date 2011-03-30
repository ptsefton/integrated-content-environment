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

import os

""" Plugin to convert media files: audio/video to .flv files """

pluginName = "ice.converter.mediaToFlv"
pluginDesc = "Convert media files to flv"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method

def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = None
    pluginClass = MediaToFlv
    pluginInitialized = True
    return pluginFunc

class MediaToFlv(object):
    mimeType = ["audio", "video"]
    
    def __init__(self, iceContext, **kwargs):
        self.iceContext = iceContext
        self.__mediaToFlvWrapper = MediaToFlvWrapper(iceContext)
        self.__isAvailable = self.__mediaToFlvWrapper.isAvailable
        self.__convertServer = None
        if self.__isAvailable==False:
            self.__convertServer = iceContext.getPluginClass("ice.extra.convertServer")

    @property
    def isAvailable(self):
        return self.__isAvailable
    
    def convert(self, fromToObj, **kwargs):
        """
            fromToObj must support the following methods:
                getFromFile(), getToFile(), getData(), putData(data=data [, name=None])
        """
        return self.__mediaToFlvWrapper.ffmpeg(fromToObj)

############################


class MediaToFlvWrapper(object):
    """ Conversion of media file to flv format and vice versa """
    
    "Not tested extension: mov,3gp,3g2,mj2"
    def __init__(self, iceContext):
        self.iceContext = iceContext
        self.__fs = iceContext.fs
        self.__system = iceContext.system
        self.__ffmpegAvailable = None

    @property
    def isAvailable(self):
        if self.__ffmpegAvailable is None:
            self.__ffmpegAvailable = self.__ffmpegAvailableCheck()
        return self.__ffmpegAvailable

    def ffmpeg(self, inputFile, outputFile = None, outputType=".flv", **kwargs):
        """ run ffmpeg to convert the audio/video to flv
        @param inputFile: absolute path of the audio/video file
        @type inputFile: String
        @param outputFile: absolute path of the converted audio/video file
        @type inputFile: String
        
        @rtype: String
        @return: outputFile path
        
        Parameters of ffmpeg
        #-y :: overwrite the output file if it already exists
        #-i [inputFile.ext] :: the input video file
        #-acodec libfaac :: using the aac codec    --> This acodec might not be necessary as it require the codec to be installed
        #-ar 44100 :: the audio sampling rate
        #-ab 96k :: the audio bitrate
        #-vcodec libx264 :: use the x264 codec
        #-s 1280x540 :: the size of the output video
        #-b 1600k :: the bitrate of the output video
        #-g 250 :: frequency of keyframes
        #-r 20 :: the frame rate
        #[outputFile.ext] :: the output file
        
        #converting .mp4 to .flv
        #ffmpeg -i test.mp4 -sameq -deinterlace -s 384x288 -aspect 4:3 -b 512k -y -ac 1 testmp4.flv     
        
        #converting .wav to .flv
        #ffmpeg -i test.wav -ab 8000 testwav.flv
        
        #converting .wmv to .flv
        #ffmpeg -i "test.wmv" -sameq -ar 22050 -ab 96000 -deinterlace -nr 500 -s 320x240 -aspect 4:3 -r 20 -g 500 -me_range 20 -b 270k -deinterlace -f flv -y "testwmv.flv" //-acodec libmp3lame is removed
        
        #converting .mov to .flv
        #ffmpeg -y -i trailerTest.mov -ar 44100 -ab 96k -coder ac -me full -me_range 16 -subq 5 -sc_threshold 40 -s 1280x544 -b 1600k -cmp +chroma -partitions +parti4x4+partp8x8+partb8x8 -i_qfactor 0.71 -keyint_min 25 -b_strategy 1 -g 250 -r 20 87.mp4;
        """
        
        path, name, ext = self.__fs.splitPathFileExt(inputFile)
        if outputFile is None:
            outputFile = self.__fs.join(path, name + outputType)
        
        cmd = ""
        if ext == ".mp4":
            cmd = 'ffmpeg -i "%s" -sameq -deinterlace -s 384x288 -aspect 4:3 -b 512k -y -ac 1 "%s"' % (inputFile, outputFile)
        elif ext == ".wav":
            cmd = 'ffmpeg -i "%s" -ab 8000 -ar 11025 "%s"' % (inputFile, outputFile)
        elif ext == ".wma":
            cmd = 'ffmpeg -i "%s" -ab 8000 "%s"' % (inputFile, outputFile)
        elif ext == ".wmv":
            cmd = 'ffmpeg -i "%s" -sameq -ar 22050 -ab 96000 -deinterlace -nr 500 -s 320x240 -aspect 4:3 -r 20 -g 500 -me_range 20 -b 270k -deinterlace -f flv -y "%s"' % (inputFile, outputFile)
        elif ext == ".mov":
            #cmd = 'ffmpeg -y -i "%s" -ar 44100 -ab 96k -coder ac full -me_range 16 -subq 5 -sc_threshold 40 -s 1280x544 -b 1600k -cmp +chroma -partitions +parti4x4+partp8x8+partb8x8 -i_qfactor 0.71 -keyint_min 25 -b_strategy 1 -g 250 -r 20 "%s"' % (inputFile, outputFile);
            cmd = 'ffmpeg -i "%s" -ar 22050 -ab 128k -b 400k -s 320x240 -aspect 4:3 -f flv "%s"' % (inputFile, outputFile)
        elif ext == ".mp3":
            cmd = 'ffmpeg -y -i "%s" -f flv -ab 64 -ac 1 "%s"' % (inputFile, outputFile)
        elif ext == ".m4a":
            cmd = 'ffmpeg -i "%s" -f flv -b 300000 -s 360x240 -r 30 -ac 2 -ab 64k -ar 44100 -vcodec flv "%s"' % (inputFile, outputFile)
        elif ext == ".mpg" or ext == ".mpeg":
            cmd = 'ffmpeg -i "%s" -ar 22050 -ab 32 -f flv -s 320x240 -aspect 4:3 -y "%s"' % (inputFile, outputFile)
        else:
            outputFile = ""
            raise Exception("Unsupported extension: %s" % ext)
        
        result = os.popen(cmd)
#            for i in result.readlines():
#                print "result: ", i
        return outputFile

    def __ffmpegAvailableCheck(self):
        """ check if ffmpeg is install locally
        @rtype: boolean
        @return: true if lame is installed locally
        """
        result = os.popen("ffmpeg -version")
        for line in result.readlines():
            if line.startswith("FFmpeg"):
                return True       
        return False
