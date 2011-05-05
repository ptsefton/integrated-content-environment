#
#    Copyright (C) 2006  Distance and e-Learning Centre, 
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


class FileBrowser(object):
    TEMPLATE_FILENAME = "fileBrowser.tmpl"
    TemplateFile = None

    def __init__(self, iceContext):
        self.iceContext = iceContext
        #self.TemplateFile =

    def render(self, fileBrowserPath, display=True):
        htmlTemplate = self.iceContext.HtmlTemplate(
                                templateFile=self.TemplateFile, allowMissing=True)
        parentPath = self.iceContext.fs.split(fileBrowserPath.rstrip("/"))[0]
        fileBrowserPathParts = []
        path = "/"
        for part in [p for p in fileBrowserPath.split("/") if p!=""]:
            path += part + "/"
            fileBrowserPathParts.append( (part, path) )
        folders, files = self.__getFoldersAndFiles(fileBrowserPath)
        dataDict = {
                    "display":display,
                    "fileBrowserPath":fileBrowserPath,
                    "parentPath":parentPath,
                    "fileBrowserPathParts":fileBrowserPathParts,
                    "folders":folders,
                    "files":files,
                   }

        html = htmlTemplate.transform(dataDict)
        return html


    def __getFoldersAndFiles(self, path):
        folders, files = [], []
        if path is not None:
            if not path.endswith("/"):
                path += "/"
            item = self.iceContext.rep.getItem(path)
            listItems = item.listItems()
            files = [i for i in listItems if i.isFile and i.name[0] != "~"]
            # if folder and not hidden
            folders = [i for i in listItems if i.isDirectory and not i.isHidden ]
            exts = [".doc", ".docx", ".odt"] # Note: not including '.book.odt'
            files = [i for i in files if i.ext in exts]
            folders.sort()
            files.sort()
            folders = [(i.relPath, i.name) for i in folders]
            files = [(i.relPath, i.name) for i in files]
        return folders, files




    
    




