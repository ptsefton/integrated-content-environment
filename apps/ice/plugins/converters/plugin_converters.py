
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

""" Plugin to load the rest of the converter plugins"""

pluginName = "ice.converters"
pluginDesc = "File format converters"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    """ plugin declaration method 
    @param iceContext: IceContext type
    @param kwargs: optional list of key=value pair params
    @return: handler object
    """
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = None
    pluginClass = Converts
    pluginInitialized = True
    return pluginFunc


class Converters(object):
    """ Base class for Converters Class """ 
    def __init__(self, iceContext, **kwargs):
        """ Converters Constructor method 
        @param iceContext: Current ice context
        @type iceContext: IceContext 
        @param kwargs: optional list of key=value pair params
        @type kwargs: dict
        @rtype: void
        """
        self.iceContext = iceContext
        self.__convertersFromTo = {}            # e.g. {(".docx", ".odt"):converter, ... }
        converterNames = iceContext.getPluginsOfType("ice.converter.")
        for converterName in converterNames:
            try:
                converter = iceContext.getPlugin(converterName).pluginClass(iceContext)
                for fromExt in converter.fromExts:
                    for toExt in converter.toExts:
                        self.__convertersFromTo[(fromExt, toExt)] = converter
            except Exception, e:
                pass
    
    
    def getConverter(self, fromExt, toExt):
        """ get the converter based on fromExt to toExt
        @param fromExt: the extension of file to be converted 
        @type fromExt: String
        @param toExt: the extension of converted file
        @type toExt: String
        
        @rtype: plugin
        @return: the selected converter plugin
        """
        return self.__convertersFromTo.get((fromExt, toExt))
    
    
    def getFromToExts(self):
        """ get the list of extension that has plugin
        @rtype: list
        @return: list of extension that
        """
        return self.__convertersFromTo.keys()









