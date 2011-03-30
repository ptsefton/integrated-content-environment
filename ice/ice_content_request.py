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



def processContentRequest(iceContext):
    requestData = iceContext.requestData
    responseData = iceContext.responseData
    session = iceContext.session
    item = iceContext.item
    ext = item.ext
    path = iceContext.path
    mimeType = "text/html"

    try:
        # log all request except '/favicon.ico', '/skin/*', or with a extension of *
        if path!="/favicon.ico" and path.find("/skin/")==-1 and \
                ext not in [".png", ".gif", ".jpg"]:
            iceContext.logger.iceInfo(str(requestData).replace("%", "%%"))
        
        # Serve
        ice = createIceSite(iceContext)
        if ice is None:
            raise Exception("Failed to createIceSite")
        iceContext.iceSite = ice
        r = ice.serve(item)
        ice = None
        try:
            data, mimeType, downloadFilename = r[:3]
        except:
            data, mimeType = r[:2]
            downloadFilename = None
        if mimeType=="ChangeRep":
            # HACK for changed to a repository that needs to be checkout (with login) first
            session.workingOffline = False
            if session.get("xhtmlTemplateFilename") is not None:
                session.pop("xhtmlTemplateFilename")
            redirectUrl = "/rep.%s/" % r[0]
            responseData.setRedirectLocation(redirectUrl)
            #return self.processRequest(requestData, responseData)    #, request
            return processContentRequest(iceContext, path)
        elif mimeType=="error":
            if iceContext.output is not None:
                iceContext.output.write("ChangeRepository error - %s\n" % data)
            mimeType = "text/html"
        if downloadFilename is not None:
            if mimeType is None or mimeType=="":
                mimeType = iceContext.getMimeTypeFor(downloadFilename)
            if data is None:
                data = iceContext.fs.readFile(downloadFilename)
                if data is None:
                    raise Exception("downloadFilename is '%s', but data is None!" % downloadFilename)
            downloadName = iceContext.fs.split(downloadFilename)[1]
            responseData.setDownloadFilename(downloadName)
        responseData.setResponse(data, mimeType)
    except iceContext.RedirectException, e:
        responseData.setRedirectLocation(e.redirectUrl)
        return True
    except Exception, e:
        iceContext.logger.exception("Unhandled exception in iceRequest.processRequest()")
        html = "<div style='color:red;padding:1em;'>ERROR: Unhandled exception in iceRequest.processRequest() - %s</div>" % str(e)
        err = iceContext.formattedTraceback(lines=1)
        html = iceContext.textToHtml(err) + "\n<br/><hr/>Stack trace<hr/>\n"
        
        html += iceContext.textToHtml(str(err)) + "<br/>\n"
        html += iceContext.textToHtml(str(e)) + "<br/>"
        responseData.setResponse(html)
    iceContext.logger.flush()
    # check if we need to return a 404
    if item.uriNotFound:
        pass
        #print "Not Found!"
        #responseData.notFound = True
    return True


def createIceSite(iceContext):
    siteData, new, filename = __getSiteData(iceContext)
    
    rep = iceContext.rep
    if new:
        iceSite = execSiteData(iceContext.rep.iceContext, siteData, filename)
        iceContext.iceFunctions = iceContext.rep.iceContext.iceFunctions
        rep.tags["iceSite"] = iceSite
    else:
        iceSite = rep.tags.get("iceSite")
    if iceSite is None:
        return None
    
    ice = iceSite(iceContext)
    ice.includeSource = bool(iceContext.settings.get("includeSource", False))
    return ice


# a callback method for the repository to use to create it's site class
#  NOTE: this is exported (Used by ice_request.py)
def execSiteData(iceContext, data, filename):
    site = None
    try:
        iceContext.reloadIceFunctions()
        iceContext
        global IceSite
        IceSite = iceContext.IceSite
        try:
            exec data
        except Exception, e:
            if len(data)>1:
                print "Warning: repositories '%s' file is not valid - '%s'" % (filename, str(e))
            else:
                raise e
        site = IceSiteMap
    except Exception, e:
        if iceContext.output is not None:
            iceContext.output.write("* ice_request.__execSiteData() %s\n" % str(e))
        site = iceContext.IceSite
        site.errorMessage = "Error: " + str(e)
    return site


def __getSiteData(iceContext):
    rep = iceContext.rep
    filename = rep.tags.get("siteFilename", None)
    data = None
    isNew = False
    if filename is not None:
        item = rep.getItem(filename)
        mDateTime = item.lastModifiedDateTime
        if mDateTime==rep.tags.get("siteFileDateTime", None):
            # has not changed
            data = rep.tags.get("siteData", None)
    if data is None:
        #print "data is None"
        for filename in [("/.site/site%s.py" % n) for n in ["2.1"]]:  #["2.0", "1.3", "1.0", ""]]:
            #print "  filename='%s'" % filename
            data = rep.getItem(filename).read()
            if data is not None:
                item = rep.getItem(filename)
                mDateTime = item.lastModifiedDateTime
                if iceContext.output is not None:
                    if rep.tags.has_key("siteData"):
                        iceContext.output.write("reloading site from %s\n" % rep.getAbsPath(filename))
                    else:
                        iceContext.output.write("loading site from %s\n" % rep.getAbsPath(filename))
                rep.tags["siteFilename"] = filename
                rep.tags["siteFileDateTime"] = mDateTime
                rep.tags["siteData"] = data
                isNew = True
                break
    filename = rep.tags.get("siteFilename")
    return data, isNew, filename
    



