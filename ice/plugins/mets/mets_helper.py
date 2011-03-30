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


import sys
sys.path.append("../ice-utils")

import os
from base64 import b64encode
from datetime import datetime

try:
    from xml.etree import ElementTree as ElementTree
except ImportError:
    try:
        import cElementTree as ElementTree
    except ImportError:
        from elementtree import ElementTree


METS_NS = "http://www.loc.gov/METS/"
MODS_NS = "http://www.loc.gov/mods/v3"
PREMIS_NS = "http://www.loc.gov/standards/premis/v1"
XLINK_NS = "http://www.w3.org/1999/xlink"
XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"


try:
    ElementTree._namespace_map[METS_NS] = "mets"
    ElementTree._namespace_map[MODS_NS] = "mods"
    ElementTree._namespace_map[PREMIS_NS] = "premis"
    ElementTree._namespace_map[XLINK_NS] = "xlink"
    ElementTree._namespace_map[XSI_NS] = "xsi"
except:
    pass

METS_NLA_PROFILE = "Australian METS Profile 1.0"


def CreateMetsElement(tag, text = None):
    elem = ElementTree.Element("{%s}%s" % (METS_NS, tag))
    if text != None:
        elem.text = text
    return elem


def CreateMetsSubElement(parent, tag, text = None):
    subElem = ElementTree.SubElement(parent, "{%s}%s" % (METS_NS, tag))
    if text != None:
        subElem.text = text
    return subElem


def SetMetsAttribute(elem, name, value):
    if value != None:
        elem.set(name, value)


def SetXLinkAttribute(elem, name, value):
    if value != None:
        elem.set("{%s}%s" % (XLINK_NS, name), value)



class MetsHeader(object):    
    def __init__(self, createDate, lastModDate):
        self.setCreateDate(createDate)
        self.setLastModDate(lastModDate)
    
    
    def setCreateDate(self, createDate):
        if type(createDate) == type(datetime.now()):
            self.createDate = createDate.isoformat() + 'Z'
        else:
            self.createDate = str(createDate)
    
    
    def setLastModDate(self, lastModDate):
        if type(lastModDate) == type(datetime.now()):
            self.lastModDate = lastModDate.isoformat() + 'Z'
        else:
            self.lastModDate = str(lastModDate)
    
    
    def getElement(self):
        metsHdr = CreateMetsElement("metsHdr")
        SetMetsAttribute(metsHdr, "CREATEDATE", self.createDate)
        SetMetsAttribute(metsHdr, "LASTMODDATE", self.lastModDate)
        return metsHdr



class MetsAgent(object):
    ROLE_DISSEMINATOR = "DISSEMINATOR"
    ROLE_CREATOR = "CREATOR"
    TYPE_ORGANIZATION = "ORGANIZATION"
    TYPE_INDIVIDUAL = "INDIVIDUAL"
    TYPE_OTHER = "OTHER"
    
    def __init__(self, role, type, name, id = None, otherRole = None, otherType = None):
        self.role = role
        self.type = type
        self.name = name
        self.id = id
        self.otherRole = otherRole
        self.otherType = otherType
    
    
    def getElement(self):
        agent = CreateMetsElement("agent")
        SetMetsAttribute(agent, "ROLE", self.role)
        SetMetsAttribute(agent, "TYPE", self.type)
        SetMetsAttribute(agent, "ID", self.id)
        SetMetsAttribute(agent, "OTHERROLE", self.otherRole)
        SetMetsAttribute(agent, "OTHERTYPE", self.otherType)
        CreateMetsSubElement(agent, "name", self.name)
        return agent



class MetsContentWrapper(object):
    def __init__(self, tag):
        self.tag = tag
        self.binData = None
        self.xmlData = None
    
    
    def setBinData(self, binData):
        self.xmlData = None
        self.binData = b64encode(binData)
    
    
    def setXmlData(self, xmlData):
        self.binData = None
        self.xmlData = xmlData
    
    
    def getElement(self):
        wrapper = CreateMetsElement(self.tag)
        if self.binData == None and self.xmlData != None:
            xmlData = CreateMetsSubElement(wrapper, "xmlData")
            xmlData.append(self.xmlData)
        if self.binData != None and self.xmlData == None:
            CreateMetsSubElement(wrapper, "binData", self.binData)
        return wrapper


    
class MetsMetadataWrap(MetsContentWrapper):    
    def __init__(self, mdType, id = None, otherMdType = None, mimeType = None, label = None):
        MetsContentWrapper.__init__(self, "mdWrap")
        self.mdType = mdType
        self.id = id
        self.otherMdType = otherMdType
        self.mimeType = mimeType
        self.label = label
    
    
    def getElement(self):
        mdWrap = MetsContentWrapper.getElement(self)
        SetMetsAttribute(mdWrap, "MDTYPE", self.mdType)
        SetMetsAttribute(mdWrap, "ID", self.id)
        SetMetsAttribute(mdWrap, "OTHERMDTYPE", self.otherMdType)
        SetMetsAttribute(mdWrap, "MIMETYPE", self.mimeType)
        SetMetsAttribute(mdWrap, "LABEL", self.label)
        return mdWrap


    
class MetsMetadataRef(object):
    def __init__(self, locType, mdType, href, otherMdType = None, mimeType = None,
                 label = None, otherLocType = None, xptr = None):
        self.locType = locType
        self.mdType = mdType
        self.href = href
        self.otherMdType = otherMdType
        self.mimeType = mimeType
        self.label = label
        self.otherLocType = otherLocType
        self.xptr = xptr
    
    
    def getElement(self):
        mdRef = CreateMetsElement("mdRef")
        SetMetsAttribute(mdRef, "LOCTYPE", self.locType)
        SetMetsAttribute(mdRef, "MDTYPE", self.mdType)
        SetMetsAttribute(mdRef, "OTHERMDTYPE", self.otherMdType)
        SetMetsAttribute(mdRef, "MIMETYPE", self.mimeType)
        SetMetsAttribute(mdRef, "LABEL", self.label)
        SetMetsAttribute(mdRef, "OTHERLOCTYPE", self.otherLocType)
        SetMetsAttribute(mdRef, "XPTR", self.xptr)
        SetXLinkAttribute(mdRef, "href", self.href)
        return mdRef



class MetsDescMetadataSec(object):
    def __init__(self, id, admId = None, created = None, groupId = None, status = None):
        self.id = id
        self.admId = admId
        self.created = created
        self.groupId = groupId
        self.status = status
        self.metadata = None
    
    
    def setMetadata(self, metadata):
        self.metadata = metadata
    
    
    def getElement(self):
        dmdSec = CreateMetsElement("dmdSec")
        SetMetsAttribute(dmdSec, "ID", self.id)
        SetMetsAttribute(dmdSec, "ADMID", self.admId)
        SetMetsAttribute(dmdSec, "CREATED", self.created)
        SetMetsAttribute(dmdSec, "GROUPID", self.groupId)
        SetMetsAttribute(dmdSec, "STATUS", self.status)
        if self.metadata != None:
            dmdSec.append(self.metadata.getElement())
        return dmdSec


    
class MetsFileSec(object):
    def __init__(self, id = None):
        self.id = id;
        self.fileGroup = []
    
    
    def addFileGroup(self, fileGroup):
        self.fileGroup.append(fileGroup)
    
    
    def getElement(self):
        fileSec = CreateMetsElement("fileSec")
        SetMetsAttribute(fileSec, "ID", self.id)
        for fileGroup in self.fileGroup:
            fileSec.append(fileGroup.getElement())
        return fileSec


    
class MetsFileGroup(object):
    def __init__(self, id = None, admId = None, use = None, versDate = None):
        self.id = id
        self.admId = admId
        self.use = use
        self.versDate = versDate
        self.file = []
    
    
    def addFile(self, file):
        self.file.append(file)
    
    
    def getElement(self):
        fileGrp = CreateMetsElement("fileGrp")
        SetMetsAttribute(fileGrp, "ID", self.id)
        SetMetsAttribute(fileGrp, "ADMID", self.admId)
        SetMetsAttribute(fileGrp, "USE", self.use)
        SetMetsAttribute(fileGrp, "VERSDATE", self.versDate)
        for file in self.file:
            fileGrp.append(file.getElement())
        return fileGrp


    
class MetsFile(object):
    def __init__(self, id, checksum = None, checksumType = None, mimeType = None,
                 size = None, admId = None, created = None, dmdId = None, groupId = None,
                 ownerId = None, seq = None, use = None):
        self.id = id
        self.checksum = checksum
        self.checksumType = checksumType
        self.mimeType = mimeType
        self.size = size
        self.admId = admId
        self.created = created
        self.dmdId = dmdId
        self.groupId = groupId
        self.ownerId = ownerId
        self.seq = seq
        self.use = use
        self.fContent = None
        self.fLocat = None
    
    
    def getFContent(self, use = None):
        if self.fContent == None:
            self.fLocat = None
            self.fContent = MetsContentWrapper("FContent")
            self.fContent.use = use
        return self.fContent
    
    
    def setFLocat(self, locType, href, id = None, use = None, otherLocType = None):
        self.fContent = None
        self.fLocat = MetsFLocat(locType, href, id, use, otherLocType)
    
    
    def getElement(self):
        file = CreateMetsElement("file")
        SetMetsAttribute(file, "ID", self.id)
        SetMetsAttribute(file, "CHECKSUM", self.checksum)
        SetMetsAttribute(file, "CHECKSUMTYPE", self.checksumType)
        SetMetsAttribute(file, "MIMETYPE", self.mimeType)
        SetMetsAttribute(file, "SIZE", self.size)
        SetMetsAttribute(file, "ADMID", self.admId)
        SetMetsAttribute(file, "CREATED", self.created)
        SetMetsAttribute(file, "DMDID", self.dmdId)
        SetMetsAttribute(file, "GROUPID", self.groupId)
        SetMetsAttribute(file, "OWNERID", self.ownerId)
        SetMetsAttribute(file, "SEQ", self.seq)
        SetMetsAttribute(file, "USE", self.use)
        if self.fContent == None and self.fLocat != None:
            file.append(self.fLocat.getElement())
        if self.fContent != None and self.fLocat == None:
            fContent = self.fContent.getElement()
            file.append(fContent)
        return file


    
class MetsFLocat(object):
    def __init__(self, locType, href, id = None, use = None, otherLocType = None):
        self.locType = locType
        self.href = href
        self.id = id
        self.use = use
        self.otherLocType = otherLocType
    
    
    def getElement(self):
        fLocat = CreateMetsElement("FLocat")
        SetMetsAttribute(fLocat, "LOCTYPE", self.locType)
        SetMetsAttribute(fLocat, "ID", self.id)
        SetMetsAttribute(fLocat, "USE", self.use)
        SetMetsAttribute(fLocat, "OTHERLOCTYPE", self.otherLocType)
        SetXLinkAttribute(fLocat, "href", self.href)
        return fLocat


    
class MetsStructMap(object):
    def __init__(self):
        self.div = []
    
    
    def addDiv(self, div):
        self.div.append(div)
    
    
    def getElement(self):
        div = CreateMetsElement("structMap")
        for nested in self.div:
            div.append(nested.getElement())
        return div


    
class MetsDiv(object):
    def __init__(self, type = None, dmdId = None, id = None, amdId = None,
                 contentIds = None, label = None, order = None, orderLabel = None):
        self.type = type
        self.dmdId = dmdId
        self.amdId = amdId
        self.id = id
        self.contentIds = contentIds
        self.label = label
        self.order = order
        self.orderLabel = orderLabel
        self.div = []
        self.fptr = []
    
    
    def addDiv(self, div):
        self.div.append(div)
    
    
    def addFPtr(self, fileId):
        self.fptr.append(fileId)
    
    
    def getElement(self):
        div = CreateMetsElement("div")
        SetMetsAttribute(div, "TYPE", self.type)
        SetMetsAttribute(div, "ID", self.id)
        SetMetsAttribute(div, "DMDID", self.dmdId)
        SetMetsAttribute(div, "AMDID", self.amdId)
        SetMetsAttribute(div, "CONTENTIDS", self.contentIds)
        SetMetsAttribute(div, "LABEL", self.label)
        SetMetsAttribute(div, "ORDER", self.order)
        SetMetsAttribute(div, "ORDERLABEL", self.orderLabel)
        for fileId in self.fptr:
            fptr = CreateMetsElement("fptr")
            SetMetsAttribute(fptr, "FILEID", fileId)
            div.append(fptr)
        for nested in self.div:
            div.append(nested.getElement())
        return div










