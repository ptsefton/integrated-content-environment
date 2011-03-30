#
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
from rsvg_wrapper import rsvg_options, rsvg_available, rsvg_convert

pluginName = "ice.extra.SVGConverter"
pluginDesc = "SVG converter"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method



def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = SvgConverter(iceContext)
    pluginClass = SvgConverter
    pluginInitialized = True
    return pluginFunc



class SvgConverter(object):    
    def __init__(self, iceContext):
        self.iceContext = iceContext
    
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
    
    def convert(self, svgFile, options):
        if rsvg_available():
            args = ["--%s=%s" % (k, v) for k, v in options.iteritems()
                                            if k in rsvg_options
                                            and v is not None and v != ""]
            args.append("-o")
            tmpDir = self.iceContext.fs.createTempDirectory()
            tmpFile = tmpDir.absPath("temp.png")
            args.append(tmpFile)
            rsvg_convert(svgFile, *args)
            pngData = tmpDir.readFile("temp.png")
            tmpDir.delete()
            return pngData
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
    
    def __call__(self, svgFile, options):
        return self.convert(svgFile, options)
        