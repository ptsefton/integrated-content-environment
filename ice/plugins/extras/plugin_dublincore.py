
#    Copyright (C) 2006/2008  Distance and e-Learning Centre, 
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

""" Extra plugin to produce Dublin Core metadata """

pluginName = "ice.extra.DublinCore"
pluginDesc = ""
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    """ plugin declaration method 
    @param iceContext: IceContext type
    @param kwargs: optional list of key=value pair params
    @return: handler object
    """
    global pluginFunc, pluginClass, pluginInitialized
    pluginClass = DublinCore
    pluginFunc = None
    pluginInitialized = True
    return pluginFunc

class DublinCore(object):
    """ Base class for DublinCore to produce DC metadata
    @ivar OAI_DC_NS: namespace for OAI DC
    @ivar DC_TERM_NS: namespace for DC term
    @ivar DC_NS: namespace for DC   
    """
    
    OAI_DC_NS = 'http://www.openarchives.org/OAI/2.0/oai_dc/'
    DC_TERM_NS = 'http://purl.org/dc/terms/'
    DC_NS = 'http://purl.org/dc/elements/1.1/'
    
    
    def __init__(self, iceContext):
        """ DublinCore Constructor method
        @param iceContext: Current ice context
        @type iceContext: IceContext 
        @rtype: void
        """
        self.iceContext = iceContext
        self.ET = self.iceContext.ElementTree
        
        if self.ET.VERSION < '1.3':
            self.ET._namespace_map[self.OAI_DC_NS] = 'oai_dc'
            self.ET._namespace_map[self.DC_NS] = 'dc'
            self.ET._namespace_map[self.DC_TERM_NS] = 'dcterms'
        else:
            self.ET.register_namespace('oai_dc', self.OAI_DC_NS)
            self.ET.register_namespace('dc', self.DC_NS)
            self.ET.register_namespace('dcterms', self.DC_TERM_NS)
    
    def getPackageDC(self, manifest):
        """ producing DC package
        @param manifest: Ice manifest detail
        @type manifest: ImsManifest
        @rtype: String
        @return: dublin core information produced from the manifest
        """
        if self.iceContext.output is not None:
            self.iceContext.output.write('Generating DC from package manifest\n')
        
        path = self.iceContext.fs.splitPathFileExt(self.iceContext.path)[0][1:]
        packageName = path.replace("/", ":")
        
        oaidc = self.__getBasicDC(manifest.defaultOrganization.title,
                                  identifier=packageName)
        
        # TODO add more DC elements
        dcXml = self.ET.tostring(oaidc)
        return dcXml
    
    
    def getDocumentDC(self, meta=None, item=None):
        """ generating DC from document metadata
        @param meta: metadata list to be added into DC 
        @param meta: dict
        @param item: document item used to produce DC
        @param item: IceItem
        
        @rtype: String
        @return: dublin core information produced from the manifest
        """
        if self.iceContext.output is not None:
            self.iceContext.output.write('Generating DC from document metadata\n')
        
        assignTitleFromDocument = False
        title = None
        if item is not None:
            title = item.getMeta('title')
        oaidc = None
        if title is not None and title!="" and title!="Untitled":
            oaidc = self.__getBasicDC(title)
        else:
            assignTitleFromDocument = True
        
        # TODO add more DC elements
        if meta is not None:
            #do title first
            if meta.has_key("title") and assignTitleFromDocument:
                oaidc = self.__getBasicDC(meta["title"])
            for key in meta.keys():
                #print key,'=',meta[key]
                metaValue = meta[key]

                if key != 'authors':
                    try:
                        metaValue = unicode(metaValue, "UTF-8")
                    except:
                        metaValue = metaValue.decode("UTF-8")
                if oaidc is None:
                    continue
                if key == 'abstract':
                    dcDesc = self.ET.SubElement(oaidc, '{%s}description' % self.DC_NS)
                    try:
                        dcDesc.text = unicode(metaValue, "UTF-8")
                    except:
                        metaValue = self.iceContext.cleanUpString(metaValue);
                        dcDesc.text = metaValue.decode("UTF-8")
                elif key == 'authors':
                    authors = meta[key]
                    for author in authors:
                        dcAuth = self.ET.SubElement(oaidc, '{%s}creator' % self.DC_NS)
                        try:                            
                            dcAuth.text = unicode(author["name"], "UTF-8")
                        except:
                            dcAuth.text = author["name"].decode("UTF-8")
                        if author.has_key("affiliation"):
                            dcAff = self.ET.SubElement(oaidc, '{%s}contributor' % self.DC_NS)
                            try:
                                dcAff.text = unicode(author["affiliation"], "UTF-8")
                            except:
                                dcAff.text = author["affiliation"].decode("UTF-8")
                elif key=='date':
                    dcIssued = self.ET.SubElement(oaidc, '{%s}date' % self.DC_NS)
                    try:
                        dcIssued.text = unicode(metaValue, "UTF-8") 
                    except Exception,e :
                        dcIssued.text = metaValue.decode("UTF-8") 
                elif key == 'date-issued':
                    dcIssued = self.ET.SubElement(oaidc, '{%s}issued' % self.DC_TERM_NS)
                    try:
                        dcIssued.text = unicode(metaValue, "UTF-8")
                    except:
                        dcIssued.text = metaValue.decode("UTF-8")
                elif key != 'title':
                    dcRelation = self.ET.SubElement(oaidc, '{%s}relation' % self.DC_NS)
                    #metaValue = metaValue.replace(u'\xa0', ' ');
                    try:
                        value = unicode(metaValue, "UTF-8")
                        #dcRelation.text = "%s::%s" % (key, unicode(metaValue, "UTF-8"))
                    except:
                        try:
                            value = metaValue.decode("UTF-8")
                            #dcRelation.text = "%s::%s" % (key, metaValue.decode("UTF-8"))
                        except:
                            value = metaValue.encode('ascii', 'xmlcharrefreplace')
                            #dcRelation.text = "%s::%s" % (key, metaValue)
                    if value.find("::")>-1:
                        dcRelation.text = value
                    else:
                        dcRelation.text = "%s::%s" % (key, value)
                    
        dcXml = None
        if oaidc is None:
            oaidc = self.ET.Element('{%s}dc' % self.OAI_DC_NS)
        dcXml = self.ET.tostring(oaidc)
        return dcXml
    
    
    def __getBasicDC(self, title, identifier=None):
        """ producing basic DC element tags
        @param title: title of the tag
        @tytpe title: String
        @param identifier: identifier of the tag
        @param identifier: String
        
        @rtype: Element in Element tree
        @return: created element
        """
        oaidc = self.ET.Element('{%s}dc' % self.OAI_DC_NS)
        dcTitle = self.ET.SubElement(oaidc, '{%s}title' % self.DC_NS)
        dcTitle.text = unicode(title, "UTF-8")
        if identifier is not None:
            dcIdentifier = self.ET.SubElement(oaidc, '{%s}identifier' % self.DC_NS)
            dcIdentifier.text = identifier
        return oaidc

