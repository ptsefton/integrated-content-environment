#!/usr/bin/env python
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

try:
    from ice_common import IceCommon
    IceCommon.setup()
except:
    import sys, os
    sys.path.append(os.getcwd())
    sys.path.append(".")
    os.chdir("../../")
    from ice_common import IceCommon
# XmlTestCase        # self.assertSameXml

from urllib import quote

testDataDir = "plugins/render/testData/"
testData = "%sont_test_document" % testDataDir

docNS = {"ve": "http://schemas.openxmlformats.org/markup-compatibility/2006", 
         "o" : "urn:schemas-microsoft-com:office:office",
         "r" : "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
         "m" : "http://schemas.openxmlformats.org/officeDocument/2006/math",
         "v" : "urn:schemas-microsoft-com:vml",
         "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing", 
         "w10" : "urn:schemas-microsoft-com:office:word",
         "w" : "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
         "wne" : "http://schemas.microsoft.com/office/word/2006/wordml"
         } 

class DocXtest(IceCommon.TestCase):
    def setUp(self):
        self.iceContext = IceCommon.IceContext
        pass
    
    def tearDown(self):
        pass
    
    def testInit(self):
        pass
    
    def __processRelationship(self, relationshipsXml, customXmlList):
        relationshipsNode = relationshipsXml.getRootNode()
        relationshipNodes = relationshipsNode.getChildren()
        lastRelationshipId = 1
        if relationshipNodes:
            for relationshipNode in relationshipNodes:
                Id = relationshipNode.getAttribute("Id")
                idNumber = int(Id[3:])
                if lastRelationshipId < idNumber:
                    lastRelationshipId = idNumber
        
        for textValue, attr in customXmlList:
            lastRelationshipIdStr = "rId%s" % lastRelationshipId
            url = ""
            if attr.has_key("url"):
                url = attr["url"]
            textValue = quote(textValue)
            targetStr = "http://ontologize.me/meta/?r=%s&o=%s" % (textValue, url)
            
            newRelationshipNode = relationshipsXml.createElement("Relationship")
            newRelationshipNode.setAttribute("Id", lastRelationshipIdStr)
            newRelationshipNode.setAttribute("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink")
            newRelationshipNode.setAttribute("Target", targetStr)
            newRelationshipNode.setAttribute("TargetMode", "External")
        
            relationshipsNode.addChild(newRelationshipNode)
            lastRelationshipId+=1
            
        return relationshipsXml
    
    
    def xtestRelationshipFile(self):
        relationships = "%s/word/_rels/_document.xml.rels" % testData   #for hyperlink
        
        customXmlList = [("syndrome", {"url": "http://purl.org/obo/owl/DOID#DOID_225"}),
                         ("another syndrome", {"url": "http://purl.org/obo/owl/DOID#DOID_226"})]
    
        relationshipsXml = self.iceContext.Xml(relationships)
        
        relationshipsXml = self.__processRelationship(relationshipsXml, customXmlList)
        
        expected = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink" Target="http://ontologize.me/meta/?r=syndrome&amp;o=http://purl.org/obo/owl/DOID#DOID_225" TargetMode="External"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink" Target="http://ontologize.me/meta/?r=another%20syndrome&amp;o=http://purl.org/obo/owl/DOID#DOID_226" TargetMode="External"/></Relationships>"""
        #self.assertEquals(str(relationshipsXml), expected)
        relationshipsXml.close()
    
    def __getLastRelationshipId(self, relationshipDocument):
        relationshipXml = self.iceContext.Xml(relationshipDocument)
        relationships = relationshipXml.getRootNode()
        lastRelationshipId = 1
        
        for relationshipNode in relationships.getChildren():
            Id = relationshipNode.getAttribute("Id")
            idNumber = int(Id[3:])
            if lastRelationshipId < idNumber:
                lastRelationshipId = idNumber
                
        relationshipXml.close()
        return lastRelationshipId
        
    
    def testConvertOntology(self):
        documentName = "%s/ont_test_document.docx" % testDataDir
        
        documentTempDir = self.iceContext.fs.unzipToTempDirectory(documentName)
        document = self.iceContext.fs.join (documentTempDir.absPath(), "word/document.xml")
        relationships = self.iceContext.fs.join (documentTempDir.absPath(), "word/_rels/document.xml.rels")
#        document = "%s/word/document.xml" % testData
#        relationships = "%s/word/_rels/document.xml.rels" % testData   #for hyperlink
        customXmlList = {}
        try:
            lastRelationshipId = self.__getLastRelationshipId(relationships)
            
            #Getting customXml information
            documentXml = self.iceContext.Xml(document, docNS.items())
            customXmls = documentXml.getNodes("//w:customXml")
            for customXml in customXmls:
                lastRelationshipIdStr = "rId%s" % lastRelationshipId
                attrList = {}
                
                customXmlPrAttributes = customXml.getNodes("./*[local-name()='customXmlPr']/*[local-name()='attr']")
                for attr in customXmlPrAttributes:
                    name = attr.getAttribute("name").strip()
                    val = attr.getAttribute("val").strip()
                    attrList[name] = val
                url = ""
                anchor = ""
                if attrList.has_key("url"):
                    url = attrList["url"]
                    anchor = self.__getAnchor(url)
                
                text = self.__getTextContent(customXml)
                
                #replacing smart tag with new hyperlink tag
                smartTag = customXml.getNode("./*[local-name()='smartTag']")
                rsidRPr = ""
                if smartTag:
                    #get old rsidRPRr id from the w:r in smarttag
                    wr = smartTag.getNode("./*[local-name()='r']")
                    if wr:
                        rsidRPr = wr.getAttribute("rsidRPr")
                else:
                    smartTag = customXml.getNode("./*[local-name()='r']")
                    if smartTag:
                        rsidRPr = smartTag.getAttribute("rsidRPr")
                
                #new hyperlink Tag
                hyperlinkNode = documentXml.createElement("w:hyperlink")
                hyperlinkNode.setAttribute("r:id", lastRelationshipIdStr)
                hyperlinkNode.setAttribute("w:anchor", anchor)
                hyperlinkNode.setAttribute("w:history", "1")
                
                #new w:r node
                newWrNode = documentXml.createElement("w:r")
                newWrNode.setAttribute("w:rsidRPr", rsidRPr)
                hyperlinkNode.addChild(newWrNode)
                
                #new w:rPr hyperlink Node
                newWPrNode = documentXml.createElement("w:rPr")
                newWrNode.addChild(newWPrNode)
                
                #new w:rStyle node
                newRStyleNode = documentXml.createElement("w:rStyle")
                newRStyleNode.setAttribute("w:val", "Hyperlink")
                newWPrNode.addChild(newRStyleNode)
                
                #new w:t node (can we just copy the old node??)
                newWTNode = documentXml.createElement("w:t")
                newWTNode.setContent(text)
                newWrNode.addChild(newWTNode)
                
                if smartTag: 
                    smartTag.replace(hyperlinkNode)    
                customXmlList[lastRelationshipIdStr] = (text, attrList)
                
                lastRelationshipId+=1
            documentXml.saveFile()
            
            #relationship
            relationshipXml = self.iceContext.Xml(relationships)
            relationshipsNode = relationshipXml.getRootNode()
            for key in customXmlList:
                textValue, attr = customXmlList[key]
                url = ""
                if attr.has_key("url"):
                    url = attr["url"]
                textValue = quote(textValue)
                targetStr = "http://ontologize.me/meta/?r=%s&o=%s" % (textValue, url)
                
                newRelationshipNode = relationshipXml.createElement("Relationship")
                newRelationshipNode.setAttribute("Id", key)
                newRelationshipNode.setAttribute("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink")
                newRelationshipNode.setAttribute("Target", targetStr)
                newRelationshipNode.setAttribute("TargetMode", "External")
            
                relationshipsNode.addChild(newRelationshipNode)
            relationshipXml.saveFile()
            relationshipXml.close()
            
            documentXml.close()
            
            documentTempDir.zip(self.iceContext.fs.absPath(documentName))
            documentTempDir.delete()
            
        except Exception, e:
            raise e
            
    def testplainOntoXml(self):
        testContent = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:ve="http://schemas.openxmlformats.org/markup-compatibility/2006" 
            xmlns:o="urn:schemas-microsoft-com:office:office" 
            xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" 
            xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" 
            xmlns:v="urn:schemas-microsoft-com:vml" 
            xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" 
            xmlns:w10="urn:schemas-microsoft-com:office:word" 
            xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" 
            xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml">
<w:body>
    <w:customXml w:uri="http://biolit.ucsd.edu/biolitschema" w:element="biolit-term">
        <w:customXmlPr>
            <w:attr w:name="id" w:val="DOID:225"/>
            <w:attr w:name="type" w:val="Human disease"/>
            <w:attr w:name="status" w:val="true"/>
            <w:attr w:name="OntName" w:val="Human disease"/>
            <w:attr w:name="url" w:val=" http://purl.org/obo/owl/DOID#DOID_225"/>
        </w:customXmlPr>
        <w:smartTag w:uri="BioLitTags" w:element="tag1">
            <w:r w:rsidRPr="00AE6E4A">
                <w:rPr>
                <w:highlight w:val="yellow"/>
                </w:rPr>
                <w:t>syndrome</w:t>
            </w:r>
        </w:smartTag>
    </w:customXml>
</w:body></w:document>
"""

        documentXml = self.iceContext.Xml(testContent, docNS.items())
        customXmls = documentXml.getNodes("//w:customXml")
        
        fakeId = "rId%s"
        count =1
        attrList = {}
        for customXml in customXmls:
            fakeIdStr = fakeId % count
            
            customXmlPrAttributes = customXml.getNodes("./*[local-name()='customXmlPr']/*[local-name()='attr']")
            for attr in customXmlPrAttributes:
                name = attr.getAttribute("name").strip()
                val = attr.getAttribute("val").strip()
                attrList[name] = val
            url = ""
            anchor = ""
            if attrList.has_key("url"):
                url = attrList["url"]
                anchor = self.__getAnchor(url)
            
            text = self.__getTextContent(customXml)
            
            #replacing smart tag with new hyperlink tag
            smartTag = customXml.getNode("./*[local-name()='smartTag']")
            #get old rsidRPRr id from the w:r in smarttag
            wr = smartTag.getNode("./*[local-name()='r']")
            rsidRPr = ""
            if wr:
                rsidRPr = wr.getAttribute("rsidRPr")
            
            #new hyperlink Tag
            hyperlinkNode = documentXml.createElement("w:hyperlink")
            hyperlinkNode.setAttribute("r:id", fakeIdStr)
            hyperlinkNode.setAttribute("w:anchor", anchor)
            hyperlinkNode.setAttribute("w:history", "1")
            
            #new w:r node
            newWrNode = documentXml.createElement("w:r")
            newWrNode.setAttribute("w:rsidRPr", rsidRPr)
            hyperlinkNode.addChild(newWrNode)
            
            #new w:rPr hyperlink Node
            newWPrNode = documentXml.createElement("w:rPr")
            newWrNode.addChild(newWPrNode)
            
            #new w:rStyle node
            newRStyleNode = documentXml.createElement("w:rStyle")
            newRStyleNode.setAttribute("w:val", "Hyperlink")
            newWPrNode.addChild(newRStyleNode)
            
            #new w:t node (can we just copy the old node??)
            newWTNode = documentXml.createElement("w:t")
            newWTNode.setContent(text)
            newWrNode.addChild(newWTNode)
            
            expected="""<w:hyperlink r:id="rId1" w:anchor="DOID_225" w:history="1">
                            <w:r w:rsidRPr="00AE6E4A">
                                <w:rPr>
                                    <w:rStyle w:val="Hyperlink"/>
                                </w:rPr>
                                <w:t>syndrome</w:t>
                            </w:r>
                        </w:hyperlink>"""

            smartTag.replace(hyperlinkNode)
        
            
        documentXml.close()

    def __getAnchor(self, url):
        anchor = ""
        anchorLocation = url.find("#")
        if anchorLocation!=-1:
            anchor = url[anchorLocation+1:]
        return anchor
        
    def __getTextContent(self, customXml):
        textValue = ""
        text = customXml.getNode("./*[local-name()='r']/*[local-name()='t']")
        if text:
            textValue = text.getContent()
        else:
            text = customXml.getNode("./*[local-name()='smartTag']/*[local-name()='r']/*[local-name()='t']")
            if text:
                textValue = text.getContent()
                
        return textValue.strip()

if __name__ == "__main__":
    IceCommon.runUnitTests(locals())






