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
#    along with this program; if not, write to the Free Soutoftware
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

import os
from file_system import FileSystem
from system import System

fs = FileSystem()
system = System()


def tts_available(engine = "native"):
    nativeAvailable = False
    if engine == "native":
        nativeAvailable = macosx_say_available() or windows_say_available()
    # fallback to other if possible
    if nativeAvailable:
        return True
    else:
        if other_available():
            return True
        else:
            return False

def text_to_speech(inputFile, outputFile = None, engine = "native"):
    ttsFunc = None
    canUseOther = other_available()
    if engine == "native":
        # check for native TTS engines
        if macosx_say_available():
            ttsFunc = macosx_say
        elif windows_say_available():
            ttsFunc = windows_say
    elif engine == "other" and canUseOther:
        ttsFunc = other_client
    else:
        raise Exception("Unknown speech engine: %s" % engine)
    
    # fallback on other if possible
    if ttsFunc is None and canUseOther:
        ttsFunc = other_client
    if callable(ttsFunc):
        return ttsFunc(inputFile, outputFile)
    return None


def macosx_say_available():
    if system.isMac:
        tmpFs = fs.createTempDirectory()
        tmpFile = tmpFs.absPath("test.aiff")
        retval = os.system("say -o %s test" % tmpFile)
        tmpFs.delete()
        return retval == 0
    else:
        return False

def macosx_say(inputFile, outputFile = None):
    if outputFile is None:
        path, name, _ = fs.splitPathFileExt(inputFile)
        outputFile = fs.join(path, name + ".aiff")
    _, stderr = __execute3("say", "-o", outputFile, "-f", inputFile)
    if len(stderr) > 0:
        raise Exception(stderr)
    return outputFile


def other_available():
    if system.isWindows:
        #test text2wav is working
        tmpFs = fs.createTempDirectory()
        tmpFile = tmpFs.absPath("test.txt")
        outFile = tmpFs.absPath("test.wav")
        fs.writeFile(tmpFile, "testing")
        try:
            stdoutData, stderrData = __execute3("text2wav", "--filename=\"%s\"" % outFile,"--textfile=\"%s\"" % tmpFile)
        except Exception, e:
            print str(e)
        if fs.isFile(outFile):
            tmpFs.delete()
            return True
    elif system.isMac:
        #try to get environment variable for festival
        #need value for cmd
        cmd = "festival_client.exe"
        stdoutData = ""
        try:
            stdoutData, stderrData = system.executeNew(cmd, "--output", "nul", "--ttw", stdinData="test\n\x1a\n")
        except Exception, e:
            return False
        return stdoutData.startswith("festival_client")
    else:
        #test text2wave is working
        tmpFs = fs.createTempDirectory()
        tmpFile = tmpFs.absPath("test.txt")
        outFile = tmpFs.absPath("test.wav")
        fs.writeFile(tmpFile, "testing")
        try:
            stdoutData, stderrData = __execute3("text2wave", "-f", "8000", "-o", outFile, tmpFile)
        except Exception, e:
            pass
            #print "Exception in tts_wrapper: ", str(e)
        if fs.isFile(outFile):
            tmpFs.delete()
            return True
    return False

def other_client(inputFile, outputFile = None):
    if outputFile is None:
        path, name, _ = fs.splitPathFileExt(inputFile)
        outputFile = fs.join(path, name + ".wav")
    if system.isMac:
        _, stderr = __execute3("festival_client",
                               "--output", outputFile,
                               "--ttw", inputFile)
    elif system.isWindows:
        stdout, stderr = __execute3("text2wav", "--filename=\"%s\"" % outputFile, "--textfile=\"%s\"" % inputFile)
    else:
        stdout, stderr = __execute3("text2wave", "-f", "8000", "-o", outputFile, inputFile)
    return outputFile


__windows_say_available = None
def windows_say_available():
    global __windows_say_available
    if __windows_say_available is not None:
        return __windows_say_available
    if system.isWindows:
        tmpFs = fs.createTempDirectory()
        tmpFile = tmpFs.absPath("test.txt")
        outFile = tmpFs.absPath("test.wav")
        fs.writeFile(tmpFile, "testing")
        windows_say(tmpFile)
        __windows_say_available = fs.isFile(outFile)
        tmpFs.delete()
    else:
        __windows_say_available = False
    return __windows_say_available

def windows_say(inputFile, outputFile=None):
    if outputFile is None:
        path, name, _ = fs.splitPathFileExt(inputFile)
        outputFile = fs.join(path, name + ".wav")
    if system.isWindows:
        cmd = fs.absPath("bin/say.exe")
        cmd =r"%s " %  cmd
        try:
            system.executeNew(cmd, inputFile, outputFile)
        except:
            cmd = fs.absPath("say.exe")
            cmd =r"%s " %  cmd
            system.executeNew(cmd, inputFile, outputFile)
    return outputFile


def __execute3(cmd, *args, **kwargs):
    stdout, stderr = system.executeNew(cmd, *args)
    return stdout, stderr
#    out = ""
#    err = ""
#    readout = kwargs.get("readout", False)
#    readerr = kwargs.get("readout", True)
#    try:
#        _, stdout, stderr = system.execute3(cmd, *args)
#        if readout:
#            out = stdout.read()
#            stdout.close()
#        if readerr:
#            err = stderr.read()
#            stderr.close()
#    except Exception, e:
#        print "Warning: %s: %s" % (cmd, str(e))
#    return out, err
