#
#    Copyright (C) 2005  Distance and e-Learning Centre, 
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

import os
import re
import sys
from glob import glob


# check if a value matches mask and doesn't match ignoreMask
def match(value, mask, ignoreMask):
    result = re.compile(mask).match(value)
    if ignoreMask is not None:
        result = result and not re.compile(ignoreMask).match(value)
    return result

# recursive glob with regex matching
def rglob(path, fileMask = ".*", ignoreFileMask = None, dirMask = ".*", ignoreDirMask = r"\.svn"):
    dirEntries = []
    fileEntries = []
    for root, dirs, files in os.walk(path):
        if match(root, dirMask, ignoreDirMask):
            if not root in dirEntries:
                dirEntries.append(root)
            for dir in dirs:
                if not match(dir, dirMask, ignoreDirMask):
                    dirs.remove(dir)
                else:
                    dirPath = os.path.join(root, dir)
                    if not dirPath in dirEntries:
                        dirEntries.append(dirPath)
            for file in files:
                if match(file, fileMask, ignoreFileMask):
                    fileEntries.append(os.path.join(root, file))
    return dirEntries, fileEntries

# include all source dirs under apps in python path, filtered using regex
NON_SRC_DIRS = r"(.*\.svn)|(.*Svn.*)|(.*Rep.*)|(.*[Tt]est.*)|(\.indexes)|(fake\.skin)|(ice\-maker)"
sourceDirs, _ = rglob("..", ignoreDirMask = NON_SRC_DIRS)
for sourceDir in sourceDirs:
    sys.path.append(sourceDir)

# attempt to import plugins so deps are available to py2{exe,app}
_, pluginFiles = rglob(r"../ice/plugins", fileMask = r".+\.py$", ignoreFileMask = r".*[Tt]est.*")


icepy = open("ice.py", "w")
icepy.write("# generated by setup.py")
icepy.write("""
# don't import if running from exe, just need dependencies during build
import imp, os, sys
if sys.platform == "darwin":
    sys.path = [os.path.join(os.environ['RESOURCEPATH'], 'lib', 'python2.6', 'lib-dynload')] + sys.path
if not hasattr(sys, "frozen"):""")
for pluginFile in pluginFiles:
    _, name = os.path.split(pluginFile)
    icepy.write("""
    try:
        import %(name)s
    except Exception, e:
        print "%(name)s", str(e)""" % {"name": name[:-3]})
##
for pluginFile in ["openid", "textile"]:
    _, name = os.path.split(pluginFile)
    icepy.write("""
    try:
        import %(name)s
    except Exception, e:
        print "%(name)s", str(e)""" % {"name": name[:-3]})
##
icepy.write("""
from ice2 import main
if __name__ == "__main__": sys.exit(main(list(sys.argv), sys, sys.stdout.write))
""")
icepy.close()

def datadir(relPath, path, fileMask = ".*", ignoreFileMask = None, dirMask = ".*", ignoreDirMask = r"(\.svn)|(.*[Tt]est.*)"):
    data = []
    alldirs, allfiles = rglob(path, fileMask, ignoreFileMask, dirMask, ignoreDirMask)
    for d in alldirs:
        files = []
        for f in allfiles:
            sd, _ = os.path.split(f)
            if sd == d:
                files.append(f)
        if relPath == ".":
            baseDir = relPath
        else:
            baseDir = d[d.find(relPath):]
        data.append((baseDir, files))
    return data
if sys.platform == "win32": 
    import py2exe
    origIsSystemDLL = py2exe.build_exe.isSystemDLL
    def isSystemDLL(pathname):
        print pathname
        if os.path.basename(pathname).lower() in ("jvm.dll"):
            return 1
        return origIsSystemDLL(pathname)
    py2exe.build_exe.isSystemDLL = isSystemDLL


# include data files, templates, etc
supportFiles = datadir(".", r"../ice",
                       ignoreFileMask = r"(.+\.py[co]*$)|(.*[Tt]est.*)",
                       ignoreDirMask = r"(.*\.svn)|(.*plugins)|(.*fake\.skin)|([Tt]est.*)")
supportFiles[0][1].extend(glob(r"../ice/site*"))
supportFiles[0][1].extend(glob(r"../pdf-utils"))

fakeSkinFiles = datadir("fake.skin", r"../ice/fake.skin")
pluginFiles = datadir("plugins", r"../ice/plugins",
                      ignoreFileMask = r"(.*\.py[co]$)|(.*_test\.py[co]*)|(plugin_crystaleyeAtomToOdt\.py[co]*)|(plugin_cdx2cml_function\.py[co]*)")

# common setup options
SCRIPT = r"ice.py"
PACKAGES = ["email", "lxml", "pyPdf"]     # "rdflib" - ORE, "lucene", "curl"
DATA_FILES = supportFiles
DATA_FILES.extend(fakeSkinFiles)
DATA_FILES.extend(pluginFiles)

setupOptions = dict(name = "Ice2",
                    version = "2.0",
                    description = "ICE 2 server",
                    author = "USQ",
                    data_files = DATA_FILES)

extraOptions = dict(compressed = True,
                    optimize = True,
                    excludes = ["Tkconstants", "Tkinter", "tcl"],
                    packages = PACKAGES)

from distutils.core import setup

if sys.platform == "darwin":
    import py2app
    oooPath = "/Applications/OpenOffice.org.app/Contents"
    oooDict = { "oooPath" : oooPath }
    SCRIPT_KEY = "app"
    OPTIONS_KEY = "py2app"
    PLIST = dict(CFBundleIdentifier = "org.pythonmac.py2app.Ice",
                 CFBundleDocumentTypes = [dict(CFBundleTypeIconFile = "Ice2.icns")],
                 LSEnvironment = dict(URE_BOOTSTRAP = "vnd.sun.star.pathname:%s/program/fundamentalrc" % oooPath,
                                      DYLD_LIBRARY_PATH = "/usr/lib:plugins/ooo/py26-pyuno-macosx:%(oooPath)s/basis-link/program:%(oooPath)s/basis-link/ure-link/lib" % oooDict),
                 PyResourcePackages = ["lib/python2.6/lib-dynload"])
    extraOptions.update(dict(iconfile = "Ice2.icns", plist = PLIST, includes = ["imghdr"]))
elif sys.platform == "win32":
    import py2exe
    SCRIPT_KEY = "console"
    OPTIONS_KEY = "py2exe"
    PACKAGES.extend(["PIL"])
    # include lucene jars
    luceneFiles = datadir("lucene", r"%s\Lib\site-packages\lucene" % sys.prefix, fileMask=r".*\.jar")
    DATA_FILES.extend(luceneFiles)
else:
    print "Unsupported platform '%s'" % sys.platform
    sys.exit(1)

setupOptions.update({SCRIPT_KEY: [SCRIPT]})
setupOptions.update(options = {OPTIONS_KEY: extraOptions})
setup(**setupOptions)