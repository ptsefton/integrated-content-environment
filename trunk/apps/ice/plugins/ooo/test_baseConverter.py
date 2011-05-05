#    Copyright (C) 2006  Distance and e-Learning Centre, 
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

from baseConverter import *
from diff_util import *



class mockRelativeLinkMethod(object):
    def __init__(self, sourceFilename):
        self.__count = 0
        self.__sourceFilename = sourceFilename
        
    def relativeLinkMethod(self, sourceFilename, url):
        return url

def copyToMethod(fromFilename, toFilename):
        if fromFilename!=sourceFilename:
            raise Exception("Unexcepted filename!")
        f = open(testOdtFile, "rb")
        data = f.read()
        f.close()
        f = open(toFilename, "wb")
        f.write(data)
        f.close()


class mockOooConverter:
    def __init__(self, sourceFilename, htmlFiles=[], pdfFile=None, htmlData=None):
        self.__sourceFilename = sourceFilename
        self.__htmlFiles = htmlFiles
        self.__pdfFile = pdfFile
        self.__htmlData = htmlData
        
    def convertDocumentTo(self, sourceFilename, destFilename):
        #print "mockOooConverter.convert DocTo('%s', '%s')" % (sourceFilename, destFilename)
        destName, ext = os.path.splitext(destFilename)
        destPath, destName = os.path.split(destName)
        if ext==".html":
            for htmlFile in self.__htmlFiles:
                htmlName = os.path.split(htmlFile)[1]
                self.__copy(htmlFile, os.path.join(destPath, htmlName))
            if self.__htmlData is not None:
                f = open(destFilename, "wb")
                f.write(self.__htmlData)
                f.close()
        elif ext==".pdf":
            #self.__copy(self.__pdfFile, destFilename)
            f = open(destFilename, "wb")
            f.write("PDF Data")
            f.close()
        else:
            raise Exception("trying to convert to an unknown type!")
        return True, ""
        
        
    def __copy(self, source, dest):
        #print "coping from %s to %s" % (source, dest)
        f = open(source, "rb")
        data = f.read()
        f.close()
        f = open(dest, "wb")
        f.write(data)
        f.close()



def test_embedObjectStd():
    expectedXmlStr = """<div>
    <p class="P1">MP3</p>
    <p>
    <object type="audio/mpeg" data="http://localhost:8000/packages/mypackage/media/audio/sample.mp3" height="45" width="200">
      <param name="src" value="http://localhost:8000/packages/mypackage/media/audio/sample.mp3"/>
      <param name="type" value="audio/mpeg"/>
      <param name="autoStart" value="0"/>
      <param name="controller" value="true"/>
      <p title="Object failed to load, alternative text provided">
         <a href="http://localhost:8000/packages/mypackage/media/audio/sample.mp3">This is a sample MP3 (alt Text)</a>
      </p>
    </object>
    </p>
    <p>The end.</p>
</div>"""
    sourceFilename = "/packages/test/modules/test.htm"
    testOdtFile = "testData/embedTest/stdObject.odt"
    testHtmlData = "<html><head/><body></body></html>"

    relativeLinkMethod = mockRelativeLinkMethod(sourceFilename).relativeLinkMethod
    oooConverter = mockOooConverter(testOdtFile, htmlData=testHtmlData).convertDocumentTo
    converter = BaseConverter(relativeLinkMethod, oooConverter)
    convertedData = converter.renderMethod(file=sourceFilename, absFile=testOdtFile)
    xmlStr = convertedData.getRendition(".xhtml.body")
    assertSameXml(xmlStr, expectedXmlStr)


def test_embedObjectShockwave():
    expectedXmlStr = """<div>
    <h1><a id="id1" name="id1"><!--id1--></a>Example of embedding a media file</h1>
    <p>Embedding using linked text</p>
    <p>
        <object width="300" height="120" type="application/x-shockwave-flash"
            classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000"
            codebase="http://fpdownload.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=8,0,0,0">
            <param name="movie" value="http://localhost:8000/packages/examples/media/video/player_flv.swf?media=vid_wide2.flv"/>
            <param name="url" value="http://localhost:8000/packages/examples/media/video/player_flv.swf?media=vid_wide2.flv"/>
            <param name="autoStart" value="0"/>
            <param name="base" value="."/>
            <!--[if gte IE 7]> <!-->
            <object type="application/x-shockwave-flash"
                data="http://localhost:8000/packages/examples/media/video/player_flv.swf?media=vid_wide2.flv" width="300" height="120">
                <param name="base" value="."/>
                <param name="autoStart" value="0"/>
                <p title="Object failed to load, alternative text provided">
                    <a href="http://localhost:8000/packages/examples/media/video/player_flv.swf">http://localhost:8000/packages/examples/media/video/player_flv.swf?embed&amp;media=vid_wide2.flv&amp;width=300&amp;height=120</a>
                </p>
            </object>
            <!--<![endif]-->
        </object>
    </p>
    <p/>
    <p>Embedding by linking an image</p>
    <p>
    <object width="300" height="120" type="application/x-shockwave-flash"
            classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000"
            codebase="http://fpdownload.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=8,0,0,0">
            <param name="movie" value="http://localhost:8000/packages/examples/media/video/player_flv.swf?media=vid_wide2.flv"/>
            <param name="url" value="http://localhost:8000/packages/examples/media/video/player_flv.swf?media=vid_wide2.flv"/>
            <param name="autoStart" value="0"/>
            <param name="base" value="."/>
            <!--[if gte IE 7]> <!-->
            <object type="application/x-shockwave-flash"
                data="http://localhost:8000/packages/examples/media/video/player_flv.swf?media=vid_wide2.flv" width="300" height="120">
                <param name="base" value="."/>
                <param name="autoStart" value="0"/>
                <p title="Object failed to load, alternative text provided">
                    <a href="http://localhost:8000/packages/examples/media/video/player_flv.swf"></a>
                </p>
            </object>
            <!--<![endif]-->
        </object>
      
    </p>
    <p/>
    <p>
    <object width="300" height="120" type="application/x-shockwave-flash"
            classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000"
            codebase="http://fpdownload.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=8,0,0,0">
            <param name="movie" value="http://localhost:8000/packages/examples/media/flash/flash.swf"/>
            <param name="url" value="http://localhost:8000/packages/examples/media/flash/flash.swf"/>
            <param name="autoStart" value="0"/>
            <param name="base" value="."/>
            <!--[if gte IE 7]> <!-->
            <object type="application/x-shockwave-flash"
                data="http://localhost:8000/packages/examples/media/flash/flash.swf" width="300" height="120">
                <param name="base" value="."/>
                <param name="autoStart" value="0"/>
                <p title="Object failed to load, alternative text provided">
                    <a href="http://localhost:8000/packages/examples/media/flash/flash.swf">http://localhost:8000/packages/examples/media/flash/flash.swf?embed&amp;width=300&amp;height=120</a>
                </p>
            </object>
            <!--<![endif]-->
        </object>
    </p>
    <p/>
    </div>"""
    sourceFilename = "/packages/test/modules/objects.htm"
    testOdtFile = "testData/embedTest/objects.odt"
    testPdfFile = "testData/embedTest/objects.pdf"
    testHtmlFiles = ["testData/embedTest/temp.html", "testData/embedTest/temp_html_m36b96d90.png"]
    
    relativeLinkMethod = mockRelativeLinkMethod(sourceFilename).relativeLinkMethod
    oooConverter = mockOooConverter(testOdtFile, testHtmlFiles, testPdfFile).convertDocumentTo
    
    converter = BaseConverter(relativeLinkMethod, oooConverter)
    convertedData = converter.renderMethod(file=sourceFilename, absFile=testOdtFile)
    #print 
    #print str(convertedData)
    #print 
    xmlStr = convertedData.getRendition(".xhtml.body")
    #print xmlStr
    assertSameXml(xmlStr, expectedXmlStr)


def test_specialCharacter():
    expected = """<div><p class="P1"><span class="spCh spChx201c">\xe2\x80\x9c</span>Hello<span class="spCh spChx201d">\xe2\x80\x9d</span></p><p class="P2"/></div>"""
    sourceFilename = "/packages/test/modules/specialChar.htm"
    testOdtFile = "testData/specialCharacters/specialChar.odt"
    testHtmlData = "<html><head/><body></body></html>"

    relativeLinkMethod = mockRelativeLinkMethod(sourceFilename).relativeLinkMethod
    oooConverter = mockOooConverter(testOdtFile, htmlData=testHtmlData).convertDocumentTo
    
    converter = BaseConverter(relativeLinkMethod, oooConverter)
    convertedData = converter.renderMethod(file=sourceFilename, absFile=testOdtFile)

    xmlStr = convertedData.getRendition(".xhtml.body")
    print "===="
    print xmlStr
    print "===="
    assert xmlStr == expected











    