
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

pluginName = "ice.functions"
pluginDesc = ""
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = None
    pluginClass = IceFunctions
    pluginInitialized = True
    return pluginFunc



class IceFunctions(object):
    # Constructor:
    #   __init__(iceContext)
    # Properties:
    #   groups          # {}
    #   allFunctions    # {}
    # Methods:
    #   add(func, group="toolbar", position=None,
    #        label=None, title=None, accessKey=None, toolbarHtml=None,
    #        displayIf=None, enableIf=None, postRequired=True,
    #        destPath=None, argPath=None,
    #        serverMethod=True, serverOnlyMethod=False, extras={}, **kwargs)
    #   get(func)                   # gets the IceFunction
    #   getFunction(self, func)     # get the function
    #   remove(func)
    #   replace(oldFunc, newFunc=None, **args)

    
    def __init__(self, iceContext):
        self.iceContext = iceContext
        self.groups = {}
        self.allFunctions = {}
    
    
    def add(self, func, group="toolbar", position=None,
            label=None, title=None, accessKey=None, toolbarHtml=None,
            displayIf=None, enableIf=None, postRequired=True,
            destPath=None, argPath=None,
            serverMethod=True, serverOnlyMethod=False, extras={}, **kwargs):
        group = group.lower()
        groupDictObj = self.groups.get(group, None)
        if groupDictObj is None:
            groupDictObj = self.iceContext.SortedDictionary()
            groupDictObj.setSortByValueProperty("position")
            groupDictObj.group = group
            groupDictObj.defaultPosition = 10000
            self.groups[group] = groupDictObj
        if position is None:
            position = groupDictObj.defaultPosition
            groupDictObj.defaultPosition += 1
        iceFunction = self.IceFunction(self.iceContext, func, groupDictObj=groupDictObj, position=position,
                        label=label, title=title, accessKey=accessKey, toolbarHtml=toolbarHtml,
                        displayIf=displayIf, enableIf=enableIf, postRequired=postRequired,
                        destPath=destPath, argPath=argPath,
                        serverMethod=serverMethod, serverOnlyMethod=serverOnlyMethod,
                        extras=extras)
        name = func.__name__
        groupDictObj[name] = iceFunction
        self.allFunctions[name] = iceFunction
        return self.groups
    
    
    def get(self, func):
        if callable(func):
            funcName = func.__name__
        else:
            funcName = func
        f = self.allFunctions.get(funcName, None)
        return f
    
    
    def getFunction(self, func):
        f = self.get(func)
        if f is not None:
            return f._func
    
    
    def remove(self, func):
        if callable(func):
            funcName = func.__name__
        else:
            funcName = func
        iceFunc = self.allFunctions.get(funcName, None)
        if func is not None:
            del self.allFunctions[funcName]
            groupDictObj = iceFunc.groupDictObj
            del groupDictObj[funcName]
        return func
    
    
    def replace(self, oldFunc, newFunc=None, **args):
        if callable(oldFunc):
            funcName = oldFunc.__name__
            if newFunc is None:
                newFunc = oldFunc
        else:
            funcName = oldFunc
        func = self.get(funcName)
        if func is not None:
            if not callable(newFunc):
                raise self.iceContext.IceException("newFunc argument is not callable!")
            func._setFunction(newFunc)
        else:
            print "IceFunctions.replace() function not found!"
    
    
    class IceFunction(object):
        def __init__(self, iceContext, func, groupDictObj, position=None, 
                    label=None, title=None, accessKey=None, toolbarHtml=None,
                    displayIf=None, enableIf=None,
                    postRequired=True, destPath=None, argPath=None,
                    serverMethod=True, serverOnlyMethod=False,
                    extras={}):
            self.iceContext = iceContext
            self.__func = func
            self.name = func.__name__
            self.groupDictObj = groupDictObj
            self.position = position
            
            self.__toolbarHtml = toolbarHtml
            self.postRequired = postRequired
            self.enabled = False
            self.display = False
            if accessKey is None:
                if label is not None and label.find("_")>-1:
                    accessKey = label[label.find("_")+1]
                    label = "".join(label.split("_", 1))
            self.label = label
            self.title = title
            self.accessKey = accessKey
            self.__destPath = destPath
            self.__argPath = argPath
            self.destPath = destPath
            self.argPath = argPath
            self.serverMethod = serverMethod
            self.serverOnlyMethod = serverOnlyMethod
            self.extras = extras
            
            self.__displayIf = displayIf
            self.__enableIf = enableIf
        
        @property
        def _func(self):
            return self.__func
        
        def hasHtml(self):
            return self.__toolbarHtml!=None
        
        def asHtml(self, context):
            if not self.display:
                return ""
            toolbarHtml = self.__toolbarHtml
            if toolbarHtml is None:
                if self.label is not None:
                    action = ""
                    title = self.title
                    label = self.label
                    if self.accessKey:
                        p1, p2 = label.split(self.accessKey, 1)
                        label = "%s<u>%s</u>%s" % (p1, self.accessKey, p2)
                        title += " (Alt+%s)" % self.accessKey.upper()
                    destPath = self.destPath
                    if destPath is None or destPath=="":
                        destPath = "%(path)s"
                    destPath = self.iceContext.escapeXmlAttribute(destPath)
                    destPath = "/rep.%s%s" % (context.rep.name, destPath)
                    packagePath = context.packagePath
                    if packagePath is None:
                        packagePath = ""
                    if not packagePath.endswith("/"):
                        packagePath += "/"
                    destPath = destPath.replace("%(package-path)s", packagePath)
                    
                    s = "\n<form style='display:inline;' action='%s' method='POST'>" % destPath
                    s += "<input type='hidden' name='func' value='%s'/>\n" % self.name
                    s += "<input type='hidden' name='argPath' value='%(argPath)s'/>\n"
                    s += "<button type='submit' name='do' title='%s' accesskey='%s'>%s</button>" % (title, self.accessKey, label)
                    s += "</form>\n"
                    toolbarHtml = s
                else:
                    toolbarHtml = ""
            else:
                if callable(toolbarHtml):
                    toolbarHtml = toolbarHtml(context)
            
            try:
                html = str(toolbarHtml) % context
            except Exception, e:
                #unsupported format character
                html = ""
            if self.enabled==False:
                html = html.replace("<input type='submit'", "<input type='submit' disabled='disabled' class='disabled'")
                html = html.replace("<button type='submit'", "<button type='submit' disabled='disabled' class='disabled'")
            return html
        
        def _setFunction(self, function):
            self.__func = function
        
        def _update(self, context):
            self.display = self.__testIf(context, self.__displayIf)
            # also check self.serverMethod and self.serverOnlyMethod
            self.enabled = self.__testIf(context, self.__enableIf)
            if self.__destPath is None:
                self.destPath = context["path"]
            if self.__argPath is None:
                self.argPath = context["path"]
            if callable(self.extras.get("update")):
                self.extras.get("update")(context, self)
            # closure
            cl = [context]
            def asHtml(context=None):
                if context is None:
                    context = cl[0]
                return self.asHtml(context)
            #self.asHtml = asHtml
            return asHtml
        
        def _execute(self, context):
            if callable(self.__func):
                return self.__func(context)
            else:
                return False
        
        
        def __testIf(self, context, testObj):
            # 
            if testObj is None:         # If not set then default is True (enabled)
                r = True
            elif callable(testObj):
                r = bool(testObj(context))
            else:
                r = bool(testObj)
            return r
        
        
        def __getProp(self, name, oldFunction, **args):
            if args.has_key(name):
                return args[name]
            elif oldFunction.__dict__.has_key(name):
                return oldFunction.__dict__[name]
            return None
        
        #def __call__(self, context):
        #    return self.execute(context)
        
        def __str__(self):
            return "[IceFunction] name='%s'" % self.name









##    #Decorator
    


