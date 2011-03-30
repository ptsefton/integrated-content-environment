
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

import gzip

pluginName = "ice.render.text"
pluginDesc = "Text render"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginClass = TextConverter
    pluginFunc = None
    pluginInitialized = True
    return pluginFunc


class TextConverter(object):
    fromToExts = {".txt":[".htm"], ".text":[".htm"]}
    
    def __init__(self, iceContext):
        self.iceContext = iceContext
    
    
    def render(self, item, convertedData, **kwargs):
        file = item.relPath
        self.__convertedData = convertedData
        try:
            absFile = self.iceContext.rep.getAbsPath(file)
            text = self.__readFile(absFile)
            html = self.iceContext.textToHtml(text)
            html = "<div>%s</div>" % html
            title = "A text document"
            title = self.iceContext.fs.split(file)[1]
            title = self.iceContext.textToHtml(title)
            convertedData.addMeta("title", title)
            convertedData.addRenditionData(".xhtml.body", html)
        except Exception, e:
            traceInfo = self.iceContext.formattedTraceback()
            errMsg = "'%s' - \n%s" % (str(e), traceInfo)
            convertedData.addErrorMessage(errMsg)
        return convertedData
    
    def __readFile(self, absFile):
        data = self.iceContext.fs.readFile(absFile)
        text = self.__encode(data)
        if text is None:
            # could be gzip compressed
            print " * might be gzipped..."
            try:
                f = gzip.open(absFile, "rb")
                data = f.read()
                text = self.__encode(data)
                f.close()
            except IOError:
                print " * not gzipped"
            if text is None:
                errMsg = "File encoding is unknown, use UTF8 or UTF16"
                text = "[%s]" % errMsg
                self.__convertedData.addErrorMessage(errMsg)
        return text
    
    def __encode(self, data):
        text = None
        try:
            text = data.decode("utf8")
            print " * utf8 ok"
        except UnicodeDecodeError:
            print " * utf8 failed, trying utf16..."
            try:
                text = data.decode("utf16")
                print " * utf16 ok"
            except UnicodeDecodeError:
                print " * utf16 failed, falling back to iso-8859-1"
                try:
                    text = data.decode("ISO-8859-1")
                except:
                    print " * iso-8859-1 failed"
                
        if text is not None:
            text = text.encode("utf-8")
        return text
    
    