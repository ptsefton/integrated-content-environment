#
#    Copyright (C) 2005  Distance and e-Learning Centre, 
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


""" Module to read configuration parameters from atomConfig.xml """
from element import *

pluginName = "ice.atom.config"
pluginDesc = "Atom Configuration"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method

def pluginInit(iceContext, **kwargs):
    """ plugin declaration method
    """
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = None
    pluginClass = AtomConfig
    pluginInitialized = True
    return pluginFunc

class AtomConfig():
    atomSettings = None
    
    def __init__(self, iceContext, configFile=None):
        self.__system = iceContext.system
        self.__fs = iceContext.fs
        self.__xmlUtils = iceContext.xmlUtils
        if configFile is None:
            configFile = self.__getConfigFileLocation()
        self.configFile = configFile
        self.__settings = {}
        self.__load()

    @property
    def settings(self):
        return self.__settings
    
    def __load(self):
        xml = None
        configFile = self.configFile
        #Should change to self.__fs.isFile(config)
        if (not self.__fs.isFile(configFile)) and (not configFile.startswith("<")):
            print "Atom Config xml file '%s' not found!" % configFile
        else:
            try:
                xml = self.__xmlUtils.xml(configFile)
                rootNode = xml.getRootNode()
                #atompubs
                nodes = rootNode.getNodes("//user")
                if nodes is not None:
                    for node in nodes:
                        username,atoms =self.__getAtomPubData(node)
                        self.__settings[username] = [username,atoms]
                xml.close()
            except Exception,e :
                print "Error in loading Atom Config xml file '%s" % configFile
                  
        
        
        
    
    
    def saveSettings(self, url,username,loginUsername,authType,category):
        configFile = self.configFile
        try:
            xml = self.__xmlUtils.xml(configFile)
        except Exception,e :
            print "Error in saving Atom Config xml file '%s" % configFile    
#            print str(e)
            print "Creating a new file....."
            xmlStr = "<atompubs></atompubs>"
            xml = self.__xmlUtils.xml(xmlStr)
            
            xml.saveFile(configFile)
        rootNode = xml.getRootNode()
        #checking existing data
        #todo cannot get the node. 
        # try get it and save to xml
        userNode = rootNode.getNode("//user[@name = '%s']" % username)
        if userNode is not None:
        #user record exists
        #check this url exist
            atomNode = userNode.getNode("//atompub[@url= '%s']" %url)
            if atomNode is None:
                #new url 
                print "Adding new Atom URL ..."
                atomNode = xml.createElement("atompub",name="",url=url)
                loginNode = xml.createElement("login",name=loginUsername,type=authType)
                atomNode.addChild(loginNode)
                categoryNode = xml.createElement("category",name = category,term=category)
                atomNode.addChild(categoryNode)
                userNode.addChild(atomNode)
            else:
                #url exists so check category
                categoryNode = atomNode.getNode("//category[@name = '%s']" % category)
                if categoryNode is None:
                    print "Adding new category ..."
                    #new category
                    categoryNode = xml.createElement("category",name = category,term=category)
                    atomNode.addChild(categoryNode)
        else: 
            #no user record
            print "Creating new user record...."
            userNode = xml.createElement("user",name = username)
            atomNode = xml.createElement("atompub",name="",url=url)
                
            loginNode = xml.createElement("login",name=loginUsername,type=authType)
            commentNode = xml.createComment(" ")
            loginNode.addChild(commentNode)
            atomNode.addChild(loginNode)
                
            categoryNode = xml.createElement("category",name = category,term=category)
            commentNode = xml.createComment(" ")
            categoryNode.addChild(commentNode)
            atomNode.addChild(categoryNode)
                
            userNode.addChild(atomNode)           
            rootNode.addChild(userNode) 
                
        print "saving the data...."
            
        xml.saveFile(configFile)
        xml.close()
            
        #reload the value
        self.__load()
                

            
            
            
           
         
       
        
        
        
    def __getAtomPubData(self,atomNode):
        username = atomNode.getAttribute("name")
        nodes = atomNode.getNodes("//user[@name = '%s']/atompub" % username)
        atoms = dict()
        if nodes is not None:
            for node in nodes:
                url = node.getAttribute("url")
                loginUsername = node.getNode("login").getAttribute("name")
                loginType =node.getNode("login").getAttribute("type")
                catNodes = node.getNodes("category")
                categories = dict()
                for catNode in catNodes:
                    catName = catNode.getAttribute("name")
                    catTerm = catNode.getAttribute("term")
                    categories[catName] = [catName,catTerm]
                atoms[url] = [url,loginUsername,loginType, categories]
        return username, atoms
    
    def __getConfigFileLocation(self):
        configFilename = "atomConfig.xml"
        if self.__fs.isFile(configFilename):
            return self.__fs.absPath(configFilename)
        path = self.__system.getOsConfigPath("ice", create=True)
        fullPath = self.__fs.join(path, configFilename)
        return fullPath