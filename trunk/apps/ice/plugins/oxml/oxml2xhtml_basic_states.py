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


class NullState(BaseState):
    pass


class DocumentState(BaseState):
    pass


class BodyState(BaseState):
    pass


class ParaState(BaseState):     # Heading, BlockQuote, DT, DD, Lists, etc...
    def __init__(self, parentState, name=None, attrs={}):
        BaseState.__init__(self, parentState, name, attrs)
        self.__pLastChild  = self.parentState._currentHtmlElement.getLastChild()
        self._currentHtmlElement = self._currentHtmlElement.addChildElement("p")
        self._numId = ""
        self._nestedLevel = ""

    def startElement(self, name, attrs):
        if name=="w:bookmarkStart":
            bookmarkId = attrs.get("w:id")
            bookmarkName = attrs.get("w:name")
            prefix = self._oxml.idPrefix + self._oxml.bookmarkPrefix
            self._currentHtmlElement.addAttribute("id", prefix + bookmarkName)
        elif name=="w:bookmarkEnd":
            bookmarkId = attrs.get("w:id")

    def endState(self):
        style = self._style or ""
        pce = self.parentState._currentHtmlElement
        e = self._currentHtmlElement
        if style.startswith("Heading"):
            style = "h" + style[-1]
        if style.startswith("h"):
            e.name = style
        elif style.startswith("bq"):
            level = int(style[2])
            e.name = "blockquote"
            e.setAttribute("class", "bq level%s %s" % (level, style))
            e = e.addChildElement("p")
        elif style.startswith("dt") or style.startswith("dd"):
            try:
                level = int(style[2])
            except:
                level = 0
            ename = style[:2]
            if self.__pLastChild and self.__pLastChild.name=="dl":
                dl = self.__pLastChild
            else:
                dl = pce.addChildElement("dl")
            e.name = ename
            e.setAttribute("class", "%s level%s" % (style, level-1))
            #e = dl.addChildElement(ename, {"class": "%s level%s" % (style, level-1)})
            dl.addChild(e)
        elif style.startswith("li") or style=="ListParagraph":
            listType = "ol"         # default
            attStyle = ""
            if style=="ListParagraph":      # Word lists
                #self._numId
                level = self._nestedLevel
                ltype = style
                info = self._oxml.numbering.getNumLevelInfo(self._numId, level)
                format = info.get("format", "")
                try:
                    leftIndent = info.get("leftIndent", "0")
                    leftIndent = int(int(leftIndent)/180)
                    attStyle += "padding-left:%sex;" % leftIndent
                except:
                    pass
                if format=="bullet":
                    listType = "ul"
                    classStyle = "ulb"
                elif format=="decimal":
                    classStyle = "lin"
                elif format=="lowerLetter":
                    classStyle = "lia"
                elif format=="lowerRoman":
                    classStyle = "lii"
                elif format=="upperLetter":
                    classStyle = "liA"
                elif format=="upperRoman":
                    classStyle = "liI"
                else:
                    classStyle = style
            else:
                level = int(style[2])
                ltype = style[3]
                classStyle = style[:2] + style[3]
                if ltype=="b":
                    listType = "ul"
            # Find the pe(parent element) that we should be attacting to
            def isListElement(e):
                return e and (e.name=="ol" or e.name=="ul")
            pListElems = []
            pLastChild = self.__pLastChild          # __pLastChild = parentState htmlElement lastChild
            while isListElement(pLastChild):        # find the depthest listElement first
                pListElems.insert(0, pLastChild)    # process depthest first
                try:
                    #pLastChild = ul/li:last/ul:last
                    pLastChild = pLastChild.getLastChild().getLastChild()
                except:
                    break
            #print "pListElems='%s'" % len(pListElems)
            listElem = None
            for listE in pListElems:
                if listE.tag==style + self._numId + self._nestedLevel:
                    listE.addChildElement("li").addChild(e)
                    listElem = listE
                    break
                else:
                    if level>listE.tagLevel:
                        li = listE.getLastChild()
                        ## add to listItem or add to listItem's p element
                        addTo = li      # add to the listItems
                        # or add to the listItem's p element
                        # p = li.getLastChild()
                        # addTo = p
                        ## NOTE: also the while loop above needs to be changed
                        ##    #pLastChild = ul/li:last/p:last/ul:last
                        ##    pLastChild = pLastChild.getLastChild().getLastChild().getLastChild()
                        ##
                        newListElem = addTo.addChildElement(listType, {"class":classStyle})
                        newListElem.tag = style + self._numId + self._nestedLevel
                        newListElem.tagLevel = level
                        newListElem.addChildElement("li").addChild(e)
                        listElem = newListElem
                        break
            if listElem is None:
                # create a new top-level list element
                newListElem = pce.addChildElement(listType, {"class":classStyle})
                newListElem.tag = style + self._numId + self._nestedLevel
                newListElem.tagLevel = level
                newListElem.addChildElement("li").addChild(e)
        elif style=="Title":
            e.name = "h1"
            e.setAttribute("class", "title")
            if self.html.title=="":
                self.html.title = e.text
        elif style=="p-center":
            e.setAttribute("class", "centered")
        elif style=="p-right":
            e.setAttribute("class", "right-aligned")
        elif style=="p-indent":
            e.setAttribute("class", "indented")
        elif style.startswith("pre"):
            level = 0
            try:
                level = int(style[3])
            except:
                pass
            e.name = "pre"
            e.setAttribute("class", "pre level%s" % level)
        else:
            pass
        # return False if endState is canceled
        return True

    def __processList(self):
        pass



class ParaPropState(BaseState):
    # w:pPr
    def __init__(self, parentState, name=None, attrs={}):
        BaseState.__init__(self, parentState, name, attrs)

    def startElement(self, name, attrs):
        if name=="w:pStyle":
            self._style = attrs.get("w:val", "")

    def endState(self):
        p = self.parentState
        p._style = self._style
        # return False if endState is canceled
        return True


class ParaNumPropState(BaseState):
    def __init__(self, parentState, name=None, attrs={}):
        BaseState.__init__(self, parentState, name, attrs)

    def startElement(self, name, attrs):
        if name=="w:numId":
            val = attrs.get("w:val", "")
            p = self.parentState.parentState
            p._numId = val
        elif name=="w:ilvl":
            val = attrs.get("w:val", "0")
            p = self.parentState.parentState
            p._nestedLevel = val



class RunState(BaseState):      # inline
    def __init__(self, parentState, name=None, attrs={}):
        BaseState.__init__(self, parentState, name, attrs)
        self._styles = []

    def startElement(self, name, attrs):
        if name=="w:br":
            self._text += "\n"
        elif name=="w:tab":
            self._text += "\t"

    def endState(self):
        ce = self._currentHtmlElement
        text = self._text
        children = []
        # HACK - treat code as pre-formatted ???
        if "code" in self._styles:
            t = self._html.createText(text)
            t = str(t)
            t = t.replace("\n", "<br/>").replace("\t", "&#160;"*4)
            text = self._html.createRawText(t)
            children.append(text)
        elif text.find("\n")==-1:  # no new lines found
            children.append(text)
        else:
            lines = text.split("\n")
            children.append(lines.pop(0))
            for line in lines:
                #ce.addChildElement("br")
                children.append(self.html.createElement("br"))
                children.append(line)
        # HACK - megre sibling code elements into one ???
        if len(self._styles)==1 and ce.getLastChild().name==self._styles[0]:
            ce = ce.getLastChild()
        else:
            for style in self._styles:
                ce = ce.addChildElement(style)
        for child in children:
            ce.addChild(child)

        # return False if endState is canceled
        return True

    def addStyle(self, style):
        self._styles.append(style)



class RunPropState(BaseState):
    # w:rPr
    def __init__(self, parentState, name=None, attrs={}):
        BaseState.__init__(self, parentState, name, attrs)

    def startElement(self, name, attrs):
        p = self.parentState
        styleName = None
        if name=="w:rStyle":
            name = attrs.get("w:val", "")
            if name=="i-code":
                styleName = "code"
            elif name=="i-sub":
                styleName = "sub"
            elif name=="i-sup":
                styleName = "sup"
        elif name=="w:b":
            styleName = "b"
        elif name=="w:i":
            styleName = "i"
        if styleName is not None:
            p.addStyle(styleName)

    def endState(self):
        # return False if endState is canceled
        return True



class TextState(BaseState):
    # r:t
    def __init__(self, parentState, name=None, attrs={}):
        BaseState.__init__(self, parentState, name, attrs)

    def characters(self, text):
        self.parentState._text += text



class HyperlinkState(BaseState):
    # w:hyperlink
    def __init__(self, parentState, name=None, attrs={}):
        BaseState.__init__(self, parentState, name, attrs)
        ce = self._currentHtmlElement
        aName = attrs.get("w:anchor")
        rId = attrs.get("r:id")              #="rId5"
        if aName:
            prefix = self._oxml.idPrefix + self._oxml.bookmarkPrefix
            href = "#" + prefix + aName
            ce = ce.addChildElement("a", href=href)
        else:
            docRels = self._oxml.docRels
            target, tMode = docRels.getTarget(rId), docRels.getTargetMode(rId)
            ce = ce.addChildElement("a", href=target)
            if tMode.lower()=="external":
                ce.addAttribute("type", "external")
        self._currentHtmlElement = ce

    def endState(self):
        # return False if endState is canceled
        return True



class IgnoreState(BaseState):
    pass

class UnknownState(BaseState):
    def __init__(self, parentState, name=None, attrs={}):
        BaseState.__init__(self, parentState, name, attrs)

    def startElement(self, name, attrs):
        pass
    
    def characters(self, text):
        pass

    def endState(self):
        # return False if endState is canceled
        return True

class SectPropState(BaseState):
    def __init__(self, parentState, name=None, attrs={}):
        BaseState.__init__(self, parentState, name, attrs)

    def endState(self):
        # return False if endState is canceled
        return True







