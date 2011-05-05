
#    Copyright (C) 2010  Distance and e-Learning Centre,
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
import ldap

pluginName = "ice.auth.ldap"
pluginDesc = ""
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = None
    pluginClass = AuthLDAP
    pluginInitialized = True
    return pluginFunc


class AuthLDAP(object):
    def __init__(self, iceContext, **kwargs):
        self.iceContext = iceContext
        settings = iceContext.settings
        self.ldapUrl = settings.get("ldapUrl")
        self.ou = settings.get("ldapOU", "Staff")
        self.dc = settings.get("ldapDC", "dc=usq,dc=edu,dc=au")


    def checkAuthentication(self, userID, password):
        if password is None or password=="":
            return False
        result = False
        try:
            who = "uid=%s,ou=%s,%s" % (userID, self.ou, self.dc)
            con = ldap.open(self.ldapUrl)
            try:
                rcode, rarr = con.simple_bind_s(who, password)
                if rcode==97:
                    result = True
            finally:
                con.unbind()
        except Exception, e:
            result = False
        return result


    

# cn=CommonName, sn=SurName, uid=UserID, ou=OrganizationalUnit
# con.search_s(base, scope, filter, attr=["cn"])    // Note attr is optional
#   base = "ou=Staff,dc=usq,dc=edu,dc=au"
#   scope = ldap.SCOPE_SUBTREE
#   filter = "sn=X*"    // Note: a filter must be supplied  '*' wild card sn=*x* all surnames with an 'x' in them





