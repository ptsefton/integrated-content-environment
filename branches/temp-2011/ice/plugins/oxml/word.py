#!/usr/bin/env ip
#
#    Copyright (C) 2010  Distance and e-Learning Centre,
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
try:
    import clr
    import System
    clr.AddReference("System.Windows.Forms")
    from System.Windows.Forms import MessageBox
    clr.AddReference("Microsoft.Office.Interop.Word")
    from Microsoft.Office.Interop import Word
    errorMsg = None
except Exception, e:
    errorMsg = "ERROR: %s" % str(e)



class MSWord(object):
    ErrorMessage = None

    def __init__(self):
        self.__app = Word.ApplicationClass()
        self.__missing = System.Type.Missing
        self.__pdfFormat = Word.WdExportFormat.wdExportFormatPDF
        self.__optimizeFor = Word.WdExportOptimizeFor.wdExportOptimizeForPrint
        self.__rangeAll = Word.WdExportRange.wdExportAllDocument
        self.__itemDocContent = Word.WdExportItem.wdExportDocumentContent
        self.__createBookmarks = Word.WdExportCreateBookmarks.wdExportCreateWordBookmarks
        self.__doc = None
        self.__file = None
        self.__extMap = {
                            ".txt": Word.WdSaveFormat.wdFormatText,
                            ".utxt": Word.WdSaveFormat.wdFormatUnicodeText,
                            ".odt": Word.WdSaveFormat.wdFormatOpenDocumentText,
                            ".doc": Word.WdSaveFormat.wdFormatDocument,
                            ".docx": Word.WdSaveFormat.wdFormatXMLDocument,
                            ".html": Word.WdSaveFormat.wdFormatFilteredHTML,
                            ".htm": Word.WdSaveFormat.wdFormatFilteredHTML,
                            ".fullhtml": Word.WdSaveFormat.wdFormatHTML,
                            ".fxml": Word.WdSaveFormat.wdFormatFlatXML,
                            ".webarc": Word.WdSaveFormat.wdFormatWebArchive,
                            ".dos": Word.WdSaveFormat.wdFormatDOSText,
                            ".rdf": Word.WdSaveFormat.wdFormatRTF,
                            ".pdf": None
                        }

    def open(self, file):
        self.closeDoc()
        try:
            self.__file = file
            self.__doc = self.__app.Documents.Open(file)
        except Exception, e:
            self.__file = None
            raise e

    def createNew(self):
        self.closeDoc()
        self.__doc = self.__app.Documents.Add()

    def setWebPixelsPerInch(self, pixelsPerInch=120):
        self.__doc.WebOptions.PixelsPerInch = pixelsPerInch

    def saveAsPDF(self, file=None):
        if file is None:
            file = self.__getFileWithExt(".pdf") 
        self.__doc.ExportAsFixedFormat(file, self.__pdfFormat, False, self.__optimizeFor,
                            self.__rangeAll, 0, 0, self.__itemDocContent, True, True,
                            self.__createBookmarks, True, True, False)
        return file

    def saveAsHTML(self, file=None):
        return self.saveAs(file, ".html")

    def saveAsODT(self, file=None):
        return self.saveAs(file, ".odt")

    def saveAsText(self, file=None):
        return self.saveAs(file, ".txt")

    def saveAsXML(self, file=None):
        return self.saveAs(file, ".xml")

    def saveAsXMLDocument(self, file=None):
        if file is None:
            file = self.__getFileWithExt(".docx")
        return self.__doc.SaveAs(file, Word.WdSaveFormat.wdFormatXMLDocument)
    saveAsDocx = saveAsXMLDocument

    def saveAsDoc97(self, file=None):
        if file is None:
            file = self.__getFileWithExt(".doc")
        return self.__doc.SaveAs(file, Word.WdSaveFormat.wdFormatDocument97)

    def saveAs(self, file=None, ext=None):
        if ext is None and file is None:
            raise Exception("the file or ext argument must be given!")
        if ext is None and file is not None:
            ext = self.__splitExt(file)[1]
        ext = ext.lower()
        if ext==".pdf":
            return self.saveAsPDF(file)
        saveFormat = self.__extMap.get(ext)
        if saveFormat is None:
            raise Exception("Unsuppored ext format!")
        if file is None:
            file = self.__getFileWithExt(ext)
        self.__doc.SaveAs(file, saveFormat)
        return file

    def extractObjectImages(self, fs, file, objDocument):
        hFile = None
        try:
            oDocx = fs.absPath("obj.docx").replace("/", "\\")
            fs.copy(file, oDocx)
            data = objDocument.encode("utf-8")
            fs.addToZipFile(oDocx, "word/document.xml", data)
            self.open(oDocx)
            self.setWebPixelsPerInch(2*96)       # or 2*120)
            #self.setWebPixelsPerInch(240)
            hFile = self.saveAsHTML()
        finally:
            self.close()
        return hFile

    # For Testing only
    #  Doc - .Range(), .Repaginate(), .Paragraphs(), .Bookmarks, .Sections, .Sentences
    #  Range - .Text, .InsertFile(), .Font, .Style, etc
    #  doc.ActiveWindow.Selection - .Text, .XML, .ClearFormatting, .InsertFile, .TypeText, .EndKey, HomeKey, etc
    def _insertText(self, text=None):
        if text is None:
            text = "Hello MSWord\r"
        range = self.__doc.Range(0,0)
        range.Text = text

    def _insertTable(self):
        range = self.__doc.Range(0,0)
        table = self.__doc.Tables.Add(range, 3, 4)
        table.Cell(3,4).Range.Text = "Cell 3x4" # Note: 1 offset
        table.Cell(1,1).Range.Text = "Cell 1x1"
        table.Style = Word.WdBuiltinStyle.wdStyleTableLightList

    def _insertSomeHeadings(self):
        r = self.__doc.Range(0,0)
        r.Text = "Heading1\rHeading2a\rHeading3\rHeading2b\rHeading three\rHeading One\r"
        r.Paragraphs[1].Style="Heading 1"   # Note: also sets Paragraphs.OutlineLevel to 1
        r.Paragraphs[2].Style="Heading 2"
        r.Paragraphs[3].Style="Heading 3"
        r.Paragraphs[4].Style="Heading 2"
        r.Paragraphs[5].Style="Heading 3"
        r.Paragraphs[6].Style="Heading 1"

    def _insertTOC(self, upperHeadingLevel=1, lowerHeadingLevel=3):
        range = self.__doc.Range(0,0)
        toc = self.__doc.TablesOfContents.Add(range, True,
                                        upperHeadingLevel, lowerHeadingLevel)
        toc.Update()        # or doc.TablesOfContent[1].Update()  #Note: 1 offset

    def _show(self):
        self.__app.Application.Visible = True

    def _hide(self):
        self.__app.Application.Visible = False

    @property
    def _doc(self):
        return self.__doc

    def __del__(self):
        self.close()

    def closeDoc(self):
        if self.__doc is not None:
            self.__doc.Close(False)
            self.__doc = None
            self.__file = None

    def close(self):
        #System.Console.WriteLine("close")
        self.closeDoc()
        if self.__app is not None:
            self.__app.Quit(False)
            self.__app = None


    def __getFileWithExt(self, ext):
        return self.__splitExt(self.__file)[0] + ext


    def __str__(self):
        s = "[MsWord Object]"
        if self.__app is None:
            s += " Closed"
        if self.__file is not None:
            s += " %s" % self.__file
        elif self.__app is not None:
            s += " (NewDocument)"
        return s

    def __splitExt(self, file):
        r = file.rsplit(".", 1)
        if len(r)>1:
            r[1] = "." + r[1]
        return r

MSWord.ErrorMessage = errorMsg 




def test():
    pass

if __name__=="__main__":
    test()
