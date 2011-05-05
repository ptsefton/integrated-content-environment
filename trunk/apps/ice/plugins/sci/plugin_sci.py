
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

pluginName = "ice.sci"
pluginDesc = ""
pluginFunc = None           # either (or both) pluginFunc or pluginClass should
pluginClass = None          #   be set by the pluginInit() method
pluginInitialized = False   # set to True by pluginInit() method


def pluginInit(iceContext, **kwargs):
    global pluginFunc, pluginClass, pluginInitialized
    pluginFunc = None
    pluginClass = SciXml
    pluginInitialized = True
    return pluginFunc


from xhtmlToSciXml import XhtmlToSciXml
from oscar3 import Oscar3


class SciXml(object):
    def __init__(self, iceContext, oscar3ServerUri="http://localhost:8181"):
        self.iceContext = iceContext
        self.__oscar3ServerUri = oscar3ServerUri
    
    def markupWithSci(self, xhtmlStr):
        x = XhtmlToSciXml(xhtmlStr)
        sciXmlStr = x.sciXmlStr
        oscar = Oscar3(self.iceContext, serverUri=self.__oscar3ServerUri)
        inlineAnnotatedSci = oscar.inlineAnnotate(sciXmlStr)
        sciXhtml = oscar.process(inlineAnnotatedSci=inlineAnnotatedSci, xhtml=xhtmlStr)
        return sciXhtml
    



# x = XhtmlToSciXml(xhtmlStr)
# x.sciXmlStr





testSciXmlStr = """<PAPER><BODY><DIV><HEADER/><P test="testing">(1R,2R,3aS,4S,6R,8R,8aR)-4,8-bis(acetyloxy)-6-(butanoyloxy)-1,4-dimethyldecahydro-2-azulenyl (2Z)-2-methyl-2-butenoate
</P><DIV><P id='2'>To a solution of <SPAN>x-lcohol</SPAN> 110 (6.7 mg, 0.0174 mmol) in x-oluene (0.5 mL)</P><P x='1'>xy tol<B>uene z</B></P></DIV><DIV><P><P><SPAN>alcohol</SPAN></P></P></DIV>
<DIV><P><SPAN><DIV><P x='2'>butanoyloxy</P></DIV></SPAN></P></DIV>
<TABLE>
 <TR><TD>toluene</TD> <TH>alcohol</TH></TR>
</TABLE>
<LIST>
 <LI>in toluene (0.5 ml)</LI>
 <LI>To a solution of alcohol 110 (6.7 mg, 0.0174 mmol) in toluene (0.5 mL)</LI>
</LIST>
<P>SERCA inhibition was measured at the Department of Medicinal Chemistry, Danish University of Pharmaceutical Sciences, Copenhagen.  The IC50 values were measured as the rate of hydrolysis of ATP by the Ca2+-ATPase in the SR vesicles of isolated rabbit white muscle cells, using thapsigargin as a positive control.  Experimental details were the same as those described in previous publications from the Ley group.58
</P>
</DIV></BODY>
</PAPER>"""

testXhtmlStr = """<div>
<p>(1R,2R,3aS,4S,6R,8R,8aR)-4,8-bis(acetyloxy)-6-(butanoyloxy)-1,4-dimethyldecahydro-2-azulenyl (2Z)-2-methyl-2-butenoate
</p>
<div><p>To a solution of <span>x-lcohol</span> 110 (6.7 mg, 0.0174 mmol) in x-oluene (0.5 mL)</p>
    <p>xy tol<b>uene z</b></p>
</div>
<div><p><p><span>alcohol</span></p></p></div>
<div><p><span><div><p>butanoyloxy</p></div></span></p></div>
<table><tbody>
 <tr><td>toluene</td> <th>alcohol</th></tr>
</tbody></table>
<ol>
 <li>in toluene (0.5 ml)</li>
 <li>To a solution of alcohol 110 (6.7 mg, 0.0174 mmol) in toluene (0.5 mL)</li>
</ol>
<p>SERCA inhibition was measured at the Department of Medicinal Chemistry, Danish University of Pharmaceutical Sciences, Copenhagen.  The IC50 values were measured as the rate of hydrolysis of ATP by the Ca2+-ATPase in the SR vesicles of isolated rabbit white muscle cells, using thapsigargin as a positive control.  Experimental details were the same as those described in previous publications from the Ley group.58
</p>
</div>"""


if __name__ == "__main__":
    import sys, os
    print "Testing"
    os.chdir("../..")
    sys.path.append(os.getcwd())
    from ice_common import IceCommon
    #iceContext = IceCommon.IceContext()
    #print iceContext
    xhtml = testXhtmlStr
    x = XhtmlToSciXml(testXhtmlStr)
    sciXmlStr = x.sciXmlStr
    oscar = Oscar3(IceCommon)
    inlineAnnotatedSci = oscar.inlineAnnotate(sciXmlStr)
    sciXhtml = oscar.process(xhtml=xhtml)
    cmls = oscar.getCmls()
    #print sciXhtml
    #print inlineAnnotatedSci
    print cmls.keys()
    print cmls["cml1"]

