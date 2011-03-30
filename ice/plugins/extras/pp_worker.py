import os, sys, time
import types, string

try:
    import ppsetup
except:
    pass

try:
    import ooo_automate 
    reload(ooo_automate)
except:
    class Obj(object): 
        def __str__(self):
            return "ERROR"
    def ppMain(data):
        o = Obj()
        o.stdErr = "pp_worker failed to import ooo_automate\nBad remote setup!"
        return o

def OoAuto(data):
    import ooo_automate
    return ooo_automate.ppMain(data)

def test():
    return "workerOK"

def getcwd():
    return os.getcwd()

def listdir(path="."):
    return os.listdir(path)

def addPath(path):
    code = "if '%s' not in sys.path:\n  sys.path.append('%s')\n  r='Added'" % (path, path)
    return ctest(code)

def ctest(code):
    import os, sys, time, types, string
    r = None
    exec(code)
    return r
