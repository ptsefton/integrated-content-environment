#!/usr/bin/env python
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

"""
"""

from ice_common import IceCommon
import ice_web



def upgrade(options, fs, outputWriter):
    if options.get("help") is not None:
        outputWriter("Usage: %s -upgrade -directory=PathToUpgrade\n" % (progName))
        return 0
    directory = options.get("directory")
    if directory is None:
        outputWriter("%S\n" % options)
        outputWriter("argument '-directory=PathToUpgrade' is required!\n")
        return 1
    if not fs.isDirectory(directory):
        outputWriter("The given directory '%s' does not exist!\n" % directory)
        return 1
    dryRun = bool(options.get("dryrun"))
    verbose = bool(options.get("verbose"))
    if dryRun:
        outputWriter(" *** dryRun ***\n")
        verbose = True

    # OK first get all BookInfo objects from the old SVN Properties
    #   and add to the new .ice properties
    SvnPropertyDel = iceContext.getPluginClass("ice.svnPropDel")
    BookInfo = iceContext.getPluginClass("ice.book.bookInfo")
    svnPropDel = SvnPropertyDel()
    directory = fs.absolutePath(directory)
    svnFiles = svnPropDel.getListOfAllSvnFiles(path=directory)
    bookInfos = {}
    for file in svnFiles:
        props = svnPropDel.getListOfPropertiesForFile(file)
        if "meta-bookInfo" in props:
            #outputWriter(" *** Found meta-bookInfo\n")
            data = svnPropDel.getProperty(file, "meta-bookInfo")
            bookInfo = BookInfo.loads(iceContext, data.values()[0])
            #outputWriter("%s\n" % bookInfo)
            bookInfos[file] = bookInfo
    class temp(object):
        def getRenderableFrom(self, ext):
            return []
    #
    from ice_rep import IceRepository       # OLD REPOSITORY
    rep = IceRepository(basePath=directory, iceRender=temp(), fileSystem=fs)
    #for file, bookInfo in bookInfos.iteritems():
    #    file = file[len(directory):]
    #    if verbose:
    #        outputWriter("Updating bookInfo for '%s'\n" % file)
    #    item = rep.getItem(file)
    #    item.setMeta("bookInfo???", bookInfo)
    #    if dryRun==False:
    #        item.close()
    # Now delete all of the old properties
    svnPropDel.deleteAllProperties(path=directory, verbose=verbose, dryRun=dryRun)
    if not dryRun:
        outputWriter("\nNow use - svn commit %s -m \"removed properites\" - to commit all changes\n" % directory)
    return 0


def main(args, sys, outputWriter):
    shortOptionNames = {"h":"help", "f":"file", "d":"directory", "dir":"directory",
                        "converter":"convert", "v":"verbose", "test":"testing"}
    flags = ["help", "convert", "atompub", "atomconvertpub", "upgrade",
             "verbose", "asserviceonly", "enableexternalaccess", "test", "open"]
    progName = args.pop(0)
    options = IceCommon.getOptions(args, shortOptionNames, flags)
    fs = IceCommon.FileSystem(IceCommon.workingDirectory)
    convert = options.get("convert", False)
    atompub = options.get("atompub", False) or options.get("atomconvertpub", False)
    if convert or atompub:
        file = options.get("file")
        directory = options.get("directory")
        template = options.get("template")
        if file is not None:
            options["file"] = fs.absolutePath(file)
        if directory is not None:
            options["directory"] = fs.absolutePath(directory)
        if template is not None:
            options["template"] = fs.absolutePath(template)
        class OurOutput(object):
            def __init__(self):
                import tempfile
                self.__f = open(tempfile.gettempdir() + "/ice.log", "wb")
            def write(self, data):
                sys.stdout.write(data)
                self.__f.write(data.replace("\n", "\r\n"))
            def close(self):
                self.__f.close()
        output = OurOutput()
        stderr = sys.stderr
        sys.stderr = output
        converterAppMain(progName, options, fs=fs, output=output)
        output.close()
        sys.stderr = stderr
    elif options.get("svn", None) is not None:
        # SVN command
        usageMessage = "Usage: -svn:export -path:UrlOrAbsolutePathToExport -dir:exportToDirectory"
        svnCommand = options.get("svn").lower()
        if options.get("help") is not None:
            outputWriter("%s\n" % usageMessage)
            return(1)
        if svnCommand=="export":
            # from 'path' to 'dir'
            path = options.get("path")
            toDir = options.get("directory")
            if path is None or toDir is None:
                outputWriter("%s\n" % usageMessage)
            else:
                try:
                    outputWriter("Exporting '%s' to '%s'.  Please wait...\n" % (path, toDir))
                    import pysvn
                    client = pysvn.Client()
                    #path = fs.absolutePath(path)
                    #toDir = fs.absolutePath(toDir)
                    result = client.export(path, toDir, force=True, revision=pysvn.Revision(pysvn.opt_revision_kind.head), recurse=True)

                    outputWriter("Exported: %s\n" % str(result))
                    outputWriter("Export completed.\n")
                except Exception, e:
                    outputWriter("Error exporting: %s\n" % str(e))
        else:
            outputWriter("%s\n" % usageMessage)
    elif options.get("upgrade", False):
        retCode = upgrade(options, fs, outputWriter)
        if retCode>0:
            return retCode
    elif options.get("help", False) and options.get("ice") is None:
        usageMessage = "Usage: -help -svn         For svn usage help\n" + \
                       "       -help -convert     For converter usage help\n" + \
                       "       -help -atomPub     For atom publishing usage help\n" + \
                       "       -help -upgrade     For upgrading usage help\n" + \
                       "       -help -ice         For ICE usage help\n" + \
                       "  or no arguments to run the ICE server.\n"
        outputWriter("%s\n" % usageMessage)
    else:
        ice_web.iceWebServer(IceCommon, options, outputWriter)
    outputWriter("\n")
    return 0



def converterAppMain(progName, options, testing=False, fs=None, output=None):
    if output is None:
        output = sys.stdout
    if fs is None:
        fs = Global.fs
    usageMessage = "Usage: \n %s -convert -f:odtOrDocFile -d:outputDirectory [-options]" % progName
    usageMessage += "\n  Options:"
    usageMessage += "\n    -pdfLink              - include a link to the PDF rendition in the HTML"
    usageMessage += "\n    -sourceLink           - include a link to the source document in the HTML (including derived ODT from DOC)"
    usageMessage += "\n    -includetitle:False          - do not include the title in the body of the HTML"
    usageMessage += "\n    -toc:False            - turn off the page TOC in the HTML"
    usageMessage += "\n    -template templateFile    - use the given xhtml template file when generating the HTML"
    usageMessage += "\n    -templateString \"templateString\"    - use the given xml template string when generating the HTML"
    usageMessage += "\n    -oooPort:#            - use the given port number for communication with OpenOffice.org"
    usageMessage += "\n    -oooPath pathToOOo    - use the OpenOffice.org at the given path"
    usageMessage += "\n    -open                 - to auto open the converted file"
    usageMessage += "\nOR to atom publish"
    usageMessage += "\n %s -atomPub -f:htmlFile [-options]" % progName
    usageMessage += "\n %s -atomConvertPub -f:odtOrDocFile -d:outputDirectory [-options]" % progName
    usageMessage += "\n  Options:"
    usageMessage += "\n    -atomPubUrl=url       - required for first post"
    usageMessage += "\n    -categories=\"categories\"  - A list of cateogories for the post separated by ;, "
    usageMessage += "\n                             eg. \"Category1;Categor2\"(default is Uncategorized)"
    usageMessage += "\n    -title=\"Title\"        - required"
    usageMessage += "\n    -authType=None|Basic|Blogger   - (default is None)"
    usageMessage += "\n    -username=username    - required if authType is Basic or Blogger"
    usageMessage += "\n    -password=password    - required if authType is Basic or Blogger"
    usageMessage += "\n    -author=author        - required if username has not been given (default is username)"
    usageMessage += "\n    -summary=\"summary\"  - (default is title)"
    usageMessage += "\n    -draft:True|False     - (default is True)"
    usageMessage += "\n    -new:True|False       - (default is False, ignored if document has not been posted yet)"
    usageMessage += "\n    -open                 - to open the publish content"

    convert = options.get("convert", False)
    atomPub = options.get("atompub", False)
    atomConvertPub = options.get("atomconvertpub", False)
    if options.get("help", False) or (not convert) and (not atomPub):
        output.write("%s\n" % usageMessage)
        return True
    if options.get("testing", False):
        output.write("%s\n" % "*** Testing Mode ***")
        file = "testData/test1.odt"
        toDir = "testData/output"
        if False:
            output.write("Testing - isWindows=%s, isLinux=%s, isMac=%s\n" % (Global.isWindows, Global.isLinux, Global.isMac))
            output.write("Options=%s\n" % str(options))
            output.write("%s%s\n" % (config.settings, config.settings.get("oooPythonPath")))
    else:
        file = options.get("file", None)
        toDir = options.get("directory", None)
        if (file is None) or ((toDir is None) and (atomPub==False)):
            output.write("%s\n" % usageMessage)
            return False
    if True:
        if not fs.isFile(file):
            output.write("Can not find file '%s'!\n" % file)
            return False
        if not atomPub and fs.isFile(toDir):
            output.write("'%s' is a filename!\n" % toDir)
            return False
        #if fs.exists(toDir):
        #    print "'%s' already exists!" % toDir
        #    sys.exit(1)

    # OpenOffice.org's python path and port #
    if options.get("oooport", None) is not None:
        config.settings["oooPort"] = options.get("oooport")
    if options.get("ooopath", None) is not None:
        oooPath = options.get("ooopath")
        config.settings["oooPath"] = oooPath
        config.settings["oooPythonPath"] = config.settings.getOooPythonPath(oooPath)

    # Template file
    if options.get("template", None) is not None:
        templateFile = options["template"]
        output.write("using template file '%s'\n" % templateFile)
        if fs.isFile(templateFile):
            template = fs.readFile(templateFile)
        else:
            output.write("Can not find template file '%s'\n" % templateFile)
            return False
    elif options.get("templatestring", None) is not None:
        template = options.get("templatestring")
    else:
        template = """<html>
      <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
        <title>Default Template</title>
        <style type="text/css">
          .rendition-links { text-align: right; }
          .body table td { vertical-align: top; }
        </style>
        <style class="sub style-css" type="text/css"></style>
      </head>
      <body>
        <div class="rendition-links">
          <span class="ins source-link"></span>
          <span class="ins slide-link"></span>
          <span class="ins pdf-rendition-link"></span>
        </div>
        <h1 class="ins title"></h1>
        <div class="ins page-toc"></div>
        <div class="ins body"></div>
      </body>
    </html>"""

    iceContext = IceCommon.IceContext(loadRepositories=False, loadConfig=True)
    oooConverterApp = iceContext.getPlugin("ice.ooo.OdtDocConverter").pluginClass
    oooConverterApp = oooConverterApp(iceContext, fs, template)
    if atomPub or atomConvertPub:
        if atomConvertPub:
            result, htmlFile, pdfFile = oooConverterApp.convert(file, toDir, options)
            if htmlFile is None:
                return False
            file = htmlFile
        #App Publish
        content = fs.readFile(file)
        newEntry = options.get("new", False)
        if type(newEntry) == bool:
            newEntry = str(newEntry).lower()
        elif newEntry.strip() == "on":
            newEntry = "true"
        newEntry = newEntry.lower() == "true"
        if not newEntry:
            entryXml = fs.readFile(file + ".info")
        else:
            entryXml = None

        path, name, _ = fs.splitPathFileExt(file)
        mediaPath = "%s/%s_files" % (path, name)
        def getMedia(media = None):
            if media is None:
                files = fs.listFiles(mediaPath)
                files.append(name + ".pdf")
                return files
            else:
                if media.endswith(".pdf"):
                    file = fs.join(path, media)
                else:
                    file = fs.join(mediaPath, media)
                return fs.readFile(file)
        def saveResponse(entryXml, publishedCategory):
            fs.writeFile(file + ".info", entryXml)
        AtomPublish = iceContext.getPlugin("ice.atom.publish").pluginClass
        atomPublish = AtomPublish(iceContext, file, getMedia, saveResponse, output)
        try:
            if False:   # Comment out the style data
                et = iceContext.ElementTree
                xml = et.XML(content)
                styles = xml.findall(".//style")
                for s in styles:
                    c = et.Comment("\n"+s.text+"\n//")
                    s.text = "//"
                    s.append(c)
                content = et.tostring(xml)
            successes, responses, urls = atomPublish.publish(content, options, entryXml)
            success = True
            for s in successes:
                success = success and s
            if success:
                output.write("Published OK\n")
            else:
                output.write("Publish failed: %s\n" % responses[0])
            if urls !=[]:
                for url in urls:
                    output.write("Published URL: %s\n" % url)
            if options.get("open", False) and urls !=[]:
                for url in urls:
                    iceContext.system.startFile(url, openFileBrowserIfNoAppAssociation=False)
        except AtomPublish.BadAuthentication, e:
            output.write("Publish failed: %s\n" % str(e))
        except AtomPublish.RequestException, e:
            output.write("Publish failed: %s\n" % str(e))
        return True
    else:
        # Convert
        result, htmlFile, pdfFile = oooConverterApp.convert(file, toDir, options)
        output.write("Done. %s\n" % result)
        if options.get("open", False) and htmlFile is not None:
            iceContext.system.startFile(htmlFile, openFileBrowserIfNoAppAssociation=False)
        return True


def start(sys):
    args = list(sys.argv)
    outputWriter = IceCommon.outputWriter
    retCode = main(args, sys, outputWriter)


if __name__ == '__main__':
    import sys
    retCode = start(sys)
    sys.exit(retCode)

