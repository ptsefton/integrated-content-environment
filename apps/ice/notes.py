#
#    Copyright (C) 2007  Distance and e-Learning Centre, 
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

## NOTES: (documentation) on ICE program 
"""
    IceRequest.processRequest(requestData, responseData)  [ice/ice_request.py]
            # gets/assign rep
            # tests for EditConfig
            # tests for Atom Feed
            # tests for logout
            # checks auth
            # test for special files
            .__processAjaxRequest(requestData, responseData, session, rep)
            OR
            .__processRequest(requestData, responseData, session, rep)
    IceRequest.__processRequest(requestData, responseData, session, rep)
            ice = self.__createIceSite(session, rep)        # creates an IceSite using rep
            data, mimeType = ice.serve(item, formData=requestData, session=session) #, formData=request.args
    
    
    icesite.serve(item, formData, session)              [sitemap/ice_site.py]
            .__serve(item)
    icesite.__serve(item)
           if ._isUrlIceContent(item):  # ICE content must have no extension or a .htm extension that 
                                        #   does not directly exist in the repository
                return .__serveIceContent(item)
            else:
                # All other files, images, PDF renditions etc
                return .__serveBinaryContent(item)
    icesite.__serveIceContent(item)
            # check for toc.htm or default.htm and set altURLs
            # self.__setup() - set self["xxx"] = xxx
            self.traverse()     #[site.py traverse()]
             self.__getManifest()
             self.__executeFunction()
             if needed: self.__default_htm()
             if needed: self.__toc_htm()
            self.__createToolbar()
            
            self.render()

"""

