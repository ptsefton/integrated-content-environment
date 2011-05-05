#!/usr/bin/python
#
#    Copyright (C) 2009  Distance and e-Learning Centre,
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

"""
"""





class IceConversionServer(object):
    def __init__(self, iceContext):
        self.iceContext = iceContext
        # load converters.


    def convert(self, file, output, **options):
        """ if output is a string (assume it is a path/file string) and ends with '.zip'
                (or output is already a file)
                then output to a zipFile else output to that directory (and create if needed).
            else
                assume output is a response object
        """
        pass
    
    





if __name__ == '__main__':
    from ice_common import IceCommon
    import sys
    args = list(sys.argv)
    #outputWriter = IceCommon.outputWriter
    #retCode = main(args, sys, outputWriter)
    #sys.exit(retCode)
    print "ok"





