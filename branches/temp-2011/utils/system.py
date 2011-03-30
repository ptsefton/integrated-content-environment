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

import os
import sys
import re
import time
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





class System(object):
    # Constructor
    #    __init__()
    # Properties:
    #    platform
    #    environment
    #    sysPaths
    #    isWindows
    #    isLinux
    #    isMac
    #    username
    #    
    # Methods:
    #    sysPathAdd(path)
    #    cls()
    #    getOsConfigPath(appName, create=False)
    #    execute(command)
    #    start
    #    
    def __init__(self):
        self.__platform = sys.platform
        self.__environ = os.environ
        self.__sysPath = sys.path
        self.__isWindows = False
        self.__isLinux = False
        self.__isMac = False
        self.__isCli = False
        self.__system = None
        if self.__platform=="win32":
            self.__isWindows = True
        elif self.__platform.startswith("linux"):    #sys.platform=="linux2":
            self.__isLinux = True
        elif self.__platform=="darwin":
            self.__isMac = True
        elif self.__platform=="cli":
            self.__isCli = True
            import System as CliSystem
            self.__system = CliSystem
        else:
            raise Exception("Unknown or unsupported operating system! platform='%s'" % sys.platform)
    
    @property
    def platform(self):
        return self.__platform
    
    @property
    def environment(self):
        return self.__environ
    
    @property
    def sysPaths(self):
        return self.__sysPath
    
    @property
    def isWindows(self):
        return self.__isWindows
    
    @property
    def isLinux(self):
        return self.__isLinux
    
    @property
    def isMac(self):
        return self.__isMac
    
    @property
    def isCli(self):
        return self.__isCli
    
    @property
    def username(self):
        name = self.__environ.get("USERNAME")
        if name is None:
            name = self.__environ.get("USER")
        return name
    
    def sysPathAdd(self, path):
        if path not in self.__sysPath:
            self.__sysPath.append(path)
    
    
    def cls(self):
        """ Clears to console window """
        try:
            if self.isWindows:
                os.system("cls")
            elif self.isCli:
                self.__system.Console.Clear()
            else:
                print "\n\n\n==========================================="
                print "\n" * 64
                os.system("clear")
        except:
            print "\n\n"
    
    def getOsHomeDirectory(self):
        if self.isWindows:
            home = os.path.split(self.__getWindowsConfigPath())[0]
        else:
            home = self.__getUnixConfigPath()
        return home
    
    def getOsConfigPath(self, appName, create=False):
        appName = appName.lower()
        if self.isWindows:
            appData = self.__getWindowsConfigPath(appName)
        else:
            appData = self.__getUnixConfigPath(appName)
        if create and not os.path.exists(appData):
            os.mkdir(appData)
        return appData
    
    def __getUnixConfigPath(self, appName=None):
        appData = self.environment.get("HOME")
        if appName is not None:
            appData = os.path.join(appData, "." + appName)
        return appData
    
    def __getWindowsConfigPath(self, appName=None):
        import _winreg
        def expandvars(s):    # expand environmental variables
            def subEvn(m):    # sub %Xxxx% with os.environ variable (if there is one)
                return self.environment.get(m.group(1))
            import re
            envRegex = re.compile(r'%([^|<>=^%]+)%')
            return envRegex.sub(subEvn, s)
        
        key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, \
                "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\User Shell Folders")
        try:
            ret = _winreg.QueryValueEx(key, "AppData")
        except:
            return None
        else:
            key.Close()
            if ret[1] == _winreg.REG_EXPAND_SZ:
                appData = expandvars(ret[0])
            else:
                appData = ret[0]
        if appName is not None:
            appData = os.path.join(appData, appName.title())
        return appData
    
    def execute(self, command, *args):
        #Note: Windows bug?  (This appears to be a problem with popen)
        #       if you have a quoted command you can not have any quoted arguments
        #       and if you do not hava a quoted command you can have any number of quoted arguments!
        cmd = command
        if not self.isWindows:
            args = ['"%s"' % arg for arg in args]
        if not cmd.startswith('"'):
            if cmd.find(" ")>-1:
                cmd = '"%s"' % cmd
        if len(args)>0:
            cmd += " " + " ".join(args)
        
        #print "--------system.execute---------"
        #print "cmd='%s'" % cmd
        #print "-------------------------------"
        
        p = os.popen(cmd)
        #time.sleep(.05)
        result = p.read()
        
        msg = ""
        closedOK = False
        for x in range(10):
            try:
                p.close()
            except:
                msg += "Failed close process - retry %s\n" % str(x)
                time.sleep(0.125)
            else:
                closedOK = True
                if x:
                    msg += "OK closed process on retry\n"
                else:
                    msg += "OK closed"
                break
        if closedOK==False:
            msg += "WARNING: Failed to close process!\n"
        return result, msg
    
    def execute2(self, command, *args, **kwargs):
        #Note: Windows bug?  (This appears to be a problem with popen)
        #       if you have a quoted command you can not have any quoted arguments
        #       and if you do not hava a quoted command you can have any number of quoted arguments!
        printErr = kwargs.get("printErr", True)
        cmd = command
        if not self.isWindows:
            args = ['"%s"' % arg for arg in args]
        if not cmd.startswith('"'):
            if cmd.find(" ")>-1:
                cmd = '"%s"' % cmd
        if len(args)>0:
            cmd += " " + " ".join(args)
        
        stdin, stdout, stderr = os.popen3(cmd)
        #stdin.write()
        #stdin.flush()
        if printErr:
            elines = []
            while True:
                err = stderr.readline()
                if err=="":
                    break
                else:
                    sys.stdout.write("stderr> " + err)
                    elines.append(err)
            errResult = "".join(elines)
        else:
            errResult = stderr.read()
        outResult = stdout.read()
        stdin.close()
        stdout.close()
        stderr.close()
        return outResult, errResult
    
    def execute3(self, command, *args):
        """ returns a tuple of (stdin, stdout, stderr)
            Also Note: that these streams should be closed when finished with!
        """
        #Note: Windows bug?  (This appears to be a problem with popen)
        #       if you have a quoted command you can not have any quoted arguments
        #       and if you do not hava a quoted command you can have any number of quoted arguments!
        cmd = command
        if not self.isWindows:
            args = ['"%s"' % arg for arg in args]
        if not cmd.startswith('"'):
            if cmd.find(" ")>-1:
                cmd = '"%s"' % cmd
        if len(args)>0:
            cmd += " " + " ".join(args)
        
        stdin, stdout, stderr = os.popen3(cmd)
        stdin.close()
        return stdin, stdout, stderr


    def executeNew(self, command, *args, **kwargs):
        """
            command - the program to be executed
            (**kwargs) stdinData=data - stdin input data for the process/program
            *args - a list of arguments for the process/program
            returns a tuple of (stdoutData, stderrData)
        """
        stdinData = kwargs.pop("stdinData", None)
        args = list(args)
        args.insert(0, command)
        p = Popen(args=args, executable=command, stdin=PIPE, stdout=PIPE, stderr=PIPE, **kwargs)
        stdoutData, stderrData = p.communicate(stdinData)
        return stdoutData, stderrData


    def executeAsync(self, command, *args):
        # process.stdin, .stdout, stderr        #Note: remember to flush()
        #       .stdin.write(data) .stdin.flush()
        #       .stdout.read([amount]), .stdout.readline()
        #   .poll() -> None (still processing) or returncode (int)
        #   .kill()
        #   .communicate(input) -> (stdoutData, stderrData)  Note: waits until the process has finished
        #                                   Also closes input and output streams
        #   .returncode 
        #   -ADDED-
        #   .close() To close all input and output streams
        #   .processing() -> True while still processing
        args.insert(0, command)
        process = Popen(args=args, executable=command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        def close():
            process.stdoutData, process.stderrData = process.communicate()
        process.close = close
        def processing():
            return process.poll()==None
        process.processing = processing
        def write(data):
            process.stdin.write(data)
        return process

    
    def executeCall(self, command, *args):
        """
            returns the processes exit code
        """
        args.insert(0, command)
        return call(args)


    def openFileBrowser(self, path):
        if hasattr(os, "startfile"):
            os.startfile(path)
        elif self.isMac:
            stdin, stdouterr = os.popen4("open \"%s\"" % path)
            #time.sleep(.1)
            try:
                result = stdouterr.read()
            except:
                result = ""
            stdin.close()
            stdouterr.close()
            if result!="":
                os.system("open \"%s\"" % path)
        elif self.isLinux:
            command = "nautilus \"%s\" &" % path
            os.system(command)
    
    
    def startFile(self, file, openFileBrowserIfNoAppAssociation=True, appsExts={}):
        """ 
            file = the full path to the file to start
            appsExt = {fullPathToApplication: [listOfAssociatedExts]}
        """
        ext = os.path.splitext(file)[1]
        try:
            if hasattr(os, "startfile"):
                os.startfile(file)
            else:
                if self.isMac:
                    os.system("open \"%s\"" % file)
                elif self.isLinux:
                    # try 'mimedb -a ext' to get the associated program for this extension
                    found = False
                    if file.find("://")>0:  # if file is a valid URL then ext=".html"
                        ext = ".html"
                        if appsExts=={}:
                            appsExts["firefox"]=[".htm", ".html"]
                    elif ext==".htm" and appsExts=={}:
                        appsExts["firefox"]=[".htm", ".html"]
                    result, error = self.execute2("mimedb", "-a", ext)
                    if not error and result!="":
                        app = result[:result.find(" %")]
                        os.system('%s "%s"' % (app, file))
                        found = True
                    if found==False:
                        for app, exts in appsExts.iteritems():
                            if ext in exts:
                                os.system('%s "%s"' % (app, file))
                                found = True
                    if found==False:
                        raise Exception("No associated application found!")
        except Exception, e:
            msg = str(e)
            if msg.find("No associated application found!")>-1:
                if os.path.isfile(file):
                    print "%s for %s" % (msg, file)
                    path = os.path.split(file)[0]
                elif os.path.isdir(file):
                    path = file
                else:
                    path = os.path.split(file)[0]
                if openFileBrowserIfNoAppAssociation:
                    try:
                        self.openFileBrowser(path)
                    except:
                        pass
            else:
                raise e
        
system = System()















