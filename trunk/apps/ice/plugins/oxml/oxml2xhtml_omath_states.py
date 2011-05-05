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


class OMathState(BaseState):
    # m:oMath
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
            img.doNotResize = True
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






