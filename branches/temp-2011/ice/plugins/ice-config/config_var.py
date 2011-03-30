
#    Copyright (C) 2009  Distance and e-Learning Centre, 
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

""" """

import types


class Var(object):
    # Constructor:
    #   Var(ElementTree)
    # Methods:
    #   processVarElement(varNode)                      -> (name, value, desc)
    #   getVarElement(name, value, description=None)    -> element

    varTypes = ("string", "integer", "boolean", "list", "dictionary", "xml", "none")
    
    def __init__(self, ElementTree):
        self.__et = ElementTree
    
    
    def processVarElement(self, varNode):
        name = varNode.get("name")
        type = varNode.get("type", "string")
        type = type.lower()
        desc = varNode.get("desc")
        value = varNode.text

        if value is None:
            value = varNode.get("value", "")

        if type=="str" or type=="string":
            pass
        elif type=="int" or type=="integer":
            try:
                value = int(value)
            except:
                value = 0
        elif type=="bool" or type=="boolean":
            value = value.lower()
            if value=="false" or value=="0" or value=="":
                value = False
            else:
                value = True
        elif type=="list" or type=="array":
            value = value.strip()
            if value is not "":
                sep = varNode.get("sep", ",")
                parts = value.split(sep)
                value = [i.strip("\"' \t\n\r") for i in parts]
            else:
                value = []
                for node in varNode.findall("var"):
                    n, v, d = self.processVarElement(node)
                    value.append(v)
        elif type=="dict" or type=="dictionary":
            value = {}
            for node in varNode.findall("var"):
                n, v, d = self.processVarElement(node)
                value[n] = v
        elif type=="xml":
            children = varNode.findall("*")
            children.append(None)
            value = children[0]
        elif type=="none":
            value = None
        else:
            value = None
        return name, value, desc


    def process(self, name, type, valueStr, desc):
        value = valueStr
        if value is None:
            value = ""
        if type=="str" or type=="string":
            pass
        elif type=="int" or type=="integer":
            try:
                value = int(value)
            except:
                value = 0
        elif type=="bool" or type=="boolean":
            value = value.lower()
            if value=="false" or value=="0" or value=="":
                value = False
            else:
                value = True
        elif type=="list" or type=="array":
            value = value.strip()
            if value is not "":
                sep = varNode.get("sep", ",")                       ####
                parts = value.split(sep)                            ####
                value = [i.strip("\"' \t\n\r") for i in parts]      ####
            else:
                value = []
                for node in varNode.findall("var"):                 ####
                    n, v, d = self.processVarElement(node)          ####
                    value.append(v)                                 ####
        elif type=="dict" or type=="dictionary":
            value = {}
            for node in varNode.findall("var"):                     ####
                n, v, d = self.processVarElement(node)              ####
                value[n] = v                                        ####
        #elif type=="xml":
        #    children = varNode.findall("*")
        #    children.append(None)
        #    value = children[0]
        elif type=="none":
            value = None
        else:
            value = None
        return name, value, desc

    def getVarElement(self, name, value, description=None):
        attrs = {}
        if name is not None:
            attrs["name"] = name
        if description is not None:
            attrs["desc"] = description
        t = type(value)
        _type = None
        children = []
        if t is types.StringType:
            _type = "string"
            attrs["value"] = value
        elif t is types.IntType:
            _type = "integer"
            attrs["value"] = str(value)
        elif t is types.BooleanType:
            _type = "boolean"
            attrs["value"] = str(value)
        elif t is types.ListType:
            _type = "list"
            children = [self.getVarElement(None, v) for v in value]
        elif t is types.DictType:
            _type = "dict"
            children = [self.getVarElement(str(n), v) for n, v in value.iteritems()]
        elif t is types.NoneType:
            _type = "none"
        else:
            raise Exception("Unsupported value type!")
        attrs["type"] = _type
        element = self.__et.Element("var", attrs)
        for c in children:
            element.append(c)
        return element
    

    def __testValue(self, value):
        valueType = type(value)
        if valueType is types.StringType:
            # OK
            return True
        elif valueType is types.IntType:
            # OK
            return True
        elif valueType is types.BooleanType:
            # OK
            return True
        elif valueType is types.ListType:
            # Then test its items
            for item in value:
                if self.__testValue(item)==False:
                    raise Exception("List item value may be out of context! (is not string, bool, int, list or dict type)")
                    return False
            return True
        elif valueType is types.DictType:
            # Then test its keys and values
            for key, value in value.iteritems():
                if type(key) is not types.StringType:
                    raise Exception("Only string dictionary keys are allowed")
                    return False
                self.__testValue(value)
        else:
            raise Exception("Value may be out of context! ('%s' is not string, bool, int, list or dict type)" % valueType)
            return False












