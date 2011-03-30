#
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



def processBinaryRequest(iceContext):
    #iceContext.writeln("processing binary request path='%s'" % path)
    item = iceContext.item
    data, mimeType = item.getBinaryContent()
    if data is None:
        data = "404 '%s' not found!" % item.uri
    if mimeType is None:
        print " Unknown (or not supported) mimeType for '%s'" % item.ext
        data = ""
    iceContext.responseData.setResponse(data, mimeType)
    return True








