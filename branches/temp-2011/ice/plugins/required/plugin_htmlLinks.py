
#    Copyright (C) 2009  Distance and e-Learning Centre,
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

from html_cleanup import HtmlCleanup
from urlparse import urlparse


pluginName = "ice.HtmlLinks"
pluginDesc = ""
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = None
    pluginClass = HtmlLinks
    pluginInitialized = True
    return pluginFunc



class HtmlLinks(object):
    class _UrlAttribute(object):
        def __init__(self, node, attName):
            self.node = node
            self.attName = attName
            self.protocol, self.netloc, self.path, self.param, self.query, \
                    self.fid  = urlparse(self.url)
        def __getUrlAtt(self):
            return self.node.getAttribute(self.attName)
        def __setUrlAtt(self, value):
            self.node.setAttribute(self.attName, value)
            self.protocol, self.netloc, self.path, self.param, self.query, \
                    self.fid  = urlparse(value)
        url = property(__getUrlAtt, __setUrlAtt)
        def __str__(self):
            s = self.url
            if s is None:
                s = "[None]"
            return s

    def __init__(self, iceContext, html):
        self.iceContext = iceContext
        self.HtmlParser = HtmlCleanup
        xhtml = self.HtmlParser.convertHtmlToXml(html)
        self.xml = self.iceContext.Xml(xhtml)

    def _getHrefNodes(self):
        refNodes = self.xml.getNodes("//*[@href]")
        return refNodes

    def _getSrcNodes(self):
        srcNodes = self.xml.getNodes("//*[@src]")
        return srcNodes

    def _getParamNodes(self):
        nodes = self.xml.getNodes("//*[local-name()='param'][@name='url' or @name='movie'][@value]")
        return nodes

    def _getObjectNodes(self):
        nodes = self.xml.getNodes("//*[local-name()='object'][@data]")
        return nodes

    def getUrlAttributes(self):
        attrs = []
        for node in self._getHrefNodes():
            attrs.append(HtmlLinks._UrlAttribute(node, "href"))
        for node in self._getSrcNodes():
            attrs.append(HtmlLinks._UrlAttribute(node, "src"))
        for node in self._getParamNodes():
            attrs.append(HtmlLinks._UrlAttribute(node, "value"))
        for node in self._getObjectNodes():
            attrs.append(HtmlLinks._UrlAttribute(node, "data"))
        return attrs

    def __str__(self):
        return str(self.xml.getRootNode())

    def close(self):
        self.xml.close()

    def __del__(self):
        self.close()
