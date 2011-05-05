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

import time


def processAjaxRequest(iceContext):
    requestData = iceContext.requestData
    rep = iceContext.rep
    session = iceContext.session
    path = iceContext.path
    item = iceContext.item
    
    mimeType = "text/html"
    ext = iceContext.fs.splitExt(path)[1]
    
    ajax = requestData.value("ajax")
    func = requestData.value("func")
    if func is None:
        func = ajax
    #print "Ajax request path='%s' func='%s' ajax='%s'" % (path, func, ajax)
    ## ============
    ajaxHandler = iceContext.ajaxHandlers.get(ajax)
    if ajaxHandler is not None:
        if callable(ajaxHandler):
            try:
                #print "*** ajaxHandler found ok ***"
                data, mimeType = ajaxHandler(iceContext)
            except Exception, e:
                data = "<div class='error'>Exception message: %s</div>" % iceContext.textToHtml(str(e))
        else:
            data = "<div>Ajax results. Error: ajaxHandler is not callable!</div>"
    elif requestData.value("json")!=None:
        # JSON request
        print "*Ajax  JSON request"
        #print "  %s" % requestData.__class__.__name__
        jscript = "alert('testing json');"
        data = jscript
    elif func=="file_manager":
        print "*FileManager ajax*" + str(requestData)
        data = "<div>Ajax results</div>"
    elif func=="inlineAnnotation":
        #print "\n** AJAX - inlineAnnotation"
        if True:
            formData = requestData
            itemPath = item.relPath
            if itemPath is None:
                itemPath = path
            username = session.username
            if username is None or username=="":
                username = iceContext.system.username
                #print "\nSetting username to '%s'" % username
            plugin = iceContext.getPlugin("ice.extra.inlineAnnotate")
            data = "???"
            if plugin:
                inlineAnnotations = plugin.pluginClass.getInlineAnnotations(item)
                data = inlineAnnotations.action(username, formData)
            else:
                data = "No 'ice.extra.inlineAnnotate' plugin found!"
    elif func=="workingStatusUpdate":
        #print "* AJAX workingStatusUpdate request *"
        job = session.asyncJob
        if job is None:
            data = iceContext.jsonWrite({"html":"", "next":None})
        else:
            next = 2000
            if job.isFinished: 
                session.asyncJob = None
                next = None
            if next is None:
                print "*** AJAX workingStatusUpdate job finished - message='%s'" % job.status.message
            if not job.isFinished:
                job.status.message += " ."
            else:
                job.status.message += ""
            data = iceContext.jsonWrite({"text":job.status.message, "next":next})
    elif func=="fileManager":
        #fileManager = 
        #data = fileManager.getContent()
        data = ""
    elif func=="oscar":
        testing = requestData.value("testing")
        data = "OSCAR ajax results"
        queryString = requestData.queryString
        #print "oscar ajax request '%s'" % queryString
        http = iceContext.Http()
        if requestData.value("img"):
            if testing:
                queryString = "inchi=InChI%3D1%2FC10H16N5O13P3%2Fc11-8-5-9(13-2-12-8)15(3-14-5)10-7(17)6(16)4(26-10)1-25-30(21%2C22)28-31(23%2C24)27-29(18%2C19)20%2Fh2-4%2C6-7%2C10%2C16-17H%2C1H2%2C(H%2C21%2C22)(H%2C23%2C24)(H2%2C11%2C12%2C13)(H2%2C18%2C19%2C20)%2Ft4-%2C6-%2C7-%2C10-%2Fm1%2Fs1%2Ff%2Fh18-19%2C21%2C23H%2C11H2"
            data = http.get("http://localhost:8181/ViewMol?" + queryString)
            mimeType = "image/png"
        else:
            if testing:
                queryString = "name=ATP&type=CM&smiles=Nc1ncnc2n(cnc12)[C%40%40H]3O[C%40H](COP(O)(%3DO)OP(O)(%3DO)OP(O)(O)%3DO)[C%40%40H](O)[C%40H]3O&inchi=InChI%3D1%2FC10H16N5O13P3%2Fc11-8-5-9(13-2-12-8)15(3-14-5)10-7(17)6(16)4(26-10)1-25-30(21%2C22)28-31(23%2C24)27-29(18%2C19)20%2Fh2-4%2C6-7%2C10%2C16-17H%2C1H2%2C(H%2C21%2C22)(H%2C23%2C24)(H2%2C11%2C12%2C13)(H2%2C18%2C19%2C20)%2Ft4-%2C6-%2C7-%2C10-%2Fm1%2Fs1%2Ff%2Fh18-19%2C21%2C23H%2C11H2&ontids=CHEBI%3A15422"
            data = http.get("http://localhost:8181/NEViewer?" + queryString)
            et = iceContext.ElementTree
            x = et.XML(data)
            d = x.find(".//BODY/DIV")
            d.tag = d.tag.lower()
            for e in d.findall(".//*"):
                e.tag = e.tag.lower()
                if e.tag=="list":
                    e.tag = "ul"
                    e.attrib = {}
            title = requestData.value("name", "")
            data = "<div><h2>%s</h2>%s</div>" % (title, et.tostring(d))
            mimeType = "text/html"
    elif func=="annotea":
        data, mimeType = dannotateFunction(iceContext, requestData)
    elif func=="jsontest":
        mimeType = "application/json"
        data = "{'jsontest':'ok', 'alist':['one', 'two', 'three', 'four']}"
        callback = requestData.value("callback", "")
        print "AJAX - jsontest (callback='%s')" % callback
        data = "%s(%s)" % (callback, data)
    elif func=="delay5":
        print "ajax delay5"
        time.sleep(5.1)
        print "  done"
        data = "delayed for 5 seconds"
    else:
        print
        print "*Ajax func='%s'  ajax='%s'" % (func, ajax)
        print "  ajaxHandlers=%s" % str(iceContext.ajaxHandlers.keys())
        data = "<div>Ajax results</div>"
    iceContext.responseData.setNoCacheHeaders()
    iceContext.responseData.setResponse(data, mimeType)
    return True


# Annotea protocol (Annotation protocols)
# Ref.  http://www.w3.org/2001/Annotea/User/Protocol.html
#  Posting - a new annotation
#    POST (the annotation RDF) to the annotation server web address /Annotation
#       response with status 201 Created if OK else 4xx error status code
#       HTTP/1.1 201 Created
#       Location: http://annotea.example.org/Annotation/3ACF6D754
#       Content-Type: application/xml
#       Content-Length: 432
#       <?xml version="1.0" ?>
#       <r:RDF xmlns:r="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
#          xmlns:a="http://www.w3.org/2000/10/annotation-ns#"
#          xmlns:d="http://purl.org/dc/elements/1.1/">
#        <r:Description r:about="http://annotea.example.org/Annotation/3ACF6D754">
#         <a:annotates r:resource="http://serv1.example.com/some/page.html"/>
#         <a:body r:resource="http://serv2.example.com/mycomment.html"/>
#        </r:Description>
#       </r:RDF>
#  Querying - an annotation server.
#    GET [serverWebAddress]/Annotation/?w3c_annotates=URI   -> RDF of rdf:Description(s)
#   For replies
#    GET [serverWebAddress]/Annotation/?w3c_reply_tree=URI
#   Or both together
#    GET [serverWebAddress]/Annotation/?w3c_annotates=URI&w3c_reply_tree=URI
#  Downloading - an annotation or its body
#    GET [serverWebAddress]/Annotation/[id]  or /Annotation/body/[id]
#  [Updating - an annotation]
#    PUT [serverWebAddress]/Annotation RDF   (Note: RDF data is replaced with the new RDF data)
#     -> 200 OK
#  Deleting - an annotation
#    DELETE [serverWebAddress]/Annotation/[id]
#     -> 200 OK

def dannotateFunction(iceContext, requestData):
    mimeType = "text/xml"
    http = iceContext.Http()
    session = iceContext.session
    dannoUrl = "http://localhost:8080/danno/annotea/"
    data = "Dannotate Ajax response"
    method = requestData.value("method")
    #print "** dannotate ** method='%s'" % method
    d = requestData.value("data")
    u = requestData.value("url", "")
    if u.startswith(dannoUrl):
        pass
    else:
        u = dannoUrl + u
    if method=="get":
        data = http.get(u)
        data = data.strip()
        if data.startswith("&lt;"):
            data = data.replace("&lt;", "<").replace("&gt;", ">")
        #print "get - url='%s' data=" % u
        #print data
        #print "  data='%s'" % data
    elif method=="delete":
        data = http.delete(u)
    elif method=="put":
        data = http.put(u, data)
    elif method=="post":
        data = http.post(u, data)
    elif method=="getRootAnnos" or method=="getReplies" or method=="getAnnos":
        # "?w3c_annotates="
        # "?w3c_reply_tree="
        rdfns = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"
        dcns = "{http://purl.org/dc/elements/1.1/}"
        rdfStr = http.get(u)
        ET = iceContext.ElementTree
        rdf = ET.XML(rdfStr)
        j = []
        for desc in rdf.findall(rdfns + "Description"):
            selfUrl = dict(desc.items()).get(rdfns+"about", "")
            bodyUrl = ""
            rootUrl = ""
            inReplyToUrl = ""
            annotates = ""
            creator = ""
            created = ""
            for n in desc.getchildren():
                name = n.tag.split("}")[-1]
                if name=="creator":
                    creator = n.text
                elif name=="created":
                    created = n.text
                elif name=="context":
                    xp = n.text.split("#")[1]
                    annotates = xp.split('id("')[1].split('")')[0]
                elif name=="body":
                    bodyUrl = dict(n.items()).get(rdfns+"resource", "")
                elif name=="root":
                    rootUrl = dict(n.items()).get(rdfns+"resource", "")
                elif name=="inReplyTo":
                    inReplyToUrl = dict(n.items()).get(rdfns+"resource", "")
            if inReplyToUrl!="":
                annotates = inReplyToUrl
            if rootUrl=="":
                rootUrl = selfUrl
            j.append({"selfUrl":selfUrl, "bodyUrl":bodyUrl, "rootUrl":rootUrl,
                        "inReplyToUrl":inReplyToUrl, "annotates":annotates,
                        "creator":creator,  "created":created})
        data = iceContext.jsonWrite(j)
        mimeType = "application/json"
    elif method=="getReplies":
        d = http.get(u)
        d = d.strip()
        if d.startswith("&lt;"):
            d = d.replace("&lt;", "<").replace("&gt;", ">")
        d = {"replies":"?"}
        data = iceContext.jsonWrite(d)
        mimeType = "application/json"
    elif method=="add":
        #"inReplyToUrl"
        formData = requestData
        username = session.username
        if username is None or username=="":
            username = iceContext.system.username
        text = formData.value("text")
        paraId = formData.value("paraId")  # if None then a reply
        inReplyToUrl = formData.value("inReplyToUrl")
        rootUrl = formData.value("rootUrl")
        html = formData.value("html")
        print "dannotate add"
        #print "  %s, %s" % (username, path)
        print "  %s" % requestData.urlPath
        print "  paraId='%s', text='%s'" % (paraId, text)
        print "  rootUrl='%s', inReplyToUrl='%s'" % (rootUrl, inReplyToUrl)
        #print "  html='%s'" % html
        data = "invalid"
        if True:
            reply = dannotate(iceContext, requestData.urlPath, paraId,
                text, creator=username, rootUrl=rootUrl,  inReplyToUrl=inReplyToUrl)
            try:
                url = reply.split(':about="')[1].split('"', 1)[0]
            except:
                print "reply='%s'" % reply
                url = ""
            print "url='%s'" % url
            data = url
        print
    elif method=="close":
        pass
    return data, mimeType


def dannotate(iceContext, annotates, id, annotation, creator,
        date=None, bodyTitle="", title="", annotationType="Comment",
        rootUrl=None,  inReplyToUrl=None):
    # annotationType(s) = SeeAlso, Question, Explanation, Example, Comment,
    #           Change, Advice
    xpointer = annotates + '#xpointer(id("%s"))' % id
    if date is None:
        date = time.strftime("%Y-%m%dT%H:%M")
        if time.timezone>0:
            date += "-"
        else:
            date += "+"
        date += time.strftime("%H:%M", (0,0,0, abs(time.timezone/3600), 0,0,0,0,0))
    created = date
    bodyContent = annotation
    if title=="":
        title = annotationType
    if bodyTitle=="":
        bodyTitle = title
    # annotationType - Comment
    # annotates - http://serv1.example.com/some/page.html
    # (context)xpointer -  http://serv1.example.com/some/page.html#xpointer(id("Main")/p[2])
    # title - ''
    # creator - Fred
    # created - 1999-10-14T12:10Z
    # date - 1999-10-14T12:10Z
    # bodyTitle -
    # bodyContent -
    rdf = """<?xml version="1.0" ?>
<r:RDF xmlns:r="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
       xmlns:a="http://www.w3.org/2000/10/annotation-ns#"
       xmlns:d="http://purl.org/dc/elements/1.1/"
       xmlns:h="http://www.w3.org/1999/xx/http#">
 <r:Description>
  <r:type r:resource="http://www.w3.org/2000/10/annotation-ns#Annotation"/>
  <r:type r:resource="http://www.w3.org/2000/10/annotationType#%s"/>
  <a:annotates r:resource="%s"/>
  <a:context>%s</a:context>
  <d:title>%s</d:title>
  <d:creator>%s</d:creator>
  <a:created>%s</a:created>
  <d:date>%s</d:date>
  <a:body>
   <r:Description>
    <h:ContentType>text/html</h:ContentType>
    <h:Body r:parseType="Literal">
     <html xmlns="http://www.w3.org/1999/xhtml">
      <head>
       <title>%s</title>
      </head>
      <body>
        %s
      </body>
     </html>
    </h:Body>
   </r:Description>
  </a:body>
 </r:Description>
</r:RDF>"""
#    <h:ContentLength>289</h:ContentLength>
    replyType = annotationType  #"Comment" or "SeeAlso", "Agree", "Disagree", "Comment"
    #rootUrl = ""
    #inReplyToUrl = ""
    #title = ""
    #creator = ""
    #created = ""
    #date = ""
    #bodyTitle = ""
    #bodyContent = ""
    rRdf = """<?xml version="1.0" ?>
<r:RDF xmlns:r="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
       xmlns:a="http://www.w3.org/2000/10/annotation-ns#"
       xmlns:d="http://purl.org/dc/elements/1.1/"
       xmlns:tr="http://www.w3.org/2001/03/thread#"
       xmlns:h="http://www.w3.org/1999/xx/http#"
       xmlns:rt="http://www.w3.org/2001/12/replyType">
 <r:Description>
  <r:type r:resource="http://www.w3.org/2001/03/thread#Reply"/>
  <r:type r:resource="http://www.w3.org/2001/12/replyType#%s"/>
  <tr:root r:resource="%s"/>
  <tr:inReplyTo r:resource="%s"/>
  <d:title>%s</d:title>
  <d:creator>%s</d:creator>
  <a:created>%s</a:created>
  <d:date>%s</d:date>
  <a:body>
   <r:Description>
    <h:ContentType>text/html</h:ContentType>
    <h:Body r:parseType="Literal">
     <html xmlns="http://www.w3.org/1999/xhtml">
      <head>
       <title>%s</title>
      </head>
      <body>
        %s
      </body>
     </html>
    </h:Body>
   </r:Description>
  </a:body>
 </r:Description>
</r:RDF>"""
    http = iceContext.Http()
    dannoUrl = "http://localhost:8080/danno/annotea"

    if inReplyToUrl is None or inReplyToUrl=="":
        rdf = rdf % (annotationType, annotates, xpointer, title, creator,
                created, date, bodyTitle, bodyContent)
    else:
        if rootUrl is None:
            rootUrl = inReplyToUrl
        rdf = rRdf % (replyType, rootUrl, inReplyToUrl, title, creator,
                created, date, bodyTitle, bodyContent)
    reply = http.post(dannoUrl, data=rdf)
    return reply




