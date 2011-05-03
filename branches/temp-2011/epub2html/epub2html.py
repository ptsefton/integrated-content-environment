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
import urllib 
import subprocess

class Toc(object):
        def __init__(self, tocFile, contentDir):
                def buildToc(navNode, firstTime=False):
                    navNodes = navNode.findall("./{http://www.daisy.org/z3986/2005/ncx/}navPoint")
		    #Builds a data structure as per paquete - not used ATM but could be added later
	            #http://demo.adfi.usq.edu.au/paquete/demo/#module02.htm
		    tocEntries = []
                    if navNodes:
			if firstTime:
				self.__html += "<ul id='toc'>"
                        else:
				self.__html += "<ul>"
                        for nav in navNodes:
			    link =  nav.find("./{http://www.daisy.org/z3986/2005/ncx/}content").get("src")
	 	            #link = "./" + urllib.pathname2url(link)
                            
			    #Make path relative to dir where content.opf is
			    link = os.path.relpath(os.path.join(contentDir, link))
			    text = nav.find("./{http://www.daisy.org/z3986/2005/ncx/}navLabel/{http://www.daisy.org/z3986/2005/ncx/}text").text
			    text = text.encode("utf-8")
			    self.__html += "<li><a href='%s' target='content-frame'>%s</a>" % (link, text)
			    tocEntry = dict();
			    #tocEntry["visible"] = True
			    tocEntry["src"] = link
			    rawLink = link.partition("#")[0]
			    print rawLink
			    #if (len(self.__components) > 0) and not (self.__components[-1] == rawLink):
			    self.__components.append(rawLink)
			    tocEntry["title"] = text
			    tocEntry["children"] = buildToc(nav)
			    tocEntries.append(tocEntry)
			    self.__html += "</li>"
		        self.__html += "</ul>"
		    return tocEntries
		self.componentsPaths = {}
		self.__components = []
                toctree = ET.parse(tocFile)
		self.__html = ""
                #For node
                navMap = toctree.find("//{http://www.daisy.org/z3986/2005/ncx/}navMap")
		
               
                
                #Build JSON
                self.__json =  dict()
		self.__json = buildToc(navMap, True)
		
            
        def getHtml(self):
            return self.__html
	def getJson(self):
	    return self.__json
	def getJsonString(self):
	    return json.dumps(self.__json)

	def getComponents(self):
	    return json.dumps(self.__components)

class Epub2Html(object):
 

        #TODO Add config to include the Javascript for Monocle and others or not (defaults to including Monocle ATM)
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
			#self.__manifest.append(item) # TODO can't serialize sensisbly using ElementTree

		self.tidy = False #TODO make this an option but ATM is causing encoding probs
		self.__data = {}

		self.__mimeTypes = dict(); #only need a few
		self.__mimeTypes[".html"] = "application/xhtml+xml"
		self.__mimeTypes[".css"] = "text/css"
		self.__mimeTypes[".js"] = "application/javascript"
		(filePart,ext) = os.path.splitext(filename)
		if outputFilename == None:
			outputFilename = "%s-html%s" % (filePart, ext)
		outputDirname = os.path.splitext(outputFilename)[0]
		print "Opening zip " + filename
		self.zip = zipfile.ZipFile(filename, 'a')

		#self.zip.writestr("/test","danger!")

		#Test zip for naughty files
		for f in self.zip.namelist():
			if f.startswith("/") or f.startswith("."):
				print "ABORTING: This epub file is potentially dangerous, it has this file in it %s" % f
				sys.exit(1)

		
		
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
		htmlItems = []
		for item in items:
			mimeType = item.get("media-type", "")
			
			if mimeType=="application/x-dtbncx+xml":
				tocPath = os.path.relpath(os.path.join(self.__contentDir, item.get("href", "")))
			elif mimeType=="application/xhtml+xml":
				htmlItems.append(os.path.relpath(os.path.join(self.__contentDir, item.get("href", ""))))
		#print htmlItems
		self.__manifest = contTree.find("//{http://www.idpf.org/2007/opf}manifest")

		titleNode = contTree.find("//{http://purl.org/dc/elements/1.1/}title")
		if titleNode != None:
			title = titleNode.text
		else:
			title = "Untitled"
		authorNode = contTree.find("//{http://purl.org/dc/elements/1.1/}creator")
		if authorNode != None:
			author = authorNode.text
		else:
			author = "Unknown"
		tocFile = self.zip.open(tocPath)
		self.toc = Toc(tocFile, self.__contentDir)

		#TODO - make monocle files optional - 
		#adding to zip is easier than messing about with real files
		filesToAdd = []
		
		

		for f in filesToAdd:
			self.zip.write(f)
			addToManifest(f)

		self.zip.extractall(outputDirname)
		#Needs more work to get going
		#monocle = file("templates/monocle.html").read() % {"spine-data": self.toc.getComponents(),\
		#						   "contents-data":  self.toc.getJsonString(), \
		#						   "title": title, \
		#						   "author": author}

		index = file("templates/index.html").read() % {  "toc-html" : self.toc.getHtml(),\
								   "first-page" : self.toc.getJson()[0]["src"], \
								   "title": title, \
								   "author": author}

		#TODO test for existing index.html
		file(os.path.join(outputDirname,"index.html"), "w").write(index)
		addToManifest("index.html")


		#TODO test for existing index.html
		#file(os.path.join(outputDirname,"monocle.html"), "w").write(monocle)
		#addToManifest("monocle.html")

		self.zip.close()

		#TODO: Fix this string-based hack
		#Write as file
		file(os.path.join(outputDirname, contentPath),"w").write(self.__contString)

		

		#Code adapted from epubtools http://code.google.com/p/epub-tools/source/browse/trunk/epubtools/epubtools/epubtools/__init__.py
		
		

		# Open a new zipfile for writing
		epub = zipfile.ZipFile(outputFilename, 'w')
		mimefile = "mimetype"

		# Add the mimetype file first and set it to be uncompressed
		epub.write(os.path.join(outputDirname, mimefile), mimefile,  compress_type=zipfile.ZIP_STORED)
		
		#Tidy any HTML if necessary
		if self.tidy:
			for htmlFile in htmlItems:
				retcode = subprocess.call(["tidy", "-asxml", "-m", '-n', os.path.join(outputDirname,htmlFile)])
		
		# For the remaining paths in the EPUB, add all of their files using normal ZIP compression
		for dirpath, dirnames, filenames in os.walk(outputDirname, topdown=False):
			for name in filenames:
			    if name == mimefile:
				continue
			    f = os.path.join(dirpath, name)
                            #print "adding %s" % f
			    epub.write(f, os.path.relpath(f,outputDirname), compress_type=zipfile.ZIP_DEFLATED)
		

		epub.close()
		
		


        	

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
		
        
