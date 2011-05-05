#
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

from Cheetah.Template import Template
from htmlFilter import HtmlFilter
from Cheetah import DummyTransaction



class HtmlTemplate(object):
    def __init__(self, templateFile=None, templateString=None, allowMissing=False):
        if templateFile is None and templateString is None:
            raise Exception("templateFile OR templateString must valid! (not None)")
        self.__templateFile=templateFile
        self.__templateString=templateString
        self.__allowMissing = allowMissing
        self.__missing = []
        self.__includeStyle = ""
    
    @property
    def missing(self):
        return self.__missing
    
    @property
    def includeStyle(self):
        return self.__includeStyle
    
    def transform(self, searchDict={}, allowMissing=None):
        self.__missing = []
        if allowMissing is None:
            allowMissing = self.__allowMissing
        if allowMissing:
            sDict = SearchDict(searchDict)
        else:
            sDict = searchDict
        
        try:
            if self.__templateFile is not None:
                page = Template(file=self.__templateFile, filter=HtmlFilter, \
                                searchList=[sDict])
            else:
                page = Template(self.__templateString, filter=HtmlFilter, searchList=[sDict])
        except Exception, e:
            print "-----"
            print str(e)
            print "-----\n"
            raise e
        #page.searchList()[1] = aNewSearchDict      #to change an existing searchDict
        if hasattr(page, "includeStyle"):
            try:
                self.__includeStyle = page.includeStyle()
            except Exception, e:
                print "Error including style information - '%s'" % str(e)
        
        if allowMissing:
            self.__missing = sDict.missingKeys
            sDict.page = page
        
        return str(page)



class SearchDict(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.missingKeys = []
    
    def __getitem__(self, name):
        if not dict.has_key(self, name):
            if hasattr(self.page, name):
                #print "Page does have '%s'" % name
                return getattr(page, name)
            self.missingKeys.append(name)
            self[name] = ""
        return dict.__getitem__(self, name)



class HtmlText(object):
    # NOTE: not attribute safe
    """ Keep whitespace e.g. multispaces, tabs and newlines """
    def __init__(self, text):
        self.text = text
    
    @property
    def html(self):
        s = self.text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        s = s.replace(" ", "&#160;").replace("\n", "<br />")
        s = s.replace("\t", "&#160;&#160;&#160;&#160;")
        return s
    
    def __str__(self):
        return self.text




