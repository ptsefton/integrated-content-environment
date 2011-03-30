#
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


"""
convert internal links in a group of documents (eg course)
that has been copied from one location to another.
That is, if a course has been copied from stf/1001/2005/s2/ to stf/1001/2006/s1/
then any internal links will need to be changed accordingly.
"""


pluginName = "ice.copyLinks"
pluginDesc = "Links copier"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = convert
    pluginClass = CopyLinks
    pluginInitialized = True
    return pluginFunc


class CopyLinks(object):
    def __init__(self, iceContext, localBaseUrl="http://localhost:"):
        self.iceContext = iceContext
        self.rep = iceContext.rep
        self.__output = iceContext.output
        self.__fs = iceContext.fs
        self.__localBaseUrl = localBaseUrl


    def convert(self, copyFrom, copyTo, startPath=None):
        #print "Converting"
        # make sure leading and trailing slashes match
        copyFrom = self.__normalizePath(copyFrom)
        copyTo = self.__normalizePath(copyTo)
        if startPath==None:
            startPath = copyTo

        item = self.rep.getItem(startPath)
        for listItems in item.walk(filesOnly=True):
            for i in listItems:
                name, ext = self.__fs.splitExt(i.name)
                if ext==self.iceContext.oooDefaultExt:
                    self.__processZipFile(i, copyFrom, copyTo)
                    i.touch()
                elif (ext==self.iceContext.wordExt or ext==self.iceContext.word2007Ext) and i.hasHtml:
                    #self.__processWordDocFile(item, copyFrom, copyTo)
                    #item.touch(file)
                    pass
                i.flush()


    def __processWordDocFile(self, item, copyFrom, copyTo):
        # OK convert the word doc file to a .odt file
        if self.__output is not None:
            msg = "ProcessWordDocFile(sourceFileName=%s, copiedFrom=%s, copiedTo=%s)\n"
            msg = msg % (item.relPath, copyFrom, copyTo)
            self.__output.write(msg)

        fileName, ext = self.__fs.splitExt(item.name)
        tempDir = self.__fs.makeDirectory()
        toFile = self.__fs.join(str(tempDir), fileName + ".odt")

        # Convert
        oooConverter = self.iceContext.getOooConverter()
        #oooConverter.convert DocTo(sourceFileName, toFile)
        oooConverter.convertDocumentTo(item._absPath, toFile)

        # Extract content.xml and process
        zipTempDir = self.__fs.unzipToTempDirectory(toFile)
        contentFilename = self.__fs.join(str(zipTempDir), "content.xml")
        self.__processXmlFile(contentFilename, item, copyFrom, copyTo)

        # re-zip the contents
        zipTempDir.zip(toFile)
        zipTempDir.delete()

        # Convert back to the word docuemnt
        #oooConverter.convert DocTo(toFile, sourceFileName)
        oooConverter.convertDocumentTo(toFile, sourceFileName)
        tempDir.delete()        # remove tempDir


    def __processZipFile(self, item, copyFrom, copyTo):
        if self.__output is not None:
            #msg =  "Processing links for copy: %s from %s to %s\n"
            #msg = msg % (item.relPath, copyFrom, copyTo)
            #self.__output.write(msg)
            pass
        tempDir = item.unzipToTempDir()
        contentFilename = self.__fs.join(str(tempDir), "content.xml")
        self.__processXmlFile(contentFilename, item, copyFrom, copyTo)

        item.zipFromTempDir(tempDir)
        tempDir.delete()


    def __processXmlFile(self, xmlFileName, item, copyFrom, copyTo):
        """ xml - xml string or xml file to be transformed """
        # Note: xml can be an XML file, a XML string or a XMLDOM object
        dom = self.iceContext.Xml(xmlFileName, [("xlink", "http://www.w3.org/1999/xlink")])

        if dom==None:
            if self.__output is not None:
                msg = "*** ERROR: Failed to transformToDom! ***\n"
                msg += " Skipping sourceFile %s\n" % item.relPath
                self.__output.write(msg)
            return
        # fixup links for new path
        self.__fixupLinks(dom, copyFrom, copyTo)
        # save
        dom.saveFile(xmlFileName)
        dom.close()


    # process all xlink:href link nodes
    def __fixupLinks(self, dom, copyFrom, copyTo):
        # this method assumes all internal links are absolute links
        refNodes = dom.getNodes("//*[@xlink:href]")    # need a context with xmlns to process the xlink:href attribute

        if self.__output is not None:
            #msg = "processing %s nodes \n" % len(refNodes)
            #self.__output.write(msg)
            pass
        for ref in refNodes:
            url = ref.getAttribute("href")
            #print "changing url %s" % url
            url = self.__fixCopiedLink(url, copyFrom, copyTo)
            if url!=None:
                #print "  to url '%s'" % url
                ref.setAttribute("href", url)


    #
    def __fixCopiedLink(self, link, copyFrom, copyTo):
        if link == None:
            return None
        if link.startswith(self.__localBaseUrl):
            link = link.replace(copyFrom, copyTo)
        return link


    def __normalizePath(self, path):
        # make sure leading and trailing slashes match
        if not path.endswith("/"):
            path = path + "/"
        if not path.startswith("/"):
            path = "/" + path
        return path


    def _testFixupLinks(self, dom, copyFrom, copyTo):
        """ for unit testing only """
        copyFrom = self.__normalizePath(copyFrom)
        copyTo = self.__normalizePath(copyTo)
        self.__fixupLinks(dom, copyFrom, copyTo)


def convert(iceContext, copyFrom, copyTo, startPath=None):
    fixer = CopyLinks(iceContext)
    fixer.convert(copyFrom, copyTo, startPath)



