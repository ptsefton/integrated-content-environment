
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

""" Plugin to convert docx document to odt, htm and pdf files """

pluginName = "ice.converter.docxToX"
pluginDesc = "Converts docx files to odt, htm, pdf files"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    """ plugin declaration method 
    @param iceContext: IceContext type
    @param kwargs: optional list of key=value pair params
    @return: handler object
    """
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = None
    pluginClass = None
    pluginInitialized = True
    return pluginFunc


class DocxToXConverter(object):
    """ Base class for DocxToXConverter  
    extension to be converted: .docx
    converted extension: .odt, .htm, .pdf 
    @ivar fromExts: to be converted file extension
    @ivar toExts: converted file extension  
    """ 
    fromExts = [".docx"]
    toExts = [".odt", ".htm", ".pdf"]
    
    def __init__(self, iceContext, **kwargs):
        """ DocxToXConverter Constructor method 
        @param iceContext: Current ice context
        @type iceContext: IceContext 
        @param kwargs: optional list of key=value pair params
        @type kwargs: dict
        @rtype: void
        """
        self.iceContext = iceContext
    
    def convert(self, fromFile, toExt=None, toFileOrDir=None, fromExt=None, **kwargs):
        """ converting docx to given extension
        @param fromFile: the original file to be converted
        @type fromFile: String
        @param toExt: the extension where the file will be converted to
        @type toExt: String
        @param toFileOrDir: the name of the file/dir where the file will be converted to
                            If toFileOrDir is None then either return a tuple ("ok", [], string) of the result or
                            ("ok", fileList, tempDir) of the results 
                            if toFileOrDir is a file then return ("ok", [toFile], None)
                            if toFileOrDir is a directory then return ("ok", [toFile], dir) or ("ok", fileList, dir)
                            On Error return ("error", detailMessagesList, "oneLineErrorMessage", exception=None)
        @type toFileOrDir: String
        @param fromExt: the extension of the file to be converted
        @type fromExt: String
        @param kwargs: optional list of key=value pair params
        @type kwargs: dict 
        @rtype: void
        """
        
        fs = self.iceContext.fs
        if fromExt is None:
            fromExt = fs.splitExt(fromFile)[1]
        fromExt = fromExt.lower()
        if fromExt not in self.fromExts:
            raise Exception("Unsupported from ext '%s' for '%s'" % (fromExt, self.__class__.__name__))
        if toExt is None:
            if not fs.isFile(toFileOrDir):
                raise Exception("toExt not given!")
            toExt = fs.splitExt(toFileOrDir)[1]
        toExt = toExt.lower()
        if toExt not in self.toExts:
            raise Exception("Unsupported to ext '%s' for '%s'" % (toExt, self.__class__.__name__))







