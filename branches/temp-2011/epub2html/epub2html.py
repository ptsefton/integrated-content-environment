# Copyright (C) 2011 Peter Malcolm Sefton
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import zipfile
from xml.etree import ElementTree as ET
import json
import shutil
import os
import uuid
import sys

class Toc(object):
        def __init__(self, tocFile, contentDir):
                def buildToc(navNode, firstTime=False):
                    navNodes = navNode.findall("./{http://www.daisy.org/z3986/2005/ncx/}navPoint")
		    #Builds a data structure as per paquete - not used ATM but could be added later
	            #http://demo.adfi.usq.edu.au/paquete/demo/#module02.htm
		    tocEntries = []
                    if navNodes:
			if firstTime:
				self.__html += "<ol id='toc'>"
                        else:
				self.__html += "<ol>"
                        for nav in navNodes:
			    link = nav.find("./{http://www.daisy.org/z3986/2005/ncx/}content").get("src")
			    #Make path relative to dir where content.opf is
			    link = os.path.relpath(os.path.join(contentDir, link))
			    text = nav.find("./{http://www.daisy.org/z3986/2005/ncx/}navLabel/{http://www.daisy.org/z3986/2005/ncx/}text").text
			    self.__html += "<li><a href='%s' target='content-frame'>%s</a>" % (link, text)
			    tocEntry = dict();
			    tocEntry["visible"] = True
			    tocEntry["relPath"] = link
			    tocEntry["title"] = text
			    tocEntry["children"] = buildToc(nav)
			    tocEntries.append(tocEntry)
			    self.__html += "</li>"
		        self.__html += "</ol>"
		    return tocEntries
                toctree = ET.parse(tocFile)
		self.__html = ""
                #For node
                navMap = toctree.find("//{http://www.daisy.org/z3986/2005/ncx/}navMap")
		
               
                
                #Build JSON
                self.__json =  dict()
		self.__json["toc"] = buildToc(navMap, True)
		
            
        def getHtml(self):
            return self.__html
	def getJson(self):
	    return self.__json
	def getJsonString(self):
	    return json.dumps(self.__json)

class Epub2Html(object):
        

        #TODO - Die gracefully if not an EPUB

        #TODO - Check for dangerous file paths

        #TODO Add config to include the Javascript or not (defaults to including ATM)


        #TODO optional HTML templates
        def __init__(self, filename, outputFilename = None, explode=False):
		def addToManifest(path):
			#Add the new files to the epub manifest
			path = os.path.relpath(path, self.__contentDir)
			(f, ext) = os.path.splitext(path)
			mime = self.__mimeTypes[ext.lower()]
			#TODO use namespace prefix
			item = ET.Element("item", {"id":str(uuid.uuid1()), "href":path, "media-type":mime})   
			
			self.__contString = self.__contString.replace("</manifest>","%s\n</manifest>" % ET.tostring(item)) #HACK!
		        self.__manifest.append(item) # TODO can't serialize senisbly


		
		
                self.__mimeTypes = dict(); #only need a few
		self.__mimeTypes[".html"] = "application/xhtml+xml"
		self.__mimeTypes[".css"] = "text/css"
		self.__mimeTypes[".js"] = "application/javascript"
		(filePart,ext) = os.path.splitext(filename)
		if outputFilename == None:
			outputFilename = "%s-html.%s" % (filePart, ext)
		if outputFilename != filename:
			shutil.copyfile(filename, outputFilename)

                self.zip = zipfile.ZipFile(outputFilename, 'a')
		containerFile = self.zip.open("META-INF/container.xml")
		containerTree = ET.parse(containerFile)
		roots = containerTree.findall("//{urn:oasis:names:tc:opendocument:xmlns:container}rootfile")
                contentPath = ""
       
		for root in roots:
			if root.get("media-type","") ==  "application/oebps-package+xml":
				contentPath = root.get("full-path")
				break

		(self.__contentDir,contentFilename) = os.path.split(contentPath) 
		contFile = self.zip.open(contentPath)
	        self.__contString = self.zip.read(contentPath)
		#Load in container
		contTree = ET.parse(contFile)
		items = contTree.findall("//{http://www.idpf.org/2007/opf}item")

		for item in items:
			if item.get("media-type", "")=="application/x-dtbncx+xml":
				tocPath = os.path.relpath(os.path.join(self.__contentDir, item.get("href", "")))
				break
		self.__manifest = contTree.find("//{http://www.idpf.org/2007/opf}manifest")

                tocFile = self.zip.open(tocPath)
                self.toc = Toc(tocFile, self.__contentDir)
                title = "TODO: title"
                #inject new files - HTML & JSON
		template = file("templates/index.html").read() % (self.toc.getHtml(), self.toc.getJson()["toc"][0]["relPath"])
		
                

		#TODO test for existing index.html
		self.zip.writestr("index.html", template)
		addToManifest("index.html")
		
		#Get files from epubjs project
		filesToAdd = ["js/jquery-1.3.2.min.js",\
				"js/jquery-ui-1.7.1.custom.min.js","js/mousewheel.js",\
				"js/epubjs.js", "css/epubjs.css","css/ui-lightness/jquery-ui-1.7.1.custom.css"]
		
		for f in filesToAdd:
			self.zip.write("epubjs/%s" % f, f)
			addToManifest(f)

		#Temporary - use customized epubjs
		self.zip.write("templates/epubjs-mods.js", "js/epubjs.js")

		#TODO: Fix this string-based hack
		self.zip.writestr(contentPath, self.__contString)
	       
                #Close
		if explode:
			self.zip.extractall(filePart)


        	self.zip.close()

def usage():
	print "Usage: epub2html.py inputfile (outputfile)"

def main(argv):
    try:                         
    	filename = argv[0]

    except:
	usage()

    Epub2Html(filename)               



if __name__ == "__main__":
    main(sys.argv[1:])
		
        
