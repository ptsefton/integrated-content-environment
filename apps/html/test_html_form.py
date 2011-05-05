#
#    Copyright (C) 2006  Distance and e-Learning Centre, 
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

from html_form import htmlForm

# serverRequestData (self.formData)
#    method       - "GET" or "POST"
#    path
#    keys         - returns a list of all keys
#    has_key(key) - 
#    remove(key)  - 
#    value(key)   - return the first value for this key  (None if key is not found)
#    values(key)  - returns a list of values for the key (An empty list if the key is not found) 

class mockServerRequestData(object):
    def __init__(self):
        method = "POST"
        path = "/"
        args = {}
        
    def value(self, name):
        v = args.get(name, None)
        if isinstance(v, list):
            if len(v)>0:
                return v[0]
            else:
                return None
        else:
            return v
        
    def values(self, name):
        v = args.get(name, None)
        if v is None:
            return []
        if isinstance(v, list):
            return v
        else:
            return [v]


def test_htmlForm():
    expected = """<form method='POST' name='_fx_' id='_fx_' >
<input type='hidden' name="isPostBack" value="true" />
<input type='hidden' name="_data" value="" />
<input type='hidden' name="_act" value="" />
<script type="text/javascript">_fx=document.forms._fx_;
function test1(){ alert("OK 'testing'"); }
</script>
<a href="javascript:_fx._act.value='act';_fx._data.value='single\\' quot and a double&quot; quote';_fx.submit();" id="_id2" name="_id2">link</a>
</form>
"""
    formData = mockServerRequestData()
    h = htmlForm(formData)
    h.addJavascript("function test1(){ alert(\"OK 'testing'\"); }")
    h.addLink(text="link", action="act", data="single' quot and a double\" quote", submit=True)
    h = str(h)
    assert h == expected
    
    
def test_table():
    expected = """<table id="_id2" name="_id2">
<caption>Caption</caption>
<tbody>
<tr>
<td>One</td>
<td>Two</td>
</tr>
<tr>
<td colspan='2'>Wide</td>
</tr>
<tr>
<td>r3c1</td>
<td>r3c2</td>
</tr>
</tbody>
</table>
"""
    h = htmlForm()
    print "-- Table --"
    t = h.addTable(label="Caption")
    t.addText("One")
    t.addCell()
    t.addText("Two")
    t.addRow()
    t.addCell(colspan=2)
    t.addText("Wide")
    t.addRow()
    t.addText("r3c1")
    t.addCell()
    t.addText("r3c2")
    #print t
    assert str(t) == expected


import os
try:
    os.system("cls")
except: pass
print "Testing"
print "test_htmlForm"
test_htmlForm()
print
print "test_table()"
test_table()
print "Done."











