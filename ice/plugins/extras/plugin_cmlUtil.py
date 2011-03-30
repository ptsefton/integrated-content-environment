#!/usr/bin/python
#
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

""" Extra plugin to convert the Chemical markup language file (.cml)
to .png, .svg, .jmol, .cdx, .jpg
@requires: JUMBO and JMOL
@requires: http_util    from utils/http_util.py
@requires: os, sys, tempfile
"""

import os
import tempfile

pluginName = "ice.extras.cmlUtil"
pluginDesc = ""
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method

myPath = None

def pluginInit(iceContext, **kwargs):
    """ plugin declaration method 
    @param iceContext: IceContext type
    @param kwargs: optional list of key=value pair params
    @return: handler object
    """
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = None
    pluginClass = CmlUtil
    global myPath
    myPath =  iceContext.fs.split(__file__)[0]
    pluginInitialized = True
    return pluginFunc



class CmlUtil(object):
    """ Base class for CmlUtil """
    
    @staticmethod
    def getAppletHtml(cmlFile, width, height, archive="JmolApplet.jar"):
        """ get the applet span tag
        @param cmlFile: the location of the cml file
        @type cmlFile: String
        @param width: width of applet
        @type width: String
        @param height: height of applet
        @type height: String
        @param archive: jar file of JmolApplet
        @type archive: String

        @rtype: String
        @return: span tags of the applet
        """
        html  = '<span class="jmolapplet">'
        html += '<applet name="Jmol" code="JmolApplet" archive="%s" width="%s" height="%s">'
        html += '<param name="load" value="%s" />'
        html += '<param name="progressbar" value="true" />'
        html += '<param name="progresscolor" value="blue" />'
        html += '<param name="bgcolor" value="white" />'
        html += '</applet>'
        html += '</span>'
        return html % (archive, width, height, cmlFile)


    @staticmethod
    def getSvgHtml(svgFile, width, height):
        """ get the svg object tag
        @param svgFile: location of the svg file
        @type svgFile: String
        @param width: width of the svg object
        @type width: String
        @param height: height of the svn object
        @type height: String

        @rtype: String
        @return: object tag of the svg
        """
        html  = '<object type="image/svg+xml" data="%s" width="%s" height="%s"/>'
        return html % (svgFile, width, height)


    @staticmethod
    def getPngHtml(pngFile, width=None, height=None, title=None):
        """ get the png image tag
        @param pngFile: location of the png file
        @type pngFile: String
        @param width: width of the svg object
        @type width: String
        @param height: height of the svn object
        @type height: String
        @param title: title of the image
        @type title: String

        @rtype: String
        @return: image tag of the png
        """
        html = '<img src="%s" ' % pngFile
        if width is not None:
            html += 'width="%s" ' % width
        if height is not None:
            html += 'height="%s" ' % height
        if title is not None:
            html += 'title="%s" % title'
        html += "/>"
        return html


    @staticmethod
    def isRenderable(data):
        """ check if the file is renderable
        @param data: string of the object to be checked
        @type data: String
        @rtype: boolean
        @return: true if found <molecule and <atom
        """
        return data.find("<molecule") != -1 and data.find("<atom") != -1


    @staticmethod
    def is3D(data):
        """ check if the file is 3D
        @param data: string of the object to be checked
        @type data: String
        @rtype: boolean
        @return: true if found x3 and y3 nad z3
        """
        return data.find("x3") != -1 and data.find("y3") != -1 and data.find("z3") != -1


    @staticmethod
    def getJumboDefaults():
        """ get the jumbo defaul information
        @rtype: list
        @return: jumbo defaults parameter
        """
        try:
            file = self.iceContext.join(myPath, "jumbo.defaults")
            params = self.iceContext.readFile(file).strip()
        except:
            path = os.path.split(__file__)[0]
            defaults = os.path.join(path, "jumbo.defaults")
            f = open(defaults)
            params = f.read().strip()
            f.close()
        return params


    def __init__(self, iceContext, remoteServiceUrl=None):
        """ Chemical Markup Language Util Constructor method 
        if ice is not run as service and JUMBO and JMOL are not installed locally,
            .cml is sent to the server to be processed
        @param iceContext: Current ice context
        @type iceContext: IceContext 
        @param remoteServiceUrl: url where ice service located
        @type removeServiceUrl: String 
        
        @rtype: void
        """
        self.iceContext = iceContext
        asServiceOnly = iceContext.settings.get("asServiceOnly", False)
        if asServiceOnly:
            self.__remoteServiceUrl = None
        else:
            if remoteServiceUrl is None:
                self.__remoteServiceUrl = "http://ice-service.usq.edu.au/api/convert"
            else:
                self.__remoteServiceUrl = remoteServiceUrl


    def createPreviewImage(self, urlOrData, format, width="300", height="300",
                           params=None):
        """ creating preview for the converted image
        @param urlOrData: url or data to be previewed
                          if it's url, http_post will be performed to get the data remotely
        @type urlOrData: String
        @param format: format of the file
        @type format: String
        @param width: width of the preview
        @type width: String
        @param height: height of the preview
        @type height: String
        @param params: additional parameter list
        @type params: String
        
        @rtype: String
        @return: the converted data in preview
        """
        if params is None:
            params = self.getJumboDefaults()
        self.__cmdPath = self.__getLocalService(format)
        hasJava = self.__hasJava()
        if self.__cmdPath != None and hasJava:
            print 'Local mode using %s' % self.__cmdPath
            if self.__isUrl(urlOrData):
                data, _, errCode, msg = self.iceContext.Http().get(urlOrData,
                                            includeExtraResults=True)
                if errCode == -1:
                    raise Exception("Failed to read data from %s, %s" % (data, msg))
            else:
                data = urlOrData
            return self.__createPreviewLocal(data, format, width, height, params)
        else:
            if self.__remoteServiceUrl is None:
                raise Exception('CML services unavailable')
            print 'Remote mode using: %s' % self.__remoteServiceUrl
            return self.__createPreviewRemote(urlOrData, format, width, height, params)
    
    
    def __hasJava(self):
        cmd = "java"
        if self.iceContext.isWindows:
            return r"%s" % cmd
        stdout, stderr = self.iceContext.system.executeNew(cmd)
        if self.iceContext.isWindows:
            keyword = "recognized"
        else:
            keyword = "found"
        hasLocal = stderr.find("not " + keyword) == -1
        return hasLocal
    
    def __createPreviewLocal(self, data, format, width, height, params):
        """ creating local preview for the converted image
        @param data: data to be previewed
        @type data: String
        @param format: format of the file
        @type format: String
        @param width: width of the preview
        @type width: String
        @param height: height of the preview
        @type height: String
        @param params: additional parameter list
        @type params: String
        
        @rtype: String
        @return: the converted data in preview
        """
        ifd, inputFile = tempfile.mkstemp(".tmp", "jmol")
        os.write(ifd, data)
        os.close(ifd)
        
        ofd, outputFile = tempfile.mkstemp("." + format.lower(), "jmol")
        os.close(ofd)
        if format in ["png", "svg"]:
            self.__invokeJumbo(inputFile, outputFile, format, params)
        else:
            self.__invokeJmol(inputFile, outputFile, format, width, height)
        f = open(outputFile, "rb")
        content = f.read()
        f.close()
        
        return content
    
    
    def __createPreviewRemote(self, urlOrData, format, width, height, params):
        """ creating remote preview for the converted image
        @param urlOrData: data or url to be previewed
        @type urlOrData: String
        @param format: format of the file
        @type format: String
        @param width: width of the preview
        @type width: String
        @param height: height of the preview
        @type height: String
        @param params: additional parameter list
        @type params: String
        
        @rtype: String
        @return: the converted data in preview requested from server
        """
        baseUrl = self.__remoteServiceUrl
        postData = [('mode', 'preview'),
                    ('format', format),
                    ('width', width),
                    ('height', height),
                    ('params', params)]
        if self.__isUrl(urlOrData):
            postData.append(('url', urlOrData))
        else:
            postData.append(('file', ('preview.cml', urlOrData)))
        return self.iceContext.Http().post(baseUrl, postData)
    
    
    def __invokeJmol(self, inputFile, outputFile, format, width, height):
        """ invoking jmol command to convert the file
        @param inputFile: location path of the inputfile
        @type inputFile: String
        @param outputFile: location path of the outputFile
        @type outputFile: String
        @param format: format in which the inputFile will be converted
        @type format: String
        @param width: width of the preview
        @type width: String
        @param height: height of the preview
        @type height: String
        
        @raise Exception: if fail to convert or fail to create preview
        @rtype: void
        """
        try:
            jmolCmd = self.__getJmolCmd()
            fd, name =  tempfile.mkstemp(".jmol", "ice")
            os.write(fd, "load %s" % inputFile)
            os.close(fd)
            _, stderr = self.iceContext.system.execute2("java", "-jar", jmolCmd, "-n", 
                                                        "-g", "%sx%s" % (width, height), "-xios", name, "-w", 
                                                        "%s:%s" % (format, outputFile.replace("\\", "/")))
            if stderr != "":
                raise Exception(stderr)
            if len(stderr) > 0:
                raise Exception(stderr)
        except Exception, e:
            print "Failed to create preview: %s" % str(e)
    
    
    def __invokeJumbo(self, inputFile, outputFile, format, params):
        """ invoking jumbo command to convert the file
        @param inputFile: location path of the inputfile
        @type inputFile: String
        @param outputFile: location path of the outputFile
        @type outputFile: String
        @param format: format in which the inputFile will be converted
        @type format: String
        @param width: width of the preview
        @type width: String
        @param height: height of the preview
        @type height: String
        
        @raise Exception: if fail to convert or fail to create preview
        @rtype: void
        """
        try:
            converter = ""
            converterClass = ""
            jumboCmd = self.__getJumboCmd()
            if format == "png":
                converterClass = "org.xmlcml.cml.converters.graphics.png.CML2PNGConverter"
            elif format == "svg":
                converterClass = "org.xmlcml.cml.converters.graphics.svg.CML2SVGConverter"
            if converterClass != "":
                converter = "-converter"
            _, stderr = self.iceContext.system.execute2("java", "-jar", jumboCmd,
                    converter,  converterClass, "-it", "cml", "-ot", format,
                    "-i", inputFile, "-o", outputFile, "--", params)
            if stderr != "":
                raise Exception(stderr)
        except Exception, e:
            print "Failed to create preview: %s" % str(e)
    
    
    def extractChemDraw(self, urlOrData, outputDir = None, name = "mols.odt"):
        """ Extracting chemical draw
        @param urlOrData: url or data to be converted
        @type urlOrData: String
        @param outputDir: output location
        @type outputDir: String
        @param name: name of the file
        @type name: String
        
        @rtype: zip file content
        @return: zip file of the extracted chemical draw         
        """
        self.__cmdPath = self.__getLocalService("cdx")
        if self.__cmdPath != None:
            print 'Local mode using %s' % self.__cmdPath
            if self.__isUrl(urlOrData):
                data, _, errCode, msg = self.iceContext.Http().get(urlOrData,
                                                    includeExtraResults=True)
                if errCode == -1:
                    raise Exception("Failed to read data from %s, %s" % (data, msg))
            else:
                data = urlOrData
            return self.__extractChemDrawLocal(data, outputDir, name)
        else:
            if self.__remoteServiceUrl == None:
                raise Exception('CML services unavailable')
            print 'Remote mode using: %s' % self.__remoteServiceUrl
            return self.__extractChemDrawRemote(urlOrData, outputDir, name)
    
    
    def __extractChemDrawLocal(self, data, outputDir, name):
        """ Extracting chemical draw locally
        @param data: data to be converted
        @type data: String
        @param outputDir: output location
        @type outputDir: String
        @param name: name of the file
        @type name: String
        
        @rtype: String
        @return: zip file of the extracted chemical draw         
        """
        tmpFs = self.iceContext.fs.createTempDirectory()
        tmpFs.writeFile(name, data)
        inputFile = tmpFs.absPath(name)
        
        if outputDir is None:
            basePath = tmpFs.absPath()
            tmpFs.makeDirectory("media")
            outputDir = self.iceContext.fs.join(basePath, "media")
        
        self.__invokeCdx2Cml(inputFile, outputDir)
        
        tmpFs.zip("media.zip", "media")
        content = tmpFs.readFile("media.zip")
        tmpFs.delete()
        
        return content
    
    
    def __extractChemDrawRemote(self, urlOrData, outputDir, name):
        """ Extracting chemical draw remotely
        @param urlOrData: url or data to be converted
        @type urlOrData: String
        @param outputDir: output location
        @type outputDir: String
        @param name: name of the file
        @type name: String
        
        @rtype: String
        @return: zip file of the extracted chemical draw         
        """
        baseUrl = self.__remoteServiceUrl
        postData = [('pathext', '.cml'), ('mode', 'extract')]
        if self.__isUrl(urlOrData):
            postData.append(('url', urlOrData))
        else:
            postData.append(('file', (name, urlOrData)))
        zipData = self.iceContext.Http().post(baseUrl, postData)
        if outputDir is not None:
            tmpFs = self.iceContext.fs.createTempDirectory()
            tmpFs.writeFile("media.zip", zipData)
            tmpFs.unzipToDirectory("media.zip", outputDir)
            tmpFs.delete()
        return zipData
    
    
    def __invokeCdx2Cml(self, inputFile, outputDir):
        """ Converting .cdx to .cml
        @param inputFile: absolute path of cdx file
        @type inputFile: String
        @param outputDir: output location
        @type outputDir: String
        
        @rtype: void         
        """
        tmpFs = None
        try:
            tmpFs = self.iceContext.fs.unzipToTempDirectory(inputFile)
            toDir = tmpFs.absPath()
            tmpFs.unzipToDirectory(inputFile, toDir)
            tmpFs.makeDirectory("raw")
            tmpFs.makeDirectory("cml")
            cmdPath = self.__getChemDrawCmd()
            self.iceContext.system.execute2(cmdPath, "-INDIR", toDir,
                                     "-INSUFF", '""',
                                     "-RAWDIR", "../raw",
                                     "-RAWSUFF", ".xml",
                                     "-OUTDIR", "../cml", printErr = False)
            _, name, _ = tmpFs.splitPathFileExt(inputFile)
            for file in tmpFs.listFiles("cml"):
                srcFile = tmpFs.join("cml", file)
                outFile = tmpFs.join(outputDir, file.replace("Object ", name + "-"))
                tmpFs.copy(srcFile, outFile)
        finally:
            if tmpFs != None:
                tmpFs.delete()
    
    
    def __isUrl(self, url):
        """ to check if it's a url or a data
        @param url: url to be checked
        @type url: String
        @rtype: boolean
        @return: true if the url startswith http:// or https://  
        """
        if type(url)==str:
            return url.startswith('http://') or url.startswith('https://')
        return False
    
    
    def __getLocalService(self, format):
        """ get the local service if available
        @param format: file format to be converted 
        @type format: String
        @rtype: String
        @return: command path if exist or None if not exist locally
        """
        try:
            if format in ["png", "svg"]:
                return self.__getJumboCmd()
            elif format == "jpg":
                return self.__getJmolCmd()
            elif format == "cdx":
                return self.__getChemDrawCmd()
        except Exception, e:
            print str(e)
        return None
    
    
    def __getJmolCmd(self):
        """ get jmol command through JMOL_HOME
        @rtype: String
        @return: jmol command path
        """
        return self.__getCmd("JMOL_HOME", "Jmol.jar", "Jmol")
    
    
    def __getJumboCmd(self):
        """ get jumbo command through JUMBO_HOME
        @rtype: String
        @return jumbo command path
        """
        return self.__getCmd("JUMBO_HOME", "jumbo-converters.jar", "JUMBO")
    
    
    def __getChemDrawCmd(self):
        """ get jumbo command through JUMBO_HOME for cdx2cml
        @rtype: String
        @return jumbo command path
        """
        return self.__getCmd("JUMBO_HOME", "cdx2cml", "ChemDraw to CML")
    
    def __getCmd(self, homeEnv, cmd, desc):
        """ get the command from local installation
        @param homeEnv: system environment for the comamnd
        @type homeEnv: String
        @param cmd: command to be executed
        @type cmd: String
        @param desc: Description of the comamnd
        @type desc: String
        
        @rtype: String
        @return: if the command is installed locally, return the comannd path
        @raise Exception: if the command is not installed locally  
        """
        home = self.iceContext.system.environment.get(homeEnv, "")
        if home == '':
            #Use jumbo and jmol jar from the trunk
            cmdPath = "plugins/extras/cml/%s" % (cmd)
            cmdPath = self.iceContext.fs.absPath(cmdPath)
            cmdPath = cmdPath.replace("//", "/")
        else:
            cmdPath = "%s/%s" % (home, cmd)
            cmdPath = cmdPath.replace("//", "/")
        if self.iceContext.fs.exists(cmdPath):
            return cmdPath
        else:
            raise Exception("No %s installation in %s" % (desc, home))



if __name__ == '__main__':
    """ main function to run the cmlUtil plugin
    """
    import sys
    if len(sys.argv) < 6:
        print "usage: python %s url format width height outputFile [remoteServiceUrl]\n" % sys.argv[0]
        print "where format is one of: jpg, png, svg"
    else:
        if len(sys.argv) > 6:
            util = CmlUtil(sys.argv[6])
        else:
            util = CmlUtil()
        data = util.createPreviewImage(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
        f = open(sys.argv[5], "wb")
        f.write(data)
        f.close()
    
