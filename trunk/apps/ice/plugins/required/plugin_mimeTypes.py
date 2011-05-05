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

import sys
import os

pluginName = "ice.mimeTypes"
pluginDesc = "mime types"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = None
    pluginClass = MimeTypes
    pluginInitialized = True
    return pluginFunc



class MimeTypes(object):
    _mimeTypesDataFile =  "mimeTypes.txt"

    def __init__(self, *args):
        self.mimeTypes = {"":""}
        self.readMimeTypesDataFile()

    def get(self, ext, default=""):
        return self.mimeTypes.get(ext.lower(), default)

    def __getitem__(self, ext):
        return self.get(ext)

    def has_key(self, ext):
        return self.mimeTypes.has_key(ext.lower())

    def readMimeTypesDataFile(self):
        fileName = self._mimeTypesDataFile
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
                        self.mimeTypes[parts[0]] = parts[1].lower()
        except Exception, e:
            print "ERROR: " + str(e)

