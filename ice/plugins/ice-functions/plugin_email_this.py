
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
import re
from smtplib import SMTPAuthenticationError

from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from smtplib import SMTP


pluginName = "ice.function.emailThis"
pluginDesc = ""
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    global templatePath
    path = iceContext.fs.split(__file__)[0]
    templatePath = iceContext.fs.join(path, "email.tmpl")
    pluginFunc = mailThis
    pluginClass = None
    pluginInitialized = True
    return pluginFunc



def mailThis(self):
    """Very simple document mailer. Needs work to integrate with config system and deal with remote images"""
    settings = self.iceContext.settings
    isClient = not self.iceContext.isServer
    self.isDocContentView = False
    
    if isClient:
        
        smtpServer = settings.get("emailSmtpServer")
        fromAddress = settings.get("emailFromAddress").strip()
        username = settings.get("emailUsername")
        subject = self.item.getMeta("title", "[Untitled] '%s'" % self.item.name)
        toAddress = settings["emailToAddress"]
        #Check if fromAddress looks OK
        invalidFromAddress = re.search("[\w.-]+\@[\w-]+\.[\w]+", fromAddress) is None
        invalidSmtpServer = re.search("\.", smtpServer) is None or len(smtpServer)<5
        configError = False
        configErrorMessage = ""
        if invalidFromAddress or invalidSmtpServer:
            configError = True
            if invalidSmtpServer:
                configErrorMessage = "The SMTP server is not set! &#160;"
            if invalidFromAddress:
                configErrorMessage += " The email FromAddress is not valid!"
        self.title = "Email"
        d = {"isClient": isClient,
             "username": username,
             "password": "",
             "from": fromAddress,
             "to": "",
             "subject": subject,
             "configError": configError,
             "configErrorMessage": configErrorMessage
             }
    else:
        #if server
        smtpServer = settings.get("emailSmtpServer")
        username = self.iceContext.session.username
        fromAddress = username + "@usq.edu.au"
        toAddress = fromAddress
        subject = ""
        configError = False
        configErrorMessage = ""
        self.title = "Email"
        d = {"isClient": isClient,
             "username": "",
             "password": "",
             "from": fromAddress,
             "to": toAddress,
             "subject": subject,
             "configError": configError,
             "configErrorMessage": configErrorMessage
             }
    
    
    d["templates"] = self.rep.getSkinTemplates(["/", self.packagePath])
    template = self.session.get("xhtmlTemplateFilename", "default")
    postback = self.formData.has_key("postback")
    if postback:
        template = self.formData.value("template")
        if template == "default":
            template = "template.xhtml"
        else:
            template = "templates/%s.xhtml" % template
        
        if self.formData.has_key('to'):
            d["to"] = self.formData.value('to').strip()
        if self.formData.has_key('from'):
            d["from"] = self.formData.value('from').strip()
        if self.formData.has_key('smtp'):
            smtpServer = self.formData.value('smtp').strip()
        if self.formData.has_key("username"):
            d["username"] = self.formData.value("username").strip()
        if self.formData.has_key("password"):
            d["password"] = self.formData.value("password")
        if self.formData.has_key("subject"):
            d["subject"] = self.formData.value("subject").strip()
        
        #Check that we have all the params needed to send mail
        if d["subject"]=="":
            d["subject"] = subject
        if d["to"]==None:
            d["to"] = toAddress
            if d["to"]==None: d["to"]=""
            
        if d["to"]=="" and not isClient:
            d["to"] = d["from"]
        #If anything is missing, put up a form #TODO add values from config file
        if d["to"]=="" or d["from"]=="" or d["subject"]=="":
            d["error"] = "Please check that the <em>From</em>, <em>To</em> and <em>Subject</em> fields are filled in correctly."
        else:
            images = {}
            htmlContent = ""
            altContent = "This is the alternative plain text message."
            
            x = self.iceContext.Xml(self.render(self.iceContext, template))
            
            # Get images
            imageIndexes = dict()
            nextIndex = 0
            for img in x.getNodes("//*[local-name()='img']"):
                path = img.getAttribute("src")
                if imageIndexes.has_key(path):
                    thisIndex = imageIndexes[path]
                    img.setAttribute("src",  "cid:image%s" % thisIndex)
                else:
                    nextIndex += 1
                    imageIndexes[path] = nextIndex
                    thisIndex = nextIndex
                if path.rfind("_files") > 0: #Image stored as svn property
                    # get image data
                    imageName = self.iceContext.fs.split(path)[1]
                    data = self.rep.getItemForUri(self.path).getImage(imageName)
                else: #img on disk
                    docPath = self.iceContext.fs.split(self.path)[0]
                    dataPath = self.iceContext.fs.join(docPath, path)
                    data = self.rep.getItem(dataPath).read()
                if data!=None:
                    images[thisIndex] = data
                    img.setAttribute("src",  "cid:image%s" % thisIndex)
                else:
                    # Remove the image because we do not have any data for it
                    img.removeAttribute("src")
                
            # HACK: add a empty table to the end of the document to get the inline css to work! re:#3779
            htmlNode = x.getRootNode()
            table = x.xmlStringToElement("<table><tr><td/></tr></table>")
            htmlNode.addChild(table)
            
            htmlContent = str(x.getRootNode())
            x.close()
            try:
                if True:
                   __sendEmail(self, smtpServer, d["to"], d["from"], d["subject"], \
                        htmlContent, altTextContent=altContent, images=images, \
                        username=d["username"], password=d["password"])
                else:
                    print "-----------------------"
                    print " ***  Email Testing *** "
                    msg = "smtpServer='%s', toAddress='%s', fromAddress='%s', subject='%s'"
                    msg = msg % (smtpServer, d["to"], d["from"], d["subject"])
                    print msg
                    print "-----------------------"
                    raise Exception("Just testing")
                d["success"] = True
            except SMTPAuthenticationError:
                d["error"] = "Failed to authenticate. Invalid username or password."
            except Exception,e:
                print str(e)
                print smtpServer
                d["error"] = "Failed to connect. Please check your email server settings."
    
    selected = self.iceContext.fs.splitPathFileExt(template)[1]
    d["selected"] = selected
    htmlTemplate = self.iceContext.HtmlTemplate(templatePath)
    self["page-toc"] = ""
    self["body"] = htmlTemplate.transform(d, allowMissing=True)

def isDocView(self):
    return self.isDocView

def isClient(self):
    return not self.iceContext.isServer

mailThis.options = {"toolBarGroup":"publish", "position":60, "postRequired":True,
                    "label":"Email", "title":"Email this", "enableIf":isDocView, "displayIf":isClient}
#

def __sendEmail(self, smtpServer, toAddress, fromAddress, subject="",
            htmlContent="", altTextContent="", images={},
            username=None, password=None, testing=False):
    toAddressList = re.split("[ ,;\t\n\r]+", toAddress)
    toAddressList = [add for add in toAddressList if add!=""]
    toAddress = "; ".join(toAddressList)
    # Create the root message and fill in the from, to, and subject headers
    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = subject
    msgRoot['From'] = fromAddress
    msgRoot['To'] = toAddress
    msgRoot.preamble = 'This is a multi-part message in MIME format.'
    
    msgAlternative = MIMEMultipart('alternative')
    msgText = MIMEText(altTextContent)
    msgAlternative.attach(msgText)        
    msgText = MIMEText(htmlContent, 'html', 'utf-8')  #, "utf-8"
    msgAlternative.attach(msgText)
    msgRoot.attach(msgAlternative)
    
    # Add images
    for imgIndex, imgData in images.iteritems():
        msgImage = MIMEImage(imgData)
        msgImage.add_header('Content-ID', '<image%s>' % imgIndex)
        msgRoot.attach(msgImage)
        
    #testing = True
    if testing:
        msg = msgRoot.as_string()
        print "username='%s', password='%s'" % (username, password)
        print "Email msg="
        print msg
        return msg
    else:
        smtp = SMTP()
        try:
            smtp.connect(smtpServer)
        except Exception, e:
            raise e
        try:
            if username!=None and username!="":
                smtp.login(username, password)
            smtp.sendmail(fromAddress, toAddressList, msgRoot.as_string())
            print "Email sent using %s, from='%s', to='%s'" % (smtpServer, fromAddress, toAddress)
        finally:
            smtp.quit()


