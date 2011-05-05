<!--
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
-->
<xsl:stylesheet
	version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
  <xsl:output
	  method="xml"
	  indent="yes"
	  omit-xml-declaration="yes"
	  encoding="UTF-8"
	  media-type="text/html"/>

	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- root element -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="/">
  	<xsl:text disable-output-escaping="yes">&lt;!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"&gt;</xsl:text>
	  <html lang="en">
		  <head>
			  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
        <title>XHTML from QTI</title>
		  	<link href="sm.css" type="text/css" rel="stylesheet"/>
		  	<script src="globals.js">
          <xsl:comment>script</xsl:comment>
        </script>
		  </head>
      <body>
      	<xsl:apply-templates/>
      </body>
    </html>
  </xsl:template>
  
  
  <!-- === -->
  <!--  A  -->
	<!-- === -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- assessment -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="assessment">
		<h2>Assessment stuff</h2>
		<xsl:apply-templates/>
	</xsl:template>
	<!-- === -->
	<!--  B  -->
	<!-- === -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- b -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="b">
		<b><xsl:apply-templates/></b>
	</xsl:template>
	<!-- === -->
	<!--  D  -->
	<!-- === -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- decvar -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="decvar"/>
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="decvar" mode="actual">
		<xsl:if test="@varname= 'SCORE'">
			<xsl:text> (</xsl:text>
			<xsl:value-of select="@defaultval"/>
			<xsl:text> marks)</xsl:text>
		</xsl:if>
	</xsl:template>
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- displayfeedback -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="displayfeedback">
		<xsl:apply-templates/>
	</xsl:template>
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- duration -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="duration"/>
	<!-- === -->
	<!--  F  -->
	<!-- === -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- fieldentry -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="fieldentry">
		<xsl:apply-templates/>
	</xsl:template>
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- fieldlabel -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="fieldlabel">
		<xsl:apply-templates/>
	</xsl:template>
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- flow -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="flow">
		<xsl:param name="ItemId"/>
		<xsl:param name="NumberResponses"/>
		<xsl:param name="Cardinality"/>
		
		<xsl:apply-templates>
			<xsl:with-param name="ItemId">
				<xsl:value-of select="$ItemId"/>
			</xsl:with-param>
			<xsl:with-param name="NumberResponses">
				<xsl:value-of select="$NumberResponses"/>
			</xsl:with-param>
			<xsl:with-param name="Cardinality">
				<xsl:value-of select="$Cardinality"/>
			</xsl:with-param>
		</xsl:apply-templates>
	</xsl:template>
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="flow_label">
		<xsl:param name="ItemId"/>
		<xsl:param name="NumberResponses"/>
		<xsl:param name="Cardinality"></xsl:param>
		
		<xsl:apply-templates>
			<xsl:with-param name="ItemId">
				<xsl:value-of select="$ItemId"/>
			</xsl:with-param>
			<xsl:with-param name="NumberResponses">
				<xsl:value-of select="$NumberResponses"/>
			</xsl:with-param>
			<xsl:with-param name="Cardinality">
				<xsl:value-of select="$Cardinality"/>
			</xsl:with-param>
		</xsl:apply-templates>

		<xsl:if test="$Cardinality = 'Multiple'">
			<xsl:text disable-output-escaping="yes">&amp;nbsp;</xsl:text>
			<input>
				<xsl:attribute name="value">
					<xsl:text>Judge</xsl:text>
				</xsl:attribute>
				<xsl:attribute name="type">
					<xsl:text>button</xsl:text>
				</xsl:attribute>
				<xsl:attribute name="onClick">
					<xsl:text>cmaJudge('</xsl:text>
					<xsl:value-of select="$ItemId"/>
					<xsl:text>', </xsl:text>
					<xsl:value-of select="$NumberResponses"/>
					<xsl:text>, '</xsl:text>
					<xsl:call-template name="GenerateTFstring"/>
					<xsl:text>');</xsl:text>
				</xsl:attribute>
			</input>
		</xsl:if>
		<xsl:text disable-output-escaping="yes"> &amp;nbsp; </xsl:text>
		<input>
			<xsl:attribute name="value">
				<xsl:text>Reset</xsl:text>
			</xsl:attribute>
			<xsl:attribute name="type">
				<xsl:text>button</xsl:text>
			</xsl:attribute>
			<xsl:attribute name="onClick">
				<xsl:text>cmaClear('</xsl:text>
				<xsl:value-of select="$ItemId"/>
				<xsl:text>', </xsl:text>
				<xsl:value-of select="$NumberResponses"/>
				<xsl:text>);</xsl:text>
			</xsl:attribute>
		</input>
		<br/><br/>
	</xsl:template>
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="flow_mat">
		<xsl:apply-templates/>
	</xsl:template>
	<!-- === -->
	<!--  I  -->
	<!-- === -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- item -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="item">
		<xsl:variable name="ItemId">
			<xsl:value-of select="@ident"/>
		</xsl:variable>
		<xsl:variable name="NumberResponses">
			<xsl:value-of select="count(.//response_label)"/>
		</xsl:variable>
		<xsl:variable name="Cardinality">
			<xsl:value-of select=".//@rcardinality"/>
		</xsl:variable>
		
		<h2>
		  <xsl:text>QUESTION </xsl:text>
		  <xsl:number/>
			<xsl:text> of </xsl:text>
		  <xsl:value-of select="count(//item)"/>
		  <xsl:apply-templates select="//decvar" mode="actual"/>
		</h2>

		<xsl:apply-templates select="qticomment"/>
		<xsl:apply-templates select="duration"/>
		<xsl:apply-templates select="itemmetadata"/>
		<xsl:apply-templates select="objectives"/>
		<xsl:apply-templates select="itemcontrol"/>
		<xsl:apply-templates select="itemprecondition"/>
		<xsl:apply-templates select="itempostcondition"/>
		<xsl:apply-templates select="itemrubric|rubric"/>
			
		<xsl:apply-templates select="presentation">
			<xsl:with-param name="ItemId">
				<xsl:value-of select="$ItemId"/>
			</xsl:with-param>
			<xsl:with-param name="NumberResponses">
				<xsl:value-of select="$NumberResponses"/>
			</xsl:with-param>
			<xsl:with-param name="Cardinality">
				<xsl:value-of select="$Cardinality"/>
			</xsl:with-param>
		</xsl:apply-templates>

		<xsl:apply-templates select="resprocessing"/>
		<xsl:apply-templates select="itemproc-extension"/>
			
		<div>
			<xsl:attribute name="id">
				<xsl:value-of select="$ItemId"/>
				<xsl:text>_fb</xsl:text>
			</xsl:attribute>
			<xsl:attribute name="style">
				<xsl:text>display:none</xsl:text>
			</xsl:attribute>
			<xsl:attribute name="className">
				<xsl:text>feedback-none</xsl:text>
			</xsl:attribute>
			<xsl:apply-templates select="itemfeedback">
				<xsl:with-param name="ItemId">
					<xsl:value-of select="$ItemId"/>
				</xsl:with-param>
				<xsl:with-param name="NumberResponses">
					<xsl:value-of select="$NumberResponses"/>
				</xsl:with-param>
				<xsl:with-param name="Cardinality">
					<xsl:value-of select="$Cardinality"/>
				</xsl:with-param>
			</xsl:apply-templates>
		</div>

		<xsl:apply-templates select="reference"/>
	</xsl:template>
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- itemfeedback -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="itemfeedback">
		<xsl:param name="ItemId"/>
		<xsl:param name="NumberResponses"/>
		<xsl:param name="Cardinality"/>

		<xsl:variable name="feedback-identifier">
			<xsl:value-of select="@ident"/>
		</xsl:variable>
		<xsl:variable name="link_to_response">
			<xsl:value-of select="//resprocessing/respcondition[displayfeedback/@linkrefid = $feedback-identifier]/conditionvar/varequal"/>
		</xsl:variable>
		<xsl:variable name="score">
			<xsl:value-of select="//resprocessing/respcondition[displayfeedback/@linkrefid = $feedback-identifier]/setvar"/>
		</xsl:variable>

		<xsl:choose>
			<xsl:when test="$Cardinality = 'Single'">
				<div>
					<xsl:attribute name="id">
						<xsl:value-of select="$ItemId"/>
						<xsl:text>_</xsl:text>
						<xsl:apply-templates select="ancestor::item/presentation/flow/response_lid/render_choice/flow_label/response_label[@ident = $link_to_response]" mode="position"/>
						<xsl:text>_s</xsl:text>
					</xsl:attribute>
					<xsl:apply-templates/>
				</div>
			</xsl:when>
			<xsl:when test="$Cardinality = 'Multiple'">
				<div>
					<xsl:attribute name="id">
						<xsl:value-of select="$ItemId"/>
						<xsl:text>_</xsl:text>
						<xsl:apply-templates select="ancestor::item/presentation/flow/response_lid/render_choice/flow_label/response_label[@ident = $link_to_response]" mode="position"/>
						<xsl:text>_s</xsl:text>
					</xsl:attribute>
					<xsl:apply-templates/>
				</div>
			</xsl:when>
			<xsl:otherwise>
				
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- itemcontrol -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="itemcontrol"/>
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- itemdata -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="itemmetadata">
		<xsl:comment>
			<xsl:apply-templates/>
		</xsl:comment>
	</xsl:template>
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- itempostcondition -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="itempostcondition"/>
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- itemprecondition -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="itemprecondition"/>
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- itemproc-extension -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="itemproc-extension"/>
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- itemrubric -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="itemrubric"/>
	<!-- === -->
	<!--  M  -->
	<!-- === -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- material -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="material">
		<xsl:apply-templates/>
	</xsl:template>
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- matimage -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="matimage">
		<xsl:if test="@uri and @uri != ''">
			<img>
				<xsl:attribute name="src">
					<xsl:value-of select="@uri"/>
				</xsl:attribute>
				<xsl:attribute name="alt">
					<xsl:choose>
						<xsl:when test="@label and @label != ''">
							<xsl:value-of select="@label"/>
						</xsl:when>
						<xsl:otherwise>
							<xsl:value-of select="@uri"/>
						</xsl:otherwise>
					</xsl:choose>
				</xsl:attribute>
				<xsl:attribute name="height">
					<xsl:value-of select="@height"/>
				</xsl:attribute>
				<xsl:attribute name="width">
					<xsl:value-of select="@width"/>
				</xsl:attribute>
				<xsl:attribute name="border">0</xsl:attribute>
			</img>
		</xsl:if>
		<xsl:variable name="ElementContainsData">
			<xsl:call-template name="ElementContainsData"/>
		</xsl:variable>
		<xsl:if test="$ElementContainsData!=''">
			<br/>
			<xsl:apply-templates/>
		</xsl:if>
		<br/>
	</xsl:template>
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- mattext -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="mattext">
		<xsl:choose>
			<xsl:when test="@texttype='TEXT/HTML'">
				<xsl:apply-templates/>
			</xsl:when>
			<xsl:otherwise>
				<xsl:value-of select="."/>
			</xsl:otherwise>
		</xsl:choose>
		<br/>
	</xsl:template>
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- matemtext -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="matemtext">
		<b><xsl:apply-templates/></b>
		<br/>
	</xsl:template>
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- matbreak -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="matbreak">
		<br/>
	</xsl:template>
	<!-- === -->
	<!--  O  -->
	<!-- === -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- objectives -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="objectives"/>
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- outcomes -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="outcomes">
		<xsl:apply-templates/>
	</xsl:template>
	<!-- === -->
	<!--  P  -->
	<!-- === -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- presentation -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="presentation">
		<xsl:param name="ItemId"/>
		<xsl:param name="NumberResponses"/>
		<xsl:param name="Cardinality"/>

		<xsl:apply-templates>
			<xsl:with-param name="ItemId">
				<xsl:value-of select="$ItemId"/>
			</xsl:with-param>
			<xsl:with-param name="NumberResponses">
				<xsl:value-of select="$NumberResponses"/>
			</xsl:with-param>
			<xsl:with-param name="Cardinality">
				<xsl:value-of select="$Cardinality"/>
			</xsl:with-param>
		</xsl:apply-templates>
	</xsl:template>
	<!-- === -->
	<!--  Q  -->
	<!-- === -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- questestinterop - top-level element -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="questestinterop">
		<xsl:apply-templates/>
	</xsl:template>
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- qticomment -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="qticomment">
		<xsl:comment>
			<xsl:apply-templates/>
		</xsl:comment>
	</xsl:template>
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- qtimetadata -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="qtimetadata">
		<xsl:comment>
			<xsl:apply-templates/>
		</xsl:comment>
	</xsl:template>
	<!-- === -->
	<!--  R  -->
	<!-- === -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- reference -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="reference"/>
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- render_choice -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="render_choice">
		<xsl:param name="ItemId"/>
		<xsl:param name="NumberResponses"/>
		<xsl:param name="Cardinality"></xsl:param>

		<xsl:apply-templates>
			<xsl:with-param name="ItemId">
				<xsl:value-of select="$ItemId"/>
			</xsl:with-param>
			<xsl:with-param name="NumberResponses">
				<xsl:value-of select="$NumberResponses"/>
			</xsl:with-param>
			<xsl:with-param name="Cardinality">
				<xsl:value-of select="$Cardinality"/>
			</xsl:with-param>
		</xsl:apply-templates>
	</xsl:template>
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- render_fib -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="render_fib">
		<xsl:apply-templates/>
	</xsl:template>
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- render_hotspot -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="render_hotspot">
		<xsl:text>[rendering of hotspot goes here]</xsl:text>
	</xsl:template>
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- render_hotspot -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="render_slider">
		<xsl:text>[rendering of slider here with attributes </xsl:text>
		<xsl:for-each select="./@*">
			<xsl:value-of select="name()"/>
			<xsl:text>:</xsl:text>
			<xsl:text> </xsl:text>
			<xsl:value-of select="."/>
			<xsl:text>  </xsl:text>
		</xsl:for-each>
		<xsl:text>]</xsl:text>
	</xsl:template>
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- respcondition -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="respcondition">
		<xsl:apply-templates/>
	</xsl:template>
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- response_extension -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="response_extension">
		<xsl:apply-templates/>
	</xsl:template>
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- response_grp -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="response_grp">
		<xsl:apply-templates/>
	</xsl:template>
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- response_label -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="response_label">
		<xsl:apply-templates/>
	</xsl:template>
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="response_label" mode="position">
		<xsl:variable name="ident">
			<xsl:value-of select="@ident"/>
		</xsl:variable>
		<xsl:variable name="responses_to_date">
			<xsl:value-of select="count(preceding-sibling::*) + 1"/>
		</xsl:variable>
		<xsl:value-of select="$responses_to_date"/>
	</xsl:template>		
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="flow_label/response_label">
		<xsl:param name="ItemId"/>
		<xsl:param name="NumberResponses"/>
		<xsl:param name="Cardinality"></xsl:param>

		<xsl:variable name="option_number">
			<xsl:value-of select="position()"/>
		</xsl:variable>

		<input>
			<xsl:attribute name="id">
				<xsl:value-of select="$ItemId"/>
				<xsl:text>_</xsl:text>
				<xsl:value-of select="$option_number"/>
			</xsl:attribute>
			<xsl:attribute name="value">
				<xsl:value-of select="$option_number"/>
			</xsl:attribute>
			<xsl:attribute name="name">
				<xsl:value-of select="$ItemId"/>
			</xsl:attribute>
			<xsl:choose>
				<xsl:when test="$Cardinality = 'Single'">
					<xsl:attribute name="type">radio</xsl:attribute>
					<xsl:attribute name="onClick">
						<xsl:text>cmaOption('</xsl:text>
						<xsl:value-of select="$ItemId"/>
						<xsl:text>', </xsl:text>
						<xsl:value-of select="$option_number"/>
						<xsl:text>, </xsl:text>
						<xsl:value-of select="$NumberResponses"/>
						<xsl:text>);</xsl:text>
					</xsl:attribute>
				</xsl:when>
				<xsl:when test="$Cardinality = 'Multiple'">
					<xsl:attribute name="type">checkbox</xsl:attribute>
				</xsl:when>
				<xsl:otherwise>
					<xsl:attribute name="type">??</xsl:attribute>
				</xsl:otherwise>
			</xsl:choose>
		</input>
		<label>
			<xsl:attribute name="for">
				<xsl:value-of select="$ItemId"/>
				<xsl:text>_</xsl:text>
				<xsl:value-of select="$option_number"/>
			</xsl:attribute>
			<xsl:apply-templates/>
		</label>
  </xsl:template>
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="render_fib/response_label">
		<input type="text"/>
	</xsl:template>
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- response_lid -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="response_lid">
		<xsl:param name="ItemId"/>
		<xsl:param name="NumberResponses"/>
		<xsl:param name="Cardinality"/>
		
		<xsl:apply-templates>
			<xsl:with-param name="ItemId">
				<xsl:value-of select="$ItemId"/>
			</xsl:with-param>
			<xsl:with-param name="NumberResponses">
				<xsl:value-of select="$NumberResponses"/>
			</xsl:with-param>
			<xsl:with-param name="Cardinality">
				<xsl:value-of select="$Cardinality"/>
			</xsl:with-param>
		</xsl:apply-templates>
	</xsl:template>
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- response_num -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="response_num">
		<xsl:param name="ItemId"/>
		<xsl:param name="NumberResponses"/>
		<xsl:param name="Cardinality"/>
		
		<xsl:apply-templates>
			<xsl:with-param name="ItemId">
				<xsl:value-of select="$ItemId"/>
			</xsl:with-param>
			<xsl:with-param name="NumberResponses">
				<xsl:value-of select="$NumberResponses"/>
			</xsl:with-param>
			<xsl:with-param name="Cardinality">
				<xsl:value-of select="$Cardinality"/>
			</xsl:with-param>
		</xsl:apply-templates>
	</xsl:template>
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- response_str -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="flow/response_str">
		<xsl:param name="ItemId"/>
		<xsl:param name="NumberResponses"/>
		<xsl:param name="Cardinality"></xsl:param>
		
		<xsl:variable name="option_number">
			<xsl:number/>
		</xsl:variable>
		<xsl:variable name="num_correct">
			<xsl:value-of select="count(//resprocessing/respcondition/setvar[. = '100.0'])"/>
		</xsl:variable>
		<xsl:variable name="num_incorrect">
			<xsl:value-of select="count(//resprocessing/respcondition/setvar[. = '0.0'])"/>
		</xsl:variable>
		
		<input>
			<xsl:attribute name="id">
				<xsl:value-of select="$ItemId"/>
				<xsl:text>_</xsl:text>
				<xsl:value-of select="$option_number"/>
			</xsl:attribute>
			<xsl:attribute name="name">
				<xsl:value-of select="$option_number"/>
			</xsl:attribute>
			<xsl:attribute name="type">text</xsl:attribute>
			<xsl:attribute name="size">
				<xsl:choose>
					<xsl:when test="../../response_str/@columns">
						<xsl:value-of select="../../response_str/@columns"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:text>10</xsl:text>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
		</input>

		<xsl:text disable-output-escaping="yes">&amp;nbsp;</xsl:text>
		<input>
			<xsl:attribute name="value">
				<xsl:text>Judge</xsl:text>
			</xsl:attribute>
			<xsl:attribute name="type">
				<xsl:text>button</xsl:text>
			</xsl:attribute>
			<xsl:attribute name="onClick">
				<xsl:text>cmaJudgeAlpha('</xsl:text>
				<xsl:value-of select="$ItemId"/>
				<xsl:text>', [</xsl:text>
				<!-- correct alternatives -->
				<xsl:if test="$num_correct &gt; 0">
					<xsl:for-each select="//respcondition">
						<xsl:if test="./setvar/text() = '100.0'">
							<xsl:text>'</xsl:text>
							<xsl:value-of select="./conditionvar/varequal/text()"/>
							<xsl:text>'</xsl:text>
							<xsl:variable name="this_one">
								<xsl:number/>
							</xsl:variable>
							<xsl:if test="$num_correct != $this_one">
								<xsl:text>,</xsl:text>
							</xsl:if>
						</xsl:if>
					</xsl:for-each>
				</xsl:if>
				<xsl:text>], [</xsl:text>
				<!-- incorrect alternatives -->
				<xsl:if test="$num_incorrect &gt; 0">
					<xsl:for-each select="//respcondition">
						<xsl:if test="./setvar/text() = '0.0'">
							<xsl:text>'</xsl:text>
							<xsl:value-of select="./conditionvar/varequal/text()"/>
							<xsl:text>'</xsl:text>
							<xsl:variable name="this_one">
								<xsl:number/>
							</xsl:variable>
							<xsl:if test="$num_incorrect != $this_one">
								<xsl:text>,</xsl:text>
							</xsl:if>
						</xsl:if>
					</xsl:for-each>
				</xsl:if>
				<xsl:text>], </xsl:text>
				<xsl:choose>
					<xsl:when test="//varequal/@case = 'No'">false</xsl:when>
					<xsl:otherwise>true</xsl:otherwise>
				</xsl:choose>
				<xsl:text>);</xsl:text>
			</xsl:attribute>
		</input>
		<xsl:text disable-output-escaping="yes"> &amp;nbsp; </xsl:text>
		<input>
			<xsl:attribute name="value">
				<xsl:text>Reset</xsl:text>
			</xsl:attribute>
			<xsl:attribute name="type">
				<xsl:text>button</xsl:text>
			</xsl:attribute>
			<xsl:attribute name="onClick">
				<xsl:text>cmaClearInput('</xsl:text>
				<xsl:value-of select="$ItemId"/>
				<xsl:text>', </xsl:text>
				<xsl:value-of select="$NumberResponses"/>
				<xsl:text>, </xsl:text>
				<xsl:value-of select="$num_correct"/>
				<xsl:text>, </xsl:text>
				<xsl:value-of select="$num_incorrect"/>
				<xsl:text>);</xsl:text>
			</xsl:attribute>
		</input>
		<br/><br/>
	</xsl:template>
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="response_str">
		<xsl:param name="ItemId"/>
		<xsl:param name="NumberResponses"/>
		<xsl:param name="Cardinality"/>
		
		<xsl:apply-templates>
			<xsl:with-param name="ItemId">
				<xsl:value-of select="$ItemId"/>
			</xsl:with-param>
			<xsl:with-param name="NumberResponses">
				<xsl:value-of select="$NumberResponses"/>
			</xsl:with-param>
			<xsl:with-param name="Cardinality">
				<xsl:value-of select="$Cardinality"/>
			</xsl:with-param>
		</xsl:apply-templates>
	</xsl:template>
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- response_xy -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="response_xy">
		<xsl:param name="ItemId"/>
		<xsl:param name="NumberResponses"/>
		<xsl:param name="Cardinality"/>
		
		<xsl:apply-templates>
			<xsl:with-param name="ItemId">
				<xsl:value-of select="$ItemId"/>
			</xsl:with-param>
			<xsl:with-param name="NumberResponses">
				<xsl:value-of select="$NumberResponses"/>
			</xsl:with-param>
			<xsl:with-param name="Cardinality">
				<xsl:value-of select="$Cardinality"/>
			</xsl:with-param>
		</xsl:apply-templates>
	</xsl:template>
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- resprocessing -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="resprocessing">
		<xsl:apply-templates/>
	</xsl:template>
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- rubric -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="rubric"/>
	<!-- === -->
	<!--  S  -->
	<!-- === -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- section -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="section">
		<h2>Section</h2>
		<xsl:apply-templates/>
	</xsl:template>	

	<!-- ================= -->
	<!--  named templates  -->
	<!-- ================= -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- capitalise the first character -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template name="capitaliseFirst">
		<xsl:param name="data"/>

		<xsl:variable name="first">
			<xsl:value-of	select="substring($data,'1','1')"/>
		</xsl:variable>
		<xsl:variable name="rest">
			<xsl:value-of select="substring-after($data, $first)"/>
		</xsl:variable>
		<xsl:variable name="UCfirst">
		  <xsl:value-of select="translate($first, 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')"/>
		</xsl:variable>

		<xsl:value-of select="$UCfirst"/>
		<xsl:value-of select="$rest"/>
	</xsl:template>
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- generate string of T/F used to judge a multiple selection question -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template name="GenerateTFstring">
		<xsl:text>10110</xsl:text>
		<!--
		<xsl:for-each select="//response_label">
			<xsl:value-of select="@ident"/>
			<xsl:choose>
				<xsl:when test=""></xsl:when>
			</xsl:choose>
		</xsl:for-each>
		-->
	</xsl:template>
	
	<!-- =============================== -->
	<!--  generic nodes, elements, text  -->
	<!-- =============================== -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<!-- element contains data -->
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template name="ElementContainsData">
		<xsl:value-of select="normalize-space(.//text())"/>
		<xsl:value-of select="normalize-space(.//node())"/>
	</xsl:template>
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="node()">
		<!-- do nothing with all other elements - yet! -->
		<!--
		<xsl:value-of select="name()"/>
		<xsl:value-of select="."/>
		<xsl:for-each select="@*">
			<xsl:value-of select="name()"/>
			<xsl:value-of select="."/>
		</xsl:for-each>
		-->
	</xsl:template>
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="*">
		<!-- do nothing with all other elements - yet! -->
	</xsl:template>
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
	<xsl:template match="text()">
		<xsl:variable name="contents">
			<xsl:value-of select="."/>
		</xsl:variable>
		<xsl:variable name="lt">
			<xsl:text disable-output-escaping="yes">&lt;</xsl:text>
		</xsl:variable>
		
		<xsl:choose>
			<xsl:when test="contains($contents, $lt)">
				<!--<xsl:value-of select="translate($contents, $lt, $lt)"/>-->
				<xsl:value-of select="substring-before($contents, $lt)"/>
				<xsl:value-of select="$lt"/>
				<xsl:value-of select="substring-after($contents, $lt)"/>
			</xsl:when>
			<xsl:otherwise>
				<xsl:value-of select="$contents"/>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
	<!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
</xsl:stylesheet>
