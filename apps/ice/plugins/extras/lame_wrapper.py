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

""" program to run lame from command line to convert .mp3 to .wav
@requires: lame library
@requires: filesystem    from utils/file_system.py
@requires: system        from utils/system.py
"""

from file_system import FileSystem
from system import System

fs = FileSystem()
system = System()

def lame_available():
    """ check if lame is install locally
    @rtype: boolean
    @return: true if lame is installed locally
    """
    try:
        stdout, stderr = __execute3("lame")
        if len(stderr) > 0 and not stderr.startswith("LAME"):
            return False
        return True
    except:
        return False

def lame(inputFile, outputFile = None):
    """ run lame to convert .mp3 to .wav
    @param inputFile: absolute path of .mp3 file
    @type inputFile: String
    @param outputFile: absolute path of the converted .wav file 
    @type outputFile: String
    
    @rtype: String
    @return: outputFile path 
    """
    if outputFile is None:
        path, name, _ = fs.splitPathFileExt(inputFile)
        #print inputFile
        outputFile = fs.join(path, name + ".mp3")
        #print outputFile
    _, stderr = __execute3("lame", inputFile, outputFile)
    if len(stderr) > 0 and not (stderr.startswith("LAME") or stderr.startswith("Sound")):
        if stderr.find("unsupported audio format") > -1:
            return stderr
        else:
            print stderr
    return outputFile

def __execute3(cmd, *args, **kwargs):
    stdout, stderr = system.executeNew(cmd, *args)
    return stdout, stderr