#!/usr/bin/python
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

import sys, os
import pysvn


pluginName = "ice.svnPropDel"
pluginDesc = ""
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = None
    pluginClass = SvnPropertyDel
    pluginInitialized = True
    return pluginFunc


# list   client.status(path, recurse=recurse, get_all=True, update=false, ignore=False):
# delete client.propdel(name, path)
# propList = client.proplist(path)[0][1].keys()
# revert = client.revert(path, recurse=T|F)


# 'BookInfo' object on book files (*.book.odt ixe_globals.bookExts)
# 'iceDoc'  convertFlag - True | False(None)


class SvnPropertyDel(object):
    def __init__(self, *args):
        self.__client = pysvn.Client()

    # Main
    def deleteAllProperties(self, path=".", verbose=False, dryRun=False):
        fileCount = 0
        files = self.getListOfAllSvnFiles(path)
        for file in files:
            propNameList = self.getListOfPropertiesForFile(file)
            if propNameList!=[]:
                fileCount += 1
                if verbose:
                    print "%s (%s)" % (file, len(propNameList))
                #if file.endswith(".book.odt"):
                #    print "book = '%s'" % (file)
                #    bookInfo = self.__client.propget("meta-bookInfo", file)
                #    x = self.__client.propget("xx", file)
                #    print "%s '%s'-%s" % (len(bookInfo), x, type(x))
                if not dryRun:
                    self.deleteProperties(file, propNameList)
            if not dryRun and not file.endswith(".txt"):
                self.addSvnMimeType(file)
        if True:
            if dryRun:
                print "%s files have svn properties to be removed" % fileCount
            else:
                print "Removed svn properties from %s files" % fileCount

    def getListOfAllSvnFiles(self, path="."):
        files = self.__client.status(path, recurse=True, get_all=True, update=False)
        files = [i for i in files if i["is_versioned"] and (str(i["text_status"])!="ignored")]
        files = [i["path"] for i in files]
        return files

    def getListOfPropertiesForFile(self, file):
        properties = []
        propList = self.__client.proplist(file)
        if propList is not None and propList!=[]:
            try:
                properties = propList[0][1].keys()
            except:
                print "Error for '%s'" % file
            properties = [i for i in properties if not i.startswith("svn:")]
        return properties

    def getProperty(self, file, propName):
        data = self.__client.propget(propName, file)
        return data

    def deleteProperties(self, file, properties):
        for propName in properties:
            self.__client.propdel(propName, file)

    def addSvnMimeType(self, file):
        if os.path.isfile(file):
            self.__client.propset("svn:mime-type", "application/octet-stream", file)



def main(args):
    path = "."
    verbose = False
    dryRun = True
    progName = args.pop(0)
    if len(args)>0:
        temp = args.pop(0)
        if os.path.exists(temp):
            path = temp
        else:
            print "Error: '%s' is not a valid directory or file" % temp
            sys.exit(1)
        if len(args)>0:
            temp = args.pop(0).lower()
            if temp=="-v" or temp=="-verbose":
                verbose = True
            elif temp=='-dry' or temp=="-dryrun":
                dryRun = True
    else:
        print "Usage: %s path [-verbose]" % progName
        print "  path = svn directory where all files will be stripped of all svn properties."
        print "  optional -v | -verbose = display the files that properties are being deleted from."
        print
        sys.exit(1)

    if dryRun:
        print "dry run only. (testing)"
    svnPropDel = SvnPropertyDel()
    files = svnPropDel.deleteAllProperties(path, verbose, dryRun=dryRun)
    print
    print "Now use - svn commit %s -m \"removed properites\" - to commit all changes or" % path
    print "        - svn revert %s -R - to revert all changes." % path
    print


if __name__ == '__main__':
    main(sys.argv)








