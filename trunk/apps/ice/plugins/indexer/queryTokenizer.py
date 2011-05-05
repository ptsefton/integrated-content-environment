#    Copyright (C) 2008  Distance and e-Learning Centre, 
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


class QueryTokenizer(object):
    def __init__(self, queryText):
        self.__tokens = []
        # states = None, or a bracket state of "[" or "(" or "{" or '"'
        self.__chars = list(queryText)
        self.__chars.append(None)
        self.__process()
    
    @property
    def tokens(self):
        return self.__tokens
    
    
    def extractTag(self, tagName):
        tagTokens = []
        if not tagName.endswith(":"):
            tagName += ":"
        for token in self.__tokens:
            if token.find(tagName)!=-1:
                tagTokens.append(token)
        for tt in list(tagTokens):
            i = self.__tokens.index(tt)
            x = tagTokens.index(tt)
            if tt.endswith(":"):
                try:
                    t = self.__tokens.pop(i+1)
                    tagTokens[x] += t
                except: pass
            if i>0:
                if self.__tokens[i-1]=="+":
                    self.__tokens.pop(i-1)
                    tagTokens[x] = "+" + tagTokens[x]
        self.__tokens = [t for t in self.__tokens if t.find(tagName)==-1]
        return tagTokens
    
    
    #### Private methods ####
    def __getNextChar(self):
        chars = self.__chars
        if chars[0] is None:
            return None
        char = chars.pop(0)
        if char=="&":
            if chars[0]=="&":
                char += chars.pop(0)
        elif char=="|":
            if chars[0]=="|":
                char += chars.pop(0)
        elif char.isspace():
            char = " "
            while(chars[0] is not None and chars[0].isspace()):
                chars.pop(0)
        elif char=="\\":
            char += chars.pop(0)
        return char
    
    
    def __process(self):
        while True:
            token = self.__getNextToken()
            if token is None:
                break
            self.__tokens.append(token)
    
    
    def __getNextToken(self, endChar=None):
        chars = self.__chars
        sepChars = ["+", "-", "!", "&&", "||", " ", None]
        openBrkChars = ['"', "(", "{", "["]
        closeBrkChars = ['"', ")", "}", "]"]
        specialChars = sepChars + openBrkChars + closeBrkChars
        token = self.__getNextChar()
        if token in sepChars:
            return token
        #if token in closeBrkChars:
        #    return token
        if token==endChar:
            return token
        if token in openBrkChars:
            closingChar = closeBrkChars[openBrkChars.index(token)]
            while True:
                t = self.__getNextToken(closingChar)
                if t is None:
                    break
                token += t
                if t==closingChar:
                    break
            return token
        while True:
            char = self.__getNextChar()
            if char in specialChars:
                if char is None:
                    break
                # put it back
                chars.insert(0, char)
                break
            token += char
        return token



