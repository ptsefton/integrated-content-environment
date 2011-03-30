
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

pluginName = "ice.function.atomPub"
pluginDesc = ""
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method

AtomPublish = None
AtomConfig = None


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized, templatePath
    pluginFunc = publishThis
    pluginClass = None
    pluginInitialized = True
    path = iceContext.fs.split(__file__)[0]
    templatePath = iceContext.fs.join(path, "atom-pub.tmpl")
    global AtomPublish
    plugin = iceContext.getPlugin("ice.atom.publish")
    AtomPublish = plugin.pluginClass
    global AtomConfig
    plugin = iceContext.getPlugin("ice.atom.config")
    AtomConfig = plugin.pluginClass
    return pluginFunc



def publishThis(self):
    self.isDocContentView = False
    textToHtml = self.iceContext.textToHtml
    PROP_ATOM_URL = "_atomUrl"
    PROP_ATOM_ENTRY = "_atomEntry"
    d = {}
    d["newEntry"] = True
    d["authtype"] = "none"
    d["draft"] = True
    atomConfig = AtomConfig(self.iceContext)
    # check for stored atom properties
    path = self.path
    d["argPath"] = path
    item = self.rep.getItemForUri(path)
    name = item.relPath
    if name is None:
        print "* Can not find itemName for path '%s'" % path
        hasPropAtomUrl = False
        hasPropAtomEntry = False
    else:
        item = self.rep.getItem(name)
        hasPropAtomUrl = item.hasMeta(PROP_ATOM_URL)
        hasPropAtomEntry = item.hasMeta(PROP_ATOM_ENTRY)
    d["title"] = self.iceContext.cleanUpString(item.getMeta("title", item.name))
    d["hasPropAtomEntry"] = hasPropAtomEntry
    entryXml = None
    entry = None
    if hasPropAtomEntry:
        d["newEntry"] = False
        # attempt to parse the atom entry stored in the meta properties
        try:
            entryXml = unicode(item.getMeta(PROP_ATOM_ENTRY), "utf-8")
            # FIXME gdata still uses the old purl.org namespace
            entryXml.replace(AtomPublish.APP_NS, AtomPublish.APP_NAMESPACE)
            entry = AtomPublish.parseEntry(entryXml)
        except Exception, e:
            print "* Invalid atom entry; removing from meta: %s" % str(e)
            entry = None
            item.removeMeta(PROP_ATOM_URL)
            item.removeMeta(PROP_ATOM_ENTRY)
    self.title = 'Publish "' + d["title"] + '"'
    postback = self.formData.has_key("postback")
    sessionUsername = self.iceContext.session.username
#    print sessionUsername#
    urlList = []
    loginList = []
    categoryList = []
    atomDict = {} 
    atomSettings = atomConfig.settings
    if atomSettings.has_key(sessionUsername):
        atomSetting = atomConfig.settings[sessionUsername][1]
        for key in atomSetting:
            urlList.append(key)
            login = [atomSetting[key][1],atomSetting[key][2]]
            loginList.append(login)
            categories = atomSetting[key][3]
            catList = []
            for catkey in categories:
                catList.append(categories[catkey][1])
            categoryList.append(catList)
            atomDict[key] = [atomSetting[key][1],atomSetting[key][2],catList]
            d["hasRecord"]= True
    else:
#    if urlList is None:
        d["hasRecord"]= False
        print "No Atom Pub Data"
        urlList.append("")
        loginList.append("")
        categoryList.append("")
        atomDict[0] = [""]
    d["urlList"] = urlList
    d["loginList"] = loginList
    d["categoryList"] = categoryList
    d["atomDict"] = atomDict
    if postback:
        if hasPropAtomEntry:
            if self.formData.has_key("NewEntryvalue"):
                d["newEntry"] = self.formData.has_key("NewEntryvalue")
        d["draft"] = self.formData.has_key("draft")
        d["pdfLink"] = self.formData.has_key("pdfLink")
        d["url"] = None
        if self.formData.has_key("newURL"):
            d["newURL"] = self.formData.value("newURL")
            if (self.formData.value("newURL") == True or self.formData.value("newURL")== "newURL"):
                if self.formData.has_key("txturl"):
                    d["url"] = self.formData.value("txturl").strip()
            else:
                if self.formData.has_key("url"):
                    d["url"] = self.formData.value("url").strip()
        else:
            if self.formData.has_key("url"):
                d["url"] = self.formData.value("url").strip()
            if d["url"] is None or d["url"] == "":
                if self.formData.has_key("txturl"):
                    d["url"] = self.formData.value("txturl").strip()
        #get Category lists
        categories = []
        for key in self.formData.keys():
            if key.find("txtCategory") != -1:
                if self.formData.value(key) is not None:
                    categories.append(self.formData.value(key))
        d["categories"] = categories
        if self.formData.has_key("authtype"):
            d["authtype"] = self.formData.value("authtype").strip().lower()
        if self.formData.has_key("atompub_username"):
            d["username"] = self.formData.value("atompub_username").strip()
        if self.formData.has_key("atompub_password"):
            d["password"] = self.formData.value("atompub_password").strip()
        if self.formData.has_key("author"):
            d["author"] = self.formData.value("author").strip()
        if self.formData.has_key("title"):
            d["title"] = self.iceContext.cleanUpString(self.formData.value("title").strip())
        if self.formData.has_key("summary"):
            d["summary"] = self.formData.value("summary").strip()
        basePath, baseName, _ = self.iceContext.fs.splitPathFileExt(name)
        item.render()
        xhtmlBody = item.getRendition(".xhtml.body")
        if d["pdfLink"]:
            pdfLink = "<span class='pdf-rendition-link'><a href='%s.pdf'>View as PDF</a></span>" % baseName
        else:
            pdfLink = ""
        toc =item.getMeta("toc")
        if toc is None or toc == '' :
            toc = " <!-- toc --> "
        content = "<div>%(pdf-link)s<div class='page-toc'>%(page-toc)s</div>%(body)s</div>" \
                % {"pdf-link": pdfLink,
                   "page-toc": toc,
                   "body": xhtmlBody}
        content = content.replace("<?xml version=\"1.0\"?>","")
        dom = self.iceContext.Xml(content)
        #fix the empty anchor except comment within it
        emptyNodes = dom.getNodes("//a[not(*)]")
        for emptyAnchor in emptyNodes:
            #add extra span so that it will keep it closing tag. 
            span = dom.createElement("span")
            children = emptyAnchor.getChildren()
            for child in children:
                span.addChild(child) 
            emptyAnchor.addChild(span)
        #Fix for the footnote
        footNoteSpans = dom.getNodes("//span[@class='footnote']")
        if footNoteSpans:
            for footNoteSpan in footNoteSpans:
                footNoteSpan.setAttribute("style", "vertical-align: super;")
                aHref = footNoteSpan.getNode("./a")
                footnoteSpan = footNoteSpan.getNode("./span")
                if aHref and footnoteSpan:
                    footnoteText = footnoteSpan.getContent().strip()
                    aHref.setAttribute("title", footnoteText)
                    footnoteSpan.remove()
        content = str(dom)
        dom.close()
        if d["newEntry"]:
            entryXml = None
        try:
            if d.get("url", "") == "" and entry != None:
                if hasPropAtomUrl:
                    d["url"] = item.getMeta(PROP_ATOM_URL)
                else:
                    d["url"] = entry.GetEditLink().href
            images = item.getMeta("images")
            # get media from the repository
            def getMedia(media = None):
                item = self.rep.getItem(name)
                if media is None:
                    files = []
                    if images is not None:
                        files.extend(images)
                    # pdf rendition
                    if item.hasPdf:
                        files.append(baseName + ".pdf")
                    # linked objects
                    dom = self.iceContext.Xml(content)
                    nodes = dom.getNodes("//object/@data | \
                                          //object/param[@name='src' or @name='movie' or @name='url']/@value | \
                                          //applet/@archive | \
                                          //applet/param[@name='load']/@value")
                    for node in nodes:
                        file = node.getContent()
                        if not file.endswith(".jar"):
                            files.append(file)
                    dom.close()
                    return files
                else:
                    if images is not None and media in images:
                        return item.getImage(media)
                    elif media == (baseName + ".pdf"):
                        return item.getRendition(".pdf")
                    else:
                        # assume relative path to document
                        mediaPath = self.iceContext.fs.join(basePath, media)
                        item = self.iceContext.rep.getItemForUri(mediaPath)
                        mediaContent = item.read()
                        return mediaContent
            # save the atom info as document meta properties
            def saveResponse(response, publishedCategory):
                item = self.rep.getItem(name)
                item.setMeta(PROP_ATOM_URL, d["url"])
                item.setMeta(PROP_ATOM_ENTRY, response)
                item.close()
                url = d.get("url","")
                username = sessionUsername
                loginUsername = d.get("username", "")
                authType = d.get("authtype","")
                atomConfig.saveSettings(url,username,loginUsername,authType,publishedCategory)
            options = d.copy()
            options.update({"atompuburl": d["url"], "categories":d["categories"], "draft": str(d["draft"])})
            atomPub = AtomPublish(self.iceContext, name, getMedia, saveResponse)
            content = content
            try:
                successes, responses, publishedUrls = atomPub.publish(content, options, entryXml)
                try:
                    success = True
                    for s in successes:
                        success = success and s
                    if publishedUrls == []:
                        success = False
                    if responses != []:
                        response = self.iceContext.xmlEscape(str(responses[0]))
                except Exception, e:
                    success = False
                    response = "Unexpected server response."
            except Exception, e:
                success = False
                response = str(e)
            if success:
                self.title = d["title"]
                d["success"] = success
                d["publishedUrls"] = publishedUrls
            d["response"] = response
            d["docBody"] = self.iceContext.cleanUpString(xhtmlBody)
            d["error"] = "Failed to post."
        except Exception, details:
            details = self.iceContext.xmlEscape(str(details))
            print "* Atom Pub failed: %s" % details
            print self.iceContext.formattedTraceback()
            d["error"] = "Failed to post entry. Ensure all fields are correctly filled in."
            d["response"] = details
    else:
        if hasPropAtomUrl:
            d["url"] = item.getMeta(PROP_ATOM_URL)
        if hasPropAtomEntry:
            d["status"] = "This document has been posted"
            if entry != None:
                editUrl = entry.GetEditLink().href
                if d.get("url", "") == "":
                    d["url"] = editUrl
                if d.get("categories","") == "":
                    d["categories"] = ""
                # check for wordpress/blogger authentication
                if editUrl.find("/wp-app.php") > -1:
                    d["authtype"] = "basic"
                elif editUrl.startswith("http://www.blogger.com/"):
                    d["authtype"] = "blogger"
                d["author"] = entry.author[0].name.text
                # FIXME encoding UTF-8 fails sometimes on chars like 'smart quotes'
                d["title"] = self.iceContext.cleanUpString(entry.title.text )#entry.title.text.encode("utf-8")
                if entry.summary is not None:
                    d["summary"] = entry.summary.text 
                else:
                    d["summary"] = ""
                # check if this is a draft, which means there's no alternate url
                try:
                    d["draft"] = (entry.control.draft.text == "yes")
                except:
                    d["draft"] = False
                if not d["draft"]:
                    altLink = entry.GetAlternateLink()
                    if altLink != None:
                        d["entryLink"] = altLink.href
        else:
            d["status"] = "This document has not been posted"
    self["page-toc"] = ""
    htmlTemplate = self.iceContext.HtmlTemplate(templatePath)
    #textToHtml
    d["summary"] = textToHtml(d.get("summary", ""))

    self.body = htmlTemplate.transform(d, allowMissing=True)
    

def isDocView(self):
    return self.isDocView
publishThis.options = {"toolBarGroup":"publish", "position":31, "postRequired":True,
                       "label":"Blog", "title":"Publish this using AtomPub",
                       "enableIf": isDocView}
