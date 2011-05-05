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

""" Plugin to call a remote server """


pluginName = "ice.extra.convertServer"
pluginDesc = "Call a remote convert server"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method



def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = None
    pluginClass = ConvertServer
    pluginInitialized = True
    return pluginFunc


class ConvertServer(object):
    def __init__(self, iceContext, **kwargs):
        self.iceContext = iceContext
        self.__http = None
        self.__isAvailable = False
        self.__convertUrl = iceContext.settings.get("convertUrl")
        if self.__convertUrl is not None:
            self.__http = iceContext.Http()
            self.__isAvailable = True

    
    @property
    def isAvailable(self):
        return self.__isAvailable


    def post(self, path, postData):
        """ 
            @type path: str
            @param path: the absolute path on the server e.g. /api
            @type postData: list of tuples
            @param postData: list of tuples (name, data) that is to be posted e.g. [("name", data)]
            
            @rtype: str
            @return: the result data
        """
        if self.__isAvailable==False:
            raise Exception("ConvertServer is not available!")
        #postData = [("file", fd)]
        url = self.__convertUrl + path
        data = self.__http.post(url, postData)
        return data
















