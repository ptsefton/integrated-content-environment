#!/usr/bin/env python
#    Copyright (C) 2005  Distance and e-Learning Centre,
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

pluginName = "ice.unicode.dict"
pluginDesc = "unicode dictionary"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    UnicodeDict.dictionary = UnicodeDict.readUnicodeDataFile()
    pluginClass = UnicodeDict
    pluginFunc = None
    pluginInitialized = True
    return pluginFunc


class UnicodeDict(object):
    unicodeDataFile = "unicode.txt"
    dictionary = None

    @staticmethod
    def readUnicodeDataFile():
        unicodeDict = dict()
        fileName = UnicodeDict.unicodeDataFile
        lines = []
        if os.path.isfile(fileName)==False:
            fileName = "../ice/" + fileName
        try:
            f = open(fileName, "r")
            lines = f.readlines()
            f.close()
            for line in lines:
                line = line.strip()
                if line=="" or line.startswith("#"):
                    pass
                else:
                    parts = line.split()
                    if len(parts)>1:
                        unicodeDict[parts[0]] = parts[1]
        except Exception, e:
            print "ERROR: " + str(e)
        return unicodeDict


if __name__ == "__main__":
    print str(UnicodeDict.readUnicodeDataFile())

