
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

pluginName = "ice.extra.html2text"
pluginDesc = "html to text"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method



def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = HtmlToText()
    pluginClass = HtmlToText
    pluginInitialized = True
    HtmlToText.Xml = iceContext.Xml
    return pluginFunc




class HtmlToText(object):
    Xml = None
    
    def __init__(self, **kwargs):
        pass
    
    def htmlToText(self, xmlStr):
        content = None
        try:
            dom = self.Xml(xmlStr)
            textNodes = dom.getNodes("//text()")
            texts =[]
            for textNode in textNodes:
                texts.append(textNode.getContent())
            content = " ".join(texts)
            dom.close()
        except Exception, e:
            print "Exception in htmlToText - '%s'" % str(e)
        return content
    
    def __call__(self, xml):
        return self.htmlToText(xml)







