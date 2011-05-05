#    Copyright (C) 2010  Distance and e-Learning Centre,
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
from oxml2xhtml_baseState import BaseState
import re


class DrawingState(BaseState):
    # w:drawing
    def __init__(self, parentState, name=None, attrs={}):
        BaseState.__init__(self, parentState, name, attrs)
        self._oxml.startDataCapturing(self)

    def endState(self):
        dataCaptured = self._oxml.stopDataCapturing(self)
        if dataCaptured:
            ce = self._currentHtmlElement
            img = ce.addChildElement("img")
            srcName = self._oxml.addObjImage(img, dataCaptured)
            img.setAttribute("alt", srcName)
            img.setAttribute("title", "drawing")
        # return False if endState is canceled
        return True


class InlineState(BaseState):
    # wp:inline
    def __init__(self, parentState, name=None, attrs={}):
        BaseState.__init__(self, parentState, name, attrs)


class AnchorState(BaseState):
    # wp:anchor
    def __init__(self, parentState, name=None, attrs={}):
        BaseState.__init__(self, parentState, name, attrs)
        attrs.get("distT")
        attrs.get("distB")
        attrs.get("distL")
        attrs.get("distR")
        attrs.get("relativeHeight")     # in emu's

    #def startElement(self, name, attrs):


class GraphicState(BaseState):
    # a:graphic
    def __init__(self, parentState, name=None, attrs={}):
        BaseState.__init__(self, parentState, name, attrs)


class GraphicDataState(BaseState):
    # a:graphicData
    def __init__(self, parentState, name=None, attrs={}):
        BaseState.__init__(self, parentState, name, attrs)


class PicState(BaseState):
    # pic:pic
    # 100% = 100,000
    # twip = 1/20th of a point (or 635 emu's)
    # 1 point = 12,700 emu's
    # 1 inch = 914,400 emu's  (25.4mm)
    # 1 mm = 36,000 emu's
    EMUsPerMM = 36000
    def __init__(self, parentState, name=None, attrs={}):
        BaseState.__init__(self, parentState, name, attrs)
        self._picName = ""
        self._x = None          # / 36000 = mm
        self._y = None
        self._embed = None
        self._target = None
        self._xmm = None
        self._ymm = None
        self._lCrop = 0         # faction of 100,000
        self._tCrop = 0
        self._rCrop = 0
        self._bCrop = 0

    def __getPicName(self):
        return self._picName
    def __setPicName(self, name):
        self._picName = name
    picName = property(__getPicName, __setPicName)

    @property
    def target(self):
        return self._target

    @property
    def xmm(self):
        return self._x/self.EMUsPerMM

    @property
    def ymm(self):
        return self._y/self.EMUsPerMM

    @property
    def cropRect(self):
        return (self._lCrop, self._tCrop, self._rCrop, self._bCrop)


    def setEmbed(self, value):
        self._embed = value
        self._target = self._oxml.docRels.getTarget(value)

    def setX(self, value):
        value = int(value)
        self._x = value

    def setY(self, value):
        value = int(value)
        self._y = value

    def endState(self):
        #print self
        ce = self._currentHtmlElement
        filename = self._oxml.addImage(self)
        ce.addChildElement("img", alt=self.picName, title=self.picName, \
                src=filename, \
                style="width:%smm;height:%smm;" % (self.xmm, self.ymm))
        # Cancel my parent's DrawingState dataCapturing
        #  w:drawing/wp:anchor|wp:inline/a:graphic/a:graphicData/pic:pic(me)
        try:
            dState = self.parentState.parentState.parentState.parentState
            if dState and dState.stateName=="DrawingState":
                dState._oxml.stopDataCapturing(dState)
        except:
            pass
        # return False if endState is canceled
        return True

    def __str__(self):
        s = "[PicState picName='%s', Xmm=%s, Ymm=%s, target='%s']" % \
            (self.picName, self.xmm, self.ymm, self.target)
        return s



class PicPropState(BaseState):
    # pic:nvPicPr      - parent is PicState
    def __init__(self, parentState, name=None, attrs={}):
        BaseState.__init__(self, parentState, name, attrs)

    def startElement(self, name, attrs):
        if name=="pic:cNvPr":
            self.parentState.picName = attrs.get("name")



class PicBlipFillState(BaseState):
    # pic:blipFill      - parent is PicState
    def __init__(self, parentState, name=None, attrs={}):
        BaseState.__init__(self, parentState, name, attrs)

    def startElement(self, name, attrs):
        if name=="a:blip":
            self.parentState.setEmbed(attrs.get("r:embed"))
        elif name=="a:srcRect":
            try:
                p = self.parentState
                p._lCrop = int(attrs.get("l", "0"))
                p._tCrop = int(attrs.get("t", "0"))
                p._rCrop = int(attrs.get("r", "0"))
                p._bCrop = int(attrs.get("b", "0"))
            except:
                pass


class PicSpanPropState(BaseState):
    # pic:spPr      - parent is PicState
    def __init__(self, parentState, name=None, attrs={}):
        BaseState.__init__(self, parentState, name, attrs)



class XFormState(BaseState):
    # a:xfrm
    # a:ext @cx & @cy  /36000 = mm
    def __init__(self, parentState, name=None, attrs={}):
        BaseState.__init__(self, parentState, name, attrs)

    def startElement(self, name, attrs):
        if name=="a:ext":
            pp = self.parentState.parentState
            pp.setX(attrs.get("cx"))
            pp.setY(attrs.get("cy"))



class PictState(BaseState):
    # w:pict
    def __init__(self, parentState, name=None, attrs={}):
        BaseState.__init__(self, parentState, name, attrs)
        #print "w:pict"
        self._oxml.startDataCapturing(self)

    def endState(self):
        dataCaptured = self._oxml.stopDataCapturing(self)
        if dataCaptured:
            ce = self._currentHtmlElement
            img = ce.addChildElement("img")
            srcName = self._oxml.addObjImage(img, dataCaptured)
            img.setAttribute("alt", srcName)
            img.setAttribute("title", "drawing")
        # return False if endState is canceled
        return True


class ShapeTypeState(BaseState):
    # v:shapetype
    def __init__(self, parentState, name=None, attrs={}):
        BaseState.__init__(self, parentState, name, attrs)
        #print "v:sharptype"


class ShapeState(BaseState):
    # v:sharp
    EMUsPerPT = 12700
    EMUsPerMM = 36000
    def __init__(self, parentState, name=None, attrs={}):
        BaseState.__init__(self, parentState, name, attrs)
        #print "v:shape"
        self._picName = ""
        self._x = None          # / 36000 = mm
        self._y = None
        self._target = None
        self.__style = attrs.get("style", "")
        self._x = 0
        self._y = 0
        m = re.search("width\:([0-9.]+)pt", self.__style)
        if m:
            try:
                self._x = float(m.groups()[0]) * self.EMUsPerPT    # pt to emu
            except:
                pass
        m = re.search("height\:([0-9.]+)pt", self.__style)
        if m:
            try:
                self._y = float(m.groups()[0]) * self.EMUsPerPT  # pt to emu
            except:
                pass

    @property
    def target(self):
        return self._target

    @property
    def xmm(self):
        return self._x/self.EMUsPerMM

    @property
    def ymm(self):
        return self._y/self.EMUsPerMM

    @property
    def cropRect(self):
        return (0, 0, 0, 0)

    def startElement(self, name, attrs):
        if name=="v:imagedata":
            rId = attrs.get("r:id")
            self._picName = attrs.get("o:title")
            self._target =  self._oxml.docRels.getTarget(rId)

    def endState(self):
        #print self
        if False:
            if self._target is not None:
                ce = self._currentHtmlElement
                filename = self._oxml.addImage(self, ext=".png")
                ce.addChildElement("img", alt=self._picName, title=self._picName, \
                        src=filename, \
                        style="width:%smm;height:%smm;" % (self.xmm, self.ymm))
        # return False if endState is canceled
        return True


class ChartState(BaseState):
    # c:chart
    def __init__(self, parentState, name=None, attrs={}):
        BaseState.__init__(self, parentState, name, attrs)
        #print "c:chart"


class ObjectState(BaseState):
    # w:object
    def __init__(self, parentState, name=None, attrs={}):
        BaseState.__init__(self, parentState, name, attrs)
        #print "w:object"
        # turn on data capturing
        self._oxml.startDataCapturing(self)

    def startElement(self, name, attrs):
        if name=="o:OLEObject":
            t = attrs.get("Type")
            rId = attrs.get("r:Id")

    def endState(self):
        dataCaptured = self._oxml.stopDataCapturing(self)
        if dataCaptured:
            ce = self._currentHtmlElement
            img = ce.addChildElement("img")
            srcName = self._oxml.addObjImage(img, dataCaptured)
            img.setAttribute("alt", srcName)
            img.setAttribute("title", "drawing")
        # return False if endState is canceled
        return True


class XState(BaseState):
    def __init__(self, parentState, name=None, attrs={}):
        BaseState.__init__(self, parentState, name, attrs)

    def startElement(self, name, attrs):
        pass

    def characters(self, text):
        pass

    def endState(self):
        # return False if endState is canceled
        return True






