#!/usr/bin/env python
#    Copyright (C) 2007  Distance and e-Learning Centre,
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

import sys
import os, time

from file_system import *
import xml_util
import libxml2

updateFiles = "False"
oxtFile = "ooo/ice-toolbar.oxt"             # zip file
oxtExtract = "ooo/ice-toolbar"              # zip extracted

toolbarTextFiles = {"macros/toolbar.txt":"IceLibrary/Toolbar.xba", \
                    "macros/XRef.txt":"IceLibrary/XRef.xba", \
                    "macros/stylecreator.txt":"IceLibrary/StyleCreator.xba", \
                    "macros/publisher.txt":"IceLibrary/Publisher.xba",\
                    "macros/hint.txt":"IceLibrary/Hint.xba",\
                    "macros/StyleUnitTest.txt":"IceLibrary/StyleUnitTest.xba",\
                    "macros/styletestcommon.txt":"IceLibrary/styleTestCommon.xba",\
                    "macros/repair.txt":"IceLibrary/Repair.xba",\
                    "macros/common.txt":"IceLibrary/common.xba",\
                    "macros/imgLinks.txt":"IceLibrary/imgLinks.xba",\
                    "macros/styletestdoccreator.txt":"IceLibrary/styleTestDocCCreator.xba"}
                    #Remove these for now as they are not working
                    #"macros/stylechecker.txt":"IceLibrary/StyleChecker.xba",\
                    #"macros/styletest.txt":"IceLibrary/StyleTest.xba"
                    
xbaXmlWrapper = """<!DOCTYPE script:module PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "module.dtd">
<script:module xmlns:script="http://openoffice.org/2000/script" script:name="Toolbar" script:language="StarBasic"/>
"""
expectedFiles = ["Addons.xcu", \
                 "Paths.xcu", \
                 "IceLibrary/dialog.xlb", \
                 "IceLibrary/script.xlb", \
                 "IceLibrary/common.xba", \
                 "IceLibrary/Hint.xba",\
                 "IceLibrary/imgLinks.xba",\
                 "IceLibrary/Module1.xba", \
                 "IceLibrary/Publisher.xba", \
                 "IceLibrary/Repair.xba", \
                 "IceLibrary/StyleCreator.xba", \
                 "IceLibrary/styleTestCommon.xba",\
                 "IceLibrary/styleTestDocCreator.xba",\
                 "IceLibrary/StyleUnitTest.xba",\
                 "IceLibrary/Toolbar.xba", \
                 "IceLibrary/XRef.xba", \
                 "IceLibrary/dlgConvert.xdl", \
                 "IceLibrary/dlgCrossRef.xdl", \
                 "IceLibrary/dlgHint.xdl",\
                 "IceLibrary/dlgListType.xdl", \
                 "IceLibrary/dlgPublish.xdl", \
                 "IceLibrary/dlgShortcuts.xdl", \
                 "META-INF/manifest.xml", \
                 "Office/UI/BaseWindowState.xcu", \
                 "Office/UI/BasicIDEWindowState.xcu", \
                 "Office/UI/CalcWindowState.xcu", \
                 "Office/UI/DrawWindowState.xcu", \
                 "Office/UI/ImpressWindowState.xcu", \
                 "Office/UI/MathWindowState.xcu", \
                 "Office/UI/StartModuleWindowState.xcu", \
                 "Office/UI/WriterWindowState.xcu", \
                 "pkg-desc/pkg-description.txt", \
                 "icons/Promote_16.png", \
                 "icons/Demote_16.png", \
                 "icons/Heading_16.png", \
                 "icons/P_Left_16.png", \
                 "icons/P_Centered_16.png", \
                 "icons/P_Right_16.png", \
                 "icons/Bold_16.png", \
                 "icons/Italics_16.png", \
                 "icons/Title_16.png", \
                 "icons/Number_16.png", \
                 "icons/Bullet_16.png", \
                 "icons/Sub_16.png", \
                 "icons/Sup_16.png", \
                 "icons/Block_Quote_16.png", \
                 "icons/Clean_Up_16.png"]
#remove these files from adding
#"IceLibrary/styleTest.xba",\
#"IceLibrary/StyleChecker.xba",\

class ExtensionBuilder(object):
    def __init__(self, path="."):
        self.__fs = FileSystem(path)

    def run(self, oxtFile):
        for file in expectedFiles:
            file = oxtExtract + "/" + file
            if not self.__fs.exists(file):
                print "Error: %s was not found." % file

        if not self.__fs.exists(oxtFile):
            print "Warning: %s not found. created instead." % oxtFile
        self.__fs.zip(oxtFile, oxtExtract)

        for toolbarTextFile, toolbarXbaFile in toolbarTextFiles.items():
            toolbarText = self.__fs.readFile(toolbarTextFile)
            if toolbarText is None:
                print "File '%s' not found!" % self.__fs.absolutePath(toolbarTextFile)
                return
            #check if there weird char in the content. If there is fixed it otherwise it will break the code in the toolbar installer.
            try:
                toolbarText = toolbarText.encode("utf-8")
            except Exception,e:
                print "fileName : ", toolbarTextFile
                print "error in string: ",str(e)
                newText = ""
                t = toolbarText
                for c in t:
                    newC = c
                    if ord(c)>127:
                        print "error char : ",c
                        newC = "&#%s;" % ord(c)
                    newText += newC
                    toolbarText = newText
            xml = xml_util.xml(xbaXmlWrapper)
            xml.getRootNode().setContent(toolbarText)
            xmlStr = str(xml)
            xml.close()
            self.__fs.addToZipFile(oxtFile, toolbarXbaFile, xmlStr)

    def setVersionInfo(self):
        global oxtFile
        global updateFiles
        argv = sys.argv
        toolbarName = "ICE Style Toolbar (dev)"
        version = "test"
        releaseType = "dev"
        descriptionFile = "ooo/ice-toolbar/description.xml"
        updateFile = "ooo/ice.update.xml"           # update info file
        updateDownloadUrl = "http://ice.usq.edu.au/svn/ice/trunk/templates/ice/ooo/ice-toolbar.oxt"    # set in ice.update.xml
        updateInformationUrl = "http://ice.usq.edu.au/svn/ice/trunk/templates/ice/ooo/ice.update.xml" # set in description.xml

        helpText = "help: extensionBuilder.py version type \n"
        helpText = helpText + "version - number (e.g. 1.0.0) \n"
        helpText = helpText + "type - 'stable' or 'dev' (default) \n"
        helpText = helpText + "       'stable' updates ../../../downloads/latest/templates/ice-toolbar.oxt \n"
        helpText = helpText + "       'dev' updates %s\n" % oxtFile

        helpRunText = "Error: Try running from trunk/templates/ice not %s" % FileSystem('.')
        helpRunTextStable = "Error: Unable to update stable version, make sure you have checked out trunk/templates & downloads/latest/templates directory into the same parent directory (i.e. as per the ICE svn structure)."

        try:
            if argv[1] == "--help":
                print "%s" % (helpText)
                exit
            else:
                updateFiles = "True"
                version = argv[1]
                try:
		           releaseType = argv[2]
		           if releaseType != "stable":
		               releaseType = "dev"
                except:
                     releaseType = "dev"
                     pass
        except:
           print "%s" % (helpText)
           exit

        if updateFiles == "True":
            # Release location for download depends on releaseType
            if releaseType == "stable":
                updateDownloadUrl = "http://ice.usq.edu.au/svn/ice/downloads/latest/templates/ice-toolbar.oxt"    # set in ice.update.xml
                updateInformationUrl = "http://ice.usq.edu.au/svn/ice/downloads/latest/templates/ice.update.xml" # set in description.xml
                oxtFile = "../../../downloads/latest/templates/ice-toolbar.oxt"
                updateFile = "../../../downloads/latest/templates/ice.update.xml"
                toolbarName = "ICE Style Toolbar"
            print "Build info: Type '%s', Version '%s'" % (releaseType, version)
            try:
                # Update values in description.xml
                doc = libxml2.parseFile(descriptionFile)
                result = doc.xpathEval('//*')
                for node in result:
                    nodeName = node.name
                    if nodeName == "version":
                        node.setProp('value', version)
                    if nodeName == "update-information":
                        newUpdateNode = libxml2.newNode('update-information')
                        newNode = libxml2.newNode('src')
                        newNode.setProp('xlink:href', updateInformationUrl)
                        newUpdateNode.addChild(newNode)
                        node.replaceNode(newUpdateNode)
                    if nodeName == "display-name":
                        newNameNode = libxml2.newNode('display-name')
                        newNode = libxml2.newNode('name')
                        newNode.addContent(toolbarName)
                        newNameNode.addChild(newNode)
                        node.replaceNode(newNameNode)

                f = open(descriptionFile,'w')
                doc.saveTo(f)
                f.close
                doc.freeDoc()
                print "Modified: %s" % descriptionFile
            except:
                pass
            	print helpRunText
            	updateFiles = "False"

            try:
                # Update values in ice.update.xml
                doc = libxml2.parseFile(updateFile)
                result = doc.xpathEval('//*')
                for node in result:
                    nodeName = node.name
                    if nodeName == "version":
                        node.setProp('value', version)
                    if nodeName == "update-information":
                        newUpdateNode = libxml2.newNode('update-information')
                        newNode = libxml2.newNode('src')
                        newNode.setProp('xlink:href', updateDownloadUrl)
                        newUpdateNode.addChild(newNode)
                        node.replaceNode(newUpdateNode)
                f = open(updateFile,'w')
                doc.saveTo(f)
                f.close
                doc.freeDoc()
                print "Modified: %s" % updateFile
            except:
                pass
                if releaseType == 'stable':
            	    print helpRunTextStable
            	updateFiles = "False"


def main(argv=None):
    if argv is None:
        argv = sys.argv
    extBuilder = ExtensionBuilder('.')
    extBuilder.setVersionInfo()
    if updateFiles == "True":
        print "Updating extension: %s" % oxtFile
        extBuilder.run(oxtFile)

if __name__ == "__main__":
    sys.exit(main())