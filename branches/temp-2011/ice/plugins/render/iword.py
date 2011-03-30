
import sys
try:
    import clr
    import System
    clr.AddReference("System.Windows.Forms")
    from System.Windows.Forms import MessageBox
    clr.AddReference("Microsoft.Office.Interop.Word")
    from Microsoft.Office.Interop import Word
except Exception, e:
    print "ERROR:"
    print str(e)
    print "--END--"

def main(args):
    #MessageBox.Show("Main args=%s" % str(args))
    comms()
    
def comms():
    try:
        word = MsWord()
    except Execption, e:
        print "ERROR: " + str(e)
        print "--END--"
        return
    print "STARTED OK:"
    print "--END--"
    result = ""
    while(True):
        try:
            cmd, data = read().split(":", 1)
            cmd = cmd.lower()
            if data.endswith(":"):
                data = data[:-1]
            if cmd=="exit":
                break
            elif cmd=="message":
                MessageBox.Show(data)
            elif cmd=="word":
                exec("result = word."+data)
                write(result)
            elif cmd=="exec":
                result = ""
                exec(data)
                if result!="":
                    write(result)
            else:
                raise Exception("Unknown command '%s'" % cmd)
            write("--END--")
        except Exception, e:
            write("EXCEPTION:")
            write(str(e))
            write("--END--")
    word.close()

def read():
    return raw_input() + ":"

def write(data):
    print (data)
    sys.stdout.flush()


class MsWord(object):
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
    
    def saveAsPDF(self, file=None):
        if file is None:
            file = self.__getFileWithExt(".pdf")
        self.__doc.ExportAsFixedFormat(file, self.__pdfFormat, False, self.__optimizeFor,
                            self.__rangeAll, 0, 0, self.__itemDocContent, True, True,
                            self.__createBookmarks, True, True, False)
    
    def saveAsODT(self, file=None):
        self.saveAs(file, ".odt")

    def saveAsText(self, file=None):
        self.saveAs(file, ".txt")
    
    def saveAsHTML(self, file=None):
        self.saveAs(file, ".html")
    
    def saveAsXML(self, file=None):
        self.saveAs(file, ".xml")
    
    def saveAsXMLDocument(self, file=None):
        if file is None:
            file = self.__getFileWithExt(".docx")
        self.__doc.SaveAs(file, Word.WdSaveFormat.wdFormatXMLDocument)
    saveAsDocx = saveAsXMLDocument
    
    def saveAsDoc97(self, file=None):
        if file is None:
            file = self.__getFileWithExt(".doc")
        self.__doc.SaveAs(file, Word.WdSaveFormat.wdFormatDocument97)
    
    def saveAs(self, file=None, ext=None):
        if ext is None and file is None:
            raise Exception("the file or ext argument must be given!")
        if ext is None and file is not None:
            ext = self.__splitExt(file)[1]
        ext = ext.lower()
        if ext==".pdf":
            self.saveAsPDF(file)
            return
        saveFormat = self.__extMap.get(ext)
        if saveFormat is None:
            raise Exception("Unsuppored ext format!")
        if file is None:
            file = self.__getFileWithExt(ext)
        self.__doc.SaveAs(file, saveFormat)
    
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

	
if __name__=="__main__":
    args = sys.argv
    if(len(args)>0):
        args.pop(0)
    main(args)


