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



class TableState(BaseState):
    def __init__(self, parentState, name=None, attrs={}):
        BaseState.__init__(self, parentState, name, attrs)
        self._rows = []
        self._gCol = []
        self._style = ""

    def startElement(self, name, attrs):
        pass

    def characters(self, text):
        pass

    def endState(self):
        if len(self._rows):
            e = self._currentHtmlElement.addChildElement("table", cellspacing=0)
            if self._style!="":
                e.addAttribute("style", self._style)
            #cg = e.addChildElement("colgroup")
            #for gCol in self._gCol:
            #    cg.addChildElement("col", width=gCol)
            e = e.addChildElement("tbody")
            for row in self._rows:
                tr = e.addChildElement("tr")
                for cell in row._cells:
                    if cell is not None:
                        if cell._width:
                            w = int(cell._width)/56.62
                            w = str(w+0.05)
                            if w.find(".")!=-1:
                                w = w[:w.find(".")+2]   # one decimal place only
                            style = cell._td.getAttribute("style") or "vertical-align:top;"
                            style += "width:%smm;" % w
                            cell._td.setAttribute("style", style)
                        if cell._vMerge=="restart":
                            count = 1
                            coli = row._cells.index(cell)
                            rowi = self._rows.index(row)
                            for x in range(rowi+1, len(self._rows)):
                                r = self._rows[x]
                                c = r._cells[coli]
                                if c is None or c._vMerge is False or c._vMerge=="restart":
                                    break
                                r._cells[rowi] = None
                                count += 1
                            cell._td.addAttribute("rowspan", count)
                        tr.addChild(cell._td)
        # return False if endState is canceled
        return True


class TablePropState(BaseState):
    def __init__(self, parentState, name=None, attrs={}):
        BaseState.__init__(self, parentState, name, attrs)

    def startElement(self, name, attrs):
        if name=="w:jc":
            val = attrs.get("w:val", "")
            if val=="center":
                p = self.parentState
                p._style += "margin-left:auto;margin-right:auto;"



class TableGridState(BaseState):
    def __init__(self, parentState, name=None, attrs={}):
        BaseState.__init__(self, parentState, name, attrs)

    def startElement(self, name, attrs):
        if name=="w:gridCol":
            p = self.parentState
            w = attrs.get("w:w", "")
            p._gCol.append(w)


class TableRowState(BaseState):
    def __init__(self, parentState, name=None, attrs={}):
        BaseState.__init__(self, parentState, name, attrs)
        self._cells = []

    def endState(self):
        p = self.parentState
        if hasattr(p, "_rows"):
            p._rows.append(self)
        # return False if endState is canceled
        return True



class TableCellState(BaseState):
    def __init__(self, parentState, name=None, attrs={}):
        BaseState.__init__(self, parentState, name, attrs)
        self._preCurrentHtmlElement = self._currentHtmlElement
        self._td = self._html.createElement("td")
        self._currentHtmlElement = self._td
        self._colSpan = 1
        self._vMerge = False
        self._width = None
        self._style = ""

    def endState(self):
        p = self.parentState
        if hasattr(p, "_cells"):
            p._cells.append(self)
            if self._colSpan > 1:
                self._td.addAttribute("colspan", self._colSpan)
                for i in range(self._colSpan-1):
                    p._cells.append(None)
        if self._style!="":
            self._td.addAttribute("style", self._style)
        self._currentHtmlElement = self._preCurrentHtmlElement
        # return False if endState is canceled
        return True

    def getParentTable(self):
        # tr table
        return self.parentState.parentState


class TableCellPropState(BaseState):
    def __init__(self, parentState, name=None, attrs={}):
        BaseState.__init__(self, parentState, name, attrs)

    def startElement(self, name, attrs):
        if name=="w:gridSpan":
            val = attrs.get("w:val")
            p = self.parentState
            if val and hasattr(p, "_currentHtmlElement"):
                val = int(val)
                p._colSpan = val
        elif name=="w:vMerge":
            val = attrs.get("w:val", "true")
            p = self.parentState
            p._vMerge = val
        elif name=="w:tcW":
            w = attrs.get("w:w")
            t = attrs.get("w:type") # 'dxa'
            p = self.parentState
            if w:
                p._width = w
        elif name=="w:vAlign":
            val = attrs.get("w:val", "")
            p = self.parentState
            p._style += "vertical-align:middle;text-align:center;"



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






