<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:xalan="http://xml.apache.org/xalan"
  xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
  xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"
  xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"
  xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"
  xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
  xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
  xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:dc="http://purl.org/dc/elements/1.1/"
  xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0"
  xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0"
  xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"
  xmlns:chart="urn:oasis:names:tc:opendocument:xmlns:chart:1.0"
  xmlns:dr3d="urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0"
  xmlns:math="http://www.w3.org/1998/Math/MathML"
  xmlns:form="urn:oasis:names:tc:opendocument:xmlns:form:1.0"
  xmlns:script="urn:oasis:names:tc:opendocument:xmlns:script:1.0"
  xmlns:ooo="http://openoffice.org/2004/office" xmlns:ooow="http://openoffice.org/2004/writer"
  xmlns:oooc="http://openoffice.org/2004/calc" xmlns:dom="http://www.w3.org/2001/xml-events"
  xmlns:xforms="http://www.w3.org/2002/xforms" xmlns:xsd="http://www.w3.org/2001/XMLSchema"
  xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  exclude-result-prefixes="fo xlink office dc style text table draw svg xalan xhtml">
  <xsl:import href="office2html.xsl"/>
  <!--
       XML Style Sheet for OpenOffice.org Writer (.sxw) documents

       This file is part of the WPInterop project. See http://www.officecontent.net
       And the ICE (Integrated Content Environment) project
       
       This is designed to work with OfficeFMT

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

       Copyright University of Southern Queensland 2005



       -->
  <xsl:output encoding="UTF-8" method="xml" indent="yes" omit-xml-declaration="no"
    doctype-public="-//W3C//DTD XHTML 1.0 Transitional//EN"
    doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"/>
  <!-- Avoid endless repetition with paragraphs embedded in  "annotations" -->
  <xsl:template match="office:annotation"/>

  <xsl:template match="text:deletion">
    <xsl:element name="div">
      <xsl:attribute name="class">deletion</xsl:attribute>
      <xsl:attribute name="style">
        <xsl:text>color: red; text-decoration: line-through;</xsl:text>
      </xsl:attribute>
      <xsl:variable name="change-info">
        <xsl:text>Deletion: </xsl:text>
        <xsl:value-of select="office:change-info/dc:creator"/>
        <xsl:text> <!-- --></xsl:text> 
        <xsl:value-of select="substring-before(office:change-info/dc:date, 'T')"/>
        <xsl:text> <!-- --></xsl:text> 
        <xsl:value-of select="substring-after(office:change-info/dc:date, 'T')"/>
      </xsl:variable>
      <xsl:attribute name="title">
        <xsl:value-of select="$change-info"/>
      </xsl:attribute>
      <xsl:element name="div">
        <xsl:apply-templates select="*[name() != 'office:change-info']"></xsl:apply-templates>
      </xsl:element>
    </xsl:element>
  </xsl:template>

  <xsl:template match="office:annotation">
    <xsl:element name="div">
      <xsl:attribute name="class">annotation</xsl:attribute>
      <xsl:attribute name="style">
        <xsl:text>color: black; border: 1px solid #C0C0C0; padding: 1px; margin: 1px; background: #F1F1F1; font-size: .9em;</xsl:text>
      </xsl:attribute>
      <xsl:element name="div">
        <xsl:element name="span">
          <xsl:attribute name="class">annotation-heading</xsl:attribute>
          <xsl:attribute name="style">font-weight: bold;</xsl:attribute>
          <xsl:element name="span">
            <xsl:text>Annotation: </xsl:text>
            <xsl:value-of select="dc:creator"/>
            <xsl:text> <!-- --></xsl:text> 
            <xsl:value-of select="substring-before(dc:date, 'T')"/>
            <xsl:text> <!-- --></xsl:text> 
            <xsl:variable name="annotation-time" select="substring-after(dc:date, 'T')"></xsl:variable>
            <xsl:if test="$annotation-time != '00:00:00'">
              <xsl:value-of select="$annotation-time"/>
            </xsl:if>
          </xsl:element>
        </xsl:element>
        <xsl:apply-templates select="text:p" mode="annotation"></xsl:apply-templates>
      </xsl:element>
    </xsl:element>
  </xsl:template>
  
  <xsl:template match="text:p" mode="annotation">
    <xsl:element name="p">
      <xsl:apply-templates></xsl:apply-templates>
    </xsl:element>
  </xsl:template>

  <xsl:template name="get-heading-number">
    <xsl:param name="current-level"/>
   

    <!-- find previous sibling with style name starting with 'h' -->
    <!-- if sibling's level == current-level -->
    <!--   then the number for the current element will be sibling + 1 -->
    <!-- else if sibling's level > current-level -->
    <!--   then the number for the current element will be 1 -->
    <!--   and go through sub tree -->
    <!-- else if sibling's level < current-level -->
    <!--   keep looking backwards - find next previous sibling -->
    <xsl:variable name="start-value"
      select="//text:outline-style/text:outline-level-style[@style:num-format!=''][1]/@text:start-value"/>
    <!--
    <xsl:variable name="outline-level" select="//text:outline-style/text:outline-level-style[1][@style:num-format!=''][position()]"/>
   -->
    <xsl:variable name="outline-level">
      <xsl:value-of select="@text:outline-level"/>
    </xsl:variable>   
    <xsl:variable name="num-format-set">
      <xsl:apply-templates select="//text:outline-style" mode="outline-numbering"></xsl:apply-templates>
    </xsl:variable>
    
    <xsl:variable name="outline-depth" select="//text:outline-style/text:outline-level-style[position() = $outline-level]/@text:display-levels"></xsl:variable>
    <xsl:choose>
      <xsl:when test="$current-level = 0"/>
      <!-- If theres no start value do nothing -->
      <xsl:when test="$start-value = ''"/>
      <!-- Only set the numbering if the format is provided -->
      <xsl:when test="$num-format-set='false'"/>
      <xsl:otherwise>
        <xsl:variable name="startValue">
          <xsl:choose>
            <xsl:when test="$start-value &gt; 0"><xsl:value-of select="$start-value"/></xsl:when>
            <xsl:otherwise>
              <xsl:text>1</xsl:text>
            </xsl:otherwise>
          </xsl:choose>
        </xsl:variable>
        <xsl:choose>
          <xsl:when test="$current-level=1">
            <xsl:choose>
              <xsl:when test="(@text:outline-level and $startValue) and ($outline-level = $outline-depth) and (//text:outline-style/text:outline-level-style[1]/@style:num-prefix)">
                <xsl:value-of select="$startValue"/>
                  <xsl:text>.</xsl:text>
                  <xsl:apply-templates select="." mode="get-heading-number">
                    <xsl:with-param name="level" select="$current-level"/>
                  </xsl:apply-templates>
              </xsl:when>
              <xsl:otherwise>  
                <xsl:variable name="number">
                <xsl:apply-templates select="." mode="get-heading-number">
                  <xsl:with-param name="level" select="$current-level"/>
                </xsl:apply-templates>
                </xsl:variable>
                <xsl:choose>
                  <xsl:when test="$start-value &gt; 1">
                    <xsl:value-of select="$number + $start-value - 1"></xsl:value-of>
                  </xsl:when>
                  <xsl:otherwise><xsl:value-of select="$number"/></xsl:otherwise>
                </xsl:choose>
              </xsl:otherwise>
            </xsl:choose>             
          </xsl:when>
          <xsl:otherwise>
            <xsl:call-template name="get-heading-number">
              <xsl:with-param name="current-level" select="$current-level - 1"/>
            </xsl:call-template>
            <xsl:text>.</xsl:text>
              <xsl:apply-templates select="." mode="get-heading-number">
                <xsl:with-param name="level" select="$current-level"/>
              </xsl:apply-templates>
          </xsl:otherwise>
        </xsl:choose>    
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  
  <xsl:template match="text:outline-style" mode="outline-numbering">
    <xsl:value-of select="//text:outline-level-style/@style:num-format !=''"/>
  </xsl:template>

  <!-- Handle CSS -->
  <xsl:template name="get-styles">
    <xsl:element name="style">
      <xsl:attribute name="type">text/css</xsl:attribute>
      <xsl:text>table {border-spacing: 0;empty-cells: show;} </xsl:text>
      <xsl:variable name="styles">
        <xsl:apply-templates select="//office:styles"/>
        <xsl:apply-templates select="//office:automatic-styles" mode="css-styles"/>
      </xsl:variable>
      <xsl:value-of select="normalize-space($styles)"/>
    </xsl:element>
    <xsl:value-of select="$line-break"/>
  </xsl:template>
  <xsl:template match="office:styles|office:automatic-styles"/>
  <xsl:template match="office:styles|office:automatic-styles" mode="css-styles">
    <xsl:apply-templates select="style:style|style:default-style|text:list-style"/>
  </xsl:template>
  <xsl:template match="text:list-style"/>
  <xsl:template
    match="style:style[not(starts-with(@style:family, 'table')) and     not(starts-with(@style:family, 'graphic')) and not(starts-with(@style:family, 'text')) and     not(starts-with(@style:family, 'paragraph'))]"/>
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
              <xsl:text>h</xsl:text>
              <xsl:value-of select="$level"/>
              <xsl:text>.</xsl:text>
              <xsl:value-of select="$style-name"/>
            </xsl:when>
            <xsl:when test="contains ($parent-style, 'Heading_')">
              <xsl:variable name="level" select="substring-after($parent-style,'Heading_')"/>
              <xsl:text>h</xsl:text>
              <xsl:value-of select="$level"/>
              <xsl:text>.</xsl:text>
              <xsl:value-of select="$style-name"/>
            </xsl:when>
            <xsl:otherwise>
              <xsl:text>p.</xsl:text>
              <xsl:value-of select="$style-name"/>
            </xsl:otherwise>
          </xsl:choose>
        </xsl:when>
        <xsl:when test="$style-family = 'text'">
          <xsl:text>span.</xsl:text>
          <xsl:value-of select="$style-name"/>
        </xsl:when>
        <xsl:when test="$style-family = 'section' or $style-family = 'graphics'">
          <xsl:text>div.</xsl:text>
          <xsl:value-of select="$style-name"/>
        </xsl:when>
        <xsl:when test="$style-family = 'table'">
          <xsl:text>table.</xsl:text>
          <xsl:value-of select="$style-name"/>
        </xsl:when>
        <!--
        <xsl:when test="$style-family = 'table-column'">
          <xsl:text>col.</xsl:text><xsl:value-of select="$style-name"/>
        </xsl:when>
        -->
        <xsl:when test="$style-family = 'table-cell'">
          <xsl:text>th.</xsl:text>
          <xsl:value-of select="$style-name"/>
          <xsl:text>, td.</xsl:text>
          <xsl:value-of select="$style-name"/>
        </xsl:when>
        <xsl:when test="$style-family = 'table-row'">
          <xsl:text>tr.</xsl:text>
          <xsl:value-of select="$style-name"/>
        </xsl:when>
        <xsl:when test="$style-family = 'graphic'">
          <xsl:text>img.</xsl:text>
          <xsl:value-of select="$style-name"/>
        </xsl:when>
      </xsl:choose>
    </xsl:variable>
    <xsl:variable name="styles">
      <xsl:apply-templates select="." mode="css-style"/>
    </xsl:variable>
    <xsl:if test="string($style-group) != '' and $styles!=''">
      <xsl:value-of select="$style-group"/>
      <xsl:text> {</xsl:text>
      <xsl:copy-of select="$styles"/>
      <xsl:text>}</xsl:text>
      <xsl:value-of select="$line-break"/>
    </xsl:if>
    <xsl:if test="$style-family = 'table'">
      <xsl:text>div.</xsl:text>
      <xsl:value-of select="$style-name"/>
      <xsl:text> {</xsl:text>
      <xsl:text>width: 100%; margin: 0px; padding: 0px;</xsl:text>
      <xsl:text> } </xsl:text>
    </xsl:if>
  </xsl:template>
  <!-- special match for table cell properites vertical align. -->
  <xsl:template match="style:table-cell-properties" mode="style">
    <xsl:text>vertical-align: </xsl:text>
    <xsl:choose>
      <xsl:when test="not(@style:vertical-align)">
        <xsl:text>top;</xsl:text>
      </xsl:when>
      <xsl:when test="@style:vertical-align = ''">
        <xsl:text>top;</xsl:text>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="@style:vertical-align"/>;</xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  <xsl:template match="@style:width" mode="style">
    <xsl:choose>
      <!-- use relative width if @style:rel-width exists instead of @style:width -->
      <xsl:when test="../@style:rel-width">
        <xsl:text>width:</xsl:text>
        <xsl:value-of select="../@style:rel-width"/>
        <xsl:text>; </xsl:text>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="local-name(.)"/>
        <xsl:text>:</xsl:text>
        <xsl:call-template name="fix-inches">
          <xsl:with-param name="attrib-value" select="."/>
        </xsl:call-template>
        <xsl:text>; </xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  <!-- special match for images, only allows left and right float -->
  <xsl:template match="style:graphic-properties" mode="style">
    <xsl:variable name="float-pos">
      <xsl:if test="@style:wrap='parallel' or @style:wrap='dynamic'">
        <xsl:choose>
          <xsl:when test="contains(@style:horizontal-pos, 'left')">float: left; </xsl:when>
          <xsl:when test="contains(@style:horizontal-pos,'right')">float: right; </xsl:when>
        </xsl:choose>
      </xsl:if>
    </xsl:variable>
    <xsl:value-of select="$float-pos"/>
  </xsl:template>
  <!-- The following formatting properties are not supported in CSS -->
  <xsl:template match="@fo:clip" mode="style" priority="2"/>
  <!-- Styles not required from paragraph-properties -->
  <xsl:template match="@fo:break-before" mode="style"/>
  <xsl:template match="@fo:font-size" mode="style"/>
  <xsl:template match="@fo:text-align" mode="style"/>
  <!-- Standard procedure for processing a single style with its parent-->
  <xsl:template match="style:style" mode="css-style">
    <xsl:param name="context"/>
    <xsl:if test="@style:parent-style-name">
      <xsl:variable name="parent-name" select="@style:parent-style-name"/>
      <xsl:apply-templates select="//style:style[@style:name=$parent-name]" mode="css-style">
        <xsl:with-param name="context" select="."/>
      </xsl:apply-templates>
    </xsl:if>
    <xsl:apply-templates select="./style:table-cell-properties" mode="style"/>
    <xsl:apply-templates select="./style:graphic-properties" mode="style"/>
    <xsl:for-each
      select="style:*[substring(local-name(), string-length(local-name()) -       string-length('properties') + 1, 10)]/@*">
      <xsl:variable name="prop-name" select="name()"/>
      <xsl:if
        test="($context = '') or (not ($context/style:table-properties/@*[name() =         $prop-name])) or (not ($context/style:paragraph-properties))">
        <xsl:apply-templates select="." mode="style"/>
      </xsl:if>
    </xsl:for-each>
  </xsl:template>
  <!-- match linked objects -->
  <xsl:template match="draw:a">
    <xsl:element name="a">
      <xsl:attribute name="href">
        <xsl:value-of select="@xlink:href"/>
      </xsl:attribute>
      <xsl:if test="@office:target-frame-name">
        <xsl:attribute name="target">
          <xsl:value-of select="@office:target-frame-name"/>
        </xsl:attribute>
      </xsl:if>
      <xsl:apply-templates/>
    </xsl:element>
  </xsl:template>
  <xsl:template match="table:table[1] | text:p[1] | text:list[1] | text:h[1]">
    <xsl:if
      test="not(preceding-sibling::text:p | preceding-sibling::text:list |       preceding-sibling::table:table | preceding-sibling::text:h)">
      <xsl:apply-templates select="." mode="nesting">
        <xsl:with-param name="nesting" select="'nest'"/>
        <xsl:with-param name="container-style-name" select="''"/>
      </xsl:apply-templates>
    </xsl:if>
    <xsl:if
      test="not(preceding-sibling::text:p | preceding-sibling::text:list |       preceding-sibling::text:h | preceding-sibling::table:table)">
      <xsl:apply-templates select="." mode="nesting">
        <xsl:with-param name="nesting" select="'peer'"/>
        <xsl:with-param name="container-style-name" select="''"/>
      </xsl:apply-templates>
    </xsl:if>
  </xsl:template>
  <xsl:template match="* |table:table | text:list" mode="get-heading-number" priority="2">
    <xsl:param name="level"/>
    <!-- since parent is not included in preceding axis, choose between siblings and parent -->
    <xsl:choose>
      <!-- if there are preceding siblings that have headings, go there -->
      <xsl:when test="preceding-sibling::text:h | preceding-sibling::text:p">
        <xsl:apply-templates select="preceding-sibling::*[1]" mode="get-heading-number">
          <xsl:with-param name="level" select="$level"/>
        </xsl:apply-templates>
      </xsl:when>
      <xsl:otherwise>
        <!-- otherwise do the parent -->
        <xsl:apply-templates select="ancestor::*[1]" mode="get-heading-number">
          <xsl:with-param name="level" select="$level"/>
        </xsl:apply-templates>
      </xsl:otherwise>
    </xsl:choose>
    <!--    <xsl:apply-templates select="preceding::*[1]" mode="get-heading-number">
       <xsl:with-param name="level" select="$level"/>
    </xsl:apply-templates>
-->
  </xsl:template>
  <xsl:template match="text:p | text:h" mode="get-heading-number" priority="3">
    <xsl:param name="level"/>
    <xsl:variable name="style-name">
      <xsl:call-template name="get-style-name"/>
    </xsl:variable>
    <xsl:variable name="family">
      <xsl:call-template name="get-family">
        <xsl:with-param name="style-name" select="$style-name"/>
      </xsl:call-template>
    </xsl:variable>
    <xsl:variable name="type">
      <xsl:call-template name="get-type">
        <xsl:with-param name="style-name" select="$style-name"/>
      </xsl:call-template>
    </xsl:variable>
    <xsl:variable name="this-level">
      <xsl:call-template name="get-heading-level">
        <xsl:with-param name="style-name" select="$style-name"/>
      </xsl:call-template>
    </xsl:variable>
    <xsl:variable name="result">
      <xsl:apply-templates select="preceding-sibling::*[1]" mode="get-heading-number">
        <xsl:with-param name="level" select="$level"/>
      </xsl:apply-templates>
    </xsl:variable>
    <xsl:variable name="result-number">
      <xsl:choose>
        <xsl:when test="$result &gt; 0">
          <xsl:value-of select="$result"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:copy-of select="'0'"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:choose>
      <xsl:when test="$family = 'h' and $type = 'number'">
        <xsl:choose>
          <xsl:when test="$level = $this-level">
            <xsl:value-of select="$result-number + 1"/>
          </xsl:when>
          <xsl:when test="$level &gt; $this-level">
            <xsl:value-of select="'0'"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="$result-number"/>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$result-number"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  <xsl:template match="text()">
    <xsl:copy-of select="."/>
  </xsl:template>
  <!-- override imported matching templates here -->
  <xsl:template match="text:table-of-content"/>
  <xsl:template match="text:table-of-content" mode="nesting">
    <xsl:param name="container-style-name"/>
    <xsl:param name="nesting"/>
    <xsl:call-template name="next">
      <xsl:with-param name="container-style-name" select="$container-style-name"/>
      <xsl:with-param name="nesting" select="$nesting"/>
    </xsl:call-template>
  </xsl:template>
  <xsl:template match="text:list"/>
  <xsl:template match="text:p | text:h"/>
  <xsl:template match="table:table"/>
  <xsl:template match="table:table-column"/>
  <xsl:template match="table:table-header-rows">
    <xsl:apply-templates mode="table-header-row"/>
  </xsl:template>
  <xsl:template match="table:table-row" mode="table-header-row">
    <xsl:element name="tr">
      <xsl:apply-templates mode="header-row"/>
    </xsl:element>
  </xsl:template>
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
      <xsl:apply-templates/>
    </xsl:element>
    <xsl:value-of select="$line-break"/>
  </xsl:template>
  <!-- only match if table contains cells -->
  <xsl:template match="table:table[.//table:table-cell]" mode="nesting">
    <xsl:param name="nesting"/>
    <xsl:param name="container-style-name"/>
    <xsl:if test="$nesting='peer' and not(starts-with($container-style-name, 'li'))">
      <xsl:variable name="cells" select="number(count(.//table:table-cell))"/>
      <!-- <xsl:call-template name="get-styles"/> -->
      <xsl:call-template name="make-table"/>
      <xsl:call-template name="next">
        <xsl:with-param name="nesting" select="'peer'"/>
        <xsl:with-param name="container-style-name" select="''"/>
      </xsl:call-template>
    </xsl:if>
  </xsl:template>
  <!-- don't output text or anything else in this mode (handled elsewhere) -->
  <xsl:template match="* | text()" mode="nesting"/>
  <!-- don't output text or anything else in this mode (handled elsewhere) -->
  <xsl:template match="* | text()" mode="get-heading-number"/>
  <xsl:template match="msg">
    <xsl:message>
      <xsl:value-of select="."/>
    </xsl:message>
  </xsl:template>
  <xsl:template match="text:list-item | text:list" mode="nesting">
    <xsl:param name="container-style-name"/>
    <xsl:param name="nesting"/>
    <xsl:apply-templates select="*[1]" mode="nesting">
      <xsl:with-param name="nesting" select="$nesting"/>
      <xsl:with-param name="container-style-name" select="$container-style-name"/>
    </xsl:apply-templates>
  </xsl:template>
  <xsl:template name="get-style-name">
    <xsl:param name="local-style-name" select="@text:style-name"/>
    <xsl:choose>
      <!-- We have some indirection to deal with -->
      <xsl:when test="starts-with($local-style-name,'P')">
        <xsl:value-of select="//style:style[@style:name=$local-style-name]/@style:parent-style-name"
        />
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$local-style-name"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  <xsl:template name="get-default-style-name">
    <xsl:param name="local-style-name" select="@text:style-name"/>
    <xsl:value-of select="$local-style-name"/>
  </xsl:template>
  <xsl:template match="draw:text-box">
    <!-- contains an image/object and a caption, in that order -->
    <xsl:apply-templates/>
  </xsl:template>
  <xsl:template match="text:sequence" mode="caption">
    <xsl:value-of select="."/>
    <xsl:text> </xsl:text>
  </xsl:template>
  <xsl:template match="draw:text-box" mode="breakout">
    <xsl:element name="style">
      <xsl:attribute name="style">background-color:yellow</xsl:attribute>
      <xsl:apply-templates/>
    </xsl:element>
  </xsl:template>
  <xsl:template match="text:p | text:h" mode="nesting">
    <xsl:param name="container-style-name" select="''"/>
    <xsl:param name="nesting"/>
    <xsl:variable name="style-name">
      <xsl:call-template name="get-style-name"/>
    </xsl:variable>
    <xsl:variable name="level">
      <xsl:call-template name="get-level">
        <xsl:with-param name="style-name" select="$style-name"/>
      </xsl:call-template>
    </xsl:variable>
    <xsl:variable name="container-level">
      <xsl:call-template name="get-level">
        <xsl:with-param name="style-name" select="$container-style-name"/>
      </xsl:call-template>
    </xsl:variable>
    <xsl:variable name="type">
      <xsl:call-template name="get-type">
        <xsl:with-param name="style-name" select="$style-name"/>
      </xsl:call-template>
    </xsl:variable>
    <xsl:variable name="container-type">
      <xsl:call-template name="get-type">
        <xsl:with-param name="style-name" select="$container-style-name"/>
      </xsl:call-template>
    </xsl:variable>
    <xsl:choose>
      <xsl:when test="$nesting = 'nest'">
        <!-- Greater level: that's nesting -->
        <xsl:if test="$level &gt; $container-level">
          <xsl:call-template name="make-container">
            <xsl:with-param name="container-style-name" select="$container-style-name"/>
          </xsl:call-template>
        </xsl:if>
        <xsl:if test="$level = $container-level and $type = 'p'">
          <xsl:call-template name="make-paragraph"/>
        </xsl:if>
      </xsl:when>
      <xsl:when test="$nesting = 'continue'">
        <xsl:choose>
          <!-- Nest will have caught this-->
          <xsl:when test="$level &gt; $container-level">
            <xsl:call-template name="next">
              <xsl:with-param name="container-style-name" select="$container-style-name"/>
              <xsl:with-param name="nesting" select="'continue'"/>
            </xsl:call-template>
          </xsl:when>
          <!-- Nest will have caught this -->
          <xsl:when test="$level = $container-level and $type = 'p'">
            <xsl:call-template name="next">
              <xsl:with-param name="container-style-name" select="$container-style-name"/>
              <xsl:with-param name="nesting" select="'continue'"/>
            </xsl:call-template>
          </xsl:when>
          <!-- Nest won't catch this -->
          <xsl:when
            test="$style-name = $container-style-name or ($level=$container-level and             starts-with($style-name,'d') and starts-with($container-style-name,'d'))">
            <xsl:call-template name="make-paragraph"/>
          </xsl:when>
        </xsl:choose>
      </xsl:when>
      <xsl:when test="$nesting = 'breakout'">
        <xsl:if
          test="$container-style-name = $style-name or $level &gt; $container-level or           ($level=$container-level and starts-with($style-name,'d') and           starts-with($container-style-name,'d')) or ($level = $container-level and $type = 'p')">
          <xsl:apply-templates select="draw:text-box" mode="breakout"/>
          <xsl:call-template name="next">
            <xsl:with-param name="container-style-name" select="$container-style-name"/>
            <xsl:with-param name="nesting" select="'breakout'"/>
          </xsl:call-template>
        </xsl:if>
      </xsl:when>
      <xsl:when test="$nesting = 'peer'">
        <xsl:choose>
          <xsl:when test="$level &gt; $container-level">
            <xsl:call-template name="next">
              <xsl:with-param name="container-style-name" select="$container-style-name"/>
              <xsl:with-param name="nesting" select="'peer'"/>
            </xsl:call-template>
          </xsl:when>
          <xsl:when
            test="($style-name = $container-style-name) or ($level=$container-level and             starts-with($style-name,'d') and starts-with($container-style-name,'d'))">
            <xsl:call-template name="next">
              <xsl:with-param name="container-style-name" select="$container-style-name"/>
              <xsl:with-param name="nesting" select="'peer'"/>
            </xsl:call-template>
          </xsl:when>
          <xsl:when test="$level = $container-level and $type = 'p'">
            <xsl:call-template name="next">
              <xsl:with-param name="container-style-name" select="$container-style-name"/>
              <xsl:with-param name="nesting" select="'peer'"/>
            </xsl:call-template>
          </xsl:when>
          <xsl:when test="($container-style-name = '') or ($level = $container-level)">
            <xsl:call-template name="make-container"/>
          </xsl:when>
        </xsl:choose>
      </xsl:when>
      <xsl:otherwise> WARNING! - strange condition <xsl:value-of select="$nesting"/> Style:
          <xsl:value-of select="$style-name"/> in: <xsl:value-of select="$container-style-name"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  <!-- Test harness -->
  <xsl:template match="test-preceding">
    <preceding.elements>
      <xsl:apply-templates select="test.me" mode="preceding"/>
    </preceding.elements>
  </xsl:template>
  <!-- template which should recursively list select preceding siblings/ancestors, in reverse document order -->
  <xsl:template match="*" mode="preceding">
    <xsl:choose>
      <xsl:when test="preceding-sibling::text:h| preceding-sibling::text:p">
        <xsl:apply-templates select="preceding-sibling::*[1]" mode="preceding"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:apply-templates select="ancestor::*[1]" mode="preceding"/>
      </xsl:otherwise>
    </xsl:choose>
    <el>
      <xsl:value-of select="name()"/>
    </el>
  </xsl:template>
  <xsl:template match="text()" mode="preceding"/>
  <xsl:template match="test-get-heading-number-mode">
    <get-heading-number-mode>
      <xsl:apply-templates mode="get-heading-number"/>
    </get-heading-number-mode>
  </xsl:template>
  <xsl:template match="get-family">
    <f>
      <xsl:call-template name="get-family">
        <xsl:with-param name="style-name" select="."/>
      </xsl:call-template>
    </f>
  </xsl:template>
  <xsl:template match="get-level">
    <l>
      <xsl:call-template name="get-level">
        <xsl:with-param name="style-name" select="."/>
      </xsl:call-template>
    </l>
  </xsl:template>
  <xsl:template match="get-heading-level">
    <l>
      <xsl:call-template name="get-heading-level">
        <xsl:with-param name="style-name" select="."/>
      </xsl:call-template>
    </l>
  </xsl:template>
  <xsl:template match="get-type">
    <t>
      <xsl:call-template name="get-type">
        <xsl:with-param name="style-name" select="."/>
      </xsl:call-template>
    </t>
  </xsl:template>
  <!--Actual code-->
  <xsl:template name="generate-id">
    <xsl:choose>
      <!-- HACK: to work when running under testing
        NOTE: There must be a better way to do this!
        This needs to be refactored.
      -->
      <xsl:when test="/*[1][name()!='office:document-content']">
        <xsl:text>test</xsl:text>
      </xsl:when>
      <!-- Note: This no longer works under the newer version of UTFX -->
      <xsl:when test="ancestor::*[local-name()='utfx-wrapper']">
        <xsl:text>test</xsl:text>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="generate-id()"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  <xsl:template name="next">
    <xsl:param name="container-style-name"/>
    <xsl:param name="nesting"/>
    <xsl:apply-templates
      select="(following-sibling::* |       ancestor::text:list-item/following-sibling::* |       ancestor::text:list/following-sibling::*)[1]"
      mode="nesting">
      <xsl:with-param name="container-style-name" select="$container-style-name"/>
      <xsl:with-param name="nesting" select="$nesting"/>
    </xsl:apply-templates>
  </xsl:template>
  <xsl:template name="make-paragraph">
    <xsl:param name="level">
      <xsl:call-template name="get-level"/>
    </xsl:param>
    <xsl:variable name="style-name">
      <xsl:call-template name="get-style-name"/>
    </xsl:variable>
    <xsl:variable name="default-style-name">
      <xsl:call-template name="get-default-style-name"/>
    </xsl:variable>
    <xsl:variable name="family">
      <xsl:call-template name="get-family">
        <xsl:with-param name="style-name" select="$style-name"/>
      </xsl:call-template>
    </xsl:variable>
    <xsl:variable name="type">
      <xsl:call-template name="get-type">
        <xsl:with-param name="style-name" select="$style-name"/>
      </xsl:call-template>
    </xsl:variable>
    <xsl:choose>
      <!-- This allows new p styles to be added to the template without having to add them to the xsl -->
      <!-- Needs refactoring DdB -->
      <xsl:when test="$type!='' and $family = 'p'">
        <xsl:element name="p">
          <xsl:if test="$type!='' and $type!='bullet' and $type!='number' and $type!='a'">
            <xsl:attribute name="class">
              <xsl:value-of select="$type"/>
            </xsl:attribute>
            <xsl:choose>
              <xsl:when test="$type = 'nowrap'">
                <xsl:attribute name="style">
                  <xsl:text>white-space: nowrap;</xsl:text>
                </xsl:attribute>
              </xsl:when>
            </xsl:choose>
          </xsl:if>
          <xsl:call-template name="make-paragraph-contents"/>
        </xsl:element>
        <xsl:call-template name="next">
          <xsl:with-param name="container-style-name" select="$style-name"/>
          <xsl:with-param name="nesting" select="'nest'"/>
        </xsl:call-template>
      </xsl:when>
      <xsl:when test="$family='bq' or ($family = 'li' and $type='p')">
        <xsl:element name="p">
          <xsl:call-template name="make-paragraph-contents"/>
        </xsl:element>
        <xsl:call-template name="next">
          <xsl:with-param name="container-style-name" select="$style-name"/>
          <xsl:with-param name="nesting" select="'nest'"/>
        </xsl:call-template>
      </xsl:when>
      <xsl:when test="$family='h'">
        <xsl:variable name="heading-level">
          <xsl:call-template name="get-heading-level">
            <xsl:with-param name="style-name" select="$style-name"/>
          </xsl:call-template>
        </xsl:variable>
        <xsl:variable name="h-level">
          <xsl:choose>
            <xsl:when test="$heading-level &gt; 0">
              <xsl:value-of select="$heading-level"/>
            </xsl:when>
            <xsl:otherwise>
              <!-- if it wasn't non-zero, use h6 -->
              <xsl:text>6</xsl:text>
            </xsl:otherwise>
          </xsl:choose>
        </xsl:variable>
        <xsl:element name="h{$h-level}">
          <xsl:value-of select="$line-break"/>
          <xsl:variable name="id">
            <xsl:call-template name="generate-id"/>
          </xsl:variable>
          <xsl:element name="a">
            <xsl:attribute name="name">
              <xsl:value-of select="$id"/>
            </xsl:attribute>
            <xsl:comment>
              <xsl:value-of select="$id"/>
            </xsl:comment>
          </xsl:element>
          <xsl:if test="$type = 'number'">
            <xsl:call-template name="get-heading-number">
              <xsl:with-param name="current-level">
                <xsl:call-template name="get-heading-level">
                  <xsl:with-param name="style-name" select="$style-name"/>
                </xsl:call-template>
              </xsl:with-param>
            </xsl:call-template>
            <xsl:text> </xsl:text>
          </xsl:if>
          <xsl:call-template name="make-paragraph-contents"/>
        </xsl:element>
        <xsl:call-template name="next">
          <xsl:with-param name="container-style-name" select="$style-name"/>
          <xsl:with-param name="nesting" select="'nest'"/>
        </xsl:call-template>
      </xsl:when>
      <xsl:when test="$family='pre'">
        <xsl:call-template name="make-paragraph-contents"/>
        <xsl:text>&#xa;</xsl:text>
      </xsl:when>
      <xsl:when test="$family='dt'">
        <xsl:element name="dt">
          <xsl:call-template name="make-paragraph-contents"/>
        </xsl:element>
        <xsl:call-template name="next">
          <xsl:with-param name="container-style-name" select="$style-name"/>
          <xsl:with-param name="nesting" select="'nest'"/>
        </xsl:call-template>
      </xsl:when>
      <xsl:when test="$family='dd'">
        <xsl:element name="dd">
          <xsl:call-template name="make-paragraph-contents"/>
        </xsl:element>
        <xsl:call-template name="next">
          <xsl:with-param name="container-style-name" select="$style-name"/>
          <xsl:with-param name="nesting" select="'nest'"/>
        </xsl:call-template>
      </xsl:when>
      <xsl:when test="$family='title'">
        <!--  <h1>
          <xsl:call-template name="make-paragraph-contents"/>
        </h1>
        -->
        <xsl:call-template name="next">
          <xsl:with-param name="container-style-name" select="$style-name"/>
          <xsl:with-param name="nesting" select="'nest'"/>
        </xsl:call-template>
      </xsl:when>
      <xsl:when test="$family = 'p' and $default-style-name !='p' and $style-name='p'">
        <xsl:element name="p">
          <xsl:attribute name="class">
            <xsl:value-of select="$default-style-name"/>
          </xsl:attribute>
          <xsl:call-template name="make-paragraph-contents"/>
        </xsl:element>
        <xsl:call-template name="next">
          <xsl:with-param name="container-style-name" select="$style-name"/>
          <xsl:with-param name="nesting" select="'nest'"/>
        </xsl:call-template>
      </xsl:when>
      <xsl:when test="$family = 'p'">
        <xsl:element name="p">
          <xsl:call-template name="make-paragraph-contents"/>
        </xsl:element>
        <xsl:call-template name="next">
          <xsl:with-param name="container-style-name" select="$style-name"/>
          <xsl:with-param name="nesting" select="'nest'"/>
        </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
        <xsl:element name="{$family}">
          <xsl:element name="p">
            <xsl:call-template name="make-paragraph-contents"/>
          </xsl:element>
          <xsl:call-template name="next">
            <xsl:with-param name="container-style-name" select="$style-name"/>
            <xsl:with-param name="nesting" select="'nest'"/>
          </xsl:call-template>
        </xsl:element>
      </xsl:otherwise>
    </xsl:choose>
    <xsl:call-template name="next">
      <xsl:with-param name="container-style-name" select="$style-name"/>
      <xsl:with-param name="nesting" select="'continue'"/>
    </xsl:call-template>
  </xsl:template>
  <xsl:template name="make-paragraph-contents">
    <xsl:choose>
      <xsl:when test="child::* or child::text()">
        <xsl:apply-templates/>
      </xsl:when>
      <!-- If this paragraph is empty, the css is set to use empty-cells=show rather then using a non-breaking space later -->
      <!-- commented out for accessibility reasons -->
      <!--
      <xsl:otherwise>
        <xsl:if test="name(..)='table:table-cell'">
          <xsl:text>&#160;</xsl:text>
        </xsl:if>
      </xsl:otherwise>
      -->
    </xsl:choose>
  </xsl:template>
  <xsl:template match="text:span[starts-with(@text:style-name,'i-')]">
    <xsl:variable name="style-name">
      <xsl:value-of select="substring-after(@text:style-name,'i-')"/>
    </xsl:variable>
    <xsl:choose>
      <xsl:when test="$style-name = 'bi'">
        <xsl:element name="b">
          <xsl:element name="i">
            <xsl:apply-templates/>
          </xsl:element>
        </xsl:element>
      </xsl:when>
      <xsl:when test="$style-name = 'underline'">
        <xsl:element name="span">
          <xsl:attribute name="class">
            <xsl:value-of select="$style-name"/>
          </xsl:attribute>
          <xsl:attribute name="style">
            <xsl:text>text-decoration: underline;</xsl:text>
          </xsl:attribute>
          <xsl:element name="span">
            <xsl:apply-templates/>
          </xsl:element>
        </xsl:element>
      </xsl:when>
      <xsl:when test="$style-name = 'double-underline'">
        <xsl:element name="span">
          <xsl:attribute name="class">
            <xsl:value-of select="$style-name"/>
          </xsl:attribute>
          <xsl:attribute name="style">
            <xsl:text>border-bottom: 1px solid; text-decoration: underline; padding-bottom: .2em;</xsl:text>
          </xsl:attribute>
          <xsl:element name="span">
            <xsl:apply-templates/>
          </xsl:element>
        </xsl:element>
      </xsl:when>
      <xsl:when
        test="$style-name = 'b' or $style-name = 'i' or $style-name = 'sub' or $style-name =  'sup' or $style-name = 'code'">
        <xsl:element name="{$style-name}">
          <xsl:apply-templates/>
        </xsl:element>
      </xsl:when>
      <xsl:otherwise>
        <xsl:element name="span">
          <xsl:attribute name="class">
            <xsl:value-of select="$style-name"/>
          </xsl:attribute>
          <xsl:apply-templates/>
        </xsl:element>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  <xsl:template name="get-family">
    <xsl:param name="style-name" select="@text:style-name"/>
    <xsl:choose>
      <xsl:when test="starts-with($style-name, 'li')">
        <xsl:text>li</xsl:text>
      </xsl:when>
      <xsl:when test="starts-with($style-name, 'bq')">
        <xsl:text>bq</xsl:text>
      </xsl:when>
      <xsl:when test="starts-with($style-name, 'pre')">
        <xsl:text>pre</xsl:text>
      </xsl:when>
      <xsl:when test="starts-with($style-name, 'dd')">
        <xsl:text>dd</xsl:text>
      </xsl:when>
      <xsl:when test="starts-with($style-name, 'dt')">
        <xsl:text>dt</xsl:text>
      </xsl:when>
      <xsl:when test="starts-with($style-name, 'p')">
        <xsl:text>p</xsl:text>
      </xsl:when>
      <xsl:when test="starts-with($style-name, 'h')">
        <xsl:text>h</xsl:text>
      </xsl:when>
      <xsl:when test="starts-with($style-name, 'Title')">
        <xsl:text>title</xsl:text>
      </xsl:when>
      <xsl:otherwise>
        <xsl:text>p</xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  <xsl:template name="get-level">
    <xsl:param name="style-name" select="@text:style-name"/>
    <xsl:variable name="family">
      <xsl:call-template name="get-family">
        <xsl:with-param name="style-name" select="$style-name"/>
      </xsl:call-template>
    </xsl:variable>
    <xsl:variable name="raw-level">
      <xsl:choose>
        <xsl:when test="string-length($family) = string-length($style-name)">
          <xsl:value-of select="'0'"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="number(substring($style-name,string-length($family) + 1,1))"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:choose>
      <xsl:when test="$family = 'h'">
        <xsl:copy-of select="'0'"/>
      </xsl:when>
      <xsl:when test="$raw-level &gt; 0">
        <xsl:copy-of select="$raw-level"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:copy-of select="'0'"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  <xsl:template name="get-heading-level">
    <xsl:param name="style-name" select="@text:style-name"/>
    <xsl:variable name="family">
      <xsl:call-template name="get-family">
        <xsl:with-param name="style-name" select="$style-name"/>
      </xsl:call-template>
    </xsl:variable>
    <xsl:variable name="type">
      <xsl:call-template name="get-type">
        <xsl:with-param name="style-name" select="$style-name"/>
      </xsl:call-template>
    </xsl:variable>
    <xsl:variable name="raw-level"
      select="number(substring($style-name,string-length($family) +       1,1))"/>
    <xsl:choose>
      <xsl:when test="$type = 'module'">
        <xsl:choose>
          <xsl:when test="$raw-level &gt; 0">
            <xsl:value-of select="$raw-level + 1"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="1"/>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>
      <xsl:when test="$family = 'h' and $raw-level &gt; 0">
        <xsl:value-of select="$raw-level"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:copy-of select="'0'"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  <xsl:template name="get-type">
    <xsl:param name="style-name" select="@text:style-name"/>
    <xsl:variable name="family">
      <xsl:call-template name="get-family">
        <xsl:with-param name="style-name" select="$style-name"/>
      </xsl:call-template>
    </xsl:variable>
    <xsl:variable name="level">
      <xsl:call-template name="get-level">
        <xsl:with-param name="style-name" select="$style-name"/>
      </xsl:call-template>
    </xsl:variable>
    <xsl:variable name="raw-type"
      select="substring($style-name,string-length($family) +       string-length($level) + 1,1)"/>
    <xsl:choose>
      <xsl:when test="contains($style-name, '-')">
        <xsl:value-of select="substring-after($style-name, '-')"/>
      </xsl:when>
      <xsl:when test="$raw-type = 'b'">
        <xsl:text>bullet</xsl:text>
      </xsl:when>
      <xsl:when test="$raw-type = 'n'">
        <xsl:text>number</xsl:text>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$raw-type"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  <!-- 
       ================================
       make-container
       encloses things in <ul>, <ol>, <dl> etc as appropriate
       ================================
  -->
  <xsl:template name="make-container">
    <xsl:param name="container-style-name"/>
    <xsl:param name="level">
      <xsl:call-template name="get-level"/>
    </xsl:param>
    <xsl:variable name="style-name">
      <xsl:call-template name="get-style-name"/>
    </xsl:variable>
    <xsl:variable name="family">
      <xsl:call-template name="get-family">
        <xsl:with-param name="style-name" select="$style-name"/>
      </xsl:call-template>
    </xsl:variable>
    <xsl:variable name="type">
      <xsl:call-template name="get-type">
        <xsl:with-param name="style-name" select="$style-name"/>
      </xsl:call-template>
    </xsl:variable>
    <xsl:variable name="container-family">
      <xsl:call-template name="get-family">
        <xsl:with-param name="style-name" select="$container-style-name"/>
      </xsl:call-template>
    </xsl:variable>
    <xsl:if test="$level &lt; 2">
      <xsl:apply-templates select="draw:text-box" mode="breakout"/>
      <xsl:if test="$level = 1">
        <xsl:call-template name="next">
          <xsl:with-param name="container-style-name" select="$style-name"/>
          <xsl:with-param name="nesting" select="'breakout'"/>
        </xsl:call-template>
      </xsl:if>
    </xsl:if>
    <xsl:variable name="container">
      <xsl:choose>
        <xsl:when test="$family='li' and $type='bullet'">
          <xsl:text>ul</xsl:text>
        </xsl:when>
        <xsl:when test="$family='li'">
          <xsl:text>ol</xsl:text>
        </xsl:when>
        <xsl:when test="$family='bq'">
          <xsl:text>blockquote</xsl:text>
        </xsl:when>
        <xsl:when test="$family='pre'">
          <xsl:text>pre</xsl:text>
        </xsl:when>
        <xsl:when test="$family='dd' or $family='dt'">
          <xsl:text>dl</xsl:text>
        </xsl:when>
        <xsl:otherwise>
          <xsl:text/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:choose>
      <!-- TODO REMOVE REPETITION -->
      <xsl:when test="$container-family = 'dt'">
        <xsl:element name="dd">
          <xsl:element name="{$container}">
            <xsl:if test="$container='ol' or $container='ul'">
              <xsl:attribute name="class">
                <xsl:value-of select="concat($family,substring($type, 1, 1))"/>
              </xsl:attribute>
            </xsl:if>
            <xsl:call-template name="make-paragraph"/>
          </xsl:element>
        </xsl:element>
      </xsl:when>
      <xsl:when test="$family = 'pre'">
        <xsl:element name="pre">
          <xsl:call-template name="make-paragraph"/>
        </xsl:element>
        <xsl:call-template name="next">
          <xsl:with-param name="container-style-name" select="$style-name"/>
          <xsl:with-param name="nesting" select="'nest'"/>
        </xsl:call-template>
      </xsl:when>
      <xsl:when test="$container = ''">
        <xsl:call-template name="make-paragraph"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:element name="{$container}">
          <xsl:variable name="short-type">
            <xsl:value-of select="concat($family,substring($type, 1, 1))"/>
          </xsl:variable>
          <xsl:choose>
            <xsl:when test="$container='ul' or $container='blockquote'">
              <xsl:attribute name="class">
                <xsl:value-of select="$short-type"/>
              </xsl:attribute>
            </xsl:when>
            <xsl:when test="$container='ol'">
              <xsl:attribute name="class">
                <xsl:choose>
                  <xsl:when test="$short-type = 'lii'">
                    <xsl:value-of select="$family"/>
                    <xsl:text>-lower-roman</xsl:text>
                  </xsl:when>
                  <xsl:when test="$short-type = 'liI'">
                    <xsl:value-of select="$family"/>
                    <xsl:text>-upper-roman</xsl:text>
                  </xsl:when>
                  <xsl:when test="$short-type = 'lia'">
                    <xsl:value-of select="$family"/>
                    <xsl:text>-lower-alpha</xsl:text>
                  </xsl:when>
                  <xsl:when test="$short-type = 'liA'">
                    <xsl:value-of select="$family"/>
                    <xsl:text>-upper-alpha</xsl:text>
                  </xsl:when>
                  <xsl:otherwise>
                    <xsl:value-of select="$short-type"/>
                  </xsl:otherwise>
                </xsl:choose>
              </xsl:attribute>
              <xsl:variable name="list-style-type">
                <xsl:choose>
                  <xsl:when test="$short-type = 'lii'">
                    <xsl:text>lower-roman</xsl:text>
                  </xsl:when>
                  <xsl:when test="$short-type = 'liI'">
                    <xsl:text>upper-roman</xsl:text>
                  </xsl:when>
                  <xsl:when test="$short-type = 'lia'">
                    <xsl:text>lower-alpha</xsl:text>
                  </xsl:when>
                  <xsl:when test="$short-type = 'liA'">
                    <xsl:text>upper-alpha</xsl:text>
                  </xsl:when>
                  <xsl:otherwise>
                    <xsl:text>decimal</xsl:text>
                  </xsl:otherwise>
                </xsl:choose>
              </xsl:variable>
              <xsl:attribute name="style">
                <xsl:text>list-style: </xsl:text>
                <xsl:value-of select="$list-style-type"/>
                <xsl:text>;</xsl:text>
              </xsl:attribute>
            </xsl:when>
          </xsl:choose>
          <xsl:call-template name="make-paragraph"/>
        </xsl:element>
      </xsl:otherwise>
    </xsl:choose>
    <xsl:call-template name="next">
      <xsl:with-param name="container-style-name" select="$style-name"/>
      <xsl:with-param name="nesting" select="'peer'"/>
    </xsl:call-template>
  </xsl:template>
  <!--Interface to office2html -->
  <!-- Seems to have been missed -->
  <xsl:template match="office:forms"/>

  <xsl:template name="show-document">
    <xsl:element name="body">
      <xsl:value-of select="$line-break"/>
      <xsl:apply-templates select="//office:body"/>
      <xsl:if test="//text:note[@text:note-class='footnote']">
        <xsl:element name="hr"/>
        <xsl:value-of select="$line-break"/>
        <xsl:apply-templates select="//text:note[@text:note-class='footnote']" mode="note-body"/>
      </xsl:if>
      <xsl:if test="//text:note[@text:note-class='endnote']">
        <xsl:element name="hr"/>
        <xsl:value-of select="$line-break"/>
        <xsl:apply-templates select="//text:note[@text:note-class='endnote']" mode="note-body"/>
      </xsl:if>
    </xsl:element>
    <xsl:value-of select="$line-break"/>
  </xsl:template>
  <xsl:template name="get-first-h-style">
    <xsl:variable name="style-name">
      <xsl:call-template name="get-style-name"/>
    </xsl:variable>
    <xsl:choose>
      <!-- if this has a h- style, return -->
      <xsl:when test="starts-with($style-name, 'h-')">
        <xsl:value-of select="$style-name"/>
      </xsl:when>
      <xsl:otherwise>
        <!-- otherwise find the children and call recursively -->
        <xsl:for-each select="child::*">
          <xsl:call-template name="get-first-h-style"/>
        </xsl:for-each>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  <xsl:template name="make-table">
    <!-- if a table contains a style that starts with h- then add it to the class -->
    <xsl:variable name="table-type">
      <xsl:call-template name="get-first-h-style"/>
    </xsl:variable>
    <xsl:variable name="table-type-value">
      <xsl:if test="$table-type !=''">
        <xsl:text> </xsl:text>
        <xsl:value-of select="substring-after($table-type, 'h-')"/>
      </xsl:if>
    </xsl:variable>
    <xsl:choose>
      <!--TODO get rid of the space at the front of this variable - not good-->
      <xsl:when test="$table-type-value=' slide'">
        <div class="slide">
          <h1>
            <xsl:apply-templates select=".//table:table-row[1]//text:p/text()"/>
          </h1>
          <xsl:apply-templates select=".//table:table-row[2]/table:table-cell/*"/>
        </div>
      </xsl:when>
      <xsl:otherwise>
        <xsl:variable name="style-name">
          <xsl:value-of select="@table:style-name"/>
        </xsl:variable>
        <xsl:variable name="align">
          <xsl:value-of
            select="//style:style[@style:name=$style-name]/style:table-properties/@table:align"/>
        </xsl:variable>
        <!-- Default alignment left -->
        <xsl:variable name="set-align">
          <xsl:choose>
            <xsl:when test="$align='center' or $align='right'">
              <xsl:value-of select="$align"/>
            </xsl:when>
            <xsl:otherwise>left</xsl:otherwise>
          </xsl:choose>
        </xsl:variable>
        <xsl:variable name="table">
          <xsl:element name="table">
            <xsl:if test="@table:style-name">
              <xsl:attribute name="class">
                <xsl:value-of select="translate (@table:style-name, ' .', '__')"/>
                <xsl:value-of select="$table-type-value"/>
              </xsl:attribute>
            </xsl:if>
            <!-- Added to fix the problem with spacing between the borders and instead of using the css element border-spacing -->
            <!-- Not valid xhtml -->
            <!-- <xsl:attribute name="cellspacing">0px</xsl:attribute> -->
            <xsl:element name="tbody">
              <xsl:value-of select="$line-break"/>
              <xsl:value-of select="$line-break"/>
              <xsl:apply-templates/>
            </xsl:element>
          </xsl:element>
        </xsl:variable>
        <xsl:choose>
          <xsl:when test="@table:is-sub-table='true'">
            <xsl:copy-of select="$table"/>
          </xsl:when>
          <xsl:otherwise>
            <!-- div added to control table alignment and rel-width -->
            <xsl:element name="div">
              <xsl:attribute name="align">
                <xsl:value-of select="$set-align"/>
              </xsl:attribute>
              <xsl:attribute name="class">
                <xsl:value-of select="$style-name"/>
              </xsl:attribute>
              <xsl:copy-of select="$table"/>
            </xsl:element>
          </xsl:otherwise>
        </xsl:choose>
        <xsl:copy-of select="$line-break"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  <xsl:template name="get-title">
    <xsl:variable name="indirect">
      <xsl:value-of
        select="//style:style[starts-with(@style:parent-style-name,         'Title')]/@style:name"/>
    </xsl:variable>
    <xsl:variable name="direct-title">
      <!--<xsl:value-of select="//*[@text:style-name = 'Title']"/>   -->
      <xsl:value-of select="//*[starts-with(@text:style-name, 'Title')]"/>
    </xsl:variable>
    <xsl:element name="title">
      <xsl:choose>
        <xsl:when test="$indirect != ''">
          <xsl:value-of select="//*[@text:style-name=$indirect]"/>
        </xsl:when>
        <xsl:when test="$direct-title != ''">
          <xsl:value-of select="$direct-title"/>
        </xsl:when>
        <xsl:otherwise> Untitled </xsl:otherwise>
      </xsl:choose>
    </xsl:element>
  </xsl:template>
  <!-- Limited support for images -->
  <xsl:template match="draw:image">
    <xsl:element name="img">
      <xsl:choose>
        <xsl:when test="starts-with(../@draw:name, 'HTTP:')">
          <xsl:attribute name="style">
            <xsl:text>border: 0px;</xsl:text>
          </xsl:attribute>          
        </xsl:when>
      </xsl:choose>
      <xsl:attribute name="alt">
        <xsl:value-of select="../@draw:name"/>
      </xsl:attribute>
      <!-- Add class to image -->
      <xsl:if test="../../draw:frame/@draw:style-name[1]">
        <xsl:attribute name="class">
          <xsl:value-of select="translate (../../draw:frame/@draw:style-name[1], ' .', '__')"/>
        </xsl:attribute>
      </xsl:if>
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
      <xsl:if test="../@svg:width">
        <xsl:attribute name="width">
          <xsl:call-template name="convert-units">
            <xsl:with-param name="value" select="../@svg:width"/>
          </xsl:call-template>
        </xsl:attribute>
      </xsl:if>
      <xsl:if test="../@svg:height">
        <xsl:attribute name="height">
          <xsl:call-template name="convert-units">
            <xsl:with-param name="value" select="../@svg:height"/>
          </xsl:call-template>
        </xsl:attribute>
      </xsl:if>
    </xsl:element>
  </xsl:template>
  <!-- Limited support embedded objects -->
  <xsl:template match="draw:plugin">
    <xsl:element name="a">
      <xsl:attribute name="name">
        <xsl:value-of select="../@draw:name"/>
      </xsl:attribute>
    </xsl:element>
    <xsl:element name="embed">
      <xsl:attribute name="name">
        <xsl:value-of select="../@draw:name"/>
      </xsl:attribute>
      <xsl:attribute name="alt">
        <xsl:value-of select="../@draw:name"/>
      </xsl:attribute>
      <xsl:attribute name="title">
        <xsl:value-of select="../@draw:name"/>
      </xsl:attribute>
      <xsl:attribute name="src">
        <xsl:choose>
          <xsl:when test="@xlink:href">
            <xsl:value-of select="@xlink:href"/>
          </xsl:when>
        </xsl:choose>
      </xsl:attribute>
      <xsl:attribute name="type">
        <xsl:choose>
          <xsl:when test="@draw:mime-type">
            <xsl:value-of select="@draw:mime-type"/>
          </xsl:when>
        </xsl:choose>
      </xsl:attribute>
      <xsl:if test="../@svg:width">
        <xsl:attribute name="width">
          <xsl:call-template name="convert-units">
            <xsl:with-param name="value" select="../@svg:width"/>
          </xsl:call-template>
        </xsl:attribute>
      </xsl:if>
      <xsl:if test="../@svg:height">
        <xsl:attribute name="height">
          <xsl:call-template name="convert-units">
            <xsl:with-param name="value" select="../@svg:height"/>
          </xsl:call-template>
        </xsl:attribute>
      </xsl:if>
    </xsl:element>
  </xsl:template>
  <xsl:template name="convert-units">
    <xsl:param name="value"/>
    <xsl:choose>
      <xsl:when test="contains($value, 'inch')">
        <xsl:value-of select="round(number(substring-before($value, 'inch'))*96)"/>
      </xsl:when>
      <xsl:when test="contains($value, 'cm')">
        <xsl:value-of select="round(number(substring-before($value, 'cm'))*37.8)"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$value"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  <!-- Bookmark -->
  <xsl:template match="text:bookmark-start">
    <xsl:element name="a">
      <xsl:attribute name="name">
        <xsl:value-of select="@text:name"/>
      </xsl:attribute>
      <!-- comment added to resolve issue with empty anchors in definition lists -->
      <xsl:comment>
        <xsl:value-of select="@text:name"/>
      </xsl:comment>
    </xsl:element>
  </xsl:template>
  <!-- Bookmark -->
  <xsl:template match="text:bookmark">
    <xsl:element name="a">
      <xsl:attribute name="name">
        <xsl:value-of select="@text:name"/>
      </xsl:attribute>
      <!-- comment added to resolve issue with empty anchors in definition lists -->
      <xsl:comment>
        <xsl:value-of select="@text:name"/>
      </xsl:comment>
    </xsl:element>
  </xsl:template>
  <!-- Added support for text:tab -->
  <xsl:template match="text:tab">&#160;&#160;&#160;&#160;</xsl:template>
  <!-- Link -->
  <xsl:template match="text:a">
    <xsl:variable name="href">
      <xsl:call-template name="replace">
        <xsl:with-param name="str" select="@xlink:href"/>
        <xsl:with-param name="find">%0B</xsl:with-param>
      </xsl:call-template>
    </xsl:variable>
    <xsl:choose>
      <xsl:when
        test="starts-with(following-sibling::*[1]/@xlink:href, @xlink:href) and string-length(normalize-space(following-sibling::text())) &lt; 2"> </xsl:when>
      <xsl:otherwise>
        <xsl:element name="a">
          <xsl:attribute name="href">
            <xsl:value-of select="$href"/>
          </xsl:attribute>
          <xsl:if test="@office:target-frame-name">
            <xsl:attribute name="target">
              <xsl:value-of select="@office:target-frame-name"/>
            </xsl:attribute>
          </xsl:if>
          <xsl:apply-templates select="preceding-sibling::*[1]" mode="match-preceding-links">
            <xsl:with-param name="href" select="$href"/>
          </xsl:apply-templates>
          <xsl:apply-templates/>
        </xsl:element>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  <xsl:template match="text:a" mode="match-preceding-links">
    <xsl:param name="href"/>
    <xsl:if test="starts-with($href, @xlink:href)">
      <xsl:apply-templates select="preceding-sibling::*[1]" mode="match-preceding-links">
        <xsl:with-param name="href" select="$href"/>
      </xsl:apply-templates>
      <xsl:apply-templates/>
    </xsl:if>
  </xsl:template>
  <xsl:template match="*" mode="match-preceding-links">
    <xsl:param name="href"/>
  </xsl:template>
  <xsl:template match="text:a" mode="link">
    <xsl:apply-templates/>
  </xsl:template>

  <!-- A string replace function  -->
  <xsl:template name="replace">
    <xsl:param name="str"/>
    <xsl:param name="find"/>
    <xsl:param name="replace"/>
    <xsl:choose>
      <xsl:when test="contains($str, $find)">
        <xsl:variable name="href-before" select="substring-before($str, $find)"/>
        <xsl:variable name="href-after" select="substring-after($str, $find)"/>
        <xsl:call-template name="replace">
          <xsl:with-param name="str" select="concat($href-before, $href-after)"/>
          <xsl:with-param name="find" select="$find"/>
        </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$str"/>
      </xsl:otherwise>
    </xsl:choose>
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

  <!-- Footnote/endnote processing in body text 
    (only note reference should appear) -->
  <xsl:template match="text:note">
    <xsl:variable name="note-id" select="@text:id"/>
    <xsl:variable name="note-type" select="@text:note-class"/>
    <xsl:variable name="citation-name" select="concat('text:', local-name(.), '-citation')"/>
    <xsl:apply-templates select="*[name()=$citation-name]" mode="notes">
      <xsl:with-param name="note-type" select="$note-type"/>
      <xsl:with-param name="anchor-name" select="concat($note-id, '-text')"/>
      <xsl:with-param name="anchor-ref" select="concat ('#', $note-id)"/>
    </xsl:apply-templates>
  </xsl:template>

  <!-- Processing footnote/endnote block (note contents are shown) -->
  <xsl:template match="text:note" mode="notes">
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
  <xsl:template match="text:note-citation" mode="notes">
    <xsl:param name="note-type"/>
    <xsl:param name="anchor-name"/>
    <xsl:param name="anchor-ref"/>
    <xsl:variable name="config-name" select="concat('text:', $note-type, 's-configuration')"/>
    <xsl:variable name="style-name"
      select="//*[name()=$config-name][1]/@text:citation-body-style-name"/>
    <xsl:element name="a">
      <xsl:attribute name="name">
        <xsl:value-of select="$anchor-name"/>
      </xsl:attribute>
      <xsl:attribute name="href">
        <xsl:value-of select="$anchor-ref"/>
      </xsl:attribute>
      <xsl:element name="span">
        <xsl:attribute name="style">
          <xsl:text>vertical-align: super;</xsl:text>
        </xsl:attribute>
        <xsl:element name="span">
          <xsl:attribute name="class">
            <xsl:value-of select="$note-type"/>
          </xsl:attribute>
          <xsl:apply-templates/>
        </xsl:element>
      </xsl:element>
    </xsl:element>
  </xsl:template>

  <xsl:template match="text:note" mode="note-body">
    <xsl:param name="note-type"/>
    <xsl:value-of select="$line-break"/>
    <xsl:element name="div">
      <xsl:attribute name="style">
        <xsl:text>font-size: .9em;</xsl:text>
      </xsl:attribute>
        <xsl:element name="div">
          <xsl:attribute name="class">
            <xsl:value-of select="@text:note-class"/>
          </xsl:attribute>
          <xsl:element name="a">
            <xsl:attribute name="name">
              <xsl:value-of select="@text:id"/>
            </xsl:attribute>
            <xsl:attribute name="href">#<xsl:value-of select="@text:id"/>-text</xsl:attribute>
            <xsl:value-of select="text:note-citation"/>
          </xsl:element>
          <xsl:text><!-- required for space --> <!-- --></xsl:text>
          <xsl:apply-templates select="text:note-body//text:p" mode="content-only"/>
        </xsl:element>
      </xsl:element>
    <xsl:value-of select="$line-break"/>
  </xsl:template>

  <xsl:template match="text:p" mode="content-only">
    <xsl:apply-templates></xsl:apply-templates>
    <xsl:value-of select="$line-break"/>
    <xsl:element name="br"></xsl:element>
  </xsl:template>
</xsl:stylesheet>
