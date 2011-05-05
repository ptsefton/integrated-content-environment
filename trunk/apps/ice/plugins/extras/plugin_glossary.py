
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

pluginName = "ice.extra.glossary"
pluginDesc = "Glossary"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method

from cPickle import loads, dumps
import re

def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = None
    pluginClass = Glossary
    pluginInitialized = True
    return pluginFunc


class Glossary(object):
    
    def __init__(self, iceContext, item=None):
        self.iceContext = iceContext
        if item is None:
            self.__terms = dict()
        else:
            self.__loadTerms(item)
    
    @property
    def terms(self):
        return self.__terms
    
    def __loadTerms(self, item):
        self.__terms = dict()
        try:
            packageItem = item.packageRootItem
            glossaryItems = packageItem.getMeta("glossary-items")
            if glossaryItems is not None:
                items = set(loads(glossaryItems))
                for it in items:
                    print " * loading glossary terms from '%s'" % it
                    glossaryItem = item.getIceItem(it)
                    glossaryTerms = glossaryItem.getMeta("glossary-terms")
                    if glossaryTerms is not None:
                        self.__terms.update(loads(glossaryTerms))
        except Exception, e:
            print " * failed to load glossary terms: %s" % str(e)
        return self.__terms
    
    def addScript(self, convertedData):
        xml = self.iceContext.Xml(convertedData.getRendition(".xhtml.body"))
        JQUERY_JS = "package-root/skin/jquery.js"
        GLOSSARY_JS = "package-root/skin/glossary.js"
        bodyNode = xml.getRootNode()
        scriptNode = bodyNode.getNode("/*[local-name()='script' and @src='%s']" % GLOSSARY_JS)
        if bodyNode is not None and scriptNode is None:
            jqueryNode = xml.createElement("script", type="text/javascript", src=JQUERY_JS)
            jqueryNode.addChild(xml.createComment(" "))
            bodyNode.addChild(jqueryNode)
            glossaryNode = xml.createElement("script", id="ice_glossary_script", type="text/javascript", src=GLOSSARY_JS )
            glossaryNode.addChild(xml.createComment(" "))
            bodyNode.addChild(glossaryNode)
        convertedData.addRenditionData(".xhtml.body", str(xml))
        xml.close()
        return convertedData
    
    def extractTerms(self, item, convertedData):
        #getting glossary term from the documents
        itemTerms = dict()
        # extract terms from html tables - assumes div as root
        html = self.iceContext.Xml(convertedData.getRendition(".xhtml.body"))
        tables = html.getNodes("//*[local-name()='table']/*[local-name()='tbody']")
        for table in tables:
            rows = table.getNodes(".//*[local-name()='tr']")
            for row in rows:
                cols = row.getNodes(".//*[local-name()='td']")
                if len(cols) >= 2:
                    term = cols[0].getContent()
                    term = term.strip()
                    # check that term is valid
                    if term is not None and term.strip() != "":
                        #nodes can be more than p
                        nodes = cols[1].getNodes("./*")
                        definition = ""
                        # adding more than one elements for defintion term 
                        for n in nodes:
                            n.removeAttribute("id") #remove id on the element
                            definition += n.serialize()
                        #itemTerms.update({term.lower() : definition})
                        itemTerms.update({term : definition})
                else:
                    print " * unknown glossary table layout (cols=%s)" % len(cols)
                    break;
        html.close()
        try:
            # save glossary terms for the item
            convertedData.addMeta("glossary-terms", dumps(itemTerms))
            # add to list of package glossaries
            packageItem = item.packageRootItem
            glossaryItems = packageItem.getMeta("glossary-items")
            if glossaryItems is not None:
                items = set(loads(glossaryItems))
                items.add(item.relPath)
                packageItem.setMeta("glossary-items", dumps(items))
                packageItem.close()
        except Exception, e:
            print " * failed to save glossary terms: %s" % str(e)
        return itemTerms
    
    def addTooltips(self, convertedData):
        
        template = "\\1<span class=\"glossary-term\">\\2<span class=\"glossary-mark\">*</span></span>\\3"
        template2 = "<div id=\"%s\" class=\"glossary-def\">%s</div>"
        if len(self.__terms) > 0:
            #terms = [t.lower() for t in self.__terms.keys()]
            terms = self.__terms.keys()
            regex = ""
            data = convertedData.getRendition(".xhtml.body")
            data = data.strip().rstrip("</div>")
            if not data.endswith(">"):
                data = data+ ">"
            for term in terms:
                regex = "([^\\w])(%s)([^\\w])" % term
                if re.search(term,data):
                    resultdata = re.sub(regex, template, data)
                    data = resultdata+ (template2 % (term,self.__terms.get(term)))
            data = data+"</div>"
            data = self.__cleanupData(data)
            
            convertedData.addRenditionData(".xhtml.body", data)
        else:
            print " * no glossary terms to substitute"
        return convertedData
    
    def __cleanupData(self,data):
        try:
            
            #dataStr = "<body>%s</body>" % data
            
            xml = self.iceContext.Xml(data)
            body = xml.getRootNode()
            nodes = body.getNodes("//sup/span[./span/@class='footnote-text' and ./span/span/@class='glossary-term']")
            if nodes != []:
                for node in nodes:
                    #if there is sup element then remove it. 
                    parentNode = node.getParent()
                    parentNode.replace(node)
            data = str(body)
            xml.close()
            if data.find("<?xml version=\"1.0\"?>")!= -1:
                #strip off xml version tag if exists:
                # to fix the parser error
                data = data.replace("<?xml version=\"1.0\"?>","")        
            return data
        except Exception,e:
            print "Error in Cleanup data - '%s'" % str(e)
    



