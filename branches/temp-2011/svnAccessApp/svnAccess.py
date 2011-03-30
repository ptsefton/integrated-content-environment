import os, sys, re

class SvnAccess(object):
    def __init__(self, authFilename):
        self.__filename = authFilename
        self.__dirs = Dir("", None)
        self.__groups = Groups()
        self.__processFile()
    
    def __processFile(self):
        f = open(self.__filename, "rb")
        lines = f.readlines()
        f.close()
        
        stateObj = None
        
        for line in lines:
            l = line.strip()
            if l=="":
                continue
            if l.startswith("#"):
                #comment
                continue
            if l.startswith("["):
                if l.lower().startswith("[groups]"):
                    #Groups section - change to group state
                    stateObj = self.__groups
                else: # path info
                    m = re.search("\[(.*?)\]", l)
                    if m is not None:
                        path = m.groups()[0].strip()
                        dir = self.__dirs.getDir(path)
                        stateObj = dir
            elif stateObj is not None:
                if l.find("#")>0:
                    l, comment = l.split("#")
                    l = l.strip()
                stateObj.processLine(l)
    
    def getXml(self):
        lines = []
        lines.append("<svnAuthz>")
        for line in self.__groups.getXmlLines():
            lines.append("  " + line)
        for line in self.__dirs.getXmlLines():
            lines.append("  " + line)
        lines.append("</svnAuthz>")
        return "\n".join(lines)
    
    def __str__(self):
        s = str(self.__groups)
        s += str(self.__dirs)
        return s


class Dir(object):
    def __init__(self, name, parent):
        self.parent = parent
        self.name = name
        self.__dirs = {}
        self.__defaultAccess = None # None=Inherited or ""=AllUsersNone or 
                                    # "r"=AllUsersRead or "rw"=AllUsersReadWrite
        self.__groups = {}
        self.__users = {}
    
    @property
    def path(self):
        if self.parent is not None:
            return self.parent.path + "/" + self.name
        else:
            return ""
    
    def processLine(self, line):
        # valid lines will be of the form user=|r|rw or @group=|r|rw
        if line.find("=")==-1:
            line += "="
        user, access = [i.strip() for i in line.split("=", 1)]
        access = access.lower()
        if access!="" and access!="r" and access!="rw":
            # Invalid access type
            return
        if line.startswith("@"):    # group
            groupName = user[1:]
            self.__groups[groupName] = access
        elif line.startswith("*"):  #default
            self.__defaultAccess = access
        else:                       # user
            self.__users[user] = access

    def getDir(self, path):
        if path.startswith("/"):
            path = path[1:]
        if path=="":
            return self
        if not path.endswith("/"):
            path += "/"
        name, rest = path.split("/", 1)
        if self.__dirs.has_key(name):
            dir = self.__dirs[name]
            dir = dir.getDir(rest)
        else:
            dir = Dir(name, self)
            self.__dirs[name] = dir
            dir = dir.getDir(rest)
        return dir
    
    def getAllSubDirs(self):
        return self.__dirs.values()
    
    def getXmlLines(self):
        lines = []
        # not yet implemented
        lines.append("<-- Dir.getXmlLines() not yet implemented! -->")
        return lines
    
    def __str__(self):
        s = ""
        if True:
        #if self.__defaultAccess is not None or self.__groups!={} or self.__users!={}:
            s += "\n[%s]" % self.path
            if self.__defaultAccess is not None:
                s += "\n* = %s" % self.__defaultAccess
                s += "    # default all users have %s access" % \
                        {"":"NO", "r":"Read", "rw":"Read/Write"}[self.__defaultAccess]
            else:
                pass
                s += "\n# default access inherited from parent"
            for groupName, groupAccess in self.__groups.iteritems():
                s += "\n@%s = %s" % (groupName, groupAccess)
            for userName, access in self.__users.iteritems():
                s += "\n%s = %s" % (userName, access)
        else:
            s += "\n#[%s]" % self.path
        for dir in self.__dirs.values():
            s += str(dir).replace("\n", "\n  ")
        #s += "\n# end %s\n" % self.path
        return s


class Groups(dict):
    def __init__(self):
        dict.__init__(self)
    
    def processLine(self, line):
        # groupName = list, of, users, and, @otherGroups
        if line.find("=")==-1:
            line += "="
        groupName, usersAndGroups = [i.strip() for i in line.split("=", 1)]
        usersAndGroups = [i.strip() for i in line.split(",")]
        group = Group(groupName, usersAndGroups, self)
        self[groupName] = group
    
    def getXmlLines(self):
        lines = []
        lines.append("<groups>")
        for group in self.values():
            for line in group.getXmlLines():
                lines.append("  " + line)
        lines.append("</groups>")
        return lines
    
    def __str__(self):
        s = "[groups]\n"
        for group in self.values():
            s += str(group)
        return s
    

class Group(object):
    def __init__(self, name, usersAndGroups, parent):
        self.name = name
        self.usersAndGroups = usersAndGroups
        self.parent = parent
    
    @property
    def users(self):
        users = []
        for ug in self.usersAndGroups:
            if ug.startswith("@"):
                for u in self.parent.get(ug[1:], []):
                    users.append(u)
            else:
                users.append(ug)
        return users
    
    def getXmlLines(self):
        lines = []
        lines.append("<group name='%s'>" % self.name)
        for ug in self.usersAndGroups:
            if ug.startswith("@"):
                lines.append("  <group name='%s'/>" % ug[1:])
            else:
                lines.append("  <user name='%s'/>" % ug)
        lines.append("</group>")
        return lines

    def __str__(self):
        s = "%s = %s\n" % (self.name, ", ".join(self.usersAndGroups))
        return s



if __name__=="__main__":
    args = sys.argv
















