
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

pluginName = "ice.function.ChemDrawCMLExtractor"
pluginDesc = "ChemDraw to CML extractor"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method

CmlUtil = None


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
#    cdx2cml.toolBarGroup = "advanced"
#    cdx2cml.label = "ChemDraw to CML"
#    cdx2cml.title = "Convert ChemDraw objects to CML"
    cdx2cml.enableIf = isDocViewAndOdt
    pluginFunc = cdx2cml
    pluginClass = None
    pluginInitialized = True
    global CmlUtil
    CmlUtil = iceContext.getPlugin("ice.extras.cmlUtil").pluginClass
    return pluginFunc


def isDocViewAndOdt(self):
    if self.item == None:
        return False
    return not self.isFileView and self.item.ext==".odt"



def cdx2cml(self):
    inputFile = self.item._absPath
    outputDir, name, ext = self.self.iceContext.fs.splitPathFileExt(inputFile)
    outputDir = self.self.iceContext.fs.join(outputDir, "media", "cml")
    try:
        data = self.iceContext.fs.readFile(inputFile)
        util = CmlUtil(self.iceContext, self.self.iceContext.settings.get("convertUrl"))
        util.extractChemDraw(data, outputDir, name + ext)
    except Exception, e:
        print "Failed to extract ChemDraw: %s" % str(e)
    





