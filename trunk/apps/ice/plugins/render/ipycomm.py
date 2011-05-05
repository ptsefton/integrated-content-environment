import sys
import os
try:
    from subprocess import Popen, PIPE #, STDOUT, call
    #   PIPE - Special value that can be used as the stdin, stdout or stderr argument
    #       to Popen and indicates that a pipe to the standard stream should be opened.
    #   STDOUT - Special value that can be used as the stderr argument to Popen and
    #       indicates that standard error should go into the same handle as standard output.
except Exception, e:
    try:
        import clr
        from System.Diagnostics import Process
        PIPE = True
        class Popen(object):
            def __init__(self, args, executable, stdin=None, stdout=None, stderr=None):
                self.p = Process()
                i = self.p.StartInfo
                i.UseShellExecute = False
                i.RedirectStandardInput = True
                i.RedirectStandardOutput = True
                i.RedirectStandardError = True
                i.FileName = executable
                args.pop(0)
                i.Arguments = " ".join(args)

            def communicate(self, stdinData=None):
                self.p.Start()
                stdin = self.p.StandardInput
                stdout = self.p.StandardOutput
                stderr = self.p.StandardError
                if stdinData is not None:
                    stdin.AutoFlush = True
                    stdin.Write(stdinData)
                    stdin.Flush()
                    # ? problem when we have input data only!
                stdoutData = stdout.ReadToEnd()
                stderrData = stderr.ReadToEnd()
                if not self.p.HasExited:
                    self.p.Kill()
                stdin.Close()
                stdout.Close()
                stderr.Close()
                self.p.Close()
                return stdoutData, stderrData
    except:
        raise e



class IPYComm(object):
    def __init__(self, ipyfile="iword.py"):
        if not os.path.isfile(ipyfile):
            if os.path.isfile("plugins/render/" + ipyfile):
                ipyfile = "plugins/render/" + ipyfile
        self.__ipyfile = ipyfile
        self._init()
    
    def _init(self):
        self.__error = ""
        try:
            self.__p = Popen(["ipy", self.__ipyfile], stdin=PIPE, stdout=PIPE, stderr=PIPE)
            result = self.__p.stdout.readline()
            if not result.startswith("STARTED OK:"):
                self.__error = result
                try:
                    self.terminate()
                except:
                    pass
            else:
                self.__read()
        except Exception, e:
            self.__error = "Failed to find IronPython"


    @property
    def _p(self):
        return self.__p

    @property
    def error(self):
        return self.__error
    
    @property
    def isRunning(self):
        try:
            return self.__p.poll() is None
        except:
            return False
    
    def messageBox(self, msg):
        self.__write("message:" + msg)
        return self.__read()
    
    def word(self, cmdStr):
        self.__write("word:" + cmdStr)
        return self.__read()
    
    def openDoc(self, file):
        self.__write("word:open(r" + repr(file) + ")")
        self.__read()
    
    def closeDoc(self):
        self.__write("word:closeDoc()")
        self.__read()
    
    def saveDocAs(self, file):
        self.__write("word:saveAs(r" + repr(file) + ")")
        self.__read()
        
    def execute(self, cmdStr):
        self.__write("exec:" + cmdStr)
        return self.__read()
    
    def close(self):
        try:
            self.__write("exit:")
        except: pass
    
    def terminate(self):
        try:
            self.__p.terminate()
        except: pass
    
    def __write(self, data):
        self.__p.stdin.write(data + "\n")
        self.__p.stdin.flush()
    
    def __read(self):
        lines = []
        while True:
            d = self.__p.stdout.readline()
            if d.startswith("--END--"):
                return "".join(lines)
            lines.append(d)





