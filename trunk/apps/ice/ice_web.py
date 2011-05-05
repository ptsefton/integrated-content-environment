#!/usr/bin/python
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

"""
"""

from ice_common import IceCommon

from ice_server import IceServer
from request_data import ServerRequestData
from response_data import ServerResponseData
from ice_request import IceRequest


def iceWebServer(IceCommon, options, outputWriter):
    iceContext = IceCommon.IceContext(options=options)
    iceContext.loadRepositories()
    settings = iceContext.settings
    asServiceOnly = bool(options.get("asserviceonly", 
                    settings.get("asServiceOnly", False)))
    enableExternalAccess = bool(options.get("enableexternalaccess", 
                    settings.get("enableExternalAccess", False)))
    port = int(options.get("port", options.get("p", iceContext.config.port)))
    settings["asServiceOnly"] = asServiceOnly
    settings["enableExternalAccess"] = enableExternalAccess
    webserver = options.get("webserver", settings.get("webServer", "default"))
    iceContext.isServer = options.get("server", settings.get("server", False))
    settings["webserver"] = webserver
    iceContext.config.setPort(str(port))
    if asServiceOnly:
        outputWriter("* asServiceOnly *\n")
    if enableExternalAccess:
        outputWriter("* external access enabled *\n")
    if iceContext.isServer:
        outputWriter("* running as a server!\n")
    iceServer = IceServer(iceContext, IceRequest, ServerRequestData, ServerResponseData)
    iceServer.serve()



def main(IceCommon, args, sys, outputWriter):
    shortOptionNames = {"h":"help", "f":"file", "d":"directory", "dir":"directory",
                        "converter":"convert", "v":"verbose", "test":"testing"}
    flags = ["help", "convert", "atompub", "atomconvertpub", "upgrade",
             "verbose", "asserviceonly", "enableexternalaccess", "test"]
    progName = args.pop(0)
    options = IceCommon.getOptions(args, shortOptionNames, flags)
    iceWebServer(IceCommon, options, outputWriter)
    outputWriter("\n")
    return 0


if __name__ == '__main__':
    import sys
    args = list(sys.argv)
    outputWriter = IceCommon.outputWriter
    retCode = main(IceCommon, args, sys, outputWriter)
    sys.exit(retCode)










