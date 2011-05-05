#!/usr/bin/python

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

pluginName = "ice.converter.svg"
pluginDesc = "Scalable Vector Graphics conversion service"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method
pluginPath = None


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized, pluginPath
    pluginFunc = None
    pluginClass = SvgConverter
    pluginInitialized = True
    if pluginPath is None:
        pluginPath = iceContext.fs.split(__file__)[0]
    return pluginFunc


class SvgConverter(object):
    exts = [".svg"]

    def __init__(self, iceContext):
        self.iceContext = iceContext
        self.__svgWrapper = SvgWrapper(iceContext)


    @property
    def isAvaliable(self):
        return self.__svgWrapper.isAvaliable


    def convert(self, fromToObj, **kwargs):
        """

        """
        format = kwargs.get("format", None)
        if format is None:
            format = "png"

        svgWrapper = SvgWrapper(self.iceContext)
        data = svgWrapper.rsvgConvert(fromToObj.getData(), "--format=%s" % format)
        fromToObj.putData(data)

    

    def convertX(self, svgFile, options):
        if rsvg_available():
            args = tuple("--%s=%s" % (k, v) for k, v in options.iteritems()
                                            if k in rsvg_options
                                            and v is not None and v != "")
            return rsvg_convert(svgFile, *args)
        else:
            convertUrl = self.iceContext.settings.get("convertUrl")
            if convertUrl == None:
                raise Exception("SVG conversion service not available")
                return "SVG conversion service not available", "", None
            else:
                print "Using SVG service at", convertUrl
                options.update({"sessionid": ""})

                fd = open(svgFile)
                postData = [(k, v) for k, v in options.iteritems()]
                postData.append(("file", fd))
                http = self.iceContext.Http()
                data = http.post(convertUrl, postData)
                fd.close()

                return data

#    def service(self, document, options, request, response):
#        url = options.get("url")
#        format = options.get("format", None)
#        if format is None:
#            options.update({"format": "png"})
#            format = "png"
#
#        sessionId = options.get("sessionid")
#        if sessionId == None:
#            raise self.iceContext.IceException("No session ID")
#
#        tmpFs = self.iceContext.FileSystem(sessionId)
#        if document == url:
#            _, filename = tmpFs.split(document)
#            http = self.iceContext.Http()
#            document, _, errCode, msg = http.get(url, includeExtraResults=True)
#            if errCode == -1:
#                raise self.iceContext.IceException("Failed to get %s (%s)" % (url, msg))
#        else:
#            filename = request.uploadFilename("file")
#
#        svgFilePath = tmpFs.absPath(filename)
#        tmpFs.writeFile(filename, document)
#
#        svgConvert = self.iceContext.getPlugin("ice.extra.SVGConverter").pluginFunc
#        content = svgConvert(svgFilePath, options)
#        mimeType = self.iceContext.MimeTypes["." + format]
#
#        if format in ["pdf", "ps"]:
#            _, name, _ = tmpFs.splitPathFileExt(filename)
#            response.setDownloadFilename(name + "." + format)
#
#        return content, mimeType
#
#    def options(self):
#        tmpl = self.iceContext.HtmlTemplate(templateFile = "plugins/service/svg-service.tmpl")
#        return tmpl.transform()


    def getHtml(self, svgFile, width = "", height = ""):
        html  = '<object type="image/svg+xml" data="%(name)s.svg" width="%(width)s" height="%(height)s">'
        html += '<img src="%(name)s.png" />'
        html += '</object>'

        # attempt to parse the width and height from the svg file
        tree = self.iceContext.ElementTree.parse(svgFile)
        root = tree.getroot()
        w = root.get("width", "")
        h = root.get("height", "")

        _, name, _ = self.iceContext.fs.splitPathFileExt(svgFile)

        return html % {"name": name, "width": w, "height": h}

    def __call__(self, svgFile, options):
        return self.convert(svgFile, options)



class SvgWrapper(object):
    RSVG_OPTIONS = ["dpi-x", "dpi-y", "x-zoom", "y-zoom", "zoom", "width", "height",
                    "format", "output", "keep-aspect-ratio", "version", "base-uri",
                    "background-color"]     # --background-color=#FFFFFF
    RSVG_FORMATS = ["png", "pdf", "ps", "svg"]


    def __init__(self, iceContext):
        self.iceContext = iceContext
        self.__system = iceContext.system
        self.__isAvaliable = None


    @property
    def isAvaliable(self):
        if self.__isAvaliable is None:
            stdout, _ = self.__system.executeNew("rsvg-convert", "--version")
            self.__isAvaliable = stdout.startswith("rsvg-convert")
        return self.__isAvaliable


    def rsvgConvertFile(self, filename, *args):
        if filename is not None:
            args = list(args)
            args.append(filename)
            out, err = self.__system.executeNew("rsvg-convert", *args)
            if len(err) > 0 and err.find("WARNING") == -1:
                raise Exception(err + out)
            return out
        else:
            raise Exception("Error: No SVG file specified")


    def rsvgConvert(self, data, *args):
        out, err = self.__system.executeNew("rsvg-convert", stdinData=data, *args)
        if len(err) > 0 and err.find("WARNING") == -1:
            raise Exception(err + out)
        return out



class FromToObjSample(object):
    def __init__(self, iceContext, data):
        self.__fs = iceContext.fs
        self.__data = data
        self.__result = None
        self.__tempDir = None
    @property
    def result(self):
        return self.__result
    def getData(self):
        return self.__data
    def putData(self, data):
        self.__result = data
    def copyResultTo(self, file):
        self.__fs.write(file, self.__result)
    def getFromFile(self):
        if self.__tempDir is None:
            self.__tempDir = self.__fs.createTempDirectory()
        self.__tempDir.write("fromFile", self.__data)
        return self.__tempDir.absPath("fromFile")
    def getToFile(self):
        if self.__tempDir is None:
            self.__tempDir = self.__fs.createTempDirectory()
        return self.__tempDir.absPath("toFile")
    def close(self):
        if self.__tempDir is not None:
            self.__tempDir.delete()
            self.__tempDir = None
    def __del__(self):
        self.close()


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

    pluginInit(iceContext)
    fs = iceContext.fs.clone(cwd)
    svg = fs.read("testData/test.svg")
    fromToObj = FromToObjSample(iceContext, svg)
    svgConverter = SvgConverter(iceContext)
    print svgConverter.isAvaliable
    svgConverter.convert(fromToObj)
    fs.write("testData/test.png", fromToObj.result)
