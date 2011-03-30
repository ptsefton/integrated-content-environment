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



def processApiRequest(iceContext, requestContext):
    requestData = requestContext.requestData
    responseData = requestContext.responseData
    path = requestContext.path
    try:
        if path.startswith("/api/test/"):
            #print "-- Testing --"
            p = path[len("/api/test/"):]
            name = p.split("/", 1)[0]
            if name=="openid":
                OpenId = iceContext.getPlugin("ice.openid").pluginClass
                openId = OpenId(iceContext)
                openId.test(requestContext, iceContext)
            elif name=="access":
                RamAccess = iceContext.getPlugin("ice.ramAccess").pluginClass
                RamAccess.test(iceContext, requestContext)
            else:
                print "-- API Test '%s'" % name
                print "   no '%s' test registered!"
                xmlMsg = "<ice-error><description>404 '%s' not found!</description></ice-error>"
                xmlMsg = xmlMsg % path
                responseData.setResponse(xmlMsg, "text/xml")
            return True
        if path.startswith("/api/converter"):
            ###################################################################
            handler = iceContext.getPluginSingletonObject("ice.web.converter.handler")
            if handler is None:
                raise Exception("Handler for api converter not found!")
            handler.processRequest(requestData, responseData)
            ###################################################################
        elif path.startswith("/api/convert"):
            iceContext.iceServices.convert(requestData, responseData)
        else:
            xmlMsg = "<ice-error><description>404 '%s' not found!</description></ice-error>"
            xmlMsg = xmlMsg % path
            responseData.setResponse(xmlMsg, "text/xml")
        return True
    except Exception, e:
        msg = "Exception in processApiRequest: Error - '%s'\n" % str(e)
        if iceContext.output is not None:
            iceContext.output.write(msg)
        xmlError = "<ice-error><description>%s</description></ice-error>" % str(e)
        responseData.setResponse(xmlError, "text/xml")
        err = iceContext.formattedTraceback()
        print "---"
        print "Error in processApiRequest()"
        print err
        print "---"
        return True























