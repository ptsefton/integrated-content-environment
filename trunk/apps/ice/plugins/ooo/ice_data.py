#
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

from cPickle import loads, dumps
from base64 import encodestring, decodestring


class DataClass(object):
    def decodeData(edata):
        """ recreate DataClass object from encodedData """
        pdata = decodestring(edata)
        data = loads(pdata)
        return data
    decodeData = staticmethod(decodeData)
    
    def getEncodedData(self):
        pdata = dumps(self)
        edata = encodestring(pdata).replace("\n", "").replace("\r", "")
        return edata
    
    def __str__(self):
        s = "[DataClass object]"
        for k, v in self.__dict__.iteritems():
            s += "\n  %s = %s" % (k, v)
        return s
    
    


