Attribute VB_Name = "Repair"
#Const MSWD = True
#Const OOO = Not MSWD
Rem *********************************************************************
Rem    University of Southern Queensland
Rem    Author : Cynthia
Rem *********************************************************************

Sub Repair()
Rem this is for Word Hover problem
    #If MSWD Then
        isFile = fnIsThereAFile()
        If Not isFile Then
            Exit Sub
        End If
    #End If
    Call subCheckDocument
End Sub

Sub RepairTitleStyle()
Rem Dummy call for fixing the title style
    Call FixTitle
End Sub

Sub subFixLinks()
    #If OOO Then
        Rem For NOw it is to fix underline in Links.
        oStyles = ThisComponent.styleFamilies.getByName("CharacterStyles")
         If oStyles.hasByName("Internet Link") Then
            oStyles.getByName("Internet Link").charUnderline = 0
         End If
         If oStyles.hasByName("Visited Internet Link") Then
            oStyles.getByName("Visited Internet Link").charUnderline = 0
         End If
    #End If
End Sub


Sub subFixBulletList()
    For i = 1 To 5
        sStyle = fnMakeStyleName("li", i, "b")
        If fnHasStyle(sStyle) Then
            ResetNumberingRules (sStyle)
        End If
    Next
End Sub

Sub subRemoveUsedNumberingStyles()
#If OOO Then
    oTextElementEnum = ThisComponent.Text.GetText().createEnumeration
    While oTextElementEnum.hasMoreElements()
        oTextElement = oTextElementEnum.nextElement()
        If oTextElement.supportsService("com.sun.star.text.Paragraph") Then
            oCursor = oTextElement.Text.createTextCursorByRange(oTextElement)
            Rem removing all the numberingstyle in the paragraph.
            oCursor.NumberingStyleName = ""
        End If
    Wend
#End If
End Sub


Sub ResetNumberingRules(sStyle As String)
    ThisComponent.styleFamilies.getByName("NumberingStyles").removeByName (sStyle)
    subCreateMissingStyle (sStyle)
End Sub

Sub subFixHeadingNumberingStyle()
    Rem remove the list
    styleNames = Array("Title-chapter", "h1n", "h2n", "h3n", "h4n", "h5n")
    Rem fix the paragraph styles
    oStyles = ThisComponent.styleFamilies.getByName("ParagraphStyles")
    For Each StyleName In styleNames
        If oStyles.hasByName(StyleName) Then
            oStyle = oStyles.getByName(StyleName)
            If oStyle.NumberingStyleName <> "Outline" Then
                nLevel = fnGetLevel(StyleName) + 1
                oStyle.setPropertyValue("OutlineLevel",nLevel)
                oStyle.setPropertyValue("NumberingStyleName","Outline")
            End If
        Else
            subCreateMissingStyle (StyleName)
        End If
    Next StyleName
    Rem fix the outline numbering rules.
    oNumRules = ThisComponent.getChapterNumberingRules
    For i = 0 To 5
        Set mSetOfRules = oNumRules.getByIndex(i)
        j = fnFindPropertyIndex(mSetOfRules, "HeadingStyleName")
        mSetOfRules(j).value = styleNames(i)
        oNumRules.replaceByIndex(i, mSetOfRules)
    Next i
    ThisComponent.getChapterNumberingRules = oNumRules
End Sub

Sub subCheckDocument()
Rem on Error Goto ErrMsg
    Rem Call FixTitle
   Call subFixLinks
   #If OOO Then
        Rem need to be remove from the paragraphs otherwise it does not work
        Call subRemoveUsedNumberingStyles
        Call subFixBulletList
        Call subFixHeadingNumberingStyle
   #End If
   Call subCheckTextRange
   Exit Sub
errMsg:
    printMsgbox ("Error in getting the document contents. Try deselecting.")
End Sub

Sub subCheckTextRange()
#If OOO Then
    oTextElementEnum = ThisComponent.Text.GetText().createEnumeration
    While oTextElementEnum.hasMoreElements()
        oTextElement = oTextElementEnum.nextElement()
        If oTextElement.supportsService("com.sun.star.text.Paragraph") Then
            subCheckParagraph (oTextElement)
            Rem To fix the hyperlink in graphics when editing .doc in ooo
            Call RepairParaGraphics(oTextElement)
            Call RepairCharGraphics(oTextElement)
        End If
    Wend
    Rem need to run two time to copy the url
    oTextElementEnum = ThisComponent.Text.GetText().createEnumeration
    While oTextElementEnum.hasMoreElements()
        oTextElement = oTextElementEnum.nextElement()
        If oTextElement.supportsService("com.sun.star.text.Paragraph") Then
            Call RepairParaGraphics(oTextElement)
            Call RepairCharGraphics(oTextElement)
        End If
    Wend
#Else
    Rem create bookmark to remember the current position
    Selection.Bookmarks.Add ("CurrentCursorPosition")
    
    For i = 1 To ActiveDocument.Paragraphs.count
        ActiveDocument.Paragraphs(i).Range.Select

        If Not Selection.Information(wdWithInTable) And Not isField() Then
            Rem if the paragraph is not in the table, reset the style.
            sStyle = Selection.style
            varPageBreakBefore = Selection.ParagraphFormat.PageBreakBefore
            varKeepTogether = Selection.ParagraphFormat.KeepTogether
            varKeepWithNext = Selection.ParagraphFormat.KeepWithNext
            If fnGetFamily(sStyle) = "h" Then
                sType = fnGetType(sStyle)
                If sType <> "" And sType <> "n" Then
                    nLevel = fnGetLevel(sStyle)
                    If nLevel <> 0 Then
                        sStyle = fnGetFamily(sStyle) + nLevel
                    Else
                        sStyle = fnGetFamily(sStyle) + Trim(str(1))
                    End If
                End If
            End If
            Call subSetParaStyleName(Selection.Range, sStyle)
            Rem reset pagination
            Selection.ParagraphFormat.PageBreakBefore = varPageBreakBefore
            Selection.ParagraphFormat.KeepTogether = varKeepTogether
            Selection.ParagraphFormat.KeepWithNext = varKeepWithNext
        End If
    Next

    Rem reset the current position and then delete the bookmark
    Selection.GoTo what:=wdGoToBookmark, name:="CurrentCursorPosition"
    ActiveDocument.Bookmarks("CurrentCursorPosition").Delete
#End If
End Sub

Sub subCheckParagraph(oTextElement)
Dim isBold As Boolean, isItalic As Boolean
oPortionEnum = oTextElement.createEnumeration
While oPortionEnum.hasMoreElements()
    oPortion = oPortionEnum.nextElement()
    oCursor = oPortion.Text.createTextCursorByRange(oPortion)
    sStyle = oCursor.paraStyleName
    If fnGetFamily(sStyle) = "h" Then
        If fnGetType(sStyle) <> "" And fnGetType(sStyle) <> "n" And fnGetType(sStyle) <> "chapter" Then
            If fnGetLevel(sStyle) <> 0 Then
                sStyle = fnGetFamily(sStyle) + fnGetLevel(sStyle)
            Else
                sStyle = fnGetFamily(sStyle) + 1
            End If
        End If
    End If
    subSetParaStyleName(oCursor,sStyle)
Wend
End Sub


Function isField()
    Rem For Word only. Word cannot differentiate field or just normal paragraph.
    On Error GoTo notField
    isField = True
    fldtype = Selection.Fields(1).Type
    Exit Function
notField:
    isField = False
End Function
