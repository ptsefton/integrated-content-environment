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


import types
from types import UnicodeType, StringType, TypeType, ClassType
from Cheetah.Filters import Filter
from Cheetah.Template import Template



class HtmlFilter(Filter):
    # Usage:
    #   ${name, raw=True}       # no HTML escaping at all
    #   ${name, attr=True}      # (default) also escapes quotes and apos.
    #   ${name, text=True}      # does not escape quotes and apos.
    #   ${name, whiteText=True} # does not escape (" & ') but does also convert spaces, tabs and newlines
    # $name refers to an object that has an 'html' attribute THEN
    #   the value of this attribute will be used (as raw text by default) instead of the str() value of the object
    
    #@staticmethod
    #def simple():
    #    return Template(file="simple.tmpl", filter=HtmlFilter)
    
    def filter(self, val, **kw):
        # raw, attr, whiteText, text  (& rawExpr)
        #escape = self.__attr
        escape = None
        specialTypes = [TypeType, ClassType]
        t = type(val)
        if t is StringType:
            s = val
        elif t is UnicodeType:
            s = val.encode("UTF-8")
        elif hasattr(val, "html"):
            escape = str
            s = val.html
            if type(s) is UnicodeType:
                s = s.encode("UTF-8")
        elif t in specialTypes:
            s = str(val)
        elif t is types.NoneType:
            s = ""
        else:
            s = val.__str__()
            if type(s) is UnicodeType:
                # Warning: This objects __str__ method is not usable
                #           via str(obj)  'ascii codec may not be able to encode
                s = s.encode("UTF-8")
        if len(kw)>1:
            if kw.get("raw"):
                escape = str
            elif kw.get("attr"):
                escape = self.__attr
            elif kw.get("whiteText"):
                escape = self.__whiteText
            elif kw.get("text"):
                escape = self.__text
            elif kw.get("raw")==False:
                escape = self.__attr
        if escape is None:
            escape = str
        return escape(s)

    def __attr(self, s):
        s = self.__text(s)
        return s.replace("'", "&apos;").replace('"', "&quot;")

    def __text(self, s):
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def __whiteText(self, s):
        s = self.__text(s).replace(" ", "&#160;").replace("\n", "<br />")
        return s.replace("\t", "&#160;&#160;&#160;&#160;")


class Utf8Filter(Filter):
    def filter(self, val, **kw):
        if val is None:
            return ""
        elif type(val) is UnicodeType:
            return val.encode("UTF-8")
        else:
            return str(val)


#
# A Transaction can be passed to a Cheetah.Template.respond(trans=Transcation)
#   see a compiled template for more details
#
class Utf8Transaction(object):
    def __init__(self):
        self.__response = Utf8Response()

    def response(self):
        return self.__response


class Utf8Response(object):
    def __init__(self):
        self.__data = []

    def write(self, data):
        if type(data) is types.UnicodeType:
            self.__data.append(data.encode("UTF-8"))
        else:
            self.__data.append(data)

    def getvalue(self):
        return "".join(self.__data)

    def response(self):
        return self

    def __str__(self):
        return self.getvalue()

