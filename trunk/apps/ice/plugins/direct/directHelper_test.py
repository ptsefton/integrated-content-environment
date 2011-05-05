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

try:
    from ice_common import IceCommon
    IceCommon.setup()
except:
    import sys, os
    sys.path.append(os.getcwd())
    sys.path.append(".")
    os.chdir("../../")
    from ice_common import IceCommon

import tempfile
from local_directHelper import *

REPLACE_NS = ' xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0" xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"'

class mockIceContext(object):
    def __init__(self):
        pass

class DirectHelperTests(IceCommon.TestCase):
    def __init__(self, name):
        IceCommon.TestCase.__init__(self, name)
        self.fs = IceCommon.fs
        self.xml = IceCommon.Xml
        self.iceContext = IceCommon.IceContext(loadRepositories=False, loadConfig=False)

    def setUp(self):
        pass

    def teardown(self):
        pass
    
    def xtestSRMSObject(self):
        xmlcontent = """<root>
<srms_matches>
<match>
<srms_prod_ref>TPP7120CDT1</srms_prod_ref>
<srms_type>CDT</srms_type>
<direct_total>74</direct_total>
<direct_type>CD</direct_type>
</match>
<match>
<srms_prod_ref>TPP7120CDT2</srms_prod_ref>
<srms_type>CDT</srms_type>
<direct_total>32</direct_total>
<direct_type>CD</direct_type>
</match></srms_matches></root>
"""
        xml = self.xml(xmlcontent)
        requestType = "CDT"
        directTypes = ["CD"]
        srmsObject = SRMSObject(xml, requestType, directTypes)
        
        self.assertEquals(srmsObject.requestType, "CDT")
        self.assertEquals(srmsObject.direct_types, ["CD"])
        self.assertTrue(srmsObject.hasProdRef)
        self.assertEquals(srmsObject.prodRefList, {'TPP7120CDT1': 74, 'TPP7120CDT2': 32})
        
        xml = self.xml(xmlcontent)
        requestType = "WWW"
        srmsObject = SRMSObject(xml, requestType)
        self.assertFalse(srmsObject.hasProdRef)
        
        xmlcontent = """<root>
<srms_matches>
<match>
<srms_prod_ref>TPP7120SR1</srms_prod_ref>
<srms_type>SR</srms_type>
<direct_total>74</direct_total>
<direct_type>Print</direct_type>
</match>
<match>
<srms_prod_ref>TPP7120I/SB</srms_prod_ref>
<srms_type>I/SB</srms_type>
<direct_total>32</direct_total>
<direct_type>Print</direct_type>
</match></srms_matches></root>
"""
        xml = self.xml(xmlcontent)
        requestType = "SR"
        directTypes = ["Print"]
        srmsObject = SRMSObject(xml, requestType, directTypes)
        
        self.assertEquals(srmsObject.requestType, "SR")
        self.assertEquals(srmsObject.direct_types, ["Print"])
        self.assertTrue(srmsObject.hasProdRef)
        self.assertEquals(srmsObject.prodRefList, {'TPP7120SR1': 74, 'TPP7120I/SB': 32})

    def xtestRequestObject(self):
        xmlContent = """<root>
<request>
<data_source>DiReCt</data_source>
<course_code>TPP7120</course_code>
<course_name>Studying to Succeed</course_name>
<course_faculty>ELEPC</course_faculty>
<course_year>2009</course_year>
<course_semester>S1</course_semester>
<srms_prod_ref>TPP7120CW</srms_prod_ref>
</request>
</root>"""

        xml = self.xml(xmlContent)
        requestNode = xml.getNode("//request")
        sitePath = self.fs.absolutePath("plugins/direct")
        
        requestObject = RequestObject(requestNode, sitePath)
        
        self.assertEquals(requestObject.sitePath, "/home/octalina/workspace/trunk/apps/ice/plugins/direct")
        self.assertEquals(requestObject.courseCode, "TPP7120")
        self.assertEquals(requestObject.courseName, "Studying to Succeed")
        self.assertEquals(requestObject.courseFaculty, "ELEPC")
        self.assertEquals(requestObject.courseYear, "2009")
        self.assertEquals(requestObject.courseSemester, "S1")
        self.assertEquals(requestObject.prodRef, "TPP7120CW")
        self.assertEquals(requestObject.departmentName, "")
        self.assertEquals(requestObject.warning, "")
        self.assertEquals(requestObject.facultyName, "Eng Lang & Enabling Prog Cntr")
        xml.close()
    
    def xtestCopyrightNotice(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?><root/>"""
        xmlContent = self.xml(xml)
        copyrightCode = "RWP"
        copyrightNotice = ""
        cpClass = CopyRightClass(copyrightCode, copyrightNotice)
        self.assertEquals(cpClass.errorStr, "Reproduce with Permission copyright code found but the copyright notice is empty")
        self.assertTrue(cpClass.isSpecial)
        self.assertFalse(cpClass.isValid)
        self.assertEquals(cpClass.copyrightNotice, "")
        #if RWP and no notice
        codeNode = cpClass.getCopyrightCodeNode(xmlContent)
        self.assertEquals(codeNode, None)
        copyrightNotice = cpClass.getCopyrightNoticeNode(xmlContent)
        self.assertEquals(copyrightNotice, None)
        
        #VALID!
        copyrightCode = "RWP"
        copyrightNotice = "This is just reproduce with permission string"
        cpClass = CopyRightClass(copyrightCode, copyrightNotice)
        self.assertEquals(cpClass.errorStr, "")
        self.assertTrue(cpClass.isSpecial)
        self.assertTrue(cpClass.isValid)
        self.assertEquals(cpClass.copyrightNotice, "This is just reproduce with permission string")
        #if RWP, no code Node but get the notice
        codeNode = cpClass.getCopyrightCodeNode(xmlContent)
        self.assertEquals(codeNode, None)
        copyrightNotice = cpClass.getCopyrightNoticeNode(xmlContent)
        self.assertEquals(str(copyrightNotice), 
                '<text:p text:style-name="p"><text:span text:style-name="alternatives">This is just reproduce with permission string</text:span></text:p>')
        
        #VALID!
        copyrightCode = "135ZL"
        copyrightNotice = ""
        cpClass = CopyRightClass(copyrightCode, copyrightNotice)
        self.assertEquals(cpClass.errorStr, "")
        self.assertFalse(cpClass.isSpecial)
        self.assertTrue(cpClass.isValid)
        self.assertEquals(cpClass.copyrightNotice, "")
        #if not special, just get the copyright code
        codeNode = cpClass.getCopyrightCodeNode(xmlContent)
        self.assertEquals(str(codeNode), '<text:span text:style-name="copyright"> [135ZL]</text:span>')
        copyrightNotice = cpClass.getCopyrightNoticeNode(xmlContent)
        self.assertEquals(copyrightNotice, None)
        
        #VALID!
        copyrightCode = "135ZL"
        copyrightNotice = "Commonwealth of Australia ..."
        cpClass = CopyRightClass(copyrightCode, copyrightNotice)
        self.assertEquals(cpClass.errorStr, "")
        self.assertFalse(cpClass.isSpecial)
        self.assertTrue(cpClass.isValid)
        self.assertEquals(cpClass.copyrightNotice, "Commonwealth of Australia ...")
        #if not special, just get the copyright code
        codeNode = cpClass.getCopyrightCodeNode(xmlContent)
        self.assertEquals(str(codeNode), '<text:span text:style-name="copyright"> [135ZL]</text:span>')
        copyrightNotice = cpClass.getCopyrightNoticeNode(xmlContent)
        self.assertEquals(copyrightNotice, None)
        
        #VALID!
        copyrightCode = "135ZL"
        copyrightNotice = "WARNING ..."
        cpClass = CopyRightClass(copyrightCode, copyrightNotice)
        self.assertEquals(cpClass.errorStr, "")
        self.assertFalse(cpClass.isSpecial)
        self.assertTrue(cpClass.isValid)
        self.assertEquals(cpClass.copyrightNotice, "WARNING ...")
        #if not special, just get the copyright code
        codeNode = cpClass.getCopyrightCodeNode(xmlContent)
        self.assertEquals(str(codeNode), '<text:span text:style-name="copyright"> [135ZL]</text:span>')
        copyrightNotice = cpClass.getCopyrightNoticeNode(xmlContent)
        self.assertEquals(copyrightNotice, None)
        
        #VALID
        copyrightCode = "135ZL"
        copyrightNotice = "Some random notice"
        cpClass = CopyRightClass(copyrightCode, copyrightNotice)
        self.assertEquals(cpClass.errorStr, "")
        self.assertFalse(cpClass.isSpecial)
        self.assertTrue(cpClass.isValid)
        self.assertEquals(cpClass.copyrightNotice, "Some random notice")
        #if not special, just get the copyright code
        codeNode = cpClass.getCopyrightCodeNode(xmlContent)
        self.assertEquals(str(codeNode), '<text:span text:style-name="copyright"> [135ZL]</text:span>')
        copyrightNotice = cpClass.getCopyrightNoticeNode(xmlContent)
        self.assertEquals(copyrightNotice, None)
        
        copyrightCode = ""
        copyrightNotice = "Some random notice"
        cpClass = CopyRightClass(copyrightCode, copyrightNotice)
        self.assertEquals(cpClass.errorStr, "No copyright code but has copyright notice")
        self.assertFalse(cpClass.isSpecial)
        self.assertFalse(cpClass.isValid)
        self.assertEquals(cpClass.copyrightNotice, "Some random notice")
        
        copyrightCode = ""
        copyrightNotice = "Commonwealth of Australia ..."
        cpClass = CopyRightClass(copyrightCode, copyrightNotice)
        self.assertEquals(cpClass.errorStr, "No copyright code but has a standard copyright notice")
        self.assertFalse(cpClass.isSpecial)
        self.assertFalse(cpClass.isValid)
        self.assertEquals(cpClass.copyrightNotice, "Commonwealth of Australia ...")
        
        copyrightCode = ""
        copyrightNotice = ""
        cpClass = CopyRightClass(copyrightCode, copyrightNotice)
        self.assertEquals(cpClass.errorStr, "No copyright code and copyright notice")
        self.assertFalse(cpClass.isSpecial)
        self.assertFalse(cpClass.isValid)
        self.assertEquals(cpClass.copyrightNotice, "")
        
        xmlContent.close()
        
    def xtestAlt(self):
        xmlStr = """<?xml version="1.0" encoding="UTF-8"?><root/>"""
        xmlRoot = self.xml(xmlStr)
        
        #none type
        xmlContent = """<root><alternatives>
<alt><prod_ref>TPP7120</prod_ref><type>none</type><reason/></alt>
</alternatives></root>"""

        xml = self.xml(xmlContent)
        altNode = xml.getNode("//root/alternatives")
        altClass = AlternativeObject("WWW", altNode)
        self.assertEquals(altClass.altStr, 'This reading is not available online for this course')
        self.assertFalse(altClass.isDrProduct)
        self.assertFalse(altClass.isInAnotherPrinting)
        self.assertTrue(altClass.typeIsNone) #means none of the smrs is ticked
        altNode = altClass.getAltNode(xmlRoot)
        self.assertEquals(str(altNode), 
                '<text:p text:style-name="p"><text:span text:style-name="alternatives">This reading is not available online for this course</text:span></text:p>')
        xml.close()
        
        #none type
        xml = self.xml(xmlContent)
        altNode = xml.getNode("//root/alternatives")
        altClass = AlternativeObject("CDT", altNode)
        self.assertEquals(altClass.altStr, 'This reading is not available on the CD for this course')
        self.assertFalse(altClass.isDrProduct)
        self.assertFalse(altClass.isInAnotherPrinting)
        self.assertTrue(altClass.typeIsNone)
        altNode = altClass.getAltNode(xmlRoot)
        self.assertEquals(str(altNode),  
                '<text:p text:style-name="p"><text:span text:style-name="alternatives">This reading is not available on the CD for this course</text:span></text:p>')
        xml.close()
        
        #none type
        xml = self.xml(xmlContent)
        altNode = xml.getNode("//root/alternatives")
        altClass = AlternativeObject("SR", altNode)
        self.assertEquals(altClass.altStr, 'This reading is not available on the printed material for this course')
        self.assertFalse(altClass.isDrProduct)
        self.assertFalse(altClass.isInAnotherPrinting)
        self.assertTrue(altClass.typeIsNone)
        altNode = altClass.getAltNode(xmlRoot)
        self.assertEquals(str(altNode),  
                '<text:p text:style-name="p"><text:span text:style-name="alternatives">This reading is not available on the printed material for this course</text:span></text:p>')
        xml.close()
        
        #print type
        xmlContent = """<root><alternatives>
<alt><prod_ref>TPP7120</prod_ref><type>Print</type><reason/></alt>
</alternatives></root>"""
        xml = self.xml(xmlContent)
        altNode = xml.getNode("//root/alternatives")
        altClass = AlternativeObject("WWW", altNode)
        self.assertEquals(altClass.altStr, 'This reading is available on the printed material for this course')
        self.assertFalse(altClass.isDrProduct)
        self.assertFalse(altClass.isInAnotherPrinting)
        self.assertFalse(altClass.typeIsNone) #means at least one of the srms is ticked
        altNode = altClass.getAltNode(xmlRoot)
        self.assertEquals(str(altNode),  
                '<text:p text:style-name="p"><text:span text:style-name="alternatives">This reading is available on the printed material for this course</text:span></text:p>')
        xml.close()
        
        xml = self.xml(xmlContent)
        altNode = xml.getNode("//root/alternatives")
        altClass = AlternativeObject("CDT", altNode)
        self.assertEquals(altClass.altStr, 'This reading is available on the printed material for this course')
        self.assertFalse(altClass.isDrProduct)
        self.assertFalse(altClass.isInAnotherPrinting)
        self.assertFalse(altClass.typeIsNone)
        altNode = altClass.getAltNode(xmlRoot)
        self.assertEquals(str(altNode),  
                '<text:p text:style-name="p"><text:span text:style-name="alternatives">This reading is available on the printed material for this course</text:span></text:p>')
        xml.close()
        
        xml = self.xml(xmlContent)
        altNode = xml.getNode("//root/alternatives")
        altClass = AlternativeObject("SR", altNode)
        self.assertEquals(altClass.altStr, 'This reading is available on another printed material for this course')
        self.assertFalse(altClass.isDrProduct)
        self.assertTrue(altClass.isInAnotherPrinting)
        self.assertFalse(altClass.typeIsNone)
        altNode = altClass.getAltNode(xmlRoot)
        self.assertEquals(str(altNode),  
                '<text:p text:style-name="p"><text:span text:style-name="alternatives">This reading is available on another printed material for this course</text:span></text:p>')
        xml.close()
        
        #DR prodref ignore...
        xmlContent = """<root><alternatives>
<alt><prod_ref>TPP7120DR1</prod_ref><type>DR</type><reason/></alt>
</alternatives></root>"""
        xml = self.xml(xmlContent)
        altNode = xml.getNode("//root/alternatives")
        altClass = AlternativeObject("WWW", altNode)
        self.assertEquals(altClass.altStr, '')
        self.assertTrue(altClass.isDrProduct)
        self.assertFalse(altClass.isInAnotherPrinting)
        self.assertFalse(altClass.typeIsNone) #means at least one of the srms is ticked
        altNode = altClass.getAltNode(xmlRoot)
        self.assertEquals(altNode, None)
        xml.close()
        
        xml = self.xml(xmlContent)
        altNode = xml.getNode("//root/alternatives")
        altClass = AlternativeObject("CDT", altNode)
        self.assertEquals(altClass.altStr, '')
        self.assertTrue(altClass.isDrProduct)
        self.assertFalse(altClass.isInAnotherPrinting)
        self.assertFalse(altClass.typeIsNone) #means at least one of the srms is ticked
        altNode = altClass.getAltNode(xmlRoot)
        self.assertEquals(altNode, None)
        xml.close()
        
        xml = self.xml(xmlContent)
        altNode = xml.getNode("//root/alternatives")
        altClass = AlternativeObject("SR", altNode)
        self.assertEquals(altClass.altStr, '')
        self.assertTrue(altClass.isDrProduct)
        self.assertFalse(altClass.isInAnotherPrinting)
        self.assertFalse(altClass.typeIsNone) #means at least one of the srms is ticked
        altNode = altClass.getAltNode(xmlRoot)
        self.assertEquals(altNode, None)
        xml.close()
        
        #CD and Online for Print request
        xmlContent = """<root><alternatives>
<alt><prod_ref>TPP7120</prod_ref><type>Online</type><reason/></alt>
<alt><prod_ref>TPP7120</prod_ref><type>CD</type><reason/></alt>
</alternatives></root>"""
        xml = self.xml(xmlContent)
        altNode = xml.getNode("//root/alternatives")
        altClass = AlternativeObject("SR", altNode)
        self.assertEquals(altClass.altStr, 'This reading is available on the CD and online for this course')
        self.assertFalse(altClass.isDrProduct)
        self.assertFalse(altClass.isInAnotherPrinting)
        self.assertFalse(altClass.typeIsNone) #means at least one of the srms is ticked
        altNode = altClass.getAltNode(xmlRoot)
        self.assertEquals(str(altNode), 
                '<text:p text:style-name="p"><text:span text:style-name="alternatives">This reading is available on the CD and online for this course</text:span></text:p>')
        xml.close()
        
        #url
        altClass = AlternativeObject("WWW", hasUrl=True)
        self.assertEquals(altClass.altStr, "")
        altClass = AlternativeObject("CDT", hasUrl=True)
        self.assertEquals(altClass.altStr, "To access this reading you must be connected to the internet.")
        altNode = altClass.getAltNode(xmlRoot)
        self.assertEquals(str(altNode), 
                '<text:p text:style-name="p"><text:span text:style-name="alternatives">To access this reading you must be connected to the internet.</text:span></text:p>')
        
        altClass = AlternativeObject("SR", hasUrl=True)
        self.assertEquals(altClass.altStr, "Please access this reading via the DiReCt link on your USQStudyDesk.")
        altNode = altClass.getAltNode(xmlRoot)
        self.assertEquals(str(altNode), 
                '<text:p text:style-name="p"><text:span text:style-name="alternatives">Please access this reading via the DiReCt link on your USQStudyDesk.</text:span></text:p>')
        
        xmlRoot.close()
    
    def xtestCitation(self):
        xmlStr = """<?xml version="1.0" encoding="UTF-8"?><root/>"""
        xmlRoot = self.xml(xmlStr)
        
        xmlContent="""<root><citations>
<lecturer_preference>harvard</lecturer_preference>
<citation_type>online</citation_type>
<harvard>Bedford, T 2003, <i>Keeping a personal journal</i>, pp. 1-2.</harvard>
<apa>Bedford, T. (2003). <i>Keeping a personal journal</i> (pp 1-2).</apa>
</citations></root>"""

        xml = self.xml(xmlContent)
        citeObject = Citation(xml.getNode("//citations"))
        self.assertEquals(citeObject.lecturerPref, "harvard")
        self.assertEquals(citeObject.citationType, "online")
        self.assertEquals(citeObject.citation, "Bedford, T 2003, <i>Keeping a personal journal</i>, pp. 1-2.")
        citationNode = citeObject.getCitationNode(xmlRoot, self.iceContext)
        self.assertEquals(str(citationNode), 
                          '<text:p text:style-name="p">Bedford, T 2003, &lt;i&gt;Keeping a personal journal&lt;/i&gt;, pp. 1-2.</text:p>')
        xml.close()
        
        xmlRoot.close()
    
    def xtestFile(self):
        #test high res file
        xmlContent="""<root><file_list>
<file><name>Bedford_2003_1_hires.pdf</name>
      <export_url>http://testPath.com?file=Bedford_2003_1_hires.pdf&amp;user=</export_url>
      <size>135922</size>
</file></file_list></root>"""

        xml = self.xml(xmlContent)
        fileNodes = xml.getNodes("//file")
        for file in fileNodes:
            fileObject = FileObject(file, self.iceContext)
            self.assertEquals(fileObject.fileName, "Bedford_2003_1_hires.pdf")
            self.assertEquals(fileObject.exportUrl, "http://testPath.com?file=Bedford_2003_1_hires.pdf&user=")
            self.assertTrue(fileObject.isHighRes)
        xml.close()
        
        #test low res file
        xmlContent="""<root><file_list>
<file><name>Bedford_2003_1.pdf</name>
      <export_url>http://testPath.com?file=Bedford_2003_1.pdf&amp;user=</export_url>
      <size>135922</size>
</file></file_list></root>"""

        xml = self.xml(xmlContent)
        fileNodes = xml.getNodes("//file")
        for file in fileNodes:
            fileObject = FileObject(file, self.iceContext)
            self.assertEquals(fileObject.fileName, "Bedford_2003_1.pdf")
            self.assertEquals(fileObject.exportUrl, "http://testPath.com?file=Bedford_2003_1.pdf&user=")
            self.assertFalse(fileObject.isHighRes)
        xml.close()
        
        #testDownload file high res
        #IF NEED TO TEST on download, put the export pdf url in the export url variable
        xmlContent="""<root><file_list>
<file>
    <name>Dover_2002_559_hires.pdf</name>
    <export_url>
    %s
    </export_url>
    <size>465272</size>
    </file>
</file_list></root>""" 
        exportUrl = "XXX"
        xmlContent = "%s%s" % (xmlContent, exportUrl)
#        xml = self.xml(xmlContent)
#        fileNodes = xml.getNodes("//file")
#        for file in fileNodes:
#            fileObject = FileObject(file, self.iceContext)
#            
#            fileObject.downloadFile(test=True)
#            self.assertTrue(fileObject.isDownloadSuccess)
#            self.assertTrue(fileObject.isValidPdf)    
#        xml.close()


        #test the pdf (encrypted) ---Later
        
        
    def xtestReadingItemWWW(self):
        xmlStr = """<?xml version="1.0" encoding="UTF-8"?><root/>"""
        xmlRoot = self.xml(xmlStr)
        
        #CASE:
            #RWP --> will have copyright notice but no copyright code
            #LOW RES FILE
            #NO URL
        xmlStr="""<root>
<reading available="1" status="live">
    <reading_number>1.1</reading_number>
    <permalink>http://www.permalink.com</permalink>
    <citations>
        <lecturer_preference>harvard</lecturer_preference>
        <citation_type>online</citation_type>
        <harvard>XXX, T 2003, &lt;i&gt;Keeping a personal journal&lt;/i&gt;, pp. 1-2.</harvard>
        <apa>XXX, T. (2003). &lt;i&gt;Keeping a personal journal&lt;/i&gt; (pp 1-2).</apa>
    </citations>
    <copyright_notice>WARNING: reproduced wiht permission from author....</copyright_notice>
    <copyright_code>RWP</copyright_code>
    <file_list>
        <file><name>Bedford_2003_1.pdf</name>
        <export_url>http://xxx.php?uuid=xxx&amp;version=1&amp;file=Bedford_2003_1.pdf&amp;user=</export_url>
        <size>29489</size></file>
    </file_list>
</reading></root>"""
        
        xml = self.xml(xmlStr)
        readingNode = xml.getNode("/root/reading")
        readingObject = ReadingItem(readingNode, "WWW", self.iceContext)
        self.assertEquals(readingObject.status, "live")
        self.assertEquals(readingObject.available, "1")
        self.assertEquals(readingObject.readingNumber, "1.1")
        self.assertEquals(readingObject.moduleNumber, "1")
        self.assertEquals(readingObject.permalink, "http://www.permalink.com")
        
        #check for copyright object
        copyrightObject = readingObject.copyright
        copyrightNode = copyrightObject.getCopyrightCodeNode(xmlRoot)
        self.assertEqual(copyrightNode, None)
        self.assertEqual(copyrightObject.isValid, True)
        self.assertEqual(copyrightObject.errorStr, "")
        self.assertEqual(copyrightObject.isSpecial, True)
        
        #check for alternative
        altObject = readingObject.alternative
        self.assertEqual(altObject, None)
        
        #check for FileObject
        file = readingObject.fileList[0]
        self.assertFalse(file.isHighRes)    #low res
        self.assertEquals(file.fileName, "Bedford_2003_1.pdf")
        self.assertEquals(file.exportUrl, "http://xxx.php?uuid=xxx&version=1&file=Bedford_2003_1.pdf&user=")
        
#        toc = readingObject.toc.replace(REPLACE_NS, "")
#        self.assertEqual(toc, 
#            '<root><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" text:style-name="h2"><text:a xlink:href="http://www.permalink.com" office:target-frame-name="_blank" xlink:show="new">Reading 1.1</text:a></text:p><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="p">XXX, T 2003, <text:span text:style-name="i-i">Keeping a personal journal</text:span>, pp. 1-2.</text:p><text:span xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="alternatives">WARNING: reproduced wiht permission from author....</text:span></root>')
        xml.close()
        
        
        #CASE:
            #RWP --> will have copyright notice and no copyright code
            #HAVE alternative == none
        xmlStr="""<root>
<reading available="1" status="live">
    <reading_number>1.1</reading_number>
    <permalink>http://www.permalink.com</permalink>
    <citations>
        <lecturer_preference>harvard</lecturer_preference>
        <citation_type>online</citation_type>
        <harvard>XXX, T 2003, &lt;i&gt;Keeping a personal journal&lt;/i&gt;, pp. 1-2.</harvard>
        <apa>XXX, T. (2003). &lt;i&gt;Keeping a personal journal&lt;/i&gt; (pp 1-2).</apa>
    </citations>
    <copyright_notice>WARNING: reproduced wiht permission from author....</copyright_notice>
    <copyright_code>RWP</copyright_code>
    <alternatives>
        <alt><prod_ref>TPP7120</prod_ref><type>none</type><reason/></alt>
    </alternatives>
</reading></root>"""
        
        xml = self.xml(xmlStr)
        readingNode = xml.getNode("/root/reading")
        readingObject = ReadingItem(readingNode, "WWW", self.iceContext)
        self.assertEquals(readingObject.status, "live")
        self.assertEquals(readingObject.available, "1")
        self.assertEquals(readingObject.readingNumber, "1.1")
        self.assertEquals(readingObject.moduleNumber, "1")
        self.assertEquals(readingObject.permalink, "http://www.permalink.com")
        
        #check for copyright object
        copyrightObject = readingObject.copyright
        copyrightNode = copyrightObject.getCopyrightCodeNode(xmlRoot)
        self.assertEqual(copyrightNode, None)
        self.assertEqual(copyrightObject.isValid, True)
        self.assertEqual(copyrightObject.errorStr, "")
        self.assertEqual(copyrightObject.isSpecial, True)
        
#        #check for alternative
        altObject = readingObject.alternative
        self.assertTrue(altObject != None)
        self.assertEqual(altObject.altStr, "This reading is not available online for this course")
        
        #check for FileObject
        self.assertTrue(readingObject.fileList == [])
        
#        toc = readingObject.toc.replace(REPLACE_NS, "")
#        self.assertEqual(toc, 
#            '<root><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" text:style-name="h2"><text:a xlink:href="http://www.permalink.com" office:target-frame-name="_blank" xlink:show="new">Reading 1.1</text:a></text:p><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="p">XXX, T 2003, <text:span text:style-name="i-i">Keeping a personal journal</text:span>, pp. 1-2.</text:p><text:span xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="alternatives">WARNING: reproduced wiht permission from author....</text:span><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="p"><text:span text:style-name="alternatives">This reading is not available online for this course</text:span></text:p></root>')
        xml.close()
        
    
    #CASE:
            #135ZL --> Even it's low res file, put copyright code
            #LOW RES FILE
            #NO URL
        xmlStr="""<root>
<reading available="1" status="live">
    <reading_number>1.1</reading_number>
    <permalink>http://www.permalink.com</permalink>
    <citations>
        <lecturer_preference>harvard</lecturer_preference>
        <citation_type>online</citation_type>
        <harvard>XXX, T 2003, &lt;i&gt;Keeping a personal journal&lt;/i&gt;, pp. 1-2.</harvard>
        <apa>XXX, T. (2003). &lt;i&gt;Keeping a personal journal&lt;/i&gt; (pp 1-2).</apa>
    </citations>
    <copyright_notice>WARNING: Standarcd copyright notice....</copyright_notice>
    <copyright_code>135ZL</copyright_code>
    <file_list>
        <file><name>Bedford_2003_1.pdf</name>
        <export_url>http://xxx.php?uuid=xxx&amp;version=1&amp;file=Bedford_2003_1.pdf&amp;user=</export_url>
        <size>29489</size></file>
    </file_list>
</reading></root>"""
        
        xml = self.xml(xmlStr)
        readingNode = xml.getNode("/root/reading")
        readingObject = ReadingItem(readingNode, "WWW", self.iceContext)
        self.assertEquals(readingObject.status, "live")
        self.assertEquals(readingObject.available, "1")
        self.assertEquals(readingObject.readingNumber, "1.1")
        self.assertEquals(readingObject.moduleNumber, "1")
        self.assertEquals(readingObject.permalink, "http://www.permalink.com")
        
        #check for copyright object
        copyrightObject = readingObject.copyright
        copyrightNode = copyrightObject.getCopyrightCodeNode(xmlRoot)
        self.assertEqual(str(copyrightNode),
                '<text:span text:style-name="copyright"> [135ZL]</text:span>')
        self.assertEqual(copyrightObject.isValid, True)
        self.assertEqual(copyrightObject.errorStr, "")
        self.assertEqual(copyrightObject.isSpecial, False)
        
        #check for alternative
        altObject = readingObject.alternative
        self.assertEqual(altObject, None)
        
        #check for FileObject
        file = readingObject.fileList[0]
        self.assertFalse(file.isHighRes)    #low res
        self.assertEquals(file.fileName, "Bedford_2003_1.pdf")
        self.assertEquals(file.exportUrl, "http://xxx.php?uuid=xxx&version=1&file=Bedford_2003_1.pdf&user=")
        
#        toc = readingObject.toc.replace(REPLACE_NS, "")
#        self.assertEqual(toc, 
#            '<root><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" text:style-name="h2"><text:a xlink:href="http://www.permalink.com" office:target-frame-name="_blank" xlink:show="new">Reading 1.1</text:a><text:s xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:c="4"/><text:span xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="copyright"> [135ZL]</text:span></text:p><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="p">XXX, T 2003, <text:span text:style-name="i-i">Keeping a personal journal</text:span>, pp. 1-2.</text:p></root>')
        xml.close()
        
    #CASE:
            #135ZL --> no file, do not put copy right code....
            #Alternative = CD
            #NO URL
        xmlStr="""<root>
<reading available="1" status="live">
    <reading_number>1.1</reading_number>
    <permalink>http://www.permalink.com</permalink>
    <citations>
        <lecturer_preference>harvard</lecturer_preference>
        <citation_type>online</citation_type>
        <harvard>XXX, T 2003, &lt;i&gt;Keeping a personal journal&lt;/i&gt;, pp. 1-2.</harvard>
        <apa>XXX, T. (2003). &lt;i&gt;Keeping a personal journal&lt;/i&gt; (pp 1-2).</apa>
    </citations>
    <copyright_notice>WARNING: Standarcd copyright notice....</copyright_notice>
    <copyright_code>135ZL</copyright_code>
    <alternatives>
        <alt><prod_ref>TPP7120</prod_ref><type>CD</type><reason/></alt>
    </alternatives>
</reading></root>"""
        
        xml = self.xml(xmlStr)
        readingNode = xml.getNode("/root/reading")
        readingObject = ReadingItem(readingNode, "WWW", self.iceContext)
        self.assertEquals(readingObject.status, "live")
        self.assertEquals(readingObject.available, "1")
        self.assertEquals(readingObject.readingNumber, "1.1")
        self.assertEquals(readingObject.moduleNumber, "1")
        self.assertEquals(readingObject.permalink, "http://www.permalink.com")
        
        #check for copyright object
        copyrightObject = readingObject.copyright
        copyrightNode = copyrightObject.getCopyrightCodeNode(xmlRoot)
        self.assertEqual(str(copyrightNode),
                '<text:span text:style-name="copyright"> [135ZL]</text:span>')
        self.assertEqual(copyrightObject.isValid, True)
        self.assertEqual(copyrightObject.errorStr, "")
        self.assertEqual(copyrightObject.isSpecial, False)
        
        #check for alternative
        altObject = readingObject.alternative
        self.assertTrue(altObject != None)
        self.assertEqual(altObject.altStr, "This reading is available on the CD for this course")
        
        #check for FileObject
        self.assertTrue(readingObject.fileList == [])
        
#        toc = readingObject.toc.replace(REPLACE_NS, "")
#        self.assertEqual(toc, 
#            '<root><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" text:style-name="h2"><text:a xlink:href="http://www.permalink.com" office:target-frame-name="_blank" xlink:show="new">Reading 1.1</text:a></text:p><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="p">XXX, T 2003, <text:span text:style-name="i-i">Keeping a personal journal</text:span>, pp. 1-2.</text:p><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="p"><text:span text:style-name="alternatives">This reading is available on the CD for this course</text:span></text:p></root>')
        xml.close()
        
        xmlRoot.close()
        
    def xtestReadingItemCDT(self):
        xmlStr = """<?xml version="1.0" encoding="UTF-8"?><root/>"""
        xmlRoot = self.xml(xmlStr)
        #NEED TO TEST ON HIRES FILE....
        #NEED TO TEST IF CITATION type == Print and URL DOES NOT HAVE ezproxy, put URL
        #IF CITATION type == online, ignore the url tag totally
        #CASE:
            #RWP --> will have copyright notice but no copyright code
            #LOW RES FILE --> will not have pdf icon
            #NO URL
        xmlStr="""<root>
<reading available="1" status="live">
    <reading_number>1.1</reading_number>
    <permalink>http://www.permalink.com</permalink>
    <citations>
        <lecturer_preference>harvard</lecturer_preference>
        <citation_type>online</citation_type>
        <harvard>XXX, T 2003, &lt;i&gt;Keeping a personal journal&lt;/i&gt;, pp. 1-2.</harvard>
        <apa>XXX, T. (2003). &lt;i&gt;Keeping a personal journal&lt;/i&gt; (pp 1-2).</apa>
    </citations>
    <copyright_notice>WARNING: reproduced wiht permission from author....</copyright_notice>
    <copyright_code>RWP</copyright_code>
    <file_list>
        <file><name>Bedford_2003_1.pdf</name>
        <export_url>http://xxx.php?uuid=xxx&amp;version=1&amp;file=Bedford_2003_1.pdf&amp;user=</export_url>
        <size>29489</size></file>
    </file_list>
</reading></root>"""
        
        xml = self.xml(xmlStr)
        readingNode = xml.getNode("/root/reading")
        readingObject = ReadingItem(readingNode, "CDT", self.iceContext)
        self.assertEquals(readingObject.status, "live")
        self.assertEquals(readingObject.available, "1")
        self.assertEquals(readingObject.readingNumber, "1.1")
        self.assertEquals(readingObject.moduleNumber, "1")
        self.assertEquals(readingObject.permalink, "http://www.permalink.com")
        
        #check for copyright object
        copyrightObject = readingObject.copyright
        copyrightNode = copyrightObject.getCopyrightCodeNode(xmlRoot)
        self.assertEqual(copyrightNode, None)
        self.assertEqual(copyrightObject.isValid, True)
        self.assertEqual(copyrightObject.errorStr, "")
        self.assertEqual(copyrightObject.isSpecial, True)
        
        #check for alternative
        altObject = readingObject.alternative
        self.assertEqual(altObject, None)
        
        #check for FileObject
        file = readingObject.fileList[0]
        self.assertFalse(file.isHighRes)    #low res
        self.assertEquals(file.fileName, "Bedford_2003_1.pdf")
        self.assertEquals(file.exportUrl, "http://xxx.php?uuid=xxx&version=1&file=Bedford_2003_1.pdf&user=")
        
        
#        toc = readingObject.toc.replace(REPLACE_NS, "")
#        self.assertEqual(toc, 
#            '<root><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="h2">Reading 1.1</text:p><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="p">XXX, T 2003, <text:span text:style-name="i-i">Keeping a personal journal</text:span>, pp. 1-2.</text:p><text:span xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="alternatives">WARNING: reproduced wiht permission from author....</text:span></root>')
        xml.close()
        
        
        #CASE:
            #RWP --> will have copyright notice but no copyright code
            #HIGH RES FILE --> will have pdf icon
            #NO URL
        xmlStr="""<root>
<reading available="1" status="live">
    <reading_number>1.1</reading_number>
    <permalink>http://www.permalink.com</permalink>
    <citations>
        <lecturer_preference>harvard</lecturer_preference>
        <citation_type>online</citation_type>
        <harvard>XXX, T 2003, &lt;i&gt;Keeping a personal journal&lt;/i&gt;, pp. 1-2.</harvard>
        <apa>XXX, T. (2003). &lt;i&gt;Keeping a personal journal&lt;/i&gt; (pp 1-2).</apa>
    </citations>
    <copyright_notice>WARNING: reproduced wiht permission from author....</copyright_notice>
    <copyright_code>RWP</copyright_code>
    <file_list>
        <file><name>Bedford_2003_1_hires.pdf</name>
        <export_url>http://xxx.php?uuid=xxx&amp;version=1&amp;file=Bedford_2003_1.pdf&amp;user=</export_url>
        <size>29489</size></file>
    </file_list>
</reading></root>"""
        
        xml = self.xml(xmlStr)
        readingNode = xml.getNode("/root/reading")
        readingObject = ReadingItem(readingNode, "CDT", self.iceContext)
        self.assertEquals(readingObject.status, "live")
        self.assertEquals(readingObject.available, "1")
        self.assertEquals(readingObject.readingNumber, "1.1")
        self.assertEquals(readingObject.moduleNumber, "1")
        self.assertEquals(readingObject.permalink, "http://www.permalink.com")
        
        #check for copyright object
        copyrightObject = readingObject.copyright
        copyrightNode = copyrightObject.getCopyrightCodeNode(xmlRoot)
        self.assertEqual(copyrightNode, None)
        self.assertEqual(copyrightObject.isValid, True)
        self.assertEqual(copyrightObject.errorStr, "")
        self.assertEqual(copyrightObject.isSpecial, True)
        
        #check for alternative
        altObject = readingObject.alternative
        self.assertEqual(altObject, None)
        
        #check for FileObject
        file = readingObject.fileList[0]
        self.assertTrue(file.isHighRes)    #high res
        self.assertEquals(file.fileName, "Bedford_2003_1_hires.pdf")
        self.assertEquals(file.exportUrl, "http://xxx.php?uuid=xxx&version=1&file=Bedford_2003_1.pdf&user=")
        
#        toc = readingObject.toc.replace(REPLACE_NS, "")
#        self.assertEqual(toc, 
#            '<root><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0" text:style-name="h2">Reading 1.1<text:s text:c="1"/><draw:a xlink:type="simple" xlink:href="../media/readings/Bedford_2003_1_hires.pdf"><draw:frame draw:style-name="fr1" draw:name="../media/readings/Bedford_2003_1_hires.pdf" text:anchor-type="as-char" svg:width="0.741cm" svg:height="0.82cm" draw:z-index="0"><draw:image xlink:href="Pictures/pdf.gif" xlink:type="simple" xlink:show="embed" xlink:actuate="onLoad"/></draw:frame></draw:a></text:p><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="p">XXX, T 2003, <text:span text:style-name="i-i">Keeping a personal journal</text:span>, pp. 1-2.</text:p><text:span xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="alternatives">WARNING: reproduced wiht permission from author....</text:span></root>')
        xml.close()
        
        
        #CASE:
            #RWP --> will have copyright notice and no copyright code
            #HAVE alternative == none
            #HAVE url --> not ezproxy
            #citation type == Online -->ignore url
        xmlStr="""<root>
<reading available="1" status="live">
    <reading_number>1.1</reading_number>
    <permalink>http://www.permalink.com</permalink>
    <citations>
        <lecturer_preference>harvard</lecturer_preference>
        <citation_type>online</citation_type>
        <harvard>XXX, T 2003, &lt;i&gt;Keeping a personal journal&lt;/i&gt;, pp. 1-2.http://randomUrl.com</harvard>
        <apa>XXX, T. (2003). &lt;i&gt;Keeping a personal journal&lt;/i&gt; (pp 1-2).http://randomUrl.com</apa>
    </citations>
    <url>http://randomUrl.com</url>
    <copyright_notice>WARNING: reproduced wiht permission from author....</copyright_notice>
    <copyright_code>RWP</copyright_code>
    <alternatives>
        <alt><prod_ref>TPP7120</prod_ref><type>none</type><reason/></alt>
    </alternatives>
</reading></root>"""
        
        xml = self.xml(xmlStr)
        readingNode = xml.getNode("/root/reading")
        readingObject = ReadingItem(readingNode, "CDT", self.iceContext)
        self.assertEquals(readingObject.status, "live")
        self.assertEquals(readingObject.available, "1")
        self.assertEquals(readingObject.readingNumber, "1.1")
        self.assertEquals(readingObject.moduleNumber, "1")
        self.assertEquals(readingObject.permalink, "http://www.permalink.com")
        
        #check for copyright object
        copyrightObject = readingObject.copyright
        copyrightNode = copyrightObject.getCopyrightCodeNode(xmlRoot)
        self.assertEqual(copyrightNode, None)
        self.assertEqual(copyrightObject.isValid, True)
        self.assertEqual(copyrightObject.errorStr, "")
        self.assertEqual(copyrightObject.isSpecial, True)
        
#        #check for alternative
        altObject = readingObject.alternative
        self.assertTrue(altObject != None)
        self.assertEqual(altObject.altStr, "This reading is not available on the CD for this course")
        
        #check for FileObject
        self.assertTrue(readingObject.fileList == [])
        
#        toc = readingObject.toc.replace(REPLACE_NS, "")
#        self.assertEqual(toc, 
#            '<root><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" text:style-name="h2"><text:a xlink:href="http://www.permalink.com" office:target-frame-name="_blank" xlink:show="new">Reading 1.1</text:a></text:p><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="p">XXX, T 2003, <text:span text:style-name="i-i">Keeping a personal journal</text:span>, pp. 1-2.http://randomUrl.com</text:p><text:span xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="alternatives">WARNING: reproduced wiht permission from author....</text:span><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="p"><text:span text:style-name="alternatives">This reading is not available on the CD for this course</text:span></text:p></root>')
        xml.close()
        
    #CASE:
            #RWP --> will have copyright notice and no copyright code
            #HAVE alternative == none
            #HAVE url --> not ezproxy
            #citation type == Print --> set url
        xmlStr="""<root>
<reading available="1" status="live">
    <reading_number>1.1</reading_number>
    <permalink>http://www.permalink.com</permalink>
    <citations>
        <lecturer_preference>harvard</lecturer_preference>
        <citation_type>Print</citation_type>
        <harvard>XXX, T 2003, &lt;i&gt;Keeping a personal journal&lt;/i&gt;, pp. 1-2.</harvard>
        <apa>XXX, T. (2003). &lt;i&gt;Keeping a personal journal&lt;/i&gt; (pp 1-2).</apa>
    </citations>
    <url>http://randomUrl.com</url>
    <copyright_notice>WARNING: reproduced wiht permission from author....</copyright_notice>
    <copyright_code>RWP</copyright_code>
    <alternatives>
        <alt><prod_ref>TPP7120</prod_ref><type>none</type><reason/></alt>
    </alternatives>
</reading></root>"""
        
        xml = self.xml(xmlStr)
        readingNode = xml.getNode("/root/reading")
        readingObject = ReadingItem(readingNode, "CDT", self.iceContext)
        self.assertEquals(readingObject.status, "live")
        self.assertEquals(readingObject.available, "1")
        self.assertEquals(readingObject.readingNumber, "1.1")
        self.assertEquals(readingObject.moduleNumber, "1")
        self.assertEquals(readingObject.permalink, "http://www.permalink.com")
        
        #check for copyright object
        copyrightObject = readingObject.copyright
        copyrightNode = copyrightObject.getCopyrightCodeNode(xmlRoot)
        self.assertEqual(copyrightNode, None)
        self.assertEqual(copyrightObject.isValid, True)
        self.assertEqual(copyrightObject.errorStr, "")
        self.assertEqual(copyrightObject.isSpecial, True)
        
#        #check for alternative
        altObject = readingObject.alternative
        self.assertTrue(altObject != None)
        self.assertEqual(altObject.altStr, "This reading is not available on the CD for this course")
        
        #check for FileObject
        self.assertTrue(readingObject.fileList == [])
        
#        toc = readingObject.toc.replace(REPLACE_NS, "")
#        self.assertEqual(toc,
#            '<root><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" text:style-name="h2"><text:a xlink:href="http://www.permalink.com" office:target-frame-name="_blank" xlink:show="new">Reading 1.1</text:a></text:p><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="p">XXX, T 2003, <text:span text:style-name="i-i">Keeping a personal journal</text:span>, pp. 1-2.</text:p><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="p">http://randomUrl.com</text:p><text:span xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="alternatives">WARNING: reproduced wiht permission from author....</text:span><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="p"><text:span text:style-name="alternatives">This reading is not available on the CD for this course</text:span></text:p></root>')
        xml.close()
        
    #CASE:
            #135ZL --> Low res file, DO NOT PUT CODE and pdf icon
            #LOW RES FILE
            #NO URL
        xmlStr="""<root>
<reading available="1" status="live">
    <reading_number>1.1</reading_number>
    <permalink>http://www.permalink.com</permalink>
    <citations>
        <lecturer_preference>harvard</lecturer_preference>
        <citation_type>online</citation_type>
        <harvard>XXX, T 2003, &lt;i&gt;Keeping a personal journal&lt;/i&gt;, pp. 1-2.</harvard>
        <apa>XXX, T. (2003). &lt;i&gt;Keeping a personal journal&lt;/i&gt; (pp 1-2).</apa>
    </citations>
    <copyright_notice>WARNING: Standarcd copyright notice....</copyright_notice>
    <copyright_code>135ZL</copyright_code>
    <file_list>
        <file><name>Bedford_2003_1.pdf</name>
        <export_url>http://xxx.php?uuid=xxx&amp;version=1&amp;file=Bedford_2003_1.pdf&amp;user=</export_url>
        <size>29489</size></file>
    </file_list>
</reading></root>"""
        
        xml = self.xml(xmlStr)
        readingNode = xml.getNode("/root/reading")
        readingObject = ReadingItem(readingNode, "CDT", self.iceContext)
        self.assertEquals(readingObject.status, "live")
        self.assertEquals(readingObject.available, "1")
        self.assertEquals(readingObject.readingNumber, "1.1")
        self.assertEquals(readingObject.moduleNumber, "1")
        self.assertEquals(readingObject.permalink, "http://www.permalink.com")
        
        #check for copyright object
        copyrightObject = readingObject.copyright
        copyrightNode = copyrightObject.getCopyrightCodeNode(xmlRoot)
        self.assertEqual(str(copyrightNode),  
                '<text:span text:style-name="copyright"> [135ZL]</text:span>')
        self.assertEqual(copyrightObject.isValid, True)
        self.assertEqual(copyrightObject.errorStr, "")
        self.assertEqual(copyrightObject.isSpecial, False)
        
        #check for alternative
        altObject = readingObject.alternative
        self.assertEqual(altObject, None)
        
        #check for FileObject
        file = readingObject.fileList[0]
        self.assertFalse(file.isHighRes)    #low res
        self.assertEquals(file.fileName, "Bedford_2003_1.pdf")
        self.assertEquals(file.exportUrl, "http://xxx.php?uuid=xxx&version=1&file=Bedford_2003_1.pdf&user=")
        
        
#        toc = readingObject.toc.replace(REPLACE_NS, "")
#        self.assertEqual(toc,
#            '<root><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="h2">Reading 1.1</text:p><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="p">XXX, T 2003, <text:span text:style-name="i-i">Keeping a personal journal</text:span>, pp. 1-2.</text:p></root>')
        xml.close()
        
        #CASE:
            #135ZL --> put code and pdf icon
            #HIGH RES FILE
            #URL with ezproxy + citationtype = print --> ignore url
        xmlStr="""<root>
<reading available="1" status="live">
    <reading_number>1.1</reading_number>
    <permalink>http://www.permalink.com</permalink>
    <citations>
        <lecturer_preference>harvard</lecturer_preference>
        <citation_type>print</citation_type>
        <harvard>XXX, T 2003, &lt;i&gt;Keeping a personal journal&lt;/i&gt;, pp. 1-2.</harvard>
        <apa>XXX, T. (2003). &lt;i&gt;Keeping a personal journal&lt;/i&gt; (pp 1-2).</apa>
    </citations>
    <url>http://ezproxy.com</url>
    <copyright_notice>WARNING: Standarcd copyright notice....</copyright_notice>
    <copyright_code>135ZL</copyright_code>
    <file_list>
        <file><name>Bedford_2003_1_hires.pdf</name>
        <export_url>http://xxx.php?uuid=xxx&amp;version=1&amp;file=Bedford_2003_1.pdf&amp;user=</export_url>
        <size>29489</size></file>
    </file_list>
</reading></root>"""
        
        xml = self.xml(xmlStr)
        readingNode = xml.getNode("/root/reading")
        readingObject = ReadingItem(readingNode, "CDT", self.iceContext)
        self.assertEquals(readingObject.status, "live")
        self.assertEquals(readingObject.available, "1")
        self.assertEquals(readingObject.readingNumber, "1.1")
        self.assertEquals(readingObject.moduleNumber, "1")
        self.assertEquals(readingObject.permalink, "http://www.permalink.com")
        
        #check for copyright object
        copyrightObject = readingObject.copyright
        copyrightNode = copyrightObject.getCopyrightCodeNode(xmlRoot)
        self.assertEqual(str(copyrightNode), 
                '<text:span text:style-name="copyright"> [135ZL]</text:span>')
        self.assertEqual(copyrightObject.isValid, True)
        self.assertEqual(copyrightObject.errorStr, "")
        self.assertEqual(copyrightObject.isSpecial, False)
        
        #check for alternative
        altObject = readingObject.alternative
        self.assertEqual(altObject, None)
        
        #check for FileObject
        file = readingObject.fileList[0]
        self.assertTrue(file.isHighRes)    #high res
        self.assertEquals(file.fileName, "Bedford_2003_1_hires.pdf")
        self.assertEquals(file.exportUrl, "http://xxx.php?uuid=xxx&version=1&file=Bedford_2003_1.pdf&user=")
        
        
#        toc = readingObject.toc.replace(REPLACE_NS, "")
#        self.assertEqual(toc,
#            '<root><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0" text:style-name="h2">Reading 1.1<text:s text:c="1"/><draw:a xlink:type="simple" xlink:href="../media/readings/Bedford_2003_1_hires.pdf"><draw:frame draw:style-name="fr1" draw:name="../media/readings/Bedford_2003_1_hires.pdf" text:anchor-type="as-char" svg:width="0.741cm" svg:height="0.82cm" draw:z-index="0"><draw:image xlink:href="Pictures/pdf.gif" xlink:type="simple" xlink:show="embed" xlink:actuate="onLoad"/></draw:frame></draw:a><text:s xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:c="4"/><text:span xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="copyright"> [135ZL]</text:span></text:p><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="p">XXX, T 2003, <text:span text:style-name="i-i">Keeping a personal journal</text:span>, pp. 1-2.</text:p></root>')
        xml.close()
        
    #CASE:
            #135ZL --> no file, do not put copy right code and pdf icon
            #Alternative = Print
            #hav random url + citationtype = print --> put url   --> will have permalink
        xmlStr="""<root>
<reading available="1" status="live">
    <reading_number>1.1</reading_number>
    <permalink>http://www.permalink.com</permalink>
    <citations>
        <lecturer_preference>harvard</lecturer_preference>
        <citation_type>print</citation_type>
        <harvard>XXX, T 2003, &lt;i&gt;Keeping a personal journal&lt;/i&gt;, pp. 1-2.</harvard>
        <apa>XXX, T. (2003). &lt;i&gt;Keeping a personal journal&lt;/i&gt; (pp 1-2).</apa>
    </citations>
    <url>http://randomurl.com</url>
    <copyright_notice>WARNING: Standarcd copyright notice....</copyright_notice>
    <copyright_code>135ZL</copyright_code>
    <alternatives>
        <alt><prod_ref>TPP7120</prod_ref><type>Print</type><reason/></alt>
    </alternatives>
</reading></root>"""
        
        xml = self.xml(xmlStr)
        readingNode = xml.getNode("/root/reading")
        readingObject = ReadingItem(readingNode, "CDT", self.iceContext)
        self.assertEquals(readingObject.status, "live")
        self.assertEquals(readingObject.available, "1")
        self.assertEquals(readingObject.readingNumber, "1.1")
        self.assertEquals(readingObject.moduleNumber, "1")
        self.assertEquals(readingObject.permalink, "http://www.permalink.com")
        
        #check for copyright object
        copyrightObject = readingObject.copyright
        copyrightNode = copyrightObject.getCopyrightCodeNode(xmlRoot)
        self.assertEqual(str(copyrightNode), 
                '<text:span text:style-name="copyright"> [135ZL]</text:span>')
        self.assertEqual(copyrightObject.isValid, True)
        self.assertEqual(copyrightObject.errorStr, "")
        self.assertEqual(copyrightObject.isSpecial, False)
        
        #check for alternative
        altObject = readingObject.alternative
        self.assertTrue(altObject != None)
        self.assertEqual(altObject.altStr, "This reading is available on the printed material for this course")
        
        #check for FileObject
        self.assertTrue(readingObject.fileList == [])
        
#        toc = readingObject.toc.replace(REPLACE_NS, "")
#        self.assertEqual(toc,
#            '<root><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" text:style-name="h2"><text:a xlink:href="http://www.permalink.com" office:target-frame-name="_blank" xlink:show="new">Reading 1.1</text:a></text:p><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="p">XXX, T 2003, <text:span text:style-name="i-i">Keeping a personal journal</text:span>, pp. 1-2.</text:p><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="p">http://randomurl.com</text:p><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="p"><text:span text:style-name="alternatives">This reading is available on the printed material for this course</text:span></text:p></root>')
        xml.close()
        xmlRoot.close()
    
    def testReadingItemCDTBOOK(self):
        xmlStr = """<?xml version="1.0" encoding="UTF-8"?><root/>"""
        xmlRoot = self.xml(xmlStr)
        #NEED TO TEST ON HIRES FILE....
        #NEED TO TEST IF CITATION type == Print and URL DOES NOT HAVE ezproxy, put URL
        #IF CITATION type == online, ignore the url tag totally
        #CASE:
            #RWP --> will have copyright notice but no copyright code
            #LOW RES FILE --> always without pdf icon
            #NO URL
        xmlStr="""<root>
<reading available="1" status="live">
    <reading_number>1.1</reading_number>
    <permalink>http://www.permalink.com</permalink>
    <citations>
        <lecturer_preference>harvard</lecturer_preference>
        <citation_type>online</citation_type>
        <harvard>XXX, T 2003, &lt;i&gt;Keeping a personal journal&lt;/i&gt;, pp. 1-2.</harvard>
        <apa>XXX, T. (2003). &lt;i&gt;Keeping a personal journal&lt;/i&gt; (pp 1-2).</apa>
    </citations>
    <copyright_notice>WARNING: reproduced wiht permission from author....</copyright_notice>
    <copyright_code>RWP</copyright_code>
    <file_list>
        <file><name>Bedford_2003_1.pdf</name>
        <export_url>http://xxx.php?uuid=xxx&amp;version=1&amp;file=Bedford_2003_1.pdf&amp;user=</export_url>
        <size>29489</size></file>
    </file_list>
</reading></root>"""
        
        xml = self.xml(xmlStr)
        readingNode = xml.getNode("/root/reading")
        readingObject = ReadingItem(readingNode, "CDT", self.iceContext, printVersion=True)
        self.assertEquals(readingObject.status, "live")
        self.assertEquals(readingObject.available, "1")
        self.assertEquals(readingObject.readingNumber, "1.1")
        self.assertEquals(readingObject.moduleNumber, "1")
        self.assertEquals(readingObject.permalink, "http://www.permalink.com")
        
        #check for copyright object
        copyrightObject = readingObject.copyright
        copyrightNode = copyrightObject.getCopyrightCodeNode(xmlRoot)
        self.assertEqual(copyrightNode, None)
        self.assertEqual(copyrightObject.isValid, True)
        self.assertEqual(copyrightObject.errorStr, "")
        self.assertEqual(copyrightObject.isSpecial, True)
        
        #check for alternative
        altObject = readingObject.alternative
        self.assertEqual(altObject, None)
        
        #check for FileObject
        file = readingObject.fileList[0]
        self.assertFalse(file.isHighRes)    #low res
        self.assertEquals(file.fileName, "Bedford_2003_1.pdf")
        self.assertEquals(file.exportUrl, "http://xxx.php?uuid=xxx&version=1&file=Bedford_2003_1.pdf&user=")
        
        
#        toc = readingObject.toc.replace(REPLACE_NS, "")
#        self.assertEqual(toc, 
#            '<root><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="h2">Reading 1.1</text:p><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="p">XXX, T 2003, <text:span text:style-name="i-i">Keeping a personal journal</text:span>, pp. 1-2.</text:p><text:span xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="alternatives">WARNING: reproduced wiht permission from author....</text:span></root>')
        xml.close()
        
        #CASE:
            #RWP --> will have copyright notice but no copyright code
            #HIGH RES FILE --> will not have PDF ICON
            #NO URL
        xmlStr="""<root>
<reading available="1" status="live">
    <reading_number>1.1</reading_number>
    <permalink>http://www.permalink.com</permalink>
    <citations>
        <lecturer_preference>harvard</lecturer_preference>
        <citation_type>online</citation_type>
        <harvard>XXX, T 2003, &lt;i&gt;Keeping a personal journal&lt;/i&gt;, pp. 1-2.</harvard>
        <apa>XXX, T. (2003). &lt;i&gt;Keeping a personal journal&lt;/i&gt; (pp 1-2).</apa>
    </citations>
    <copyright_notice>WARNING: reproduced wiht permission from author....</copyright_notice>
    <copyright_code>RWP</copyright_code>
    <file_list>
        <file><name>Bedford_2003_1_hires.pdf</name>
        <export_url>http://xxx.php?uuid=xxx&amp;version=1&amp;file=Bedford_2003_1.pdf&amp;user=</export_url>
        <size>29489</size></file>
    </file_list>
</reading></root>"""
        
        xml = self.xml(xmlStr)
        readingNode = xml.getNode("/root/reading")
        readingObject = ReadingItem(readingNode, "CDT", self.iceContext, printVersion=True)
        self.assertEquals(readingObject.status, "live")
        self.assertEquals(readingObject.available, "1")
        self.assertEquals(readingObject.readingNumber, "1.1")
        self.assertEquals(readingObject.moduleNumber, "1")
        self.assertEquals(readingObject.permalink, "http://www.permalink.com")
        
        #check for copyright object
        copyrightObject = readingObject.copyright
        copyrightNode = copyrightObject.getCopyrightCodeNode(xmlRoot)
        self.assertEqual(copyrightNode, None)
        self.assertEqual(copyrightObject.isValid, True)
        self.assertEqual(copyrightObject.errorStr, "")
        self.assertEqual(copyrightObject.isSpecial, True)
        
        #check for alternative
        altObject = readingObject.alternative
        self.assertEqual(altObject, None)
        
        #check for FileObject
        file = readingObject.fileList[0]
        self.assertTrue(file.isHighRes)    #high res
        self.assertEquals(file.fileName, "Bedford_2003_1_hires.pdf")
        self.assertEquals(file.exportUrl, "http://xxx.php?uuid=xxx&version=1&file=Bedford_2003_1.pdf&user=")
        
#        toc = readingObject.toc.replace(REPLACE_NS, "")
#        self.assertEqual(toc, 
#            '<root><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="h2">Reading 1.1</text:p><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="p">XXX, T 2003, <text:span text:style-name="i-i">Keeping a personal journal</text:span>, pp. 1-2.</text:p><text:span xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="alternatives">WARNING: reproduced wiht permission from author....</text:span></root>')
        xml.close()
        
        
        #CASE:
            #RWP --> will have copyright notice and no copyright code
            #HAVE alternative == none
            #HAVE url --> not ezproxy
            #citation type == Online -->ignore url
            #Will have permalink ;)
        xmlStr="""<root>
<reading available="1" status="live">
    <reading_number>1.1</reading_number>
    <permalink>http://www.permalink.com</permalink>
    <citations>
        <lecturer_preference>harvard</lecturer_preference>
        <citation_type>online</citation_type>
        <harvard>XXX, T 2003, &lt;i&gt;Keeping a personal journal&lt;/i&gt;, pp. 1-2.http://randomUrl.com</harvard>
        <apa>XXX, T. (2003). &lt;i&gt;Keeping a personal journal&lt;/i&gt; (pp 1-2).http://randomUrl.com</apa>
    </citations>
    <url>http://randomUrl.com</url>
    <copyright_notice>WARNING: reproduced wiht permission from author....</copyright_notice>
    <copyright_code>RWP</copyright_code>
    <alternatives>
        <alt><prod_ref>TPP7120</prod_ref><type>none</type><reason/></alt>
    </alternatives>
</reading></root>"""
        
        xml = self.xml(xmlStr)
        readingNode = xml.getNode("/root/reading")
        readingObject = ReadingItem(readingNode, "CDT", self.iceContext, printVersion=True)
        self.assertEquals(readingObject.status, "live")
        self.assertEquals(readingObject.available, "1")
        self.assertEquals(readingObject.readingNumber, "1.1")
        self.assertEquals(readingObject.moduleNumber, "1")
        self.assertEquals(readingObject.permalink, "http://www.permalink.com")
        
        #check for copyright object
        copyrightObject = readingObject.copyright
        copyrightNode = copyrightObject.getCopyrightCodeNode(xmlRoot)
        self.assertEqual(copyrightNode, None)
        self.assertEqual(copyrightObject.isValid, True)
        self.assertEqual(copyrightObject.errorStr, "")
        self.assertEqual(copyrightObject.isSpecial, True)
        
#        #check for alternative
        altObject = readingObject.alternative
        self.assertTrue(altObject != None)
        self.assertEqual(altObject.altStr, "This reading is not available on the CD for this course")
        
        #check for FileObject
        self.assertTrue(readingObject.fileList == [])
        
#        toc = readingObject.toc.replace(REPLACE_NS, "")
#        self.assertEqual(toc, 
#            '<root><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" text:style-name="h2"><text:a xlink:href="http://www.permalink.com" office:target-frame-name="_blank" xlink:show="new">Reading 1.1</text:a></text:p><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="p">XXX, T 2003, <text:span text:style-name="i-i">Keeping a personal journal</text:span>, pp. 1-2.http://randomUrl.com</text:p><text:span xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="alternatives">WARNING: reproduced wiht permission from author....</text:span><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="p"><text:span text:style-name="alternatives">This reading is not available on the CD for this course</text:span></text:p></root>')
        xml.close()
        
    #CASE:
            #RWP --> will have copyright notice and no copyright code
            #HAVE alternative == none
            #HAVE url --> not ezproxy
            #citation type == Print --> set url
            #will have permalink ;)
        xmlStr="""<root>
<reading available="1" status="live">
    <reading_number>1.1</reading_number>
    <permalink>http://www.permalink.com</permalink>
    <citations>
        <lecturer_preference>harvard</lecturer_preference>
        <citation_type>Print</citation_type>
        <harvard>XXX, T 2003, &lt;i&gt;Keeping a personal journal&lt;/i&gt;, pp. 1-2.</harvard>
        <apa>XXX, T. (2003). &lt;i&gt;Keeping a personal journal&lt;/i&gt; (pp 1-2).</apa>
    </citations>
    <url>http://randomUrl.com</url>
    <copyright_notice>WARNING: reproduced wiht permission from author....</copyright_notice>
    <copyright_code>RWP</copyright_code>
    <alternatives>
        <alt><prod_ref>TPP7120</prod_ref><type>none</type><reason/></alt>
    </alternatives>
</reading></root>"""
        
        xml = self.xml(xmlStr)
        readingNode = xml.getNode("/root/reading")
        readingObject = ReadingItem(readingNode, "CDT", self.iceContext)
        self.assertEquals(readingObject.status, "live")
        self.assertEquals(readingObject.available, "1")
        self.assertEquals(readingObject.readingNumber, "1.1")
        self.assertEquals(readingObject.moduleNumber, "1")
        self.assertEquals(readingObject.permalink, "http://www.permalink.com")
        
        #check for copyright object
        copyrightObject = readingObject.copyright
        copyrightNode = copyrightObject.getCopyrightCodeNode(xmlRoot)
        self.assertEqual(copyrightNode, None)
        self.assertEqual(copyrightObject.isValid, True)
        self.assertEqual(copyrightObject.errorStr, "")
        self.assertEqual(copyrightObject.isSpecial, True)
        
#        #check for alternative
        altObject = readingObject.alternative
        self.assertTrue(altObject != None)
        self.assertEqual(altObject.altStr, "This reading is not available on the CD for this course")
        
        #check for FileObject
        self.assertTrue(readingObject.fileList == [])
        
#        toc = readingObject.toc.replace(REPLACE_NS, "")
#        self.assertEqual(toc,
#            '<root><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" text:style-name="h2"><text:a xlink:href="http://www.permalink.com" office:target-frame-name="_blank" xlink:show="new">Reading 1.1</text:a></text:p><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="p">XXX, T 2003, <text:span text:style-name="i-i">Keeping a personal journal</text:span>, pp. 1-2.</text:p><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="p">http://randomUrl.com</text:p><text:span xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="alternatives">WARNING: reproduced wiht permission from author....</text:span><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="p"><text:span text:style-name="alternatives">This reading is not available on the CD for this course</text:span></text:p></root>')
        xml.close()
        
    #CASE:
            #135ZL --> Low res file, DO NOT PUT CODE and always without pdf icon
            #LOW RES FILE
            #NO URL
        xmlStr="""<root>
<reading available="1" status="live">
    <reading_number>1.1</reading_number>
    <permalink>http://www.permalink.com</permalink>
    <citations>
        <lecturer_preference>harvard</lecturer_preference>
        <citation_type>online</citation_type>
        <harvard>XXX, T 2003, &lt;i&gt;Keeping a personal journal&lt;/i&gt;, pp. 1-2.</harvard>
        <apa>XXX, T. (2003). &lt;i&gt;Keeping a personal journal&lt;/i&gt; (pp 1-2).</apa>
    </citations>
    <copyright_notice>WARNING: Standarcd copyright notice....</copyright_notice>
    <copyright_code>135ZL</copyright_code>
    <file_list>
        <file><name>Bedford_2003_1.pdf</name>
        <export_url>http://xxx.php?uuid=xxx&amp;version=1&amp;file=Bedford_2003_1.pdf&amp;user=</export_url>
        <size>29489</size></file>
    </file_list>
</reading></root>"""
        
        xml = self.xml(xmlStr)
        readingNode = xml.getNode("/root/reading")
        readingObject = ReadingItem(readingNode, "CDT", self.iceContext)
        self.assertEquals(readingObject.status, "live")
        self.assertEquals(readingObject.available, "1")
        self.assertEquals(readingObject.readingNumber, "1.1")
        self.assertEquals(readingObject.moduleNumber, "1")
        self.assertEquals(readingObject.permalink, "http://www.permalink.com")
        
        #check for copyright object
        copyrightObject = readingObject.copyright
        copyrightNode = copyrightObject.getCopyrightCodeNode(xmlRoot)
        self.assertEqual(str(copyrightNode),
                '<text:span text:style-name="copyright"> [135ZL]</text:span>')
        self.assertEqual(copyrightObject.isValid, True)
        self.assertEqual(copyrightObject.errorStr, "")
        self.assertEqual(copyrightObject.isSpecial, False)
        
        #check for alternative
        altObject = readingObject.alternative
        self.assertEqual(altObject, None)
        
        #check for FileObject
        file = readingObject.fileList[0]
        self.assertFalse(file.isHighRes)    #low res
        self.assertEquals(file.fileName, "Bedford_2003_1.pdf")
        self.assertEquals(file.exportUrl, "http://xxx.php?uuid=xxx&version=1&file=Bedford_2003_1.pdf&user=")
        
        
#        toc = readingObject.toc.replace(REPLACE_NS, "")
#        self.assertEqual(toc,
#            '<root><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="h2">Reading 1.1</text:p><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="p">XXX, T 2003, <text:span text:style-name="i-i">Keeping a personal journal</text:span>, pp. 1-2.</text:p></root>')
        xml.close()
        
        #CASE:
            #135ZL --> put code and always no pdf icon
            #HIGH RES FILE
            #URL with ezproxy + citationtype = print --> ignore url
        xmlStr="""<root>
<reading available="1" status="live">
    <reading_number>1.1</reading_number>
    <permalink>http://www.permalink.com</permalink>
    <citations>
        <lecturer_preference>harvard</lecturer_preference>
        <citation_type>print</citation_type>
        <harvard>XXX, T 2003, &lt;i&gt;Keeping a personal journal&lt;/i&gt;, pp. 1-2.</harvard>
        <apa>XXX, T. (2003). &lt;i&gt;Keeping a personal journal&lt;/i&gt; (pp 1-2).</apa>
    </citations>
    <url>http://ezproxy.com</url>
    <copyright_notice>WARNING: Standarcd copyright notice....</copyright_notice>
    <copyright_code>135ZL</copyright_code>
    <file_list>
        <file><name>Bedford_2003_1_hires.pdf</name>
        <export_url>http://xxx.php?uuid=xxx&amp;version=1&amp;file=Bedford_2003_1.pdf&amp;user=</export_url>
        <size>29489</size></file>
    </file_list>
</reading></root>"""
        
        xml = self.xml(xmlStr)
        readingNode = xml.getNode("/root/reading")
        readingObject = ReadingItem(readingNode, "CDT", self.iceContext)
        self.assertEquals(readingObject.status, "live")
        self.assertEquals(readingObject.available, "1")
        self.assertEquals(readingObject.readingNumber, "1.1")
        self.assertEquals(readingObject.moduleNumber, "1")
        self.assertEquals(readingObject.permalink, "http://www.permalink.com")
        
        #check for copyright object
        copyrightObject = readingObject.copyright
        copyrightNode = copyrightObject.getCopyrightCodeNode(xmlRoot)
        self.assertEqual(str(copyrightNode),
                '<text:span text:style-name="copyright"> [135ZL]</text:span>')
        self.assertEqual(copyrightObject.isValid, True)
        self.assertEqual(copyrightObject.errorStr, "")
        self.assertEqual(copyrightObject.isSpecial, False)
        
        #check for alternative
        altObject = readingObject.alternative
        self.assertEqual(altObject, None)
        
        #check for FileObject
        file = readingObject.fileList[0]
        self.assertTrue(file.isHighRes)    #high res
        self.assertEquals(file.fileName, "Bedford_2003_1_hires.pdf")
        self.assertEquals(file.exportUrl, "http://xxx.php?uuid=xxx&version=1&file=Bedford_2003_1.pdf&user=")
        
        
#        toc = readingObject.toc.replace(REPLACE_NS, "")
#        self.assertEqual(toc,
#            '<root><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0" text:style-name="h2">Reading 1.1<text:s text:c="1"/><draw:a xlink:type="simple" xlink:href="../media/readings/Bedford_2003_1_hires.pdf"><draw:frame draw:style-name="fr1" draw:name="../media/readings/Bedford_2003_1_hires.pdf" text:anchor-type="as-char" svg:width="0.741cm" svg:height="0.82cm" draw:z-index="0"><draw:image xlink:href="Pictures/pdf.gif" xlink:type="simple" xlink:show="embed" xlink:actuate="onLoad"/></draw:frame></draw:a><text:s xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:c="4"/><text:span xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="copyright"> [135ZL]</text:span></text:p><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="p">XXX, T 2003, <text:span text:style-name="i-i">Keeping a personal journal</text:span>, pp. 1-2.</text:p></root>')
        xml.close()
        
    #CASE:
            #135ZL --> no file, do not put copy right code and always no pdf icon
            #Alternative = Print
            #hav random url + citationtype = print --> put url   --> will have permalink
        xmlStr="""<root>
<reading available="1" status="live">
    <reading_number>1.1</reading_number>
    <permalink>http://www.permalink.com</permalink>
    <citations>
        <lecturer_preference>harvard</lecturer_preference>
        <citation_type>print</citation_type>
        <harvard>XXX, T 2003, &lt;i&gt;Keeping a personal journal&lt;/i&gt;, pp. 1-2.</harvard>
        <apa>XXX, T. (2003). &lt;i&gt;Keeping a personal journal&lt;/i&gt; (pp 1-2).</apa>
    </citations>
    <url>http://randomurl.com</url>
    <copyright_notice>WARNING: Standarcd copyright notice....</copyright_notice>
    <copyright_code>135ZL</copyright_code>
    <alternatives>
        <alt><prod_ref>TPP7120</prod_ref><type>Print</type><reason/></alt>
    </alternatives>
</reading></root>"""
        
        xml = self.xml(xmlStr)
        readingNode = xml.getNode("/root/reading")
        readingObject = ReadingItem(readingNode, "CDT", self.iceContext)
        self.assertEquals(readingObject.status, "live")
        self.assertEquals(readingObject.available, "1")
        self.assertEquals(readingObject.readingNumber, "1.1")
        self.assertEquals(readingObject.moduleNumber, "1")
        self.assertEquals(readingObject.permalink, "http://www.permalink.com")
        
        #check for copyright object
        copyrightObject = readingObject.copyright
        copyrightNode = copyrightObject.getCopyrightCodeNode(xmlRoot)
        self.assertEqual(str(copyrightNode), 
                '<text:span text:style-name="copyright"> [135ZL]</text:span>')
        self.assertEqual(copyrightObject.isValid, True)
        self.assertEqual(copyrightObject.errorStr, "")
        self.assertEqual(copyrightObject.isSpecial, False)
        
        #check for alternative
        altObject = readingObject.alternative
        self.assertTrue(altObject != None)
        self.assertEqual(altObject.altStr, "This reading is available on the printed material for this course")
        
        #check for FileObject
        self.assertTrue(readingObject.fileList == [])
        
#        toc = readingObject.toc.replace(REPLACE_NS, "")
#        self.assertEqual(toc,
#            '<root><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" text:style-name="h2"><text:a xlink:href="http://www.permalink.com" office:target-frame-name="_blank" xlink:show="new">Reading 1.1</text:a></text:p><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="p">XXX, T 2003, <text:span text:style-name="i-i">Keeping a personal journal</text:span>, pp. 1-2.</text:p><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="p">http://randomurl.com</text:p><text:p xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" text:style-name="p"><text:span text:style-name="alternatives">This reading is available on the printed material for this course</text:span></text:p></root>')
        xml.close()
        
        xmlRoot.close()
    

if __name__ == "__main__":
    IceCommon.runUnitTests(locals())

