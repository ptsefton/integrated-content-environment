
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

pluginName = "ice.function.SwordDeposit"
pluginDesc = ""
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized, templatePath
    pluginFunc = swordDeposit
    pluginClass = None
    pluginInitialized = True
    path = iceContext.fs.split(__file__)[0]
    templatePath = iceContext.fs.join(path, "sword-deposit.tmpl")
    return pluginFunc

import atom
from request_data import ServerRequestData

def swordDeposit(self):
    
    d = { "authtype"    : "none",
          "username"    : self["username"],
          "password"    : "",
          "argPath"     : self.path,
          "collections" : None
    }
    self.isDocContentView = False
    if self.isPackage:
        path = "%stoc.rdf" % self.packagePath
        item = self.rep.getItemForUri(path)
        self.title = d["title"] = self.manifestTitle
    else:
        item = self.rep.getItemForUri(self.path)
        basePath, _ = self.iceContext.fs.splitExt(item.relPath)
        path = "%s.rdf" % basePath
        item = self.rep.getItemForUri(path)
        d["title"] = item.getMeta("title", item.name)
    
    if d["title"] is None:
        d["title"] = "Untitled"
    
    self.title = 'Deposit "' + d["title"] + '"'
    
    postback = self.formData.has_key("postback")
    if postback:
        if self.formData.has_key("url"):
            d["url"] = self.formData.value("url").strip()
        if self.formData.has_key("authtype"):
            d["authtype"] = self.formData.value("authtype").strip().lower()
        if self.formData.has_key("username"):
            d["username"] = self.formData.value("username").strip()
        if self.formData.has_key("password"):
            d["password"] = self.formData.value("password").strip()
        if self.formData.has_key("title"):
            d["title"] = self.formData.value("title").strip()
        if self.formData.has_key("collection"):
            d["collection"] = self.formData.value("collection").strip()
        try:
            IceAtomPub = self.iceContext.getPluginClass("ice.atompub")
            if IceAtomPub is None:
                raise Exception("Failed to get Atom Publishing plugin!")
            atomPub = IceAtomPub(d["url"], d["authtype"], d["username"], d["password"])
            d["collections"] = []
            if atomPub.hasServiceDocument:
                for ws in atomPub.service.workspaces:
                    for c in ws.collections:
                        formatNamespaceElems = c.getSwordElementList("formatNamespace")
                        c.supported = False
                        for formatNamespaceElem in formatNamespaceElems:
                            if formatNamespaceElem.text.strip() == "IceORE":
                                c.supported = True
                                break
                        print c
                        d["collections"].append(c)
            else:
                raise Exception, "No service document found."
            if self.formData.has_key("doDeposit"):
                d["docBody"] = self.body
                url = d.get("collection", "")
                print "Deposit to:", url
                if url == "":
                    d["status"] = "Please select a collection"
                else:
                    if self.isPackage:
                        resMap = self.serve(item, ServerRequestData(path), self.session)[0]
                    else:
                        resMap = item.getRendition(".rdf")
                    resMap = resMap.replace("?exportVersion=1", "?exportVersion=noContextLink")
                    _, filename, _ = self.iceContext.fs.splitPathFileExt(path)
                    swordHeaders = {"Content-Disposition": "filename=%s.rdf" % filename,
                                    "X-Format-Namespace": "IceORE"}
                    atomPub = IceAtomPub(url, d["authtype"], d["username"], d["password"])
                    response = atomPub.postMedia(d["title"], resMap, "text/xml", swordHeaders, url)
                    if response is not None:
                        d["success"] = True
                        d["response"] = self.iceContext.xmlEscape(str(response))
                        # TODO eprints returns links in the atom response
                        # that don't resolve so they're unusable
                        #print "response=[%s]\n" % response
                        atomXml = atom.EntryFromString(response)
                        d["contentLink"] = atomXml.content.src
                        print " * content link: %s" % d["contentLink"]
        except Exception, details:
            details = self.iceContext.xmlEscape(str(details))
            print "* SWORD Deposit failed: %s" % details
            print self.iceContext.formattedTraceback()
            d["error"] = "Failed to deposit. Ensure all fields are correctly filled in."
            d["response"] = details
    self["page-toc"] = ""
    htmlTemplate = self.iceContext.HtmlTemplate(templatePath)
    self.body = htmlTemplate.transform(d, allowMissing=True)

def isDocView(self):
    return not self.isFileView

swordDeposit.options = {"toolBarGroup":"publish", "position":32, "postRequired":True,
                        "label":"_SWORD deposit", "title":"Deposit this item via SWORD",
                        "enableIf": isDocView}
