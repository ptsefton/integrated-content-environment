
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


class Oscar3(object):
    def __init__(self, iceContext, serverUri="http://localhost:8181"):
        self.iceContext = iceContext
        self.__serverUri = serverUri
        self.__http = iceContext.Http()
        self.__inlineAnnotatedSci = None
    
    
    def inlineAnnotate(self, sciXmlStr):
        uri = self.__serverUri + "/Process"
        formDataList = [
                        ("SciXML", sciXmlStr),
                        ("output", "markedup"),
                       ]
        self.__inlineAnnotatedSci = self.__http.post(uri, formDataList)
        return self.__inlineAnnotatedSci
    
    
    def process(self, inlineAnnotatedSci=None, xhtml=None):
        et = self.iceContext.ElementTree
        if inlineAnnotatedSci is None:
            inlineAnnotatedSci = self.__inlineAnnotatedSci
        x = et.XML(inlineAnnotatedSci)
        body = x.find(".//BODY")
        # find all elements (in body) that have a direct 'ne' child element
        neParents = []
        for e in body.findall(".//*"):
            if e.find("ne") is not None:
                neParents.append(e)
        hx = et.XML(xhtml)
        
        #print et.tostring(body)
        #print
        if False:
            for p in neParents:
                loc = p.get("loc", "")
                print "==========="
                print "---- %s" % loc
                print et.tostring(p)
                print "---"
                he = self.__getXhtmlElem(hx, loc)
                if he is None:
                    print "NONE"
                else:
                    print et.tostring(he)
                    if he.find(".//*")!=None: print "*******"
                print 
        
        neParents.reverse()
        for p in neParents:
            loc = p.get("loc", "")
            he = self.__getXhtmlElem(hx, loc)
            if he is not None:
                if he.find(".//*")!=None:
                    # ignore ones with sub-elements for now
                    continue
                #nes = p.findall(".//ne")
                #print len(nes)
                # OK, now get all child elements of p
                he.text = p.text
                for c in p.getchildren():   # should be only ne elements
                    if c.tag=="ne":
                        type = c.get("type", "")
                        #confidence = c.get("confidence", "")
                        #id = c.get("id", "")
                        #surface = c.get("surface", "")
                        #InChI = c.get("InChI", "")
                        #SMILES = c.get("SMILES", "")
                        #cmlRef = c.get("cmlRef", "")
                        #ontIDs = c.get("ontIDs", "")
                        title = "; ".join(["%s = %s" % (k,v) for k,v in c.attrib.iteritems()])
                        e = et.Element("span", {"class":"sci " + type, "title":title})
                        e.text = c.text
                        e.tail = c.tail
                        he.append(e)
                    else:
                        print "unexpected element name='%s'" % c.tag
                #print et.tostring(he)
            
        # Sci Legend
        l = [   ("DATA", "Experimental data"), 
                ("ONT", "Ontology term"), 
                ("CMu", "Chemical (etc.) with structure"),
                ("CM", "Chemical (etc.), without structure"), 
                ("RN", "Reaction"), 
                ("CJ", "Chemical adjective"),
                ("ASE", "enzyme -ase word"),
                ("CPR", "Chemical prefix"),
            ]
        div = et.Element("div", {"class":"sci-legend"})
        ul = et.Element("ul")
        for c, t in l:
            li = et.Element("li")
            span = et.Element("span", {"class":c})
            span.text = t
            li.append(span)
            ul.append(li)
        div.append(ul)
        img = et.Element("img", {"class":"sci"})
        d = et.Element("div", {"id":"sci-dialog", "style":"display:none;"})
        d.text = "Dialog contents"
        div.append(d)
        div.append(img)
        hx.append(div)
        
        cmls = self.getCmls(inlineAnnotatedSci=inlineAnnotatedSci)
        
        return et.tostring(hx), cmls
    

    def getCmls(self, inlineAnnotatedSci=None):
        et = self.iceContext.ElementTree
        if inlineAnnotatedSci is None:
            inlineAnnotatedSci = self.__inlineAnnotatedSci
        # remove ns
        inlineAnnotatedSci = inlineAnnotatedSci.replace('xmlns="http://www.xml-cml.org/schema"', "")
        x = et.XML(inlineAnnotatedSci)
        cmls = {}
        cmlPile = x.find(".//cmlPile")
        for c in cmlPile.getchildren():
            if c.tag=="cml":
                id = c.get("id", "")
                cmls[id] = et.tostring(c)
        return cmls
    
    
    def __getXhtmlElem(self, x, loc):
        loc = loc.strip("/")
        steps = [int(i) for i in loc.split("/")]
        steps.pop(0)
        for step in steps:
            children = []
            if x.text is not None:
                children.append(x.text)
            for c in x.getchildren():
                children.append(c)
                if c.tail is not None:
                    children.append(c.tail)
            index = step-1
            x = children[index]
        return x

