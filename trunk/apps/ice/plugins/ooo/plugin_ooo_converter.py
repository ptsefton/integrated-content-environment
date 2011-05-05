
#    Copyright (C) 2005/2008  Distance and e-Learning Centre, 
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
import time
import re
from ice_data import DataClass
try:
    import pp
except:
    pp = None
try:
    import pp_worker
except:
    pp_worker = None

pluginName = "ice.ooo.OpenOfficeConverter"
pluginDesc = "OpenOfficeConverter"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method



def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = None
    pluginClass = OOoConverter
    pluginInitialized = True
    path = iceContext.fs.split(__file__)[0]
    OOoConverter.selfPath = path
    #print "  plugin_ooo_converter Done."
    return pluginClass



class OOoConverter(object):
    selfPath = None
    
    def __init__(self, iceContext, oooPort=None, oooPython=None, oooAutomateScriptPath=None, \
                    fileSystem=None, settings=None, oooHost=None):
        self.iceContext = iceContext
        if fileSystem is None:
            fileSystem = iceContext.FileSystem()
        self.__fs = fileSystem
        
        if settings is None:
            settings = iceContext.settings
        
        if oooPort is None:
            oooPort = settings.get("oooPort")
        self.__oooPort = oooPort
        
        if oooHost is None:
            oooHost = settings.get("oooHost")
        self.__oooHost = oooHost
        
        if oooPython is None:
            oooPython = settings.get("oooPythonPath")
        self.__oooPython = oooPython
        
        #print "OOOCONVERTER __INIT__"
        if oooAutomateScriptPath is None:
            oooAutomateScriptPath = "ooo_automate.py"
            if not self.__fs.isFile(oooAutomateScriptPath):
                oooAutomateScriptPath = self.selfPath + "/" + oooAutomateScriptPath
                if not self.__fs.isFile(oooAutomateScriptPath):
                    raise Exception("oooAutomateScript '%s' not found!" % oooAutomateScriptPath)
        self.__oooAutomateScriptPath = oooAutomateScriptPath
        
        self.__usingRemote = False
        self.__basePath = ""
        self.__remapPath = ""
        self.__remoteWorker = None
        self.__jobCount = 0
        if iceContext.settings.get("remoteRender", False):
            self.__usingRemote = True
            rrip = iceContext.settings.get("remoteRenderIP", "")
            self.__basePath = iceContext.settings.get("remoteRenderShare", "share?/")
            self.__remapPath = iceContext.settings.get("remoteRenderPath", "/share/").replace("\\", "/")
            if not self.__basePath.endswith("/"):
                self.__basePath += "/"
            if not self.__remapPath.endswith("/"):
                self.__remapPath += "/"
            print " -- plugin ooo converter using remote rendering remoteIP='%s' --" % rrip
            print "    (local)basePath='%s', remotePath='%s'" % ( self.__basePath, self.__remapPath)
            if pp is None:
                print "Warning: cannot do remote rendering! 'pp' not found/installed!"
            else:
                self.__remoteWorker = pp.Server(ncpus=0, ppservers=(rrip,))
            # Assert everything is OK
            try:
                # test that we can communicate with the remote machine
                r = self.__remoteWorker.submit(pp_worker.test)()
                assert(r=="workerOK"), "cannot communicate with the remote server"
                # test that the basePath exists and that we can write to it
                tmpDir = self.getTempDirectory()
                assert(tmpDir.exists), "basePath does not exist or cannot be written to"
                tmpDir.writeFile("assertTest.txt", "AssertTest")
                file = tmpDir.absolutePath("assertTest.txt")
                # test that we can access this file via the remote machine
                rfile = file.replace(self.__basePath, self.__remapPath)
                code = "f=open('%s', 'rb')\nr=f.read()\nf.close()" % rfile
                r = self.__remoteWorker.submit(pp_worker.ctest, args=(code, ))()
                assert(r=="AssertTest"), "remotePath is not valid (cannot read file)"
                # test that we can talk to OOo
                self.__remoteWorker.submit(pp_worker.addPath, args=(self.__remapPath,))
                code = "from ooo_automate import *\no=OoObject()\no.close()\nr='ok'"
                r = self.__remoteWorker.submit(pp_worker.ctest, args=(code, ))()
                assert(r=="ok"), "cannot talk to OOo"
                print "    passed all assertion tests ok"
                if tmpDir.isTempDirectory:
                    tmpDir.delete()
            except Exception, e:
                print "Assertion test error: '%s'" % str(e)
            
            if True:
                f = self.__remoteWorker.submit(pp_worker.getcwd)
                print "    getcwd='%s'" % f()
                f = self.__remoteWorker.submit(pp_worker.listdir, args=(".",))
                dlist = f()
                #for i in dlist:
                #    print "    '%s'" % i
                print
    
    @property
    def isUsingRemote(self):
        return self.__usingRemote
    
    @property
    def convertBaseDirectory(self):
        return self.__basePath
    
    def getTempDirectory(self):
        if self.__usingRemote:
            t = [str(i).rjust(2, "0") for i in time.localtime()[:6]]
            self.__jobCount += 1
            t.append(self.__jobCount)
            s = "D%s%s%sT%s%s%sJ%s" % tuple(t)
            s = self.__basePath + s
            self.iceContext.fs.makeDirectory(s)
            time.sleep(1)           ## Must wait atleast 1 Second ???? or else cannot write to folder!
            tempDir = self.iceContext.FileSystem(s)
            tempDir.setAsTempDirectoryToBeDeleted()
            return tempDir
        else:
            return self.iceContext.fs.createTempDirectory()
    
    
    def convertDocumentTo(self, absFilePath, toAbsFilePath=None, toExt=None, reindex=False):
        """ Returns (True|False, rawBinaryData|None|ErrorMessage(if False) """
        import os, time
        tmpDir = None
        absFromFile = absFilePath
        absToFile = toAbsFilePath
        if self.__usingRemote:
            print " doing a remote OOo convertion"
            tmpDir = self.getTempDirectory()
            absFromFile = str(tmpDir) + "/" + self.__fs.split(absFilePath)[1]
            #print "plugin convertDocumentTo() tmpDir='%s'" % str(tmpDir)
            #print "  absFromFile='%s'" % absFromFile
            try:
                self.__fs.copy(absFilePath, absFromFile)
            except Exception, e:
                print "  failed to copy from '%s' to '%s'" % (absFilePath, absFromFile)
                print "  %s" % str(e)
                raise e
            absToFile = str(tmpDir) + "/" + self.__fs.split(toAbsFilePath)[1]
            #print "---"
            #print "absFromFile='%s'" % absFromFile
            #print "absToFile='%s'" % absToFile
            #print "tmpDir='%s', list='%s'" % (str(tmpDir), os.listdir(str(tmpDir)))
            #print "reMap paths from '%s' to '%s'" % (self.__basePath, self.__remapPath)
        
        result = self.__remoteConvert(absFromFile, absToFile, toExt, reindex=reindex)
        
        if self.__usingRemote:
            self.__fs.copy(absToFile, toAbsFilePath)
            toDir, toName, toExt = self.__fs.splitPathFileExt(absToFile)
            toAbsDir = self.__fs.split(toAbsFilePath)[0]
            for f in [i for i in os.listdir(toDir) if i.startswith(toName+"_")]:
                self.__fs.copy(toDir + "/" + f, toAbsDir + "/" + f)
        if tmpDir is not None and tmpDir.isTempDirectory:
            tmpDir.delete()
            tmpDir = None
        
        if result.allOk:
            #print "  all ok"
            return True, result.binaryData
        else:
            return False, result.errorMessage
    
    
    def buildBook(self, fromBookFile, docs, toBookFile, baseUrl, 
                    title=None, tempDir=None):
        # remove and record all embedded objects
        #print "plugin_ooo_converter.buildBook"
        
        useHack = True
        if useHack:
            hack = BookObjectReplacementHack(self.iceContext, self.__fs)
            docs = hack.removeEmbeddedObjectsAndAddExtraPara(docs)       
        
        result = self.__remoteBuildBook(fromBookFile, docs, toBookFile, baseUrl, title)
        
        if not self.__fs.isFile(toBookFile):
            if useHack: 
                hack.cleanup()
            if hasattr(result, "errorMessage"):
                raise Exception("oooConverter.buildBook() failed to build book. Error message = '%s'" % result.errorMessage)
            else:
                raise Exception("oooConverter.buildBook() failed to create new book file '%s'!" % toBookFile)
            #print "done building book"
        
        # Hack: to work around a problem with OOo2.4 (unable to save to self)
        name, ext = self.__fs.splitExt(toBookFile)
        bookFile = name + "-2" + ext
        if useHack:
            #print "start replacing object"
            # replace embedded objects back into the book
            hack.replaceEmbeddedObjects(toBookFile, bookFile)
            hack.cleanup()
        else:
            self.__fs.copy(toBookFile, bookFile)
        result = self.__remoteReindexBook(bookFile, toBookFile=toBookFile)
        self.removeAddedParagraph(toBookFile)
        
        #print " done buildBook() result='%s'" % str(result)
        return result        
    
    
    def removeAddedParagraph(self, bookFile):
        pass
##        print "RemoveAddedPara"
##        tempFs = self.__fs.unzipToTempDirectory(bookFile)
##        try:
##            xml = self.iceContext.Xml(tempFs.absolutePath("content.xml"), self.nsList)
##            nodes = xml.getNodes("/office:text")
##            
##            for node in nodes:
##                print "NodeName='%s'" % node.getAttribute("name")
##                
##                #newNode = xml.xmlStringToElement(self.__xmlString % newNodeStr )
##                #newNode = newNode.getFirstChild()
##                #node.replace(newNode)
##            
##            xml.saveFile()
##            xml.close()
##            tempFs.zip(self.__fs.absolutePath(bookFile))
##        finally:
##            tempFs.delete()
    
    def __remoteConvert(self, absFromFile, absToFile, toExt, reindex=False):
        #print "reMap paths from '%s' to '%s'" % (self.__basePath, self.__remapPath)
        data = DataClass()
        data.oooPort = self.__oooPort
        data.oooHost = self.__oooHost
        data.function = "convertDocumentTo"
        data.file = absFromFile
        data.toFile = absToFile
        data.toExt = toExt
        data.reindex = reindex
        if self.__usingRemote:
            # remap paths to remote relative paths  (self.__basePath to self.__remapPath)
            data.file = absFromFile.replace(self.__basePath, self.__remapPath)
            data.toFile = absToFile.replace(self.__basePath, self.__remapPath)
            #print " remapped '%s' to '%s'" % (absFromFile, data.file)
            #print " remapped '%s' to '%s'" % (absToFile, data.toFile)
            r = self.__ppRemote(data)
        else:
            eData = data.getEncodedData()
            r = self.__remote(eData)
        return r
    
    
    def __remoteBuildBook(self, fromBookFile, docs, toBookFile, baseUrl, title):
        #print "ooo_converter __remoteBuildBook"
        data = DataClass()
        data.oooPort = self.__oooPort
        data.oooHost = self.__oooHost
        data.function = "buildBook"
        data.fromBookFile = fromBookFile
        data.docs = docs
        data.toBookFile = toBookFile
        data.baseUrl = baseUrl
        data.title = title
        if self.__usingRemote:
            # remap paths to remote relative paths  (self.__basePath to self.__remapPath)
            data.fromBookFile = fromBookFile.replace(self.__basePath, self.__remapPath)
            data.toBookFile = toBookFile.replace(self.__basePath, self.__remapPath)
            rDocs = []
            for doc in docs:
                # doc = [tmpPath, absPath, url, infoDict]
                rDoc = list(doc)
                rDoc[0] = doc[0].replace(self.__basePath, self.__remapPath)
                rDocs.append(rDoc)
            data.docs = rDocs
            r = self.__ppRemote(data)
        else:
            eData = data.getEncodedData()
            r = self.__remote(eData)
        return r
    
    
    def __remoteReindexBook(self, bookFile, toBookFile=None):
        data = DataClass()
        data.oooPort=self.__oooPort
        data.oooHost=self.__oooHost
        data.function = "reindex"
        data.bookFile = bookFile
        if toBookFile is None:
            toBookFile = bookFile
        data.toBookFile = toBookFile
        if self.__usingRemote:
            # remap paths to remote relative paths  (self.__basePath to self.__remapPath)
            data.bookFile = bookFile.replace(self.__basePath, self.__remapPath)
            data.toBookFile = toBookFile.replace(self.__basePath, self.__remapPath)
            r = self.__ppRemote(data)
        else:
            eData = data.getEncodedData()
            r = self.__remote(eData)
        return r
    
    
    def __remote(self, eData):
        #print "ooo_converter __remote"
        self.__tempDir = self.__fs.createTempDirectory()
        tempEDataFile = self.__tempDir.absolutePath("eData")
        self.__fs.writeFile(tempEDataFile, eData)
        result = None
        
        if self.iceContext.isMac and self.__oooPython is None:
            from ooo_automate import automate
            resultStr, msg = automate(tempEDataFile)
        else:
            #print "self.__oooPython='%s', self.__oooAutomateScriptPath='%s' " % (self.__oooPython, self.__oooAutomateScriptPath)
            if self.__oooPython is None:
                raise Exception("Error: cannot find OpenOffice.org for automation!")
            resultStr, msg = self.iceContext.system.execute(self.__oooPython, 
                                    self.__oooAutomateScriptPath, tempEDataFile)
        match = re.search("--{([^}]*)}--", resultStr)
        if match is not None and len(match.groups())>0:
            dataStr = match.groups()[0]
            result = DataClass.decodeData(dataStr)
            try:
                result.commandMessage = msg
            except:
                result += "\n" + msg
            errMatch = re.search("stderr{-{(.*?)}-}", resultStr, re.S)
            if errMatch is not None and len(errMatch.groups())>0:
                errStr = errMatch.groups()[0]
                print
                print "stdErr from ooo_automate='\n%s'" % errStr
        else:
            errMatch = re.search("stderr{-{(.*?)}-}", resultStr, re.S)
            if errMatch is not None and len(errMatch.groups())>0:
                errStr = errMatch.groups()[0]
                print "stdErr from ooo_automate='\n%s'" % errStr
            raise Exception("No valid data returned from ooo_automate.py!")
        self.__tempDir.delete()
        return result
    
    
    def __ppRemote(self, data):
        f = self.__remoteWorker.submit(pp_worker.OoAuto, args=(data,))
        result = f()
        result.commandMessage = "pp_worker"
        
        if hasattr(result, "stdErr") and result.stdErr!="":
            print "stdErr from ooo_automate='\n%s'" % result.stdErr
        return result



class BookObjectReplacementHack (object):
    def __init__ (self, iceContext, fileSystem):
        #print "BookObjectReplacementHack on mathtype object __init__"
        self.iceContext = iceContext
        self.__xmlString="""<root 
                    xmlns:draw='urn:oasis:names:tc:opendocument:xmlns:drawing:1.0' 
                    xmlns:xlink='http://www.w3.org/1999/xlink'
                    xmlns:text='urn:oasis:names:tc:opendocument:xmlns:text:1.0'
                    xmlns:svg='urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0'
                    xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
                    >%s</root>"""
        self.__tempDir = None
        self.__tempObjectDir = None
        
        #Creating temporary xml file to store the expected result
        self.__xmlDrawFrameStrNodes = {}        
        self.__fs = fileSystem
        self.__nsList = self.iceContext.OOoNS.items()
    
    
    def __del__ (self):
        if self.__tempDir is not None:
            self.__tempDir.delete()
            self.__tempDir = None
            print "Warning BookObjectRelacementHack fail to clean up tempDir"
        if self.__tempObjectDir is not None:
            self.__tempObjectDir.delete()
            self.__tempObjectDir = None
            print "Warning BookObjectRelacementHack fail to clean up tempObjectDir"
    
    
    def cleanup(self):
        if self.__tempDir is not None:
            self.__tempDir.delete()
            self.__tempDir = None
        if self.__tempObjectDir is not None:
            self.__tempObjectDir.delete()
            self.__tempObjectDir = None
    
    
    def removeEmbeddedObjectsAndAddExtraPara(self, docs):
        #print "BookObjectReplacementHack on mathtype object removeMathTypeOBjects"
        self.__tempDir = self.__fs.createTempDirectory()
        self.__tempObjectDir = self.__fs.createTempDirectory()
        newDocs = []
        countDoc=0
        
        for doc in docs:        #copying all documents to tempDir
            countDoc+=1
            ext = self.__fs.splitExt(doc[0])[1]
            tempFileName = self.__tempDir.absolutePath("temp%s%s" % (countDoc, ext))
            self.__fs.copy(doc[0], tempFileName)
            newDoc = [tempFileName]
            newDoc.extend(doc[1:])
            newDocs.append(newDoc)
        countObject=0
        countDoc=0
        
        #To Detect the error thrown by Open Office the port is not listening
        #And cause error during book creation
        try:   
            for doc in newDocs:     
                #print "BookObjectReplacementHack on mathtype object doc='%s'" % doc
                #Check for embedded Object
                countDoc+=1
                self.tempZipDir = self.__fs.unzipToTempDirectory(doc[0]) 
                xml = self.iceContext.Xml(self.tempZipDir.absolutePath("content.xml"), self.__nsList)
                nodes = xml.getNodes("//draw:frame[./draw:object-ole]")    # "//draw:frame[draw:object-ole]"
                
                #If there's Object in the doc, copy the object to the temp Folder
                if nodes!=[]:         
                    for node in nodes:
                        countObject+=1 
                        objectName = "Object%s" % countObject
                        #Copy Object Replacement Files and rename it
                                               
                        nodeNameContent = node.getAttribute("name")
                        objectOleNode = node.getNode("*[local-name()='object-ole']")
                        imageNode = node.getNode("*[local-name()='image']")
                        objectHref = objectOleNode.getAttribute("href")
                        imageHref = imageNode.getAttribute("href")
                        
                        if self.tempZipDir.isFile(objectHref):
                            newName = self.__fs.join(self.__fs.split(objectHref)[0], objectName)
                            self.tempZipDir.copy (objectHref, \
                                self.__tempObjectDir.absolutePath(newName))
                            objectOleNode.setAttribute("href", newName)                    
                        else:  
                            raise Exception ("Object href file does not exist")
                        
                        if self.tempZipDir.isFile(imageHref):
                            newName = self.__fs.join(self.__fs.split(imageHref)[0], objectName)
                            self.tempZipDir.copy(imageHref, \
                                self.__tempObjectDir.absolutePath(newName))
                            imageNode.setAttribute("href", newName)
                        else:  
                            raise Exception ("Image href file does not exist")
                        
                        #Rename Object in XML file and the frame style
                        #100 is use to avoid the frame that have already existed in the study book
                        #frameCount = countObject + 100
                        frameName = "frs%s" % countObject
                        oriFrameName = node.getAttribute("style-name")
                        node.setAttribute("name", objectName)
                        node.setAttribute("style-name", frameName)
                        
                        frStyle = xml.getNode("//style:style[@style:name='%s']" % oriFrameName)
                        frCopy = frStyle.copy()
                        frCopy.setAttribute("name", frameName)
                        
                        #Add to xml file before being removed
                        self.__xmlDrawFrameStrNodes[objectName] = str(node), str(frCopy)
                        
                        #Remove Child Object
                        #print 
                        #print "Removing node:"
                        #print str(objectOleNode)
                        #print "From:"
                        #print str(node)
                        objectOleNode.delete()
                        imageNode.removeAttribute("name")
                        #imageHref.delete(), if deleted the draw:frame node will be removed
                                  
                #Add extra paragraph (This is done to prevent the style from previous para/heading
                #to be applied to the next doc in the book)
                officeText = xml.getNode("//office:text")
                lastPara = officeText.getLastChild()
                newPara = xml.createElement("text:p", "--T--")
                newPara.setAttribute("text:style-name", "p")
                lastPara.addNextSibling(newPara)
                         
                xml.saveFile()
                xml.close()   
                self.tempZipDir.zip(doc[0])
                self.tempZipDir.delete()
        except:
            pass
        return newDocs
    
    
    def replaceEmbeddedObjects(self, bookFile, toBookFile=None):
        #Open created book xml file
        #print "BookObjectReplacementHack on mathtype object replaceEmbeddedObjects"
        if toBookFile is None:
            toBookFile = bookFile
        tempFs = self.__fs.unzipToTempDirectory(bookFile)
        try:
            xml = self.iceContext.Xml(tempFs.absolutePath("content.xml"), self.__nsList)
            automation = xml.getNode("//office:automatic-styles")
            nodes = xml.getNodes("//draw:frame")
##            for name in self.__xmlDrawFrameStrNodes.keys():
##                node = xml.getNode("//draw:frame[@draw:name='%s']" % name)
##                if node is None:
##                    raise Exception("Node not found in BookObjectReplacementHack.replaceEmbeddedObjects()")
##                newNodeStr = self.__xmlDrawFrameStrNodes[name]
##                newNode = xml.xmlStringToElement(self.__xmlString % newNodeStr )
##                newNode = newNode.getFirstChild()
##                node.replace(newNode)
            
            #The following code will give the same result as the commented code above.
            #But it will perform faster
            nodeNames = {}
            for node in nodes:
                name = node.getAttribute("name")
                #print "NodeName='%s'" % name, "node='%s'" % node
                nodeNames[name] = node
                
            for name in self.__xmlDrawFrameStrNodes.keys():
                node = nodeNames.get(name)
                if node is None:
                    print 
                    #print "node name='%s'" % name
                    raise Exception("Node not found in BookObjectReplacementHack.replaceEmbeddedObjects()")
                newNodeStr = self.__xmlDrawFrameStrNodes[name][0]
                newNode = xml.xmlStringToElement(self.__xmlString % newNodeStr )
                newNode = newNode.getFirstChild()
                node.replace(newNode)
                
                frameStyle = self.__xmlDrawFrameStrNodes[name][1]
                newNode = xml.xmlStringToElement(self.__xmlString % frameStyle )
                newNode = newNode.getFirstChild()
                if newNode is not None:
                    automation.addChild(newNode)
            #End of similar section       
            
            #Zip back the content.xml file
            xml.saveFile()
            xml.close()
            
            self.__tempObjectDir.copy(".", tempFs.absolutePath("."))
            tempFs.zip(self.__fs.absolutePath(toBookFile))
        finally:
            tempFs.delete()
            self.__tempDir.delete()
            self.__tempObjectDir.delete()
            self.__tempDir = None
            self.__tempObjectDir = None
    










