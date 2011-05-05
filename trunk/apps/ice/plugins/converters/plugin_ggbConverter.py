
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

""" This plugin is used to support Geogebra conversion in ICE
conversion server.
This plugin will call geoGebraExport plugin
@requires: plugins/extras/plugin_ggb_export.py
"""

pluginName = "ice.converter.geogebra"
pluginDesc = "GeoGebra converter"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method
pluginPath = None


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized, pluginPath
    pluginFunc = None
    pluginClass = GgbConverter
    pluginInitialized = True
    if pluginPath is None:
        pluginPath = iceContext.fs.split(__file__)[0]
    return pluginFunc


class GgbConverter(object):
    exts = [".ggb"]

    def __init__(self, iceContext):
        """ Geogebra Service Constructor method
        @param iceContext: Current ice context
        @type iceContext: IceContext
        @rtype: void
        """
        self.iceContext = iceContext
        self.__GeoGebraExport = self.iceContext.getPlugin("ice.extra.geoGebraExport").pluginClass
        self.__geoGebraExport = self.__GeoGebraExport(self.iceContext,
                                self.iceContext.settings.get("convertUrl"))
    

    @property
    def isAvaliable(self):
        return self.__svgWrapper.isAvaliable


    def convert(self, fromToObj, **options):
        """

        """
        url = options.get("url")
        mode = options.get("mode", "image")
        format = options.get("format", "png")
        width = str(options.get("width", 300))
        height = str(options.get("height", 300))
        document = fromToObj.getFromFile()

        if mode == "image":
            export = GeoGebraExport(self.iceContext, self.iceContext.settings.get("convertUrl"))
            content = self.__geoGebraExport.createPreviewImage(document, format, width, height)
            mimeType = self.iceContext.getMimeTypeForExt("." + format.lower())
        else:
            if document != url:
                document = request.uploadFilename("file")
            content = self.__GeoGebraExport.getAppletHtml(document, width, height)
            mimeType = self.iceContext.getMimeTypeForExt(".html")

        fromToObj.putData(content)
        fromToObj.toMimeType = mimeType
        return content, mimeType


#    def options(self):
#        """
#        @rtype: String
#        @return: transformed ggb document in html format
#        """
#        tmpl = self.iceContext.HtmlTemplate(templateFile = "plugins/service/ggb-service.tmpl")
#        return tmpl.transform()






