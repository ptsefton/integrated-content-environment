# Copyright (C) 2011 Peter Malcolm Sefton
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


import epub2html
import unittest
import json

#Test epub is generated using asciidoc like so:
#  a2x -f epub epub2html-test.txt 


class CheckEpub2Html(unittest.TestCase):
        def testNothing(self):
                p =  epub2html.Epub2Html("epub2html-test.epub","epub2html-test-html.epub", True )
                self.assertEqual(p.toc.getHtml(), "<ul id='toc'><li><a href='OEBPS/index.html' target='content-frame'>Simple test file for Paquete</a><ul><li><a href='OEBPS/index.html#anchor-1' target='content-frame'>1. Part 1</a></li><li><a href='OEBPS/ar01s02.html' target='content-frame'>2. Part 2</a></li><li><a href='OEBPS/ar01s03.html' target='content-frame'>3. Part 3</a></li></ul></li></ul>")
		tocData = json.loads(p.toc.getJsonString())
		self.assertEqual(tocData[0]["title"], "Simple test file for Paquete")
		self.assertEqual(tocData[0]["children"][1]["src"], "OEBPS/ar01s02.html")

if __name__ == "__main__":
    unittest.main()  

