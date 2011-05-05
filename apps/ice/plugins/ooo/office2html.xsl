<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
 
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
                xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
                xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
                xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
                xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
                xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
                xmlns:xlink="http://www.w3.org/1999/xlink"
                xmlns:dc="http://purl.org/dc/elements/1.1/"
                xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0"
                xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0"
                xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"
                xmlns:chart="urn:oasis:names:tc:opendocument:xmlns:chart:1.0"
                xmlns:dr3d="urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0"
                xmlns:math="http://www.w3.org/1998/Math/MathML"
                xmlns:form="urn:oasis:names:tc:opendocument:xmlns:form:1.0"
                xmlns:script="urn:oasis:names:tc:opendocument:xmlns:script:1.0"
                xmlns:ooo="http://openoffice.org/2004/office"
                xmlns:ooow="http://openoffice.org/2004/writer"
                xmlns:oooc="http://openoffice.org/2004/calc"
                xmlns:dom="http://www.w3.org/2001/xml-events"
                xmlns:xforms="http://www.w3.org/2002/xforms"
                xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                
                exclude-result-prefixes="fo xlink office dc style text table draw svg"
 >
<!-- removed  xmlns="http://www.w3.org/1999/xhtml" to resolve namespace issue -->
<!--
XML Style Sheet for OpenOffice.org Writer FlatXML documents

This file is part of the OfficeFMT for OpenOffice.org project,
Version 0.3.

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

(See the included file COPYING / GPL-2.0)

(C) Alexej Kryukov, 2004

Creating this style sheet was inspired by some ideas implemented in
the ooo2html.xsl file by Philipp "philiKON" von Weitershausen, which is 
distributed as a part of his Zope OpenOffice.org document package.
However office2html.xsl was written almost from scratch and currently
has nothing common with ooo2html.xsl. So it is licensed under GNU GPL,
as well as the rest of the OfficeFMT package.

One specific feature of office2html.xsl is that it is designed mainly not
for direct conversion of OpenOffice.org files to (X)HTML (although it may
be used for this purpose), but for displaying OpenOffice.org Writer 
FlatXML files directly in a Web browser (Mozilla or MSIE). FlatXML files
contain the same XML layout as standard OpenOffice.org documents, but are
stored without compression and include all information  which is splitted
trough several files in sxw documents. In particular all styles are
described in the same file, so that it is possible to reproduce correctly
both "hard" and "soft" formatting.

Although this style sheet is rather simple, it provides some unique
features which are not available not only in ooo2html.xsl and similar
"lightweight" style sheets, but also in the standard XHTML filter from the
OpenOffice.org distribution. In particular it has the following
advantages:

* As far as i know, office2html.xsl is the only style sheet which can
correctly handle footnotes and endnotes. Only note references are
displayed in the body text, while notes itself are collected at the end of
document. Additionally footnote and endnote marks are enclosed into <a>
tags, so that it is easy to pass from note reference to its text and vice
versa;

* a similar thing is performed for table of contents, if it is found in
the OpenOffice.org document: in this case not only paragraphs included
into the table of contents are displayed, but also links to the
corresponding headings are added;

* for the CSS 'font-family' property a physical font name, retrieved from 
the office:font-decls block, is used, rather than just a reference to that
block, which not necessarily corresponds to any real font name;

* for ordered lists their style (i. e. Arabic numerals, lowecase or uppercase 
Roman numerals, lowercase or uppercase Latin letters) is preserved. 
Unfortunately it is nearly impossible to preserve other number formatting 
properties due to the limited CSS support in browsers (both in Mozilla and 
MSIE);

* some tricks are added to workaround OpenOffice.org xml format specific
properties, which make it incompatible with other standards like CSS. For
example, all dimensions represented in inches cannot be used directly,
because the word 'inch' should be previously converted to 'in';

* table performance is improved. In particular tables which contain
spanned cells or subtables now look better in browser. However, it is
impossible to achieve an absolutely perfect result here, since some
table formatting properties are treated differently in OOo and browsers.
Moreover, you may get different results even in different versions of 
the same browser (e. g. Mozilla).

If you have any suggestions or bug reports regarding this style sheet,
please send them to Alexej Kryukov <akrioukov_at_openoffice.org>. Any feedback 
is welcome!

$Id: office2html.xsl, v 0.1 2004/07/07 Alexej Kryukov $
-->

<xsl:output encoding="UTF-8" method="xml" indent="no" omit-xml-declaration="no"
            doctype-public="-//W3C//DTD XHTML 1.0 Transitional//EN"
            doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"/>

<xsl:param name="line-break" select="'&#10;'"/>

 <xsl:template match="/" name="root-test">
 <xsl:element name="html" namespace="http://www.w3.org/1999/xhtml">
  <xsl:value-of select="$line-break"/>
  <xsl:element name="head">
   <xsl:value-of select="$line-break"/>
   <xsl:value-of select="$line-break"/>
   <xsl:call-template name="get-title"/>
   <xsl:call-template name="get-styles"/>
  </xsl:element>
  <xsl:value-of select="$line-break"/>
  <xsl:call-template name="show-document"/>
 </xsl:element>
 <xsl:value-of select="$line-break"/>
</xsl:template>

<!-- Document title -->

<xsl:template name="get-title">
 <xsl:element name="title">
  <xsl:choose>
   <xsl:when test="/office:document/office:meta/dc:title/text()[1]">
    <xsl:value-of select="/office:document/office:meta/dc:title/text()[1]"/>
   </xsl:when>
   <xsl:otherwise>
    <xsl:text>OpenOffice.org document converted by OfficeFMT</xsl:text>
   </xsl:otherwise>
  </xsl:choose>
 </xsl:element>
 <xsl:value-of select="$line-break"/>
</xsl:template>

<!-- Style handling block, used to build CSS styles needed to display
the document body-->

<xsl:template name="get-styles">
 <xsl:element name="style">
  <xsl:attribute name="type">text/css</xsl:attribute>
  <!-- Override HTML defaults -->
  <xsl:value-of select="$line-break"/>
  <xsl:text>p, ol, ul {margin-top: 0pt; margin-bottom: 0pt;}</xsl:text>
  <xsl:value-of select="$line-break"/>
  <xsl:text>ol, ul {margin-left: 0pt; padding-left: 0pt;}</xsl:text>
  <xsl:value-of select="$line-break"/>
  <xsl:text>table, tr, th, td {border-spacing: 0;}</xsl:text>
  <xsl:value-of select="$line-break"/>
  <!-- The following line is needed to display correctly table cells which 
       span through several columns. However if you have encountered any 
       problems with table columns handling block (see below), you may want 
       to remove this line too -->
  <xsl:text>table {table-layout: fixed;}</xsl:text>
  <xsl:value-of select="$line-break"/>
  <xsl:apply-templates select="/office:document/office:styles"/>
  <xsl:apply-templates select="/office:document/office:automatic-styles"/>
 </xsl:element>
 <xsl:value-of select="$line-break"/>
</xsl:template>

<xsl:template match="/office:document/office:styles|/office:document/office:automatic-styles">
 <xsl:apply-templates select="style:style|style:default-style|text:list-style"/>
</xsl:template>

<!-- Process styles and build CSS information-->
<xsl:template match="style:style">
 <xsl:param name="style-name" select="translate (@style:name, ' .', '__')"/>
 <xsl:param name="style-family" select="@style:family"/>
 <xsl:variable name="parent-style" select="translate (@style:parent-style-name, ' .', '__')"/>
 <xsl:variable name="style-group">
  <xsl:choose>
   <xsl:when test="$style-family = 'paragraph'">
    <xsl:choose>
     <xsl:when test="contains ($style-name, 'Heading_')">
      <xsl:variable name="level" select="substring-after($style-name,'Heading_')"/>
      <xsl:text>h</xsl:text><xsl:value-of select="$level"/><xsl:text>.</xsl:text><xsl:value-of select="$style-name"/>
     </xsl:when>
     <xsl:when test="contains ($parent-style, 'Heading_')">
      <xsl:variable name="level" select="substring-after($parent-style,'Heading_')"/>
      <xsl:text>h</xsl:text><xsl:value-of select="$level"/><xsl:text>.</xsl:text><xsl:value-of select="$style-name"/>
     </xsl:when>
     <xsl:otherwise>
      <xsl:text>p.</xsl:text><xsl:value-of select="$style-name"/>
     </xsl:otherwise>
    </xsl:choose>
   </xsl:when>
   <xsl:when test="$style-family = 'text'">
    <xsl:text>span.</xsl:text><xsl:value-of select="$style-name"/>
   </xsl:when>
   <xsl:when test="$style-family = 'section' or $style-family = 'graphics'">
    <xsl:text>div.</xsl:text><xsl:value-of select="$style-name"/>
   </xsl:when>
   <xsl:when test="$style-family = 'table'">
    <xsl:text>table.</xsl:text><xsl:value-of select="$style-name"/>
   </xsl:when>
   <xsl:when test="$style-family = 'table-column'">
    <xsl:text>col.</xsl:text><xsl:value-of select="$style-name"/>
   </xsl:when>
   <xsl:when test="$style-family = 'table-cell'">
    <xsl:text>th.</xsl:text><xsl:value-of select="$style-name"/><xsl:text>, td.</xsl:text><xsl:value-of select="$style-name"/>
   </xsl:when>
   <xsl:when test="$style-family = 'table-row'">
    <xsl:text>tr.</xsl:text><xsl:value-of select="$style-name"/>
   </xsl:when>
  </xsl:choose>
 </xsl:variable>
 <xsl:if test="string($style-group) != ''">
  <xsl:value-of select="$style-group"/><xsl:text> {</xsl:text>
  <xsl:apply-templates select="." mode="css-style"/>
  <xsl:text>}</xsl:text>
  <xsl:value-of select="$line-break"/>
 </xsl:if>
</xsl:template>

<!-- A simplified procedure for default paragraph style -->
<xsl:template match="style:default-style">
 <xsl:variable name="style-family" select="@style:family"/>
 <xsl:variable name="style-group">
  <xsl:choose>
   <xsl:when test="$style-family = 'paragraph'">
     <xsl:text>p</xsl:text>
   </xsl:when>
  </xsl:choose>
 </xsl:variable>
 <xsl:if test="string($style-group) != ''">
  <xsl:value-of select="$style-group"/><xsl:text> {</xsl:text>
  <xsl:apply-templates select="style:properties/@*" mode="style"/>
  <xsl:text>}</xsl:text>
  <xsl:value-of select="$line-break"/>
 </xsl:if>
</xsl:template>

<!-- Standard procedure for processing a single style with its parent-->
<xsl:template match="style:style" mode="css-style">
 <xsl:param name="context"/>
 <xsl:if test="@style:parent-style-name">
  <xsl:variable name="parent-name" select="@style:parent-style-name" />
  <xsl:apply-templates select="//style:style[@style:name=$parent-name]" mode="css-style">
   <xsl:with-param name="context" select="."/>
  </xsl:apply-templates>
 </xsl:if>
 <xsl:for-each select="style:properties/@*">
  <xsl:variable name="prop-name" select="name()"/>
  <xsl:if test="($context = '') or (not ($context/style:properties/@*[name() = $prop-name]))">
   <xsl:apply-templates select="." mode="style"/>
  </xsl:if>
 </xsl:for-each>
</xsl:template>

<!-- A special template is needed for list styles-->

<xsl:template match="text:list-style">
 <xsl:variable name="style-name" select="@style:name" />
 <xsl:apply-templates select="text:list-level-style-number|text:list-level-style-bullet" mode="css-style">
  <xsl:with-param name="style-name" select="$style-name"/>
 </xsl:apply-templates>
</xsl:template>

<xsl:template match="text:list-level-style-number|text:list-level-style-bullet" mode="css-style">
 <xsl:param name="style-name"/>
 <xsl:variable name="type">
  <xsl:choose>
   <xsl:when test="local-name(.) = 'list-level-style-number'">
    <xsl:text>ol.</xsl:text>
   </xsl:when>
   <xsl:when test="local-name(.) = 'list-level-style-bullet'">
    <xsl:text>ul.</xsl:text>
   </xsl:when>
  </xsl:choose>
 </xsl:variable>
 <xsl:variable name="level" select="@text:level"/>
  <xsl:value-of select="$type"/><xsl:value-of select="concat($style-name, '-', $level)"/>
 <xsl:text> {</xsl:text>
 <xsl:apply-templates select="@*" mode="style"/>
 <xsl:apply-templates select="style:properties/@*" mode="style"/>
 <xsl:text>}</xsl:text>
 <xsl:value-of select="$line-break"/>
</xsl:template>

<!-- Style Attributes -->

<!-- In OOo inch is named "inch", while in CSS the only possible designation 
     is "in". So all dimensions represented in inches need this conversion 
     procedure-->
<xsl:template name="fix-inches">
 <xsl:param name="attrib-value"/>
 <xsl:choose>
  <xsl:when test="contains ($attrib-value, 'inch')">
   <xsl:value-of select="concat (substring-before($attrib-value, 'inch'), 'in', substring-after($attrib-value, 'inch'))"/>
  </xsl:when>
  <xsl:otherwise>
   <xsl:value-of select="$attrib-value"/>
  </xsl:otherwise>
 </xsl:choose>
</xsl:template>

<!-- Common behavior for all fo:* attributes: by default they are just
     reproduced with their local name -->
<xsl:template match="@fo:*" mode="style" priority="0">
 <xsl:value-of select="local-name()"/><xsl:text>:</xsl:text>
 <xsl:call-template name="fix-inches">
  <xsl:with-param name="attrib-value" select="."/>
 </xsl:call-template>
 <xsl:text>; </xsl:text>
</xsl:template>

<!-- The following formatting properties are not supported in CSS -->
<xsl:template match="@fo:country|@fo:language" mode="style" priority="2"/>
<xsl:template match="@*[starts-with(name(), 'fo:hyphenat')]" mode="style" priority="2"/>
<xsl:template match="@fo:keep-with-next" mode="style" priority="2"/>

<!-- Block level formatting -->

<xsl:template match="@fo:text-align" mode="style" priority="2">
 <xsl:if test=". = 'start'">text-align:left; </xsl:if>
 <xsl:if test=". = 'center'">text-align:center; </xsl:if>
 <xsl:if test=". = 'end'">text-align:right; </xsl:if>
 <xsl:if test=". = 'justify'">text-align:justify; </xsl:if>
</xsl:template>

<xsl:template match="@fo:break-before|@fo:break-after" mode="style" priority="2">
 <xsl:choose>
  <xsl:when test="contains (., 'page')">
   <xsl:text>page-</xsl:text><xsl:value-of select="local-name()"/><xsl:text>: always; </xsl:text>
  </xsl:when>
  <xsl:otherwise>
   <xsl:text>page-</xsl:text><xsl:value-of select="local-name()"/><xsl:text>: auto; </xsl:text>
  </xsl:otherwise>
 </xsl:choose>
</xsl:template>

<xsl:template match="@style:width" mode="style">
 <xsl:value-of select="local-name(.)"/><xsl:text>:</xsl:text>
 <xsl:call-template name="fix-inches">
  <xsl:with-param name="attrib-value" select="."/>
 </xsl:call-template>
 <xsl:text>; </xsl:text>
</xsl:template>

<!-- Character formatting -->

<xsl:template match="@style:font-name" mode="style">
 <xsl:variable name="font-style" select="."/>
 <xsl:variable name="font-family" select="/office:document/office:font-decls/style:font-decl[@style:name=$font-style]/@fo:font-family"/>
 <xsl:text>font-family:</xsl:text><xsl:value-of select="$font-family"/><xsl:text>; </xsl:text>
</xsl:template>

<xsl:template match="@style:text-position" mode="style">
 <xsl:param name="position" select="." />
 <xsl:if test="contains ($position, 'super')">vertical-align:super; font-size: 60%;</xsl:if>
 <xsl:if test="contains ($position, 'sub')">vertical-align:sub; font-size: 60%;</xsl:if>
</xsl:template>

<xsl:template match="@style:text-underline" mode="style">
 <xsl:if test=". != 'none'">
   <xsl:text>text-decoration:underline; </xsl:text>
 </xsl:if>
</xsl:template>

<xsl:template match="@style:text-crossing-out" mode="style">
 <xsl:if test=". != 'none'">
  <xsl:text>text-decoration:line-through; </xsl:text>
 </xsl:if>
</xsl:template>

<xsl:template match="@style:text-blinking" mode="style">
 <xsl:if test=". != 'none'">
  <xsl:text>text-decoration:blink; </xsl:text>
 </xsl:if>
</xsl:template>

<xsl:template match="@style:text-background-color" mode="style">
 <xsl:text>background-color:</xsl:text><xsl:value-of select="." /><xsl:text>; </xsl:text>
</xsl:template>

<!-- Numbered lists-->

<xsl:template match="@style:num-format" mode="style">
 <xsl:if test=".='1'">list-style-type:decimal; </xsl:if>
 <xsl:if test=".='a'">list-style-type:lower-latin; </xsl:if>
 <xsl:if test=".='A'">list-style-type:upper-latin; </xsl:if>
 <xsl:if test=".='I'">list-style-type:upper-roman; </xsl:if>
 <xsl:if test=".='i'">list-style-type:lower-roman; </xsl:if>
</xsl:template>

<xsl:template match="@text:space-before" mode="style">
 <xsl:text>margin-left:</xsl:text>
 <xsl:call-template name="fix-inches">
  <xsl:with-param name="attrib-value" select="."/>
 </xsl:call-template>
 <xsl:text>; </xsl:text>
</xsl:template>

<xsl:template match="@text:min-label-width" mode="style">
 <xsl:text>padding-left:</xsl:text>
 <xsl:call-template name="fix-inches">
  <xsl:with-param name="attrib-value" select="."/>
 </xsl:call-template>
 <xsl:text>; </xsl:text>
</xsl:template>

<!-- Table dimensions -->

<xsl:template match="@style:column-width" mode="style">
 <xsl:text>width:</xsl:text>
 <xsl:call-template name="fix-inches">
  <xsl:with-param name="attrib-value" select="."/>
 </xsl:call-template>
 <xsl:text>; </xsl:text>
</xsl:template>

<xsl:template match="@style:min-row-height" mode="style">
 <xsl:text>min-height:</xsl:text>
 <xsl:call-template name="fix-inches">
  <xsl:with-param name="attrib-value" select="."/>
 </xsl:call-template>
 <xsl:text>; </xsl:text>
</xsl:template>

<!-- Borders -->

<xsl:template match="@*[starts-with(name(.), 'style:border')]" mode="style">
 <xsl:if test="local-name(.) = 'border-line-width'">border-width:</xsl:if>
 <xsl:if test="local-name(.) = 'border-line-width-top'">border-top-width:</xsl:if>
 <xsl:if test="local-name(.) = 'border-line-width-bottom'">border-bottom-width:</xsl:if>
 <xsl:if test="local-name(.) = 'border-line-width-left'">border-left-width:</xsl:if>
 <xsl:if test="local-name(.) = 'border-line-width-right'">border-right-width:</xsl:if>
 <xsl:call-template name="fix-inches">
  <xsl:with-param name="attrib-value" select="."/>
 </xsl:call-template>
 <xsl:text>; </xsl:text>
</xsl:template>

<!-- we need this, otherwise the processor will just print the attribute
     contents while we want unmatched attributes not to appear -->
<xsl:template match="@*" mode="style"/>

<!-- Now display the document itself -->

<xsl:template name="show-document">
 <xsl:element name="body">
  <xsl:value-of select="$line-break"/>
  <xsl:apply-templates select="/office:document/office:body"/>
  <xsl:if test="//text:footnote">
   <xsl:element name="hr"/>
   <xsl:value-of select="$line-break"/>
   <xsl:apply-templates select="//text:footnote" mode="notes"/>
  </xsl:if>
  <xsl:if test="//text:endnote">
   <xsl:element name="hr"/>
   <xsl:value-of select="$line-break"/>
   <xsl:apply-templates select="//text:endnote" mode="notes"/>
  </xsl:if>
 </xsl:element>
 <xsl:value-of select="$line-break"/>
</xsl:template>

<!-- Text Content ... pages 117ff file format documentation-->

<!-- Table of contents -->
<xsl:template match="text:table-of-content">
 <xsl:variable name="toc-depth" select="text:table-of-content-source/@text:outline-level"/>
 <xsl:element name="div">
  <xsl:attribute name="class">
   <xsl:value-of select="translate (@text:style-name, ' .', '__')"/>
  </xsl:attribute>
  <xsl:value-of select="$line-break"/>
  <xsl:element name="p">
   <xsl:variable name="toc-title" select="text:table-of-content-source/text:index-title-template"/>
   <xsl:attribute name="class">
    <xsl:value-of select="translate ($toc-title/@text:style-name, ' .', '__')"/>
   </xsl:attribute>
   <xsl:value-of select="$toc-title/text()"/>
  </xsl:element>
  <xsl:value-of select="$line-break"/>
  <xsl:apply-templates select="//text:h" mode="toc">
   <xsl:with-param name="toc-depth" select="$toc-depth"/>
  </xsl:apply-templates>
 </xsl:element>
</xsl:template>

<!-- Illustration index -->
<xsl:template match="text:illustration-index">
 <xsl:element name="div">
  <xsl:attribute name="class">
   <xsl:value-of select="translate (@text:style-name, ' .', '__')"/>
  </xsl:attribute>
  <xsl:value-of select="$line-break"/>
  <xsl:element name="p">
   <xsl:variable name="list-title" select="text:illustration-index-source/text:index-title-template"/>
   <xsl:attribute name="class">
    <xsl:value-of select="translate ($list-title/@text:style-name, ' .', '__')"/>
   </xsl:attribute>
   <xsl:value-of select="$list-title/text()"/>
  </xsl:element>
  <xsl:value-of select="$line-break"/>
  <xsl:for-each select="//text:p[@text:style-name = 'Illustration'][draw:image]">
   <xsl:apply-templates select="." mode="illustration-index"/>
  </xsl:for-each>
 </xsl:element>
</xsl:template>

<!-- Table index -->
<xsl:template match="text:table-index">
 <xsl:element name="div">
  <xsl:attribute name="class">
   <xsl:value-of select="translate (@text:style-name, ' .', '__')"/>
  </xsl:attribute>
  <xsl:value-of select="$line-break"/>
  <xsl:element name="p">
   <xsl:variable name="list-title" select="text:table-index-source/text:index-title-template"/>
   <xsl:attribute name="class">
    <xsl:value-of select="translate ($list-title/@text:style-name, ' .', '__')"/>
   </xsl:attribute>
   <xsl:value-of select="$list-title/text()"/>
  </xsl:element>
  <xsl:value-of select="$line-break"/>
  <xsl:for-each select="//text:p[@text:style-name = 'Table'][preceding-sibling::*[1][name() = 'table:table']]">
   <xsl:apply-templates select="." mode="table-index"/>
  </xsl:for-each>
 </xsl:element>
</xsl:template>

<!-- Section -->
<xsl:template match="text:section">
 <xsl:element name="div">
  <xsl:if test="@text:style-name">
   <xsl:attribute name="class">
    <xsl:value-of select="translate (@text:style-name, ' .', '__')"/>
   </xsl:attribute>
  </xsl:if>
  <xsl:value-of select="$line-break"/>
  <xsl:apply-templates />
 </xsl:element>
 <xsl:value-of select="$line-break"/>
</xsl:template>

<!-- Heading -->
<xsl:template match="text:h">
 <xsl:variable name="level" select="@text:level"/>
 <xsl:variable name="number" select="count (preceding::text:h[@text:level = $level]) + 1"/>
 <xsl:element name="h{$level}">
  <xsl:if test="@text:style-name">
   <xsl:attribute name="class">
    <xsl:value-of select="translate (@text:style-name, ' .', '__')"/>
   </xsl:attribute>
  </xsl:if>
  <xsl:element name="a">
   <xsl:attribute name="name">
    <xsl:text>h</xsl:text><xsl:value-of select="concat ($level, '-', $number)"/>
   </xsl:attribute>
  </xsl:element>
  <xsl:call-template name="number-headings">
   <xsl:with-param name="heading-context" select="self::node()"/>
   <xsl:with-param name="level" select="$level"/>
  </xsl:call-template>
  <xsl:apply-templates />
 </xsl:element>
 <xsl:value-of select="$line-break"/>
 <xsl:if test="draw:text-box">
  <xsl:apply-templates mode="frame"/>
 </xsl:if>
</xsl:template>

<!-- Heading processing for TOC entries -->
<xsl:template match="//text:h" mode="toc">
 <xsl:param name="toc-depth" select="10"/>
 <xsl:variable name="level" select="@text:level"/>
 <xsl:if test="$level &lt;= $toc-depth">
  <xsl:variable name="number" select="count (preceding::text:h[@text:level = $level]) + 1"/>
  <xsl:element name="p">
   <xsl:attribute name="class">
    <xsl:variable name="toc-class" select="//text:table-of-content-entry-template[@text:outline-level = $level]/@text:style-name"/>
    <xsl:value-of select="translate ($toc-class, ' .', '__')"/>
   </xsl:attribute>
   <xsl:element name="a">
    <xsl:attribute name="href">
     <xsl:text>#h</xsl:text><xsl:value-of select="concat ($level, '-', $number)"/>
    </xsl:attribute>
    <xsl:call-template name="number-headings">
     <xsl:with-param name="heading-context" select="self::node()"/>
     <xsl:with-param name="level" select="$level"/>
    </xsl:call-template>
    <xsl:apply-templates/>
   </xsl:element>
  </xsl:element>
 </xsl:if>
 <xsl:value-of select="$line-break"/>
</xsl:template>

<!-- Heading numbering, used both for the main text and TOC -->
<xsl:template name="number-headings">
 <xsl:param name="heading-context"/>
 <xsl:param name="level"/>
 <xsl:variable name="num-style-node" select="//text:outline-style/text:outline-level-style[@text:level=$level]"/>
 <xsl:variable name="num-format" select="$num-style-node/@style:num-format"/>
 <xsl:if test="$num-format != ''">
  <xsl:variable name="levels">
   <xsl:choose>
    <xsl:when test="$num-style-node/@text:display-levels">
     <xsl:value-of select="$num-style-node/@text:display-levels"/>
    </xsl:when>
    <xsl:otherwise>
     <xsl:text>1</xsl:text>
    </xsl:otherwise>
   </xsl:choose>
  </xsl:variable>
  <xsl:for-each select="//text:outline-style/text:outline-level-style[(@text:level &lt;= $level) and (@text:level &gt; ($level - $levels))]">
   <xsl:variable name="num-prefix" select="@style:num-prefix"/>
   <xsl:variable name="num-suffix" select="@style:num-suffix"/>
   <xsl:variable name="cur-level" select="@text:level"/>
   <xsl:variable name="cur-num-format" select="@style:num-format"/>
   <xsl:for-each select="$heading-context">
    <xsl:number level="any" count="//text:h[@text:level = $cur-level]" format="{concat ($num-prefix, $cur-num-format, $num-suffix)}"/>
   </xsl:for-each>
  </xsl:for-each>
  <xsl:text>&#160;</xsl:text>
 </xsl:if>
</xsl:template>

<!-- Paragraph -->
<xsl:template match="text:p">
 <xsl:param name="level" select="0"/>
 <xsl:param name="list-style"/>
 <xsl:element name="p">
  <xsl:if test="@text:style-name">
   <xsl:attribute name="class">
    <xsl:value-of select="translate (@text:style-name, ' .', '__')"/>
   </xsl:attribute>
  </xsl:if>
  <!-- Indents are ignored in numbered paragraphs -->
  <xsl:if test="$level > 0">
   <xsl:attribute name="style">
    <xsl:text>text-indent: 0pt;</xsl:text>
   </xsl:attribute>
  </xsl:if>
  <xsl:choose>
   <xsl:when test="child::* or child::text()">
    <xsl:apply-templates/>
   </xsl:when>
   <!-- If this paragraph is empty, insert a non breaking space to prevent it
   from disappearing in HTML document-->
   <xsl:otherwise>
    <xsl:text>&#160;</xsl:text>
   </xsl:otherwise>
  </xsl:choose>
 </xsl:element>
 <xsl:value-of select="$line-break"/>
 <xsl:if test="draw:text-box">
  <xsl:apply-templates mode="frame"/>
 </xsl:if>
</xsl:template>

<!-- Illustration index entries -->
<xsl:template match="text:p" mode="illustration-index">
 <xsl:variable name="link-name" select="draw:image/@draw:name"/>
 <xsl:element name="p">
  <xsl:attribute name="class">
   <xsl:variable name="index-class" select="//text:illustration-index-entry-template/@text:style-name"/>
   <xsl:value-of select="translate ($index-class, ' .', '__')"/>
  </xsl:attribute>
  <xsl:element name="a">
   <xsl:attribute name="href">
    <xsl:text>#</xsl:text><xsl:value-of select="$link-name"/>
   </xsl:attribute>
   <xsl:apply-templates select="child::node()[name() != 'draw:image']"/>
  </xsl:element>
 </xsl:element>
 <xsl:value-of select="$line-break"/>
</xsl:template>

<!-- Table index entries -->
<xsl:template match="text:p" mode="table-index">
 <xsl:variable name="link-name" select="preceding-sibling::table:table/@table:name"/>
 <xsl:element name="p">
  <xsl:attribute name="class">
   <xsl:variable name="index-class" select="//text:table-index-entry-template/@text:style-name"/>
   <xsl:value-of select="translate ($index-class, ' .', '__')"/>
  </xsl:attribute>
  <xsl:element name="a">
   <xsl:attribute name="href">
    <xsl:text>#</xsl:text><xsl:value-of select="$link-name"/>
   </xsl:attribute>
   <xsl:apply-templates/>
  </xsl:element>
 </xsl:element>
 <xsl:value-of select="$line-break"/>
</xsl:template>

<!-- First Paragraph in footnote/endnote: display note reference first-->
<xsl:template match="text:p" mode="footnote-first">
 <xsl:param name="note-id"/>
 <xsl:param name="note-type"/>
 <xsl:variable name="citation-name" select="concat('text:', $note-type, '-citation')"/>
 <xsl:element name="p">
  <xsl:if test="@text:style-name">
   <xsl:attribute name="class">
    <xsl:value-of select="translate (@text:style-name, ' .', '__')"/>
   </xsl:attribute>
  </xsl:if>
  <xsl:apply-templates select="ancestor::node()[2]/*[name()=$citation-name]">
   <xsl:with-param name="note-type" select="$note-type"/>
   <xsl:with-param name="anchor-name" select="$note-id"/>
   <xsl:with-param name="anchor-ref" select="concat('#', $note-id, '-text')"/>
  </xsl:apply-templates>
  <xsl:text>&#160;</xsl:text>
  <xsl:apply-templates/>
 </xsl:element>
 <xsl:value-of select="$line-break"/>
</xsl:template>

<!-- Span -->
<xsl:template match="text:span">
 <xsl:element name="span">
  <xsl:if test="@text:style-name">
   <xsl:attribute name="class">
    <xsl:value-of select="translate (@text:style-name, ' .', '__')"/>
   </xsl:attribute>
  </xsl:if>
  <xsl:apply-templates />
 </xsl:element>
</xsl:template>

<!-- Tab Stop-->
<xsl:template match="text:tab-stop">
 <xsl:text>&#160;&#160;&#160;&#160;&#160;</xsl:text>
</xsl:template>

<!-- Space -->
<xsl:template match="text:s">
 <xsl:choose>
  <xsl:when test="@text:c">
   <xsl:call-template name="for">
    <xsl:with-param name="n" select="@text:c"/>
   </xsl:call-template>
  </xsl:when>
  <xsl:otherwise>
   <xsl:text>&#160;</xsl:text>
  </xsl:otherwise>
 </xsl:choose>
</xsl:template>

<xsl:template name="for">
 <xsl:param name="i" select="0"/>
 <xsl:param name="n"/>
 <xsl:if test="$i &lt; $n">
  <xsl:text>&#160;</xsl:text>
  <xsl:call-template name="for">
   <xsl:with-param name="i" select="$i + 1"/>
   <xsl:with-param name="n" select="$n"/>
  </xsl:call-template>
 </xsl:if>
</xsl:template>

<!-- Prevents inserting text nodes which have no "text:p" ancestors,
for example, any indents or line break characters inserted in the initial
xml document for better readability, and thus allows to generate a 
clearer output. -->

<xsl:template match="text()">
 <xsl:if test="ancestor::text:p or ancestor::text:h">
  <xsl:value-of select="normalize-space(.)"/>
 </xsl:if>
</xsl:template>

<xsl:template match="text()" mode="frame"/>
<xsl:template match="text()" mode="header-row"/>

<!-- Line break  -->
<xsl:template match="text:line-break">
 <xsl:element name="br"/>
 <xsl:value-of select="$line-break"/>
</xsl:template>

<!-- Footnote/endnote processing in body text 
     (only note reference should appear) -->
<xsl:template match="text:footnote|text:endnote">
 <xsl:variable name="note-id" select="@text:id"/>
 <xsl:variable name="note-type" select="local-name()"/>
 <xsl:variable name="citation-name" select="concat('text:', local-name(.), '-citation')"/>
 <xsl:apply-templates select="*[name()=$citation-name]">
  <xsl:with-param name="note-type" select="$note-type"/>
  <xsl:with-param name="anchor-name" select="concat($note-id, '-text')"/>
  <xsl:with-param name="anchor-ref" select="concat ('#', $note-id)"/>
 </xsl:apply-templates>
</xsl:template>

<!-- Processing footnote/endnote block (note contents are shown) -->
<xsl:template match="text:footnote|text:endnote" mode="notes">
 <xsl:variable name="note-id" select="@text:id"/>
 <xsl:variable name="note-type" select="local-name(.)"/>
 <xsl:variable name="body-name" select="concat('text:', $note-type, '-body')"/>
 <xsl:apply-templates select="*[name()=$body-name]/text:p[1]" mode="footnote-first">
  <xsl:with-param name="note-id" select="$note-id"/>
  <xsl:with-param name="note-type" select="$note-type"/>
 </xsl:apply-templates>
 <xsl:apply-templates select="*[name()=$body-name]/text:p[position() > 1]"/>
</xsl:template>

<!-- Footnote/endnote citations (used both in body text and 
     footnote/endnote blocks, but with different parameters for the
     anchor tag -->
<xsl:template match="text:footnote-citation|text:endnote-citation">
 <xsl:param name="note-type"/>
 <xsl:param name="anchor-name"/>
 <xsl:param name="anchor-ref"/>
 <xsl:variable name="config-name" select="concat('text:', $note-type, 's-configuration')"/>
 <xsl:variable name="style-name" select="//*[name()=$config-name][1]/@text:citation-body-style-name"/>
 <xsl:element name="a">
  <xsl:attribute name="name"><xsl:value-of select="$anchor-name"/></xsl:attribute>
  <xsl:attribute name="href"><xsl:value-of select="$anchor-ref"/></xsl:attribute>
  <xsl:element name="span">
   <xsl:attribute name="style">
    <xsl:apply-templates select="//style:style[@style:name=$style-name]/style:properties/@*" mode="style" />
   </xsl:attribute>
   <xsl:apply-templates/>
  </xsl:element>
 </xsl:element>
</xsl:template>

<!-- Ordered or unordered lists  -->
<xsl:template match="text:ordered-list|text:unordered-list">
 <xsl:param name="level" select="1"/>
 <xsl:param name="list-style" select="@text:style-name"/>
 <xsl:variable name="type">
  <xsl:choose>
   <xsl:when test="local-name(.) = 'ordered-list'">
    <xsl:text>ol</xsl:text>
   </xsl:when>
   <xsl:when test="local-name(.) = 'unordered-list'">
    <xsl:text>ul</xsl:text>
   </xsl:when>
  </xsl:choose>
 </xsl:variable>
 <xsl:variable name="class" select="concat($list-style, '-', $level)"/>
 <xsl:element name="{$type}">
  <xsl:attribute name="class">
   <xsl:value-of select="$class"/>
  </xsl:attribute>
  <xsl:value-of select="$line-break"/>
  <xsl:apply-templates select="text:list-header|text:list-item">
   <xsl:with-param name="level" select="$level + 1"/>
   <xsl:with-param name="list-style" select="$list-style"/>
  </xsl:apply-templates>
 </xsl:element>
 <xsl:value-of select="$line-break"/>
</xsl:template>

<!-- List items -->
<xsl:template match="text:list-item">
 <xsl:param name="level"/>
 <xsl:param name="list-style"/>
 <xsl:choose>
  <xsl:when test="child::*[1][name()='text:p' or name()='text:h']">
   <xsl:element name="li">
    <xsl:value-of select="$line-break"/>
    <xsl:apply-templates select="text:ordered-list|text:unordered-list|text:p|text:h">
     <xsl:with-param name="level" select="$level"/>
     <xsl:with-param name="list-style" select="$list-style"/>
    </xsl:apply-templates>
   </xsl:element>
   <xsl:value-of select="$line-break"/>
  </xsl:when>
  <xsl:otherwise>
    <xsl:apply-templates select="text:ordered-list|text:unordered-list|text:p|text:h">
     <xsl:with-param name="level" select="$level"/>
     <xsl:with-param name="list-style" select="$list-style"/>
    </xsl:apply-templates>
  </xsl:otherwise>
 </xsl:choose>
</xsl:template>

<!-- Link -->
<xsl:template match="text:a">
 <xsl:element name="a">
  <xsl:attribute name="href"><xsl:value-of select="@xlink:href" /></xsl:attribute>
  <xsl:if test="@office:target-frame-name">
   <xsl:attribute name="target"><xsl:value-of select="@office:target-frame-name" /></xsl:attribute>
  </xsl:if>
  <xsl:apply-templates />
 </xsl:element>
</xsl:template>


<!-- Bookmark -->
<xsl:template match="text:bookmark">
 <xsl:element name="a">
  <xsl:attribute name="id"><xsl:value-of select="@text:name"/></xsl:attribute>
 </xsl:element>
</xsl:template>

<!-- Table Content ... pages 239ff file format documentation-->

<!-- Table  -->
<xsl:template match="table:table|table:sub-table">
 <xsl:element name="table">
  <xsl:if test="@table:style-name">
   <xsl:attribute name="class">
    <xsl:value-of select="translate (@table:style-name, ' .', '__')"/>
   </xsl:attribute>
  </xsl:if>
  <xsl:value-of select="$line-break"/>
  <xsl:if test="@table:name">
   <xsl:element name="a">
    <xsl:attribute name="name">
     <xsl:value-of select="@table:name"/>
    </xsl:attribute>
   </xsl:element>
  </xsl:if>
  <xsl:value-of select="$line-break"/>
  <xsl:apply-templates/>
 </xsl:element>
 <xsl:value-of select="$line-break"/>
</xsl:template>

<!-- Table Columns -->
<!-- The following block is absolutely correct and it is needed
     in order to reproduce correctly column widths, especially if a table
     contains some cells spanned through several columns. However,
     it may cause either crashes or performance problems in various versions 
     of the Mozilla browser. So if you have faced one of such problems,
     you may want to remove it. Of course this will make the resulting HTML
     output less correct.
-->
<xsl:template match="table:table-column">
 <xsl:choose>
  <xsl:when test="@table:number-columns-repeated">
   <xsl:element name="colgroup">
    <xsl:if test="@table:style-name">
     <xsl:attribute name="class">
      <xsl:value-of select="translate (@table:style-name, ' .', '__')"/>
     </xsl:attribute>
     <xsl:attribute name="span">
      <xsl:value-of select="@table:number-columns-repeated"/>
     </xsl:attribute>
    </xsl:if>
   </xsl:element>
   <xsl:value-of select="$line-break"/>
  </xsl:when>
  <xsl:otherwise>
   <xsl:element name="col">
    <xsl:if test="@table:style-name">
     <xsl:attribute name="class">
      <xsl:value-of select="translate (@table:style-name, ' .', '__')"/>
     </xsl:attribute>
    </xsl:if>
   </xsl:element>
   <xsl:value-of select="$line-break"/>
  </xsl:otherwise>
 </xsl:choose>
</xsl:template>

<!-- End of the problematic block. -->

<!-- Table Header Rows -->
<xsl:template match="table:table-header-rows">
  <xsl:apply-templates mode="header-row" />
</xsl:template>

<!-- Table Row -->
<xsl:template match="table:table-row">
 <xsl:element name="tr">
  <xsl:if test="@table:style-name">
   <xsl:attribute name="class">
    <xsl:value-of select="translate (@table:style-name, ' .', '__')"/>
   </xsl:attribute>
  </xsl:if>
  <xsl:value-of select="$line-break"/>
  <xsl:apply-templates />
 </xsl:element>
 <xsl:value-of select="$line-break"/>
</xsl:template>

<!-- Table Cell -->
<xsl:template match="table:table-cell">
 <xsl:element name="td">
  <xsl:if test="@table:style-name">
   <xsl:attribute name="class">
    <xsl:value-of select="translate (@table:style-name, ' .', '__')"/>
   </xsl:attribute>
  </xsl:if>
  <xsl:if test="@table:number-columns-spanned">
   <xsl:attribute name="colspan">
    <xsl:value-of select="@table:number-columns-spanned"/>
   </xsl:attribute>
  </xsl:if>
  <xsl:value-of select="$line-break"/>
  <xsl:apply-templates />
 </xsl:element>
 <xsl:value-of select="$line-break"/>
</xsl:template>

<!-- Table Cell (Header Row) -->
<xsl:template match="table:table-cell" mode="header-row">
 <xsl:element name="th">
  <xsl:if test="@table:style-name">
   <xsl:attribute name="class">
    <xsl:value-of select="translate (@table:style-name, ' .', '__')"/>
   </xsl:attribute>
  </xsl:if>
  <xsl:if test="@table:number-columns-spanned">
   <xsl:attribute name="colspan">
    <xsl:value-of select="@table:number-columns-spanned"/>
   </xsl:attribute>
  </xsl:if>
  <xsl:value-of select="$line-break"/>
  <xsl:apply-templates />
 </xsl:element>
 <xsl:value-of select="$line-break"/>
</xsl:template>

<!-- Graphic boxes inside paragraphs should be ignored, since they always
     contain embedded pargarphs itself -->
<xsl:template match="draw:text-box"/>

<!-- Graphic boxes are processed specialy and converted to div elements -->
<xsl:template match="draw:text-box" mode="frame">
 <xsl:element name="div">
  <xsl:if test="@draw:style-name">
   <xsl:attribute name="class">
    <xsl:value-of select="translate (@draw:style-name, ' .', '__')"/>
   </xsl:attribute>
  </xsl:if>
  <xsl:attribute name="style">
    <xsl:apply-templates select="@*" mode="style"/>
  </xsl:attribute>
  <xsl:value-of select="$line-break"/>
  <xsl:apply-templates/>
 </xsl:element>
 <xsl:value-of select="$line-break"/>
</xsl:template>

<!-- Limited support for images -->
<xsl:template match="draw:image">
 <xsl:element name="a">
  <xsl:attribute name="name"><xsl:value-of select="@draw:name"/></xsl:attribute>
 </xsl:element>
 <xsl:element name="img">
  <xsl:attribute name="alt"><xsl:value-of select="@draw:name"/></xsl:attribute>
  <xsl:attribute name="src">
   <xsl:choose>
    <xsl:when test="@xlink:href">
     <xsl:value-of select="@xlink:href"/>
    </xsl:when>
    <xsl:when test="office:binary-data">
     <xsl:text>data:image/png;base64,</xsl:text>
     <xsl:value-of select="office:binary-data/text()[1]"/>
    </xsl:when>
   </xsl:choose>
  </xsl:attribute>
 </xsl:element>
</xsl:template>

<!-- Common behavior for some graphic object attributes: by default they are 
     just reproduced with their local name -->
<xsl:template match="@svg:width|@svg:height|@draw:z-index" mode="style" priority="0">
 <xsl:value-of select="local-name()"/><xsl:text>:</xsl:text>
 <xsl:call-template name="fix-inches">
  <xsl:with-param name="attrib-value" select="."/>
 </xsl:call-template>
 <xsl:text>; </xsl:text>
</xsl:template>

</xsl:stylesheet>
