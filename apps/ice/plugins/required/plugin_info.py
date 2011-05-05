#
#    Copyright (C) 2007  Distance and e-Learning Centre,
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
import pysvn
import sys


pluginName = "ice.info"
pluginDesc = ""
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = None
    pluginClass = VersionInfo
    pluginInitialized = True
    return pluginFunc


class VersionInfo:
    def __init__(self, iceContext=None, *args):
        self.iceContext = iceContext

    def svn(self):
        return str(pysvn.svn_version)

    def pysvn(self):
        return str(pysvn.version)

    def python(self):
        return str(os.sys.version)

    def iceTrunkRevision(self):
        svn = pysvn.Client()
        return str(svn.info('../../../trunk').revision)

    def __getArgs(self):
        return self.__args

    def summary(self):
        info = VersionInfo()
        summary = "Built from ICE trunk " + info.iceTrunkRevision() + "\n"
        summary = summary + "SVN version " + info.svn() + "\n"
        summary = summary + "pysvn version " + info.pysvn() + "\n"
        summary = summary + "Python: " + info.python()
        return summary

    def getSummary(self):
        argv = sys.argv
        info = VersionInfo()
        try:
            result = "ICE version: " +  argv[1] + "\n"
            result = result + info.summary()
            return str(result)
        except:
            try:
                f = open('version_info.txt', 'r')
                info = f.read()
                f.close()
                return info
            except IOError:
                summary = "ICE version: unversioned \n"
                summary = summary + "SVN version " + info.svn() + "\n"
                summary = summary + "pysvn version " + info.pysvn() + "\n"
                summary = summary + "Python: " + info.python()
                return summary


def main(argv=None):
    if argv is None:
        argv = sys.argv

    info = VersionInfo()
    print "%s" % info.getSummary()


if __name__ == "__main__":
    sys.exit(main())





