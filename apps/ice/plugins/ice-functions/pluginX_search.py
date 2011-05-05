
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
import urllib

pluginName = "ice.function.search"
pluginDesc = ""
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    path = iceContext.fs.split(__file__)[0]
    Search.myPath = path
    Search.HtmlTemplate = iceContext.HtmlTemplate
    
    pluginFunc = search
    pluginClass = Search
    pluginInitialized = True
    return pluginFunc



# SearchToolbar
def __searchToolbar(self):
    packagePath = self.packagePath
    if packagePath is None:
        packagePath = ""
    actionPath = packagePath
    if actionPath.startswith("/"):
        actionPath = actionPath[1:]  
    if not actionPath.endswith("/") and actionPath!="":
        actionPath = actionPath + "/"  
    actionPath = self.iceContext.urlJoin(self.iceContext.urlRoot, actionPath)
    form = "\n<form style='display:inline;' method='POST' action='%s'>" % actionPath
    form += "<input type='hidden' name='ispostback' value='1'/>"
    form += "<input type='hidden' name='func' value='changeTemplate'/>\n"
    form += "<input type='hidden' name='argPath' value='%(argPath)s'/>\n"
    
    query = self.formData.value("query")
    if query is None: query = ""
    form += "<input type='text' size='30' name='query' id='query' value='%s' title='Enter search query here'><!-- --></input>\n" \
                % query
    form += "<input type='hidden' name='packagePath' value='%s'/>" % packagePath
    form += "<button type='submit' name='search' id='search' title='Search'>Search</button>"
    form += "\n</form>\n"
    return form


def search(self):
    query = self.formData.value("query").strip()
    print "search query = '%s'" % query
    
    searchFunc = Search(self.iceContext)
    
    self["title"] = "Search"    
    self["body"] = searchFunc.search(self.formData, self.rep)
    atomFeedURL = "?query=%s&#38;search=&#38;format=atom" % urllib.quote(query)
    self["style-css"] += "<link rel='alternate' type='application/atom+xml' title='ICE Atom Feed' href='%s'/>" % atomFeedURL
    return
search.options = {"toolBarGroup":"common", "position":16, "postRequired":False,
                "label":"Search?", "title":"search",
                "toolbarHtml":__searchToolbar}


class Search (object):
    searchTemplateName = 'search-template.tmpl'
    myPath = ""
    HtmlTemplate = None
    
    def __init__ (self, iceContext):
        self.iceContext = iceContext
        self.__settings = iceContext.settings
        self.__fs = iceContext.fs
        self.__system = iceContext.system
        self.__formData = None
        self.__rep = None
        self.__query = ""
        self.d = {}
        self.searchResult = []
        self.packagePath = ""
        self.searchPath = ""
        self.fileName = ""
        self.tagsOnly = ""
    
    
    def search(self, formData, rep):
        if self.__rep is None:
            self.__rep = rep
        self.__formData = formData
        
        self.__query = self.__formData.value("query")
        if self.__query:
            self.__query = self.__query.strip()
        else:
            self.__query = ""
        
        self.packagePath = self.__formData.value("packagePath", "").strip()
        self.searchPath = self.__formData.value("searchPath", "").strip()
        if self.searchPath=="":
            self.searchPath = self.packagePath
        
        self.d["tagsOnly"] = ""
        
        tagsArray = []
        self.tagsOnly = self.__formData.value("tagsOnly")
        if self.tagsOnly:
            tagsArray = self.__query.split(" ")
            self.d["tagsOnly"] = "checked='checked'"
        else:
            self.tagsOnly = ""
        
        self.fileName = self.__formData.value("fileName")
        #remove the extension: if found
        fileName = ""
        if self.fileName:
            fileName, ext = self.__fs.splitExt(self.fileName)
            
            if ext != "" and ext != ".book":
                fileName = fileName
            else:
                fileName = self.fileName             
            
            if fileName:
                fileName = fileName.strip()
        
        try:
            indexer = self.__rep.indexer
            if self.packagePath:  
                if self.fileName:
                    if self.tagsOnly:
                        foundIds = indexer.search("", tagsArray, fileName=fileName, path=self.searchPath)
                    else:
                        foundIds = indexer.search(self.__query, fileName=fileName, path=self.searchPath)
                else:
                    if self.tagsOnly:
                        foundIds = indexer.search("", tagsArray, path=self.searchPath)
                    else:
                        foundIds = indexer.search(self.__query, path=self.searchPath) 
            else:
                if self.fileName:
                    if self.tagsOnly:
                        foundIds = indexer.search("", tagsArray, fileName=fileName)
                    else:
                        foundIds = indexer.search(self.__query, fileName=fileName)
                elif self.tagsOnly:
                    foundIds = indexer.search("", tagsArray)
                else:
                    foundIds = indexer.search(self.__query)
            if foundIds==[]:
                msg = "<div>No documents matching your query were found!</div>"
                self.d["message"] = msg                
            else:
                self.searchResult = self.processResults(indexer, foundIds)
                self.d["searchResult"] = self.searchResult
                
        except Exception, e:
            html = "Error: %s" % self.iceContext.textToHtml(str(e))
            self.d["message"] = html
        return self.__transformToTemplate()
    
    def processResults(self, indexer, foundIds):
        results = []
        for id in foundIds:
            try:
                path = indexer.getPathForId(id)
                item = self.iceContext.rep.getItem(path)
                if item.guid!=id:
                    print "  document's id has changed and is now invalid!"
                    print "    removing from index!"
                    indexer.deleteIndex(id)
                    continue
                if item.exists==False:
                    print " search found item does not exist! path='%s'" % path
                    print "    removing from index!"
                    indexer.deleteIndex(id)
                    continue
                if item.hasHtml:
                    path = self.__fs.splitExt(path)[0] + ".htm"
                title = item.getMeta("title")
                #if title.strip()=="": title = "[Untitled path='%s']" % path
                try:
                    if title is not None:
                        title = title.decode("utf-8")
                    else:
                        title = "[Untitled]"
                except:
                    msg = "[Can not display title because of an encoding error!]"
                    print "%s\n title='%s' path='%s'\n" % (msg, title, path)
                    title = msg
                    
                desc = item.description
                if desc == '':
                    desc = " "
                
                path = self.iceContext.textToHtml(path, includeSpaces=False)
                title = self.iceContext.textToHtml(title)
                desc = self.iceContext.textToHtml(desc, includeSpaces=False)
                
                results.append([path, title, desc])
                
            except Exception, e:
                print "Exception: %s" % str(e)
                pass
        return results

    
    def __transformToTemplate(self):
        file = self.__fs.join (self.myPath, self.searchTemplateName)
        
        htmlTemplate = self.HtmlTemplate(templateFile=file)
        self.d["query"] = self.__query
        self.d["enableTags"] = self.iceContext.settings.get("enableTags", False)
        
        self.d["fileName"] = self.fileName
        if self.searchPath=="/":
            self.d["root"] = "checked='checked'"
            self.d["package"] = ""
        else:
            self.d["root"] = ""
            self.d["package"] = "checked='checked'"
        self.d["packagePath"] = self.packagePath
        self.d["searchPath"] = self.searchPath
        
        html = htmlTemplate.transform(self.d, allowMissing=True)        
        return html


