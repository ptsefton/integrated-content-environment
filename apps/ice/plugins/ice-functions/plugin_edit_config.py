
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

pluginName = "ice.function.editConfig"
pluginDesc = "ICE configuration editor"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = edit_config
    pluginClass = None
    pluginInitialized = True
    return pluginFunc

def isClient(self):
    return not self.iceContext.isServer


def edit_config(self):
    print "plugin_edit_config.editConfig()"
    try:
        configEditorPluginName = self.iceContext.settings.configEditorPluginName
        print "configEditorPluginName='%s'" % configEditorPluginName
        plugin = self.iceContext.getPlugin(configEditorPluginName)
        if plugin is not None:
            EditConfigXml = plugin.pluginClass
        editConfigXml = EditConfigXml(self.iceContext)
        html = editConfigXml.edit(self.formData)
    except Exception, e:
        html = "edit_config execption - '%s'" % str(e)
    if self.formData.has_key("OK"):
        return
    self["title"] = "Config editor"
    html = self.iceContext.HtmlCleanup.cleanup(html)
    xml = self.iceContext.Xml(html)
    body = str(xml.getNode("//body"))
    xml.close()
    #self["body"] = html
    #print "edit_config html="
    #print html
    #print
    self["body"] = "<div>config testing</div>" #html
    self["body"] = body
edit_config.options = {"toolBarGroup":"advanced", "position":1, "postRequired":False,
                "label":"Edit config", "displayIf": isClient,"title":"Edit the ICE configuration file"}


