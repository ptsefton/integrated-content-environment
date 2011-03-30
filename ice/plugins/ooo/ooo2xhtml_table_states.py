
#    Copyright (C) 2006  Distance and e-Learning Centre, 
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

from ooo2xhtml_utils import *
from ooo2xhtml_style import *


class tableState(stateObject):
    def __init__(self, parentState, name, atts, style=None):
        self.__colgroup = None
        self.__usingColgroup = False
        stateObject.__init__(self, parentState, name, atts)
        self.__rows = []

    def __getRows(self):
        return self.__rows
    rows = property(__getRows)

    def processElement(self, name, attrs):
        styleName = attrs.get("table:style-name", "")
        #print styleName
        self.style = self.o.styles.getOooStyle(styleName)
        #print "tableState: ", self.style
        
        div = element("div")
        #div.setAttribute("align", self.style.tableAlign)
        div.setAttribute("class", styleName)
        table = element("table")
        if self.style.tableAlign=="center":
            tableAlignStyle = "margin:auto auto; text-align:left;"
        elif self.style.tableAlign=="right":
            tableAlignStyle = "margin-left:auto; margin-right:0px; text-align:left;"
        else:
            tableAlignStyle = ""
        if styleName!="":
            table.setAttribute("class", styleName)
            self.stateElement = div
            div.addChild(table)
            # set the div style
            styles = self.o.styles
            divStyle = styles.getCssStyle("div")
            divStyle += styles.getCssStyle("div.%s" % styleName)
            divStyle += "text-align:%s;" % self.style.tableAlign
            #print "div.%s style = '%s'" % (styleName, divStyle)
            div.setAttribute("style", divStyle)
            # Set the table style
            tableStyle = styles.getCssStyle("table")
            tableStyle += styles.getCssStyle("table.%s" % styleName)
            tableStyle += tableAlignStyle
            tableStyle += "border-collapse: collapse; "
            #print "table.%s style = '%s'" % (styleName, tableStyle)
            table.setAttribute("style", tableStyle)
        else:
            div.setAttribute("style", "text-align:%s;" % self.style.tableAlign)
            if tableAlignStyle!="":
                table.setAttribute("style", tableAlignStyle)
            self.stateElement = table
        #if styleName=="Table7":
        if True:
            self.__colgroup = element("colgroup")
            table.addChild(self.__colgroup)
        tbody = element("tbody")
        table.addChild(tbody)
        self.currentElement = tbody
        self.__table = table
    
    def createNewState(self, klass, name, attrs, style=None):
        newState = klass(self, name, attrs, style=style)
        if isinstance(newState, tableColumnState):
            if self.__colgroup is not None:
                col = element("col")
                if newState.width is not None and newState.width!="":
                    col.setAttribute("style", "width:%s;" % newState.width)
                    self.__usingColgroup = True
                self.__colgroup.addChild(col)
            self.depthCount += 1
            newState = self        # keep us as the new state
        elif isinstance(newState, tableRowState):
            self.addRow(newState)
        return newState
    
    
    def addClass(self, name):
        att = self.__table.getAttribute("class")
        if att is not None:
            cls = att.value
            self.__table.setAttribute("class", cls + " " + name)
    
    def addRow(self, row):
        self.__rows.append(row)
    
    def closingState(self):
        """ do any state finalization/cleanup here """
        if self.__usingColgroup==False:
            self.__table.remove(self.__colgroup)
        if len(self.currentElement.items)==0:
            # Empty
            self.stateElement = None
        """ do clean up for IE border-right error for table that have right border. """
        tableColumnsAndRows = self.__table.getLastChild()
        
        if tableColumnsAndRows is not None:
            tableRows = tableColumnsAndRows.getChildren()
            rightBorderValue = ""
            if tableRows != []:
                for row in tableRows:
                    if row.name == "tr":
                        cell = row.getLastChild()  #Just check for last cell
                        #for cell in cells:
                        cellStyle = self.o.styles.getOooStyle(cell.getAttribute("style").value)
                        
                        if cellStyle.type == "":
                            rightBorderValue = ""
                            break
                        else:
                            relist=cellStyle.type.split(";")
                            for r in relist:
                                try:
                                    match=r.split(":")
                                    #those converted border value that is less than 1 px will be replaced
                                    if match[0].strip() == "border-right":
                                        if match[1].strip() != "none":
                                            rightBorderValue = match[1]                   
                                except:           
                                    pass
                if rightBorderValue != "":
                    #process here
                    attr = self.__table.getAttribute("style")
                    if attr is not None:
                        tableStyle = attr.value
                    else:
                        tableStyle = ""
                    tableStyle += "border: %s" % rightBorderValue
                    self.__table.setAttribute("style", tableStyle)
        # Do not display tables that only contain empty cells
        #  This is so that we can hide a table.
        allEmpty = True
        for row in self.__rows:
            for cell in row.cells:
                for c in cell.cellElement.getChildren():
                    if c.type!="comment":
                        allEmpty = False
                        break
                if allEmpty==False:
                    break
        if allEmpty:
            self.rollback()



class tableHeaderRowsState(stateObject):
    def __init__(self, parentState, name, atts, style=None):
        stateObject.__init__(self, parentState, name, atts)

    def processElement(self, name, attrs):
        pass


class tableRowState(stateObject):
    def __init__(self, parentState, name, atts, style=None):
        self.__isHeaderRow = False
        stateObject.__init__(self, parentState, name, atts)
        if isinstance(parentState, tableHeaderRowsState):
            self.__isHeaderRow = True
        self.__cells = []

    def __getCells(self):
        return self.__cells
    cells = property(__getCells)

    def __getIsHeaderRow(self):
        return self.__isHeaderRow
    isHeaderRow = property(__getIsHeaderRow)

    def processElement(self, name, attrs):
        # Find the parent tableState
        tr = element("tr")
        self.stateElement = tr

    def createNewState(self, klass, name, attrs, style=None):
        newState = klass(self, name, attrs, style=style)
        if isinstance(newState, tableCellState):
            self.__cells.append(newState)
        return newState
    
    def closingState(self):
        pass



class tableCellState(stateObject):
    def __init__(self, parentState, name, atts, style=None):
        self.__isHeaderCell = False
        self.__cellElement = None
        stateObject.__init__(self, parentState, name, atts)
    
    
    def __getCellElement(self):
        return self.__cellElement
    cellElement = property(__getCellElement)
    
    
    def processElement(self, name, attrs):
        # Find the parent rowState
        name = attrs.get("table:style-name", "")
        self.style = self.o.styles.getOooStyle(name)
        name = self.nameTranslate(name)
        
        vAlign = self.style.verticalAlign
        if self.parentState.isHeaderRow:
            self.__isHeaderCell = True
            eName = "th"
        else:
            eName = "td"
        e = element(eName)
        
#        e.setAttribute("valign", vAlign)
        eStyle = ""
        if vAlign:
            eStyle = "vertical-align: %s; " % vAlign 
        rowsSpan = attrs.get("table:number-rows-spanned", "")
        if rowsSpan!="":
            e.setAttribute("rowspan", rowsSpan)
        eStyle += self.o.styles.getCssStyle(eName)
        
        eStyle += self.o.styles.getCssStyle("%s.%s" % (eName, name))
        relist=eStyle.split(";")
        
        eStyle=""
        for r in relist:
            try:
                match=r.split(":")
                #those converted border value that is less than 1 px will be replaced
                originalBorder = match[1].split(" ")[0] 
                converted = self.convertUnits(originalBorder)
                if int(converted) <= 1:
                    match[1] = match[1].replace(originalBorder, "1.0px")
                merge = "%s:%s" % (match[0], match[1])
                eStyle += merge + "; "                   
            except:
                if r.strip() != "":
                    eStyle += r + "; "                  
                pass
        e.setAttribute("style", eStyle)
        if name!="":
            e.setAttribute("class", name)
        colspan = attrs.get("table:number-columns-spanned", "")
        if colspan!="":
            e.setAttribute("colspan", colspan)
        self.stateElement = e
        self.__cellElement = e
    
    
    def createNewState(self, klass, name, attrs, style=None):
        #print "createNewState name='%s' style='%s'" % (name, style)
        if style is not None and style.type=="Heading":
            style.resetType()   #style.type = ""
            if self.__isHeaderCell==False:
                self.__isHeaderCell = True
                e = element("th")
                for att in self.__cellElement.atts.values():
                    e.setAttribute(att)
                for n in self.__cellElement.items:
                    e.addChild(n)
                self.stateElement = e
                self.__cellElement = e
        newState = stateObject.createNewState(self, klass, name, attrs, style=style)
        return newState
    
    
    def closingState(self):
        """ do any state finalization/cleanup here """
        pass



class tableColumnState(stateObject):
    def __init__(self, parentState, name, atts, style=None):
        #self.__colgroup = None
        self.width = None
        stateObject.__init__(self, parentState, name, atts)
        #self.endOnClosingOooElement = False    # do not close this state on the closing oooElement
    
    
    def processElement(self, name, attrs):
        styleName = attrs.get("table:style-name", "")
        self.style = self.o.styles.getOooStyle(styleName)
        self.width = self.style.columnWidth
    
    
    def __addCol(self, s):
        if self.__colgroup is not None:
            col = element("col")
            self.__colgroup.addChild(col)
            width = self.style.columnWidth
            col.setAttribute("style", "width:%s;" % width)
    
    
    def closingState(self):
        """ do any state finalization/cleanup here """
        pass



class subTableState(tableState):
    def __init__(self, parentState, name, atts, style=None):
        #print "****** SubTable"
        tableState.__init__(self, parentState, name, atts)
    



