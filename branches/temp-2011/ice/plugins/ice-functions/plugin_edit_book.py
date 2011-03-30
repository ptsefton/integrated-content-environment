
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

""" """

pluginName = "ice.function.edit_book"
pluginDesc = "Book file editor"
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = editBook
    pluginClass = None
    pluginInitialized = True
    return pluginFunc



def editBook(self, file=None):
    BookEditor = self.iceContext.getPluginClass("ice.book.bookEditor")
    if BookEditor is not None:
        bookEditor = BookEditor(self.iceContext, self.formData, self.item, self.packageItem)
        html = bookEditor.edit()
        if html is not None:
            self.title = "Book editor"
            self.body = html
            self["javascript-files"].append("/skin/jquery-ui.js")
            #js = """ """
            #self["javascripts"].append(js)
        else:
            pass
editBook.options = {"toolBarGroup":"", "position":None, "postRequired":False,
                    "displayIf":False}









