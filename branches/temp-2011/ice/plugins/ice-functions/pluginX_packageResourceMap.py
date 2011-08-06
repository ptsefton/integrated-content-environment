
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

pluginName = "ice.function.toc.rdf"
pluginDesc = "RDF XML"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = servePackageResourceMap
    pluginClass = None
    pluginInitialized = True
    return pluginFunc


# ORE Resource Map using the manifest
def servePackageResourceMap(self):
    path = self.item.uri
    imsManifest = self.getImsManifest()
    if imsManifest is not None:
        OREResourceMap = self.iceContext.getPluginClass("ice.extra.ORE")
        if OREResourceMap is not None:
            rem = OREResourceMap(self.iceContext)
            rdf = rem.getPackageRdfXml(path, imsManifest)
            return (rdf, "application/rdf+xml", None)
        else:
            if self.iceContext.output is not None:
                self.iceContext.output.write("Foresite toolkit required for ORE\n")
    return None
servePackageResourceMap.options = {"postRequired":False}
servePackageResourceMap.__name__ = "toc.rdf"







