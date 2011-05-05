Attribute VB_Name = "stylecreator"
#Const MSWD = True
#Const OOO = Not MSWD

Rem *********************************************************************
Rem    Copyright (C) 2006  Distance and e-Learning Centre,
Rem    University of Southern Queensland
Rem
Rem    This program is free software; you can redistribute it and/or modify
Rem    it under the terms of the GNU General Public License as published by
Rem    the Free Software Foundation; either version 2 of the License, or
Rem    (at your option) any later version.
Rem
Rem    This program is distributed in the hope that it will be useful,
Rem    but WITHOUT ANY WARRANTY; without even the implied warranty of
Rem    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
Rem    GNU General Public License for more details.
Rem
Rem    You should have received a copy of the GNU General Public License
Rem    along with this program; if not, write to the Free Software
Rem    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
Rem
Rem *********************************************************************

Sub subCreateAllMissingStyles()
    subCreateMissingStyle ("p")
    subCreateMissingStyle ("p-indent")
    subCreateMissingStyle ("p-center")
    subCreateMissingStyle ("p-right")
    For i = 1 To 5
        Call subCreateMissingStyle(fnMakeStyleName("li", i, "a"))
        Call subCreateMissingStyle(fnMakeStyleName("li", i, "i"))
        Call subCreateMissingStyle(fnMakeStyleName("li", i, "A"))
        Call subCreateMissingStyle(fnMakeStyleName("li", i, "I"))
        Call subCreateMissingStyle(fnMakeStyleName("li", i, "n"))
        Call subCreateMissingStyle(fnMakeStyleName("li", i, "b"))
        Call subCreateMissingStyle(fnMakeStyleName("h", i, ""))
        Call subCreateMissingStyle(fnMakeStyleName("h", i, "n"))
        #If MSWD Then
            Rem in word this is not created along with the list styles
            Call subCreateMissingStyle(fnMakeStyleName("li", i, "p"))
        #End If
    Next
    subCreateMissingStyle ("bq5")
    subCreateMissingStyle ("dt1")
    subCreateMissingStyle ("dt5")
    subCreateMissingStyle ("bq5source")
    subCreateMissingStyle ("pre5")
    subCreateMissingStyle ("Title-chapter")
    subCreateMissingStyle ("Title-book")

    subCreateMissingStyle ("i-b")
    subCreateMissingStyle ("i-i")
    subCreateMissingStyle ("i-code")
    subCreateMissingStyle ("i-sub")
    subCreateMissingStyle ("i-sup")
    subCreateMissingStyle ("i-latex")
    printMsgbox ("Completed Creating Missing Styles")

End Sub


Rem ParaTopMargin          (spacing above paragraph)
Rem ParaBottomMargin       (spacing below paragraph)
Rem ParaLeftMargin         (spacing to the left)
Rem ParaRightMargin        (spacing to the right)
Rem CharWeight             (bold)
Rem ParaBackColor          (for pre only, 13421772)
Rem ParaBackTransparent    (for pre only, False)
Rem ParaLeftMargin         (Amount of Indent)
Rem ParaAdjust             (alignment, left=0, right=1, justify=2, center=3)
Rem ParaKeepTogether       (whether it should stay with the next paragraph)
Rem ParaOrphans            (number of orphans allowed)
Rem ParaSplit              (whether the paragraph can be split)
Rem ParaWidows             (number of widows allowed)
Rem NumberingStyleName     (for lists only, should be same as style name)
Rem ParaIsNumberingRestart (for lists only)
Rem CharFontFamily         (Unknown, possibly necessary)
Rem FollowStyle            (Style that will follow when press enter)
Rem ParentStyle            (The name of the style that this one inherits from)


Function subCreateMissingStyle(sNewStyle As String)
Dim sParent As String, nAlignment As Integer, sType As String, sFamily As String, nLeftMargin As Integer
    sFamily = fnGetFamily(sNewStyle)
    sType = fnGetType(sNewStyle)
    nLevel = fnGetLevel(sNewStyle)
    If nLevel > 5 Then
        nLevel = 5
        sNewStyle = fnMakeStyleName(sFamily, nLevel, sType)
    End If
    Select Case sFamily
        Case "p"
            Select Case sType
                Case "center"
                    nAlignment = 3
                    sParent = "p"
                Case "right"
                    nAlignment = 1
                    sParent = "p"
                Case "indent"
                    Call subCreateDefaultStyle(sNewStyle, "p", "Paragraph", Array( _
                            "ParaLeftMargin", 600))
                Case Else
                    nAlignment = 0
                    sParent = "Default"
            End Select
            Call subCreateDefaultStyle(sNewStyle, sParent, "Paragraph", Array( _
                "CharHeight", 11, _
                "CharFontName", "Times New Roman", _
                "CharFontFamily", 3, _
                "ParaTopMargin", 420, _
                "ParaBottomMargin", 0, _
                "ParaLeftMargin", 0, _
                "ParaRightMargin", 0, _
                "CharPosture", 0, _
                "ParaAdjust", nAlignment))
        Case "li"
            If sType <> "p" Then
                Rem This only set the List Numbering Style Postion value but not the Para Style Value.
                nLeftMargin = (nLevel - 1) * 600
                Rem This value will later be added to the ListTabStop Postion thus has to be negative
                nFirstLineIndent = -600
                nIndent = nLevel * 600
                Select Case sType
                Case "A"
                    nNumberingType = 0
                Case "a"
                    nNumberingType = 1
                Case "I"
                    nNumberingType = 2
                Case "i"
                    nNumberingType = 3
                Case "n"
                    nNumberingType = 4
                Case "b"
                    nNumberingType = 6
                End Select
            #If MSWD Then
                Call subCreateDefaultStyle(sNewStyle, "p", "Numbering", Array( _
                    "ParaLeftMargin", nLeftMargin, _
                    "ParaTopMargin", 210, _
                    "ParaBottomMargin", 0))
            #Else
                sParent = fnMakeStyleName("li", fnGetLevel(sNewStyle), "p")
                If Int(getOOoVersion()) = 2 Then
                    Call subCreateDefaultStyle(sNewStyle, "", "Numbering", Array( _
                                "LeftMargin", 600, _
                                "FirstLineOffset", nFirstLineIndent, _
                                "NumberingType", nNumberingType))
                Else
                    Call subCreateDefaultStyle(sNewStyle, "", "Numbering", Array( _
                            "IndentAt", nIndent, _
                            "ListtabStopPosition", nLeftMargin, _
                            "FirstLineIndent", nFirstLineIndent, _
                            "NumberingType", nNumberingType))
                End If

                sParent = fnMakeStyleName("li", fnGetLevel(sNewStyle), "p")
                If fnGetLevel(sNewStyle) = 1 Then
                    nLeftMargin = 0
                Else
                    nLeftMargin = 100 - (100 / (fnGetLevel(sNewStyle)))
                End If

                Call subCreateDefaultStyle(sNewStyle, sParent, "Paragraph", Array( _
                    "ParaLeftMarginRelative", nLeftMargin, _
                    "CharPosture", 0, _
                    "ParaBottomMargin", 0, _
                    "ParaTopMargin", 210))
            #End If
            ElseIf sType = "p" Then
                #If MSWD Then
                    nLeftMargin = nLevel * 600
                    Call subCreateDefaultStyle(sNewStyle, "p", "Paragraph", Array( _
                        "ParaLeftMargin", nLeftMargin, _
                        "ParaBottomMargin", 0, _
                        "ParaTopMargin", 210))
                 #Else
                    If fnGetLevel(sNewStyle) = 1 Then
                        nLeftMargin = 101
                        sParent = "p-indent"
                    Else
                        nLeftMargin = 100 + (100 / (fnGetLevel(sNewStyle) - 1))
                        sParent = fnMakeStyleName("li", fnGetLevel(sNewStyle) - 1, "p")
                    End If
                    Call subCreateDefaultStyle(sNewStyle, sParent, "Paragraph", Array( _
                        "ParaLeftMarginRelative", nLeftMargin, _
                        "CharPosture", 0, _
                        "ParaBottomMargin", 0, _
                        "ParaTopMargin", 210))
                 #End If
            End If
        Case "bq"
            Select Case sType
            Case ""
                Select Case nLevel
                Case 1
                    Call subCreateDefaultStyle(sNewStyle, "p", "Paragraph", Array( _
                        "CharPosture", 2, _
                        "ParaLeftMargin", 600))
                Case 2
                    Call subCreateDefaultStyle(sNewStyle, "bq1", "Paragraph", Array( _
                        "ParaLeftMargin", 1200))
                Case 3
                    Call subCreateDefaultStyle(sNewStyle, "bq2", "Paragraph", Array( _
                        "ParaLeftMargin", 1800))
                Case 4
                    Call subCreateDefaultStyle(sNewStyle, "bq3", "Paragraph", Array( _
                        "ParaLeftMargin", 2400))
                Case 5
                    Call subCreateDefaultStyle(sNewStyle, "bq4", "Paragraph", Array( _
                        "ParaLeftMargin", 3200))
                End Select
            Case "source"
                Select Case nLevel
                Case 1
                    Call subCreateDefaultStyle(sNewStyle, "bq1", "Paragraph", Array( _
                        "CharHeight", 9, _
                        "CharPosture", 0, _
                        "FollowStyle", "p", _
                        "ParaTopMargin", 100, _
                        "ParaLeftMargin", 600))
                Case 2
                    Call subCreateDefaultStyle(sNewStyle, "bq1source", "Paragraph", Array( _
                        "ParaLeftMargin", 1200))
                Case 3
                    Call subCreateDefaultStyle(sNewStyle, "bq2source", "Paragraph", Array( _
                        "ParaLeftMargin", 1800))
                Case 4
                    Call subCreateDefaultStyle(sNewStyle, "bq3source", "Paragraph", Array( _
                        "ParaLeftMargin", 2400))
                Case 5
                    Call subCreateDefaultStyle(sNewStyle, "bq4source", "Paragraph", Array( _
                        "ParaLeftMargin", 3200))
                End Select
            End Select
        Case "h"
            If sType <> "n" Then
                sType = ""
                sNewStyle = fnMakeStyleName("h", nLevel, "")
            End If
            Select Case sType
            Case ""
                #If OOO Then
                    oStyles = ThisComponent.styleFamilies.getByName("ParagraphStyles")
                    If Not fnHasStyle("p", "Paragraph") Then
                        nPCharHeight = 11
                    Else
                        nPCharHeight = oStyles.getByName("p").CharHeight
                    End If
                    If Not oStyles.hasByName("h1") Then
                        Rem Set default starting values
                        nH1CharHeight = 18
                        nH1ParaTopMargin = 920
                        nH1ParaBottomMargin = 350
                    Else
                        nH1CharHeight = oStyles.getByName("h1").CharHeight
                        nH1ParaTopMargin = oStyles.getByName("h1").ParaTopMargin
                        nH1ParaBottomMargin = oStyles.getByName("h1").ParaBottomMargin
                    End If
                    
                #Else
                    nPCharHeight = 11
                    nH1CharHeight = 18
                    nH1ParaTopMargin = 920
                    nH1ParaBottomMargin = 350
                #End If
                nParaTopMargin = nH1ParaTopMargin - (nH1ParaTopMargin / 5) * (fnGetLevel(sNewStyle) - 1)
                nParaBottomMargin = nH1ParaBottomMargin - (nH1ParaBottomMargin / 5) * (fnGetLevel(sNewStyle) - 1)

                Rem Calculate character height
                nCharHeight = nH1CharHeight - ((nH1CharHeight - nPCharHeight) / 6 * fnGetLevel(sNewStyle))

                Select Case nLevel
                Case 1
                    Call subCreateDefaultStyle(sNewStyle, "Heading 1", "Paragraph", Array( _
                        "CharHeight", nH1CharHeight, _
                        "CharFontName", "Helvetica-Narrow", _
                        "ParaTopMargin", nH1ParaTopMargin, _
                        "ParaBottomMargin", nH1ParaBottomMargin, _
                        "FollowStyle", "p", _
                        "ParaKeepTogether", True))
                Case 2
                    Call subCreateDefaultStyle(sNewStyle, "h1", "Paragraph", Array( _
                        "CharHeight", nCharHeight, _
                        "ParaTopMargin", nParaTopMargin, _
                        "ParaBottomMargin", nParaBottomMargin, _
                        "FollowStyle", "p"))
                Case 3
                    Call subCreateDefaultStyle(sNewStyle, "h2", "Paragraph", Array( _
                        "CharHeight", nCharHeight, _
                        "ParaTopMargin", nParaTopMargin, _
                        "ParaBottomMargin", nParaBottomMargin, _
                        "FollowStyle", "p"))
                Case 4
                    Call subCreateDefaultStyle(sNewStyle, "h3", "Paragraph", Array( _
                        "CharHeight", nCharHeight, _
                        "ParaTopMargin", nParaTopMargin, _
                        "ParaBottomMargin", nParaBottomMargin, _
                        "FollowStyle", "p"))
                Case 5
                    Call subCreateDefaultStyle(sNewStyle, "h4", "Paragraph", Array( _
                        "CharHeight", nCharHeight, _
                        "ParaTopMargin", nParaTopMargin, _
                        "ParaBottomMargin", 0, _
                        "FollowStyle", "p"))
                End Select
            Case "n"
                Select Case nLevel
                Case 0
                    Rem this is for word h-n property
                    Call subCreateDefaultStyle(sNewStyle, "h1", "Paragraph", Array( _
                        "NumberingStyleName", "Outline", _
                        "FollowStyle", "p"))
                Case 1
                    Call subCreateDefaultStyle(sNewStyle, "h1", "Paragraph", Array( _
                        "NumberingStyleName", "Outline", _
                        "FollowStyle", "p"))
                Case 2
                    Call subCreateDefaultStyle(sNewStyle, "h2", "Paragraph", Array( _
                        "NumberingStyleName", "Outline", _
                        "FollowStyle", "p"))
                Case 3
                    Call subCreateDefaultStyle(sNewStyle, "h3", "Paragraph", Array( _
                        "NumberingStyleName", "Outline", _
                        "FollowStyle", "p"))
                Case 4
                    Call subCreateDefaultStyle(sNewStyle, "h4", "Paragraph", Array( _
                        "NumberingStyleName", "Outline", _
                        "FollowStyle", "p"))
                Case 5
                    Call subCreateDefaultStyle(sNewStyle, "h5", "Paragraph", Array( _
                        "NumberingStyleName", "Outline", _
                        "FollowStyle", "p"))
                End Select
                #If OOO Then
                    Call subChangeChapterNumberingRules(ThisComponent, nLevel, Array( _
                        "ParentNumbering", nLevel, _
                        "NumberingType", 4, _
                        "HeadingStyleName", sNewStyle))
                #Else
                    Call subChangeChapterNumberingRules(sNewStyle, nLevel, Array())
                #End If
            End Select
        Case "pre"
            Select Case nLevel
            Case 1
                Call subCreateDefaultStyle(sNewStyle, "bq1", "Paragraph", Array( _
                    "CharFontName", "Courier New", _
                    "CharHeight", 10, _
                    "ParaLeftMargin", 600, _
                    "ParaBackColor", 13421772, _
                    "CharPosture", 0, _
                    "ParaBackTransparent", False))
            Case 2
                Call subCreateDefaultStyle(sNewStyle, "pre1", "Paragraph", Array( _
                    "ParaLeftMargin", 1200))
            Case 3
                Call subCreateDefaultStyle(sNewStyle, "pre2", "Paragraph", Array( _
                    "ParaLeftMargin", 1800))
            Case 4
                Call subCreateDefaultStyle(sNewStyle, "pre3", "Paragraph", Array( _
                    "ParaLeftMargin", 2400))
            Case 5
                Call subCreateDefaultStyle(sNewStyle, "pre4", "Paragraph", Array( _
                    "ParaLeftMargin", 3200))
            End Select
        Case "Title"
            Select Case sType
            Case "chapter"
                Call subCreateDefaultStyle(sNewStyle, "Title", "Paragraph", Array( _
                    "FollowStyle", "p", _
                    "NumberingStyleName", "Outline"))
                #If OOO Then
                    Call subChangeChapterNumberingRules(ThisComponent, 0, Array( _
                       "NumberingType", 4, _
                       "HeadingStyleName", sNewStyle))
                #Else
                    Call subChangeChapterNumberingRules(sNewStyle, 0, Array())
                #End If
                

            Case "book"
                Call subCreateDefaultStyle(sNewStyle, "Title", "Paragraph", Array( _
                    "CharHeight", 36, _
                    "FollowStyle", "p", _
                    "ParaTopMargin", 1400))
            End Select
        Case "dd"
            Select Case nLevel
            Case 1
                Call subCreateDefaultStyle(sNewStyle, "p", "Paragraph", Array( _
                    "ParaLeftMargin", 600, _
                    "CharPosture", 0, _
                    "ParaTopMargin", 210))
            Case 2
                Call subCreateDefaultStyle(sNewStyle, "dd1", "Paragraph", Array( _
                    "ParaLeftMargin", 1200))
            Case 3
                Call subCreateDefaultStyle(sNewStyle, "dd2", "Paragraph", Array( _
                    "ParaLeftMargin", 1800))
            Case 4
                Call subCreateDefaultStyle(sNewStyle, "dd3", "Paragraph", Array( _
                    "ParaLeftMargin", 2400))
            Case 5
                Call subCreateDefaultStyle(sNewStyle, "dd4", "Paragraph", Array( _
                    "ParaLeftMargin", 3200))
            End Select
        Case "dt"
            Select Case nLevel
            Case 1
                Call subCreateDefaultStyle(sNewStyle, "p", "Paragraph", Array( _
                    "CharWeight", 150, _
                    "FollowStyle", "dd1", _
                    "ParaLeftMargin", 0, _
                    "ParaTopMargin", 210))
                    
            Case 2
                Call subCreateDefaultStyle(sNewStyle, "dt1", "Paragraph", Array( _
                    "CharWeight", 150, _
                    "FollowStyle", "dd2", _
                    "ParaLeftMargin", 600, _
                    "ParaTopMargin", 210))
            Case 3
                Call subCreateDefaultStyle(sNewStyle, "dt2", "Paragraph", Array( _
                    "FollowStyle", "dd3", _
                    "ParaLeftMargin", 1200))
            Case 4
                Call subCreateDefaultStyle(sNewStyle, "dt3", "Paragraph", Array( _
                    "FollowStyle", "dd4", _
                    "ParaLeftMargin", 1800))
            Case 5
                Call subCreateDefaultStyle(sNewStyle, "dt4", "Paragraph", Array( _
                    "FollowStyle", "dd5", _
                    "ParaLeftMargin", 2400))
            End Select
        Case "i"
            Select Case sType
            Case "b"
                Call subCreateDefaultStyle(sNewStyle, "", "Character", Array( _
                    "CharWeight", 150))
            Case "i"
                Call subCreateDefaultStyle(sNewStyle, "", "Character", Array( _
                    "CharPosture", 2))
            Case "code"
                Call subCreateDefaultStyle(sNewStyle, "", "Character", Array( _
                    "CharFontName", "Courier New", _
                    "CharHeight", 11))
            Case "sup"
                Call subCreateDefaultStyle(sNewStyle, "", "Character", Array( _
                    "CharHeight", 9, _
                    "CharEscapement", 33))
            Case "sub"
                Call subCreateDefaultStyle(sNewStyle, "", "Character", Array( _
                    "CharHeight", 9, _
                    "CharEscapement", -33))
            Case "latex"
                Call subCreateDefaultStyle(sNewStyle, "i-code", "Character", Array())
            End Select
        Case "xRef"
            If sNewStyle = "xRef-Base" Then
                Call subCreateDefaultStyle(sNewStyle, "", "Character", Array())
            Else
                Call subCreateDefaultStyle(sNewStyle, "xRef-Base", "Character", Array())
            End If
    End Select
    
    #If MSWD Then
        sFamily = fnGetFamily(sNewStyle)
        Rem remove the underline from other styles than Title.
        If sFamily <> "Title" And sFamily <> "li" Then
            Call subNoUnderLine(sNewStyle)
        End If
    #End If
End Function

Sub subNoUnderLine(sStyleName)
    ActiveDocument.Styles(sStyleName).Font.Underline = wdUnderlineNone
End Sub

Sub subNoItalic(sStyleName)
    Rem For word only
    ActiveDocument.Styles(sStyleName).Font.Italic = False
End Sub
Sub subItalic(sStyleName)
    Rem For word only
    ActiveDocument.Styles(sStyleName).Font.Italic = True
End Sub
Sub subNoBold(sStyleName)
    Rem For word only
    ActiveDocument.Styles(sStyleName).Font.Bold = False
End Sub
Sub subBold(sStyleName)
    Rem For word only
    ActiveDocument.Styles(sStyleName).Font.Bold = True
End Sub
Sub subFixWordStyle(sStyleName)
Rem if the italic and bold are set for the paragraph, then the word regards it is part of the style
    sFamily = fnGetFamily(sStyleName)
    sType = fnGetType(sStyleName)
    If sFamily = "p" Or sFamily = "pre" Or sFamily = "dd" Or sFamily = "bq" Or _
        (sFamily = "li" And sType = "p") Or sFamily = "Title" Or (sFamily = "i" And sStyleName <> "i-b") Then
        Rem These styles must not have bold
        Call subNoBold(sStyleName)
    ElseIf sFamily <> "li" Then
        Call subBold(sStyleName)
    End If
    If sFamily = "p" Or sFamily = "pre" Or sFamily = "dd" Or sFamily = "dt" Or _
        sFamily = "h" Or sFamily = "Title" Or (sFamily = "bq" And sType = "source") Or _
        (sFamily = "li" And sType = "p") Or (sFamily = "i" And sStyleName <> "i-i") Then
        Call subNoItalic(sStyleName)
    ElseIf sFamily <> "li" Then
        Call subItalic(sStyleName)
    End If
End Sub
Sub FixTitle()
Rem To fix the title style in word 2007

    #If MSWD Then
        With ActiveDocument.Styles("Title")
            With .Font
                .name = "Arial"
                .Size = 18
                .Bold = True
                .Color = wdColorBlack
                .Spacing = 0
            End With
            With .ParagraphFormat
                .SpaceAfter = 3
                .SpaceBefore = 12
                .Alignment = wdAlignParagraphCenter
            End With
            .Borders(wdBorderBottom).Visible = False
        End With
    #End If
    
End Sub
Function fnListTemplate(sListTemplateName As String)
    Rem For word Only
    Dim oListTemplate

On Error GoTo NoListTemplate

    Set fnListTemplate = ActiveDocument.ListTemplates(sListTemplateName)
    Exit Function
NoListTemplate:
    Set oListTemplate = ActiveDocument.ListTemplates.Add
    oListTemplate.name = sListTemplateName
    oListTemplate.OutlineNumbered = True
    Set fnListTemplate = ActiveDocument.ListTemplates(sListTemplateName)
End Function

Sub subCreateDefaultStyle(sStyleName As String, sParentStyleName As String, sStyleType As String, mArgArray)
    Dim oStyles As Object, oStyle As Object, i As Integer, j As Long
    Dim sPropertyName As String, vPropertyValue


    #If MSWD Then
        If fnHasStyle(sStyleName) Then Exit Sub
        If sStyleName = "" Then Exit Sub
        Dim sListTemplateName As String, oListTemplate, nLevel As Integer
        
        If sStyleType = "Character" Then
            Set oStyle = ActiveDocument.Styles.Add(name:=sStyleName, Type:=wdStyleTypeCharacter)
            For i = 0 To UBound(mArgArray) Step 2
                Call subWordApplyProperty(oStyle, mArgArray(i), mArgArray(i + 1))
            Next
        ElseIf sStyleType = "Paragraph" Then
            Set oStyle = ActiveDocument.Styles.Add(name:=sStyleName, Type:=wdStyleTypeParagraph)
            ActiveDocument.Styles(sStyleName).AutomaticallyUpdate = False
            ActiveDocument.Styles(sStyleName).Frame.Delete
            
            On Error Resume Next
            Rem remove the list style just in case
            Rem list style causing dt2 to lost indent space(changing from list to dt2)
            'ActiveDocument.Styles(sStyleName).LinkStyle = "Normal"
            'ActiveDocument.Styles(sStyleName).ListTemplate = wdListNumberStyleNone
            ActiveDocument.Styles(sStyleName).LinkToListTemplate ListTemplate:=Nothing
            On Error GoTo 0
            If fnGetFamily(sStyleName) = "Title" And fnGetType(sStyleName) = "chapter" Then
                ActiveDocument.Styles(sStyleName).ParagraphFormat.OutlineLevel = 1
            End If
            If fnGetFamily(sStyleName) = "h" And fnGetType(sStyleName) = "n" Then
                ActiveDocument.Styles(sStyleName).ParagraphFormat.OutlineLevel = fnGetLevel(sStyleName) + 1
            End If
            
            For i = 0 To UBound(mArgArray) Step 2
                 sPropertyName = mArgArray(i)
                 vPropertyValue = mArgArray(i + 1)
                 If sPropertyName = "FollowStyle" And Not fnHasStyle(vPropertyValue) Then
                     subCreateMissingStyle (vPropertyValue)
                 End If
                 Call subWordApplyProperty(oStyle, sPropertyName, vPropertyValue)
            Next
            oStyle.Font.Color = wdBlack
            
        Else
            Dim sStyle As String
            Rem While Word doesn't have a numbering style as such, it does have ListTemplates
            sStyle = sStyleName
            sType = fnGetType(sStyleName)
            nLevel = fnGetLevel(sStyleName)
            Select Case sType
                Case "A":
                    sStyleName = Trim(fnGetFamily(sStyleName)) + Trim(str(nLevel)) + "UpperA"
                Case "a"
                    sStyleName = Trim(fnGetFamily(sStyleName)) + Trim(str(nLevel)) + "LowerA"
                Case "I"
                    sStyleName = Trim(fnGetFamily(sStyleName)) + Trim(str(nLevel)) + "UpperI"
                Case "i"
                    sStyleName = Trim(fnGetFamily(sStyleName)) + Trim(str(nLevel)) + "LowerI"
            End Select
            Set oStyle = ActiveDocument.Styles.Add(name:=sStyleName, Type:=wdStyleTypeParagraph)
            ActiveDocument.Styles(sStyleName).NameLocal = sStyle
            ActiveDocument.Styles(sStyle).AutomaticallyUpdate = False
            
            ActiveDocument.Styles(sStyle).Frame.Delete
            
            
            sListTemplateName = MakeOutlineName(sType)
            Call subChangeListTemplate(sListTemplateName, sStyle)
            oStyle.ParagraphFormat.TabStops.ClearAll
        End If
        
        
        If Not (sParentStyleName = "" Or fnHasStyle(sParentStyleName)) Then
            Call subCreateMissingStyle(sParentStyleName)
            
        End If
        If Not sStyleName = sParentStyleName Then
            If sStyle <> "" Then
                ActiveDocument.Styles(sStyle).BaseStyle = sParentStyleName
            Else
                ActiveDocument.Styles(sStyleName).BaseStyle = sParentStyleName
            End If
        End If
        Call subFixWordStyle(sStyleName)
        
    #Else
        oStyles = ThisComponent.styleFamilies.getByName(sStyleType + "Styles")
        If Not fnHasStyle(sStyleName, sStyleType) Then
            oStyle = ThisComponent.createInstance("com.sun.star.style." + sStyleType + "Style")
            If sStyleType = "Paragraph" Or sStyleType = "Character" Then
                For i = 0 To (UBound(mArgArray)) Step 2
                    sPropertyName = mArgArray(i)
                    vPropertyValue = mArgArray(i + 1)
                    If sPropertyName = "FollowStyle" And Not fnHasStyle(vPropertyValue) Then
                        subCreateMissingStyle (vPropertyValue)
                    End If
                    oStyle.setPropertyValue(sPropertyName, vPropertyValue)
                Next
            End If
            If Not (sParentStyleName = "" Or fnHasStyle(sParentStyleName)) Then
                subCreateMissingStyle (sParentStyleName)
            End If
            Rem  the insertbyname has error but still adding there. need to find out why it is giving error but still working
            On Error GoTo SkipLine
            oStyles.insertByName(sStyleName, oStyle)
SkipLine:
            If sStyleType = "Numbering" Then
                Call subChangeNumberingRules(oStyle, mArgArray)
            End If
            oStyle.setParentStyle (sParentStyleName)

        Else
            Rem for debugging
            oStyle = oStyles.getByName(sStyleName)
        End If
    #End If
End Sub



Sub subChangeListTemplate(sListTemplateName As String, sStyleName As String)
Rem  FOr Word Only
    sType = fnGetType(sStyleName)
    nLevel = fnGetLevel(sStyleName)
    If sListTemplateName = "SectOutline" Then
        nLevel = nLevel + 1
    End If

    Set oListTemplate = fnListTemplate(sListTemplateName)
    For j = 1 To nLevel
        With oListTemplate.ListLevels(j)
            If sListTemplateName = "SectOutline" Then
                numFormat = ""
                If j <> 1 Then
                    startNo = 2
                Else
                    startNo = 1
                End If
                For i = startNo To j
                    numFormat = numFormat + "%" + Trim(str(i)) + "."
                Next i
                numFormat = Left(numFormat, Len(numFormat) - 1) + " "
            ElseIf sType <> "b" Then
                numFormat = "%" + Trim(str(j)) + "."
            End If
            .NumberFormat = numFormat
            Select Case sListTemplateName
                Case "LUppercaseAlpha":
                    .NumberStyle = wdListNumberStyleUppercaseLetter
                Case "LLowercaseAlpha":
                    .NumberStyle = wdListNumberStyleLowercaseLetter
                Case "LUppercaseRoman":
                    .NumberStyle = wdListNumberStyleUppercaseRoman
                Case "LLowercaseRoman":
                    .NumberStyle = wdListNumberStyleLowercaseRoman
                Case "Lb":
                    .NumberFormat = ChrW(61623)
                    .NumberStyle = wdListNumberStyleBullet
                    With .Font
                      .name = "Symbol"
                      .Size = wdUndefined
                    End With
                Case "Ln":
                    .NumberStyle = wdListNumberStyleArabic
                Case "SectOutline":
                    .NumberStyle = wdListNumberStyleArabic

            End Select
            If sListTemplateName = "SectOutline" And nLevel = 1 Then
                .Alignment = wdListLevelAlignCenter
            Else
                .Alignment = wdListLevelAlignLeft
            End If
            oListTemplate.ListLevels(j).NumberPosition = 0
            Rem not working now.: .NumberPosition = 0

            
            .ResetOnHigher = True
            .StartAt = 1
            If sListTemplateName = "SectOutline" Then
                .TrailingCharacter = wdTrailingNone
                
                Rem calculate the numbering heading position.
                oListTemplate.ListLevels(j).NumberPosition = 0
                oListTemplate.ListLevels(j).TextPosition = 0
                oListTemplate.ListLevels(j).TabPosition = 0
            Else
                .TrailingCharacter = wdTrailingTab
                
                listPosition = 0.6 * j
                numPosition = listPosition - 0.6
                oListTemplate.ListLevels(j).NumberPosition = CentimetersToPoints(numPosition)
                Rem .NumberPosition = CentimetersToPoints(numPosition)
                oListTemplate.ListLevels(j).TextPosition = CentimetersToPoints(listPosition)
                oListTemplate.ListLevels(j).TabPosition = CentimetersToPoints(listPosition)
            End If
            
            If nLevel = j Then
                .LinkedStyle = sStyleName
            Else
                Rem no linked style yet
                If sListTemplateName = "SectOutline" Then
                    Rem if it is outline list
                    If j = 1 Then
                        sLinkedStyle = "Title-chapter"
                    Else
                        sLinkedStyle = fnGetFamily(sStyleName) + Trim(str(j - 1)) + sType
                    End If
                Else
                    sLinkedStyle = fnGetFamily(sStyleName) + Trim(str(j)) + sType
                End If
                If Not fnHasStyle(sLinkedStyle) Then
                    subCreateMissingStyle (sLinkedStyle)
                End If
                .LinkedStyle = sLinkedStyle
            End If
        End With
    Next j
End Sub

Sub subChangeNumberingRules(oObject, mArgArray)
Rem not for word
    Dim oNumRules, i As Integer, j As Integer, mSetOfRules, nRuleIndex
    Rem this is very necessary
    oNumRules = oObject.NumberingRules
    For i = 0 To (UBound(mArgArray)) Step 2
        For j = 0 To oNumRules.getCount - 1
            Rem This require inner loop as numbering rules have multiple level.
            Rem This will loop through each level and then modify the rule.
            Set mSetOfRules = oNumRules.getByIndex(j)

            nRuleIndex = fnFindPropertyIndex(mSetOfRules, mArgArray(i))
            If nRuleIndex > 0 Then
               mSetOfRules(nRuleIndex).value = mArgArray(i + 1)
               oNumRules.replaceByIndex(j, mSetOfRules)
            End If
        Next
     Next
     oObject.NumberingRules = oNumRules
End Sub

Sub subChangeChapterNumberingRules(oObject, j, mArgArray)
    Dim oNumRules, i As Integer, mSetOfRules, nRuleIndex

    #If MSWD Then
        Dim sStyle As String
         Rem  in case oObject is not string
        sStyle = oObject
        Call subChangeListTemplate("SectOutline", sStyle)
    #Else
        oNumRules = oObject.getChapterNumberingRules
        For i = 0 To (UBound(mArgArray)) Step 2
                Set mSetOfRules = oNumRules.getByIndex(j)
                nRuleIndex = fnFindPropertyIndex(mSetOfRules, mArgArray(i))

                If nRuleIndex > 0 Then
                    mSetOfRules(nRuleIndex).value = mArgArray(i + 1)
                    oNumRules.replaceByIndex(j, mSetOfRules)
               End If
        Next
        oObject.getChapterNumberingRules = oNumRules
    #End If
End Sub

Function fnFindPropertyIndex(aArrayOfProperties, cPropName As String) As Long
Rem not for word
    For i = LBound(aArrayOfProperties) To UBound(aArrayOfProperties)
        oProp = aArrayOfProperties(i)
        If oProp.name = cPropName Then
            fnFindPropertyIndex() = i
            Exit Function
        End If
    Next
End Function

Function fnCreatePropDictionary()
Rem for word only
    Set fnCreatePropDictionary = fnCreateDictionary(Array( _
        "CharEscapement", "Position", _
        "CharFontFamily", "", _
        "CharFontName", "Name", _
        "CharHeight", "Size", _
        "CharPosture", "Italic", _
        "CharWeight", "Bold", _
        "NumberingStyleName", "LinkToListTemplate", _
        "ParaAdjust", "Alignment", _
        "ParaBackColor", "BackgroundPatternColor", _
        "ParaBackTransparent", "", _
        "ParaBottomMargin", "SpaceAfter", _
        "ParaFirstLineIndent", "FirstLineIndent", _
        "ParaLeftMarginRelative", "LeftIndent", _
        "ParaLeftMargin", "LeftIndent", _
        "ParaRightMargin", "RightIndent", _
        "ParaTopMargin", "SpaceBefore", _
        "FollowStyle", "NextParagraphStyle" _
        ))
End Function

Function fnCreatePropValueDictionary()
Rem for word only
    Set fnCreatePropValueDictionary = fnCreateDictionary(Array( _
        "CharWeight_150", True, _
        "CharWeight_100", False, _
        "CharPosture_2", True, _
        "CharPosture_0", False, _
        "ParaAdjust_1", 2, _
        "ParaAdjust_3", 1, _
        "NumberingType_0", 3, _
        "NumberingType_1", 4, _
        "NumberingType_2", 1, _
        "NumberingType_3", 2, _
        "NumberingType_4", 0, _
        "NumberingType_6", 10 _
        ))
End Function

Function fnCreateConversionDictionary()
Rem for word only
    Set fnCreateConversionDictionary = fnCreateDictionary(Array( _
        "CharPosture", "Dic", _
        "CharWeight", "Dic", _
        "NumberingStyleName", "rn", _
        "ParaAdjust", "Dic", _
        "ParaBottomMargin", "2p", _
        "ParaFirstLineIndent", "2p", _
        "ParaLeftMargin", "2p", _
        "ParaRightMargin", "2p", _
        "ParaTopMargin", "2p" _
        ))
End Function

Function fnCreateDictionary(m)
Rem for word only
Dim d, i As Integer
Rem Word's help file is wrong the quotes are required in the following line
Set d = CreateObject("Scripting.Dictionary")
For i = 0 To UBound(m) Step 2
    d.Add m(i), m(i + 1)
Next
Set fnCreateDictionary = d
End Function

Sub subWordApplyProperty(oObject, sPropName, vPropValue)
Rem for word only
    Static PropDictionary, PropValueDictionary, PropConvMethodDictionary
    Dim sPropType As String, sWordProp As String, vWordPropValue, oSubObject
    Dim sConvMethod As String, oTemplate, nLevel As Integer

    If IsEmpty(PropDictionary) Then
        Set PropDictionary = fnCreatePropDictionary()
        Set PropValueDictionary = fnCreatePropValueDictionary()
        Set PropConvMethodDictionary = fnCreateConversionDictionary()
    End If
    sWordProp = PropDictionary.Item(sPropName)
    sConvMethod = PropConvMethodDictionary.Item(sPropName)
    Select Case sConvMethod
        Case ""
            vWordPropValue = vPropValue
            If sPropName = "CharEscapement" Then
                vWordPropValue = vWordPropValue / 10
            End If
        Case "Dic"
            vWordPropValue = PropValueDictionary.Item(sPropName & "_" & vPropValue)
        Case "2p"
            vWordPropValue = CentimetersToPoints(vPropValue / 1000)
        Case "rn"
               vWordPropValue = fnGetType(vPropValue)

   End Select

    sPropType = Left(sPropName, 4)
    Select Case sPropType
    Case "Char"
        Set oSubObject = oObject.Font
    Case "Para"
        Set oSubObject = oObject.ParagraphFormat
        If sPropName = "ParaBackColor" Then
            Set oSubObject = oSubObject.Shading
        End If
    Case Else
        Set oSubObject = oObject
    End Select
    If sWordProp = "" Then Exit Sub

    If sWordProp = "LinkToListTemplate" Then
        Dim sListTemplateName As String
        sListTemplateName = MakeOutlineName(vWordPropValue)
        If sListTemplateName = "L" Then
            Rem if it is Outline, Make outline Name return only "L"
            sListTemplateName = "SectOutline"
        End If
        nLevel = fnGetLevel(oObject.NameLocal)
        If nLevel = 0 Then nLevel = 1
        Set oListTemplate = fnListTemplate(sListTemplateName)
        oSubObject.LinkToListTemplate ListTemplate:=oListTemplate, ListLevelNumber:=nLevel
    Else
        CallByName oSubObject, sWordProp, VbLet, vWordPropValue
    End If
End Sub



