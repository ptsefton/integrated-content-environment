
#    Copyright (C) 2006/2008  Distance and e-Learning Centre, 
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

from odsbaseConverter import odsBaseConverter

pluginName = "ice.render.xlsConverter"
pluginDesc = "converts Excel documents to HTML and PDF"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginClass = XlsConverter
    pluginFunc = None
    pluginInitialized = True
    return pluginClass



class XlsConverter(odsBaseConverter):
    fromToExts = {".xls":[".htm", ".pdf"]}
    
    def __init__(self, iceContext):
        self.iceContext = iceContext
        odsBaseConverter.__init__(self, iceContext)
        self.convertToOdt = True
        self.priority = True
    
    
    def render(self, item, convertedData, **kwargs):
        file = item.relPath
        return self.renderMethod(file, convertedData)









