
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

pluginName = "ice.function.ref_links"
pluginDesc = ""
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = ref_links
    pluginClass = None
    pluginInitialized = True
    return pluginFunc


def ref_links(self):
    path = self.iceContext.item.relPath
    item = self.iceContext.rep.getItem(path)
    title = item.getMeta("title")
    d = { "title": title, "message": "" }
    indexer = self.iceContext.rep.indexer
    # check that ice is not using the dummy indexer
    if hasattr(indexer, "dummyFlag"):
        d["message"] = "Cannot find links because the indexer is disabled."
    else:
        foundIds = indexer.searchKeyword("+links:%s" % path)
        if foundIds == []:
            d["message"] = "No links found to this document."
        else:
            SearchPlugin = self.iceContext.getPluginClass("ice.function.search")
            if SearchPlugin is None:
                d["message"] = "ERROR: Search plugin not found!"
            else:
                search = SearchPlugin(self.iceContext)
                d["searchResult"] = search.processResults(indexer, foundIds)
    templatePath = self.iceContext.fs.split(__file__)[0]
    htmlTemplate = self.iceContext.HtmlTemplate(self.iceContext.urlJoin(templatePath, "ref-links.tmpl"))
    self.title = title
    self.body = htmlTemplate.transform(d, allowMissing=True)

def isDocView(self):
    return self.isDocView

ref_links.options={"toolBarGroup":"manage", "position":10, "postRequired":False,
                   "label":"Referring pages", "title":"Check for documents referring to this page",
                   "enableIf":isDocView}

