import types
import weakref


#  div.p = x  - replace all children of div.p with x
#  div.p += x  - addChild(x)
#  div.p[2] << x  - insert x before p[2]  (before the second p element)
#  div.p[2]._insertBefore(x)
#  div.p[2]._insertAfter(x)

# div._element  - the first child element of div   ["*"][1]   or [Elements]
# div._node     - the first child node of div                   [Nodes]
# div.p["[xpath]"] ???   or div.p("xpath")  e.g. div.p("*")



class NodeList(list):   # a node set or list
    def __init__(self):
        list.__init__(self)
    
    def _filter(self):
        # return a new filtered NodeList
        pass

class Node(object):
    def __init__(self, type, name, parent=None):
        self.__type = type
        self.__name = name
        self._parent = parent
        self.__value = None

    def __getName(self):
        return self.__name
    _name = property(__getName)

    def __getType(self):
        return self.__type
    _type = property(__getType)

    def __getParent(self):
        ref = self.__parent
        if ref is None:
            return None
        else:
            return ref()
    def __setParent(self, value):
        if value is None:
            self.__parent = None
        else:
            self.__parent = weakref.ref(value)
    _parent = property(__getParent, __setParent)

    def _delete(self):
        self.__parent = None

    # override
    def _getElement(self, name):
        return None

    # override
    def _getElements(self, name):
        elements = []
        return elements

    def __getValue(self):
        return self.__value
    def __setValue(self, value):
        self.__value = value
    _value = property(__getValue, __setValue)
    value = property(__getValue, __setValue)

    def _nextSibling(self):
        pass
    def _prevSibling(self):
        pass

    def __add__(self, other):
        t = type(other)
        if t is types.StringType:
            self._value = other
        elif t.__class__ is self.__class__:     # to is isinstance
            self._addChild(other)
        return self

    # override
    def _serialize(self, format=False):
        s = self.__value
        s = s.replace("&", "&amp;")
        s = s.replace("<", "&lt;").replace(">", "&gt;")
        return s
        
    # override
    def __str__(self):
        return self._value

    # override
    def __repr__(self):
        return self._serialize()

    def _isValidAttName(self, name):
        return True

    def _isValidElementName(self, name):
        return True


class TextNode(object):
    def __init__(self, text="", parent=None):
        self.__text = text
        self._parent = parent

    def __getName(self):
        return "[TextNode]"
    _name = property(__getName)

    def __getType(self):
        return "Text"
    _type = property(__getType)

    def __getParent(self):
        ref = self.__parent
        if ref is None:
            return None
        else:
            return ref()
    def __setParent(self, value):
        if value is None:
            self.__parent = None
        else:
            self.__parent = weakref.ref(value)
    _parent = property(__getParent, __setParent)

    def _getElement(self, name):
        return None

    def _getElements(self, name):
        elements = []
        return elements

    def __getValue(self):
        return self.__text
    def __setValue(self, text):
        self.__text = text
    _value = property(__getValue, __setValue)
    value = property(__getValue, __setValue)

    def _delete(self):
        self._parent = None

    def _remove(self, node=None):
        if node is None or node is self:
            parent = self._parent
            if parent is not None:
                parent._remove(self)
            return self

    def _serialize(self, format=False):
        s = self.__text
        s = s.replace("&", "&amp;")
        s = s.replace("<", "&lt;").replace(">", "&gt;")
        return s
        

    def __str__(self):
        return self.__text

    def __repr__(self):
        return self._serialize()


class Element(dict):
    def __init__(self, name=None, _xmlStr=None, **attributes):
        for n in attributes.keys():
            if n.startswith("_"):
                value = attributes[n]
                del attributes[n]
                attributes[n[1:]] = value
        dict.__init__(self, attributes)
        self.__name = name
        self.__parent = None    # NOTE: parent needs to be a weakref
        self.__nodes = []
        # remove all inherited methods
        methods = [m for m in dir(self) if not m.startswith("_")]
        for m in methods:
            self.__dict__[m] = None
        self._locked = False
        self.__context = None       # temp value, for use in expressions such as div._nodes[2] or div._elements[2] etc or div._[2] (short hand)

    #def __del__(self):
    #    print "__del__ element name='%s'" % self.__name

    def __getName(self):
        return self.__name
    def __setName(self, name):
        if self._locked:
            raise Exception("cannot change the name when locked!")
        else:
            self.__name = name
    _name = property(__getName)

    def __getType(self):
        return "Element"
    _type = property(__getType)

    def __getParent(self):
        ref = self.__parent
        if ref is None:
            return None
        else:
            return ref()
    def __setParent(self, value):
        parent = self.__getParent()
        if parent is not None:
            self.__parent = None
            parent._remove(self)
        if value is None:
            self.__parent = None
        else:
            self.__parent = weakref.ref(value)
    _parent = property(__getParent, __setParent)

    def _getElement(self, name=None):
        if name is None:
            for e in self.__nodes:
                if e._type=="Element":
                    return e
            return None
        for e in self.__nodes:
            if e._name==name and e._type=="Element":
                return e
        return None

    def _getElements(self, name=None):
        elements = []
        if name is None:
            for e in self.__nodes:
                if e._type=="Element":
                    elements.append(e)
        else:
            for e in self.__nodes:
                if e._name==name and e._type=="Element":
                    elements.append(e)
        return elements

    _ = property(_getElement)   # any element

    def _getNode(self):
        if len(self.__nodes)>0:
            return self.__nodes[0]
        else:
            return None
    _node = property(_getNode)          # any node
    _element = property(_getElement)    # any element

    def __addComment(self, comment):
        com = Comment(comment, self)
        self.__nodes.append(com)

    def __addPI(self, name, data):
        pass

    def __getValue(self):
        text = ""
        for n in self.__nodes:
            if n._type=="Element" or n._type=="Text":
                text += n._value
        return text
    def __setValue(self, text):
        for n in self.__nodes:
            n._remove()
        if text is None:
            return
        t = TextNode(text, self)
        self.__nodes = [t]
    _value = property(__getValue, __setValue)
    
    def _insertBefore(self, data, beforeNode=None):
        if beforeNode is not None:
            index = self.__nodes.index(beforeNode)
            if data.__class__ is self.__class__:      # to is isinstance
                node = data
            else:
                node = TextNode(str(data))
            node._parent = self
            self.__nodes.insert(index, node)
        else:
            parent = self._parent
            if parent is not None:
                parent._insertBefore(data, self)

    def __lshift__(self, data):
        self._insertBefore(data)

    def _addContent(self, content):
        t = TextNode(content, self)
        self.__nodes.append(t)

    def _addChild(self, node=None):
        # check that node is a valid node
        if node is None:
            return PlaceHolder(self._addChild)
        if node.__class__ is self.__class__:     # to is isinstance
            pass
        else:
            node = TextNode(str(node))
        node._parent = self
        self.__nodes.append(node)
        return self

    def _addChildren(self, nodes):
        for node in nodes:
            self._addChilde(node)

    def __add__(self, other):
        self._addChild(other)
        return self

    def _delete(self):
        parent = self._parent
        if parent is None:
            return
        parent._remove(self)
        self._parent = None
        for n in self.__nodes:
            n._delete()

    def _remove(self, node=None):
        if node is None:
            node = self
        if node is self:
            parent = self._parent
            if parent is not None:
                parent._remove(self)
            return self
        if node in self.__nodes:
            self.__nodes.remove(node)
            node._parent = None
            return node
        return None

    def _hasattr(self, name):
        return dict.has_key(self, name)

    def _getAttributes(self):
        return dict(dict.items(self))

    def __getitem__(self, name):
        t = type(name)
        if t is types.IntType:
            index = name
            #print "index=", index
            parent = self._parent
            if parent is None:
                #print "parent is None"
                return None
            elems = parent._getElements(self.__name)
            if index==0:
                return None
            if index<0:
                if len(elems)>=abs(index):
                    return elems[index]
                else:
                    return None
            if len(elems)>=index:
                return elems[index-1]
            elif not self._locked:
                num = index-len(elems)  # number of elements to create
                #print "%s elements to be created" % num
                while(num>0):
                    e = Element(self.__name)
                    parent._addChild(e)
                    num -= 1
                elems = parent._getElements(self.__name)
                return elems[index-1]
            else:
                return None
        elif t is types.StringType:
            return dict.get(self, name, None)
        else:
            return None

    def __setitem__(self, name, value):
        t = type(name)
        if t is types.IntType:
            e = self.__getitem__(name)
            if e is not None:
                e._value = value
        elif t is types.StringType:
            dict.__setitem__(self, name, str(value))
            if value is None:
                dict.pop(self, name)
        else:
            pass

    def __delitem__(self, name):
        t = type(name)
        if t is types.IntType:
            node = self.__getitem__(name)
            if node is not None:
                node._delete()
        elif t is types.StringType:
            if dict.has_key(self, name):
                dict.pop(self, name)
        else:
            return None
        
    
    def __getattr__(self, name):
        if name.startswith("_"):
            return None
        node = self._getElement(name)
        if node is None and self._locked==False:
            node = Element(name)
            node._parent = self
            self.__nodes.append(node)
        return node
    
    def __setattr__(self, name, value):
        if name.startswith("_"):
            klass = self.__class__
            kdict = klass.__dict__
            p = kdict.get(name)
            if type(p) is property:
                p.fset(self, value)
            else:
                self.__dict__[name] = value
        else:
            e = self.__getattr__(name)
            if e is not None:
                e._value = value
    
    def __delattr__(self, name):
        node = self.__getattr__(name)
        if node is not None:
            node._delete()

    def _serialize(self, format=False):
        attrs = ""
        for att in dict.keys(self):
            attrs += self.__getAttrRepr(att)
        if len(self.__nodes)==0:
            return "<%s%s />" % (self.__name, attrs)
        else:
            children = ""
            cr = False
            for n in self.__nodes:
                if n._type=="Text":
                    children += n._serialize(format)
                else:
                    if format:
                        cr = True
                        children += "\n\t" + n._serialize(format).replace("\n", "\n\t")
                    else:
                        children += n._serialize()
            if cr:
                children += "\n"
            return "<%s%s>%s</%s>" % (self.__name, attrs, children, self.__name)
        

    def __call__(self, *args, **kargs):
        for arg in args:
            if type(arg) is types.DictType:
                for name, value in arg.items():
                    dict.__setitem__(self, name, str(value))
        for name, value in kargs.items():
            if name.startswith("_"):
                name = name[1:]
            dict.__setitem__(self, name, str(value))
        return self

    def __str__(self):
        return self._value

    def __repr__(self):
        return self._serialize()
        
    def __getAttrRepr(self, name):
        value = dict.get(self, name, None)
        if value==None:
            return ""
        else:
            value = value.replace("&", "&amp;")
            value = value.replace("<", "&lt;").replace(">", "&gt;")
            if value.count('"')==0:
                value = '"' + value + '"'
            elif value.count("'")==0:
                value = "'" + value + "'"
            elif value.count('"')>=value.count("'"):
                value = "'" + value.replace("'", "&apos;") + "'"
            else:
                value = '"' + value.replace('"', "&quot;") + '"'
            return " %s=%s" % (name, value)


class Comment(object):
    def __init__(self, comment="", parent=None):
        self.__comment = comment
        self._parent = parent

    def __getName(self):
        return "[CommentNode]"
    _name = property(__getName)

    def __getType(self):
        return "Comment"
    _type = property(__getType)

    def __getParent(self):
        ref = self.__parent
        if ref is None:
            return None
        else:
            return ref()
    def __setParent(self, value):
        self.__parent = weakref.ref(value)
    _parent = property(__getParent, __setParent)

    def __getValue(self):
        return self.__comment
    def __setValue(self, comment):
        self.__comment = comment
    _value = property(__getValue, __setValue)
    value = property(__getValue, __setValue)

    def _delete(self):
        self.__parent = None
    
    def _getElement(self, name):
        return None

    def _getElements(self, name):
        elements = []
        return elements


class PlaceHolder(object):
    def __init__(self, method):
        self.__method = method

    def __getattr__(self, name):
        node = Element(name)
        self.__dict__["_PlaceHolder__method"](node)
        return node

    def __setattr__(self, name, value):
        if name=="_PlaceHolder__method":
            self.__dict__["_PlaceHolder__method"] = value
        else:
            node = self.__getattr__(name)
            node._value = value



div = Element("div")
div(_class="divCls")
div.p(_class="one")._value = "One"
div.p[2](_class="two")._value = "Two"


