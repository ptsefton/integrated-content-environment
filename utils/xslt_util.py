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

import libxml2
import libxslt


class xslt:
    def __init__(self, xslFile):
        styledoc = libxml2.parseFile(xslFile)
        self.style = libxslt.parseStylesheetDoc(styledoc)

    def transformToDom(self, xml):
        """ xml = a xmlFilename, an XML DOM, or an XML string
            outputFile (optional) file to write the transformed output to.
        """
        # test to see if the xml arg is a filename(str) or xml string or
        #   otherwise assume that it is an XMLDOM object
        if type(xml)==type(""):
            if xml.startswith("<"):
                doc = libxml2.parseMemory(xml, len(xml))
            else:        
                doc = libxml2.parseFile(xml)
        else:
            doc = xml
        resultDom = self.style.applyStylesheet(doc, None)
        if type(xml)==type(""):
            try:
                doc.freeDoc()
            except:
                pass
        return resultDom
        
        
    def transform(self, xml, outputFile=None):
        """ xml = a xmlFilename, an XML DOM, or an XML string
            outputFile (optional) file to write the transformed output to.
        """
        resultDom = self.transformToDom(xml)
        
        #resultStr = resultDom.serialize()
        resultStr = resultDom.getRootElement().serialize()
        #resultStr = resultStr.replace('xmlns=""','')
        try:
            resultDom.freeDoc()
        except:
            pass        
        if outputFile!=None:
            f = open(outputFile, "w")
            f.write(resultStr)
            f.close()
        return resultStr
    
    def close(self):
        try:
            self.style.freeStylesheet()
        except:
            pass
        self.style = None

    def __del__(self):
        if self.style!=None:
            self.close()


        
