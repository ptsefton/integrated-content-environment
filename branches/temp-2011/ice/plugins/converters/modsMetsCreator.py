
import re

################################################################################
class ModsCreator(object):
    TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<mods:mods xmlns:mods="%s">
</mods:mods>"""

    def __init__(self, iceContext):
        self.iceContext = iceContext
        self.__et= self.iceContext.ElementTree
        self.__Mets = iceContext.getPlugin("ice.mets").pluginClass


    def createModsStrFromMeta(self, meta):
        elem = self.createModsFromMeta(meta)
        return self.__et.tostring(elem)


    def createModsFromMeta(self, meta):
        elem = self.__et.XML(self.TEMPATE % self.__Mets.Helper.MODS_NS)
        title = self.__createElement("title")
        title.text = meta.get("title", "")
        elem.append(title)
        for author in meta.get("authors", []):
            authorName = author.get("name", "")
            name = self.__createElement("name", {"type":"personal"})
            elem.append(name)
            displayForm = self.__createElement("displayForm")
            displayForm.text = authorName
            role = self.__createElement("role")
            name.append(role)
            roleTerm = self.__createElement("roleTerm", {"type":"text"})
            roleTerm.text = "author"
            role.append(roleTerm)

            affiliation = author.get("affiliation", "")
            affil = self.__createElement("affiliation")
            affil.text = affiliation
            name.append(affil)
            email = author.get("email", "")
        abstract = meta.get("abstract", None)
        if abstract is not None:
            if abstract.lower().startswith("abstract:"):
                abstract = abstract[len("abstract:"):].strip()
            abstractElem = self.__createElement("abstract")
            abstractElem.text = abstract
            elem.append(abstractElem)
        keywords = re.split("[,\s]+", meta.get("keywords", ""))
        if keywords!=[]:
            subject = self.__createElement("subject")
            elem.append(subject)
            for keyword in keywords:
                lKeyword = keyword.lower()
                if lKeyword=="keywords:" or lKeyword==":":
                    continue
                topic = self.__createElement("topic")
                topic.text = keyword
                subject.append(topic)
        return elem

    def __createElement(self, tag, attrs={}):
        for key, value in attrs.iteritems():
            del attrs[key]
            attrs["{%s}%s" % (self.__Mets.Helper.MODS_NS, key)] = value
        return self.__et.Element("{%s}%s" % (self.__Mets.Helper.MODS_NS, tag), attrs)



################################################################################
class MetsCreator(object):
    def __init__(self, iceContext, includeExts):
        self.iceContext = iceContext
        self.__Mets = iceContext.getPlugin("ice.mets").pluginClass
        self.__mets = self.__Mets(iceContext, "ICE-METS", self.__Mets.Helper.METS_NLA_PROFILE)
        self.__includeExts = includeExts


    def createFromMeta(self, basePath, meta, inline = True):
        fs = self.iceContext.FileSystem(basePath)

        creationDate = strftime("%Y-%m-%dT%H:%M:%S", gmtime())
        self.__mets.setCreateDate(creationDate)
        self.__mets.setLastModDate(creationDate)
        self.__mets.addDisseminator(self.__Mets.Helper.MetsAgent.TYPE_INDIVIDUAL, "ICE User")
        self.__mets.addCreator("ICE 2.0")

        fileGrp = self.__mets.addFileGrp("Original")
        div1 = self.__mets.addDiv("document", "dmdSec1")

        modsCreator = ModsCreator(self.iceContext)
        if inline:
            modsData = modsCreator.createFromMeta(meta, returnAsString = False)
            dmdSec1 = self.__mets.addDmdSecWrap("dmdSec1", "MODS", modsData)
        else:
            dmdSec1 = self.__mets.addDmdSecRef("dmdSec1", "URL", "MODS", fs.absPath("mods.xml"))

        dirs, files = fs.listDirsFiles(basePath)
        for file in files:
            _, ext = fs.splitExt(file)
            if ext in self.__includeExts:
                if fs.exists(file):
                    filePath = fs.absPath(file)
                    file1 = self.__mets.addFile(fileGrp, filePath, file, dmdSec1.id,
                                              wrapped = inline)
                self.__mets.addFptr(div1, file1.id)
        div2 = self.__mets.addDiv("media", parentDiv = div1)
        for dir in dirs:
            if dir.endswith("_files"):
                for file in fs.listFiles(dir):
                    relPath = "%s/%s" % (dir, file)
                    file2 = self.__mets.addFile(fileGrp, filePath, relPath,
                                              wrapped = inline)
                    self.__mets.addFptr(div2, file2.id)

        return self.__mets.getXml()




