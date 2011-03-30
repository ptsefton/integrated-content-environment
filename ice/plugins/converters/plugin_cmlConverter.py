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

""" This plugin is used to support Chemical Markup Language conversion in ICE
conversion server.
This plugin will call cmlUtil plugin to convert .cml to SVG, PNG or JMOL, CDX, JPG
@requires: plugins/extras/plugin_cmlUtil.py
"""


pluginName = "ice.converter.cml"
pluginDesc = "Chemical Markup Language converter"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method
pluginPath = None


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized, pluginPath
    pluginFunc = None
    pluginClass = CmlConverter
    pluginInitialized = True
    if pluginPath is None:
        pluginPath = iceContext.fs.split(__file__)[0]
    return pluginFunc


class CmlConverter(object):
    exts = [".cml"]

    def __init__(self, iceContext):
        self.iceContext = iceContext
        self.__CmlUtil = iceContext.getPlugin("ice.extras.cmlUtil").pluginClass
        self.__cmlUtil = self.__CmlUtil(self.iceContext,
                                self.iceContext.settings.get("convertUrl"))
        self.__jumboDefaults = self.__CmlUtil.getJumboDefaults()
        self.__params = self.__jumboDefaults


    @property
    def isAvaliable(self):
        return self.__svgWrapper.isAvaliable


    def convert(self, fromToObj, **kwargs):
        """
            fromToObj.getFromFile()
                .putData(data)
            **kwargs (options) -
                url
                mode
                format
                width
                height
                reload
                params
        """
        options = kwargs
        url = options.get("url")
        mode = options.get("mode", "preview")
        format = options.get("format", "svg")
        width = str(options.get("width", 300))
        height = str(options.get("height", 300))
        reload = bool(options.get("reload"))
        self.__params = options.get("params", self.__jumboDefaults)

        if mode=="preview":
            content = self.__cmlUtil.createPreviewImage(document, format, width, height, params)
            mimeType = self.iceContext.getMimeTypeForExt("." + format.lower())
        elif mode=="extract":
            _, name, ext = self.iceContext.fs.splitPathFileExt(filename)
            content = self.__cmlUtil.extractChemDraw(document, name = name + ext)
            mimeType = self.iceContext.getMimeTypeForExt(".zip")
            response.setDownloadFilename("media.zip")
        elif mode=="applet":
            appletHtml = self.__CmlUtil.getAppletHtml(filename, width, height)
            content = "<div><pre>%s</pre></div>" % appletHtml
            mimeType = self.iceContext.getMimeTypeForExt(".html")
        else:
            raise Exception("Unknown mode: %s" % mode)
        if reload:
            self.__params = self.__jumboDefaults

        fromToObj.putData(content)
        fromToObj.toMimeType = mimeType
        
        return content, mimeType


    def options(self):
        """
        @rtype: String
        @return: transformed cml document in html format
        """
        tmpl = self.iceContext.HtmlTemplate(templateFile = "plugins/service/cml-service.tmpl")
        return tmpl.transform({"params": params})





if __name__=="__main__":
    import os
    import sys
    cwd = os.getcwd()
    os.chdir("../..")
    sys.path.append(".")
    from ice_common import IceContext
    iceContext = IceContext(pluginsPath="plugins", loadRepositories=False,
                    loadConfig=False, loadPlugin=False)
    __file__ = iceContext.fs.join(cwd, __file__)
    #sys.path.append(cwd)

    pluginInit(iceContext)
    print "pluginPath='%s'" % pluginPath














