
import sys
import clr
import os

ipzlib = "IronPython.Zlib.dll"

for p in sys.path:
    if p.endswith("Lib"):
        p = os.path.split(p)[0]
        #print "path='%s'" % p
        if ipzlib in os.listdir(p):
            #print "Found"
            clr.AddReferenceToFileAndPath(os.path.join(p, ipzlib))
            break
    
