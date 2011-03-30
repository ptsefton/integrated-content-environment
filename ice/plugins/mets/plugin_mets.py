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


try:
    from xml.etree import ElementTree as ElementTree
except ImportError:
    try:
        import cElementTree as ElementTree
    except ImportError:
        from elementtree import ElementTree

from datetime import datetime
from mets_helper import *
import mets_helper
from hashlib import md5


pluginName = "ice.mets"
pluginDesc = ""
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = None
    pluginClass = Mets
    Mets.Helper = mets_helper
    pluginInitialized = True
    return pluginFunc



class Mets(object):
    def __init__(self, iceContext, objId, profile=None, id=None, label=None, type=None):
        self.iceContext = iceContext
        self.profile = profile
        self.objId = objId
        self.id = id
        self.label = label
        self.type = type
        
        now = datetime.now()
        self.metsHdr = MetsHeader(now, now)
        
        self.agent = []
        self.dmdSec = []
        self.amdSec = []
        self.fileSec = None
        self.structMap = None
    
    def setCreateDate(self, createDate):
        self.metsHdr.setCreateDate(createDate)
    
    def setLastModDate(self, lastModDate):
        self.metsHdr.setLastModDate(lastModDate)
    
    def addAgent(self, role, type, name):
        agent = MetsAgent(role, type, name)
        self.agent.append(agent)
        return agent
    
    def addDisseminator(self, type, name):
        return self.addAgent(MetsAgent.ROLE_DISSEMINATOR, type, name)
    
    def addCreator(self, name):
        return self.addAgent(MetsAgent.ROLE_CREATOR, MetsAgent.TYPE_OTHER, name)
    
    def addDmdSecWrap(self, id, mdType, xmlData):
        dmdSec = MetsDescMetadataSec(id)
        mdWrap = MetsMetadataWrap(mdType)
        mdWrap.setXmlData(xmlData)
        dmdSec.setMetadata(mdWrap)
        self.dmdSec.append(dmdSec)
        return dmdSec
    
    def addDmdSecRef(self, id, locType, mdType, href):
        dmdSec = MetsDescMetadataSec(id)
        mdRef = MetsMetadataRef(locType, mdType, href)
        dmdSec.setMetadata(mdRef)
        self.dmdSec.append(dmdSec)
        return dmdSec
    
    def addFileGrp(self, use):
        if self.fileSec == None:
            self.fileSec = MetsFileSec()
        fileGrp = MetsFileGroup(use = use)
        self.fileSec.addFileGroup(fileGrp)
        return fileGrp
    
    def addFile(self, fileGrp, filePath, href, dmdId = None, admId = None,
                wrapped = False):
        path, name, ext = self.iceContext.fs.splitPathFileExt(filePath)
        fileSize = os.stat(filePath).st_size
        f = open(filePath)
        data = f.read()
        f.close()
        checksum = md5(data).hexdigest()
        
        id = href.replace('/', '.').replace(' ', '.')
        file = MetsFile(id, checksum, "MD5", self.iceContext.MimeTypes[ext.lower()], str(fileSize))
        fileGrp.addFile(file)
        if wrapped:
            fContent = file.getFContent()
            fContent.setBinData(data)
        else:
            file.setFLocat("URL", href)
        return file
    
    def addDiv(self, type, dmdId = None, parentDiv = None):
        if self.structMap == None:
            self.structMap = MetsStructMap()
        if parentDiv == None:
            parentDiv = self.structMap
        div = MetsDiv(type, dmdId)
        parentDiv.addDiv(div)
        return div
    
    def addFptr(self, div, fileId):
        fptr = div.addFPtr(fileId)
        return fptr
    
    def getElement(self):
        mets = CreateMetsElement("mets")
        SetMetsAttribute(mets, "PROFILE", self.profile)
        SetMetsAttribute(mets, "OBJID", self.objId)
        SetMetsAttribute(mets, "TYPE", self.type)
        SetMetsAttribute(mets, "ID", self.id)
        SetMetsAttribute(mets, "LABEL", self.label)
        
        metsHdr = self.metsHdr.getElement()
        mets.append(metsHdr)
        
        for agent in self.agent:
            metsHdr.append(agent.getElement())
        
        for dmdSec in self.dmdSec:
            mets.append(dmdSec.getElement())
        
        mets.append(self.fileSec.getElement())
        mets.append(self.structMap.getElement())
        
        return mets
    
    def getXml(self):
        return ElementTree.tostring(self.getElement())
    

