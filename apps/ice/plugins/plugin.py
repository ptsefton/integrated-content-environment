
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

pluginName = "ice.name"
pluginDesc = ""
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = None
    pluginClass = None
    pluginInitialized = True
    return pluginFunc



###############################################################################
###############################################################################
# Ideas for a better plugin system
#   so that plugins can be customized per context!
#
class Plugin(object):
    def __init__(self, context, name, desc, *args, **kwargs):
        self.__context = context
        self.__name = name
        self.__desc = desc
        self.__initErrMsg = ""

    @property
    def name(self):
        return self.__name

    @property
    def description(self):
        return self.__desc

    @property
    def context(self):
        return self.__context

    @property
    def initializedOK(self):
        return self.__initErrMsg==""

    @property
    def initErrorMessage(self):
        return self.__initErrMsg

    def _setInitErrorMessage(self, msg):
        self.__initErrMsg = msg

    def factory(self, *args, **kwargs):
        """ Method for creating new instances of this plugin class """
        return None

    def function(self, *args, **kwargs):
        """ Function for carrying out the default (singlar) job of this plugin """
        return None



class MyPlugin(Plugin):
    def __init__(self, context, *args, **kwargs):
        name = "MyPlugin"
        desc = "MyPlugin is a sample plugin"
        name = pluginName           # global
        desc = pluginDesciption     # global
        Plugin.__init__(self, context, name, desc, *args, **kwargs)
        Plugin._setInitErrorMessage(self, "")

    # Optional
    #def function(self, *args, **kwargs):
    #    """ Function for carrying out the default (singlar) job of this plugin """
    #    return None

    # Optional
    def factory(self, *args, **kwargs):
        """ Method for creating new instances of this plugin class """
        obj = self.context.Object()
        obj.context = context
        return obj

###############################################################################
###############################################################################



