Attribute VB_Name = "toolbar"
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

Global oCaptureDocView
Global oCaptureKeyHandler

Sub PressEscThenForwardSlashForHelp()
    Rem Do Nothing
End Sub


Sub Promote()
    #If MSWD Then
        isFile = fnIsThereAFile()
        If Not isFile Then
            Exit Sub
        End If
    #End If
    eventPromoteButton
End Sub


Sub Demote()
    #If MSWD Then
        isFile = fnIsThereAFile()
        If Not isFile Then
            Exit Sub
        End If
    #End If
    eventDemoteButton
End Sub

Sub Code()
    #If MSWD Then
        isFile = fnIsThereAFile()
        If Not isFile Then
            Exit Sub
        End If
    #End If
    toggleCode
End Sub

Sub Bullets()
    #If MSWD Then
        isFile = fnIsThereAFile()
        If Not isFile Then
            Exit Sub
        End If
    #End If
    eventBulletButton
End Sub


Sub Numbering()
    #If MSWD Then
        isFile = fnIsThereAFile()
        If Not isFile Then
            Exit Sub
        End If
    #End If
    eventNumberiseButton
End Sub


Sub ChangeListStyle()
    #If MSWD Then
        isFile = fnIsThereAFile()
        If Not isFile Then
            Exit Sub
        End If
    #End If
    eventChangeListTypeDlg
End Sub


Sub LeftAlignedParagraph()
    #If MSWD Then
        isFile = fnIsThereAFile()
        If Not isFile Then
            Exit Sub
        End If
    #End If
    eventLeftButton
End Sub

Sub IndentParagraph()
    #If MSWD Then
        isFile = fnIsThereAFile()
        If Not isFile Then
            Exit Sub
        End If
    #End If
    eventIndentButton
End Sub

Sub CenterAlignedParagraph()
    #If MSWD Then
        isFile = fnIsThereAFile()
        If Not isFile Then
            Exit Sub
        End If
    #End If
    eventCenterButton
End Sub


Sub RightAlignedParagraph()
    #If MSWD Then
        isFile = fnIsThereAFile()
        If Not isFile Then
            Exit Sub
        End If
    #End If
    eventRightButton
End Sub


Sub Title()
    #If MSWD Then
        isFile = fnIsThereAFile()
        If Not isFile Then
            Exit Sub
        End If
    #End If
    eventTitleButton
End Sub


Sub Heading()
    #If MSWD Then
        isFile = fnIsThereAFile()
        If Not isFile Then
            Exit Sub
        End If
    #End If
    eventHeadingButton
End Sub


Sub BlockQuote()
    #If MSWD Then
        isFile = fnIsThereAFile()
        If Not isFile Then
            Exit Sub
        End If
    #End If
    eventBlockQuoteButton
End Sub


Sub Definition()
    #If MSWD Then
        isFile = fnIsThereAFile()
        If Not isFile Then
            Exit Sub
        End If
    #End If
    eventDefinitionButton
End Sub

Sub Superscript()
    #If MSWD Then
        isFile = fnIsThereAFile()
        If Not isFile Then
            Exit Sub
        End If
    #End If
    toggleSup
End Sub

Sub Subscript()
    #If MSWD Then
        isFile = fnIsThereAFile()
        If Not isFile Then
            Exit Sub
        End If
    #End If
    toggleSub
End Sub


Sub Preformatted()
    #If MSWD Then
        isFile = fnIsThereAFile()
        If Not isFile Then
            Exit Sub
        End If
    #End If
    eventPreformmatedButton
End Sub


Sub DefaultFormatting()
    #If MSWD Then
        isFile = fnIsThereAFile()
        If Not isFile Then
            Exit Sub
        End If
    #End If
    eventDefaultFormattingButton
End Sub


Sub Help()
    eventShowShortcuts
End Sub


Sub eventKeyControl()
    Rem Inspired and informed by examples in http://www.pitonyak.org/AndrewMacro.odt
    #If OOO Then
        Rem Take control and listen for the next key stroke
        oCaptureDocView = ThisComponent.getCurrentController
        oCaptureKeyHandler = createUnoListener("Capture_", _
        "com.sun.star.awt.XKeyHandler")
        oCaptureDocView.addKeyHandler (oCaptureKeyHandler)

    #End If
End Sub




Function Capture_keyReleased(oEvt) As Boolean
    #If OOO Then
        Capture_keyReleased = False
    #End If
End Function


Function Capture_keyPressed(oEvt) As Boolean
    #If MSWD Then
        isFile = fnIsThereAFile()
        If Not isFile Then
            Exit Function
        End If
    #End If
    Rem capture the key pressed event.
    #If OOO Then
        skey = Right(oEvt.KeyChar, 1)
    #End If
    #If MSWD Then
        skey = oEvt
    #End If
    Select Case Asc(skey)
    Rem use ascii code as tab key has the problem
    Case 104, 72
    Rem Case "h", "H"
        Call eventHeadingButton
    Case 46, 62
    Rem Case ".", ">"
        Call eventDemoteButton
    Case 44, 60
    Rem Case ",", "<"
        Call eventPromoteButton
    Case 56, 42
    Rem Case "8", "*"
        Call eventBulletButton
    Case 35, 110, 78
    Rem Case "#", "n", "N"
        Call eventNumberiseButton
    Case 49
    Rem Case "1"
        Call subChangeListType("n")
    Case 50
    Rem Case "2"
        Call subChangeListType("i")
    Case 51
    Rem Case "3"
        Call subChangeListType("a")
    Case 52
    Rem Case "4"
        Call subChangeListType("I")
    Case 53
    Rem Case "5"
        Call subChangeListType("A")
    Case 108, 76
    Rem Case "l", "L"
        Call eventChangeListTypeDlg
    Case 102, 70
    Rem Case "f", "F"
        Call eventPreformmatedButton
    Case 112, 80
    Rem case "p", "P"
        Call eventLeftButton
    Case 9
        Rem Case vbTab
        Call eventIndentButton
    Case 91, 123
    Rem case "[", "{"
        Call eventCenterButton
    Case 93, 125
    Rem Case "]", "}"
        Call eventRightButton
    Case 100, 68
    Rem Case "d", "D"
        Call eventDefinitionButton
    Case 113, 81
    Rem Case "q", "Q"
        Call eventBlockQuoteButton
    Case 116, 84
    Rem Case  "t", "T"
        Call eventTitleButton
    Case 98, 66
    Rem Case "b", "B"
        Call toggleBold
    Case 105, 73
    Rem Case  "i", "I"
        Call toggleItalic
    Case 99, 67
    Rem Case  "c", "C"
        Call toggleCode
    Case 43, 61
    Rem Case  "+", "="
        Call toggleSup
    Case 45, 95
    Rem Case "-", "_"
        Call toggleSub
    Case 114, 82
    Rem Case "r", "R"
        Call eventRestartNumberingButton
    Case 101, 69
    Rem case  "e", "E"
        Call eventDefaultFormattingButton
    Case 120, 88
    Rem Case "x", "X"
        Call CrossReference
    Case 47, 63
    Rem Case "/", "?"
        Call eventShowShortcuts
    End Select
    Capture_keyPressed = True
    #If OOO Then
        On Error Resume Next
        oCaptureDocView.removeKeyHandler (oCaptureKeyHandler)
    #End If
End Function



Sub expt()
    Form.Show
End Sub


Sub eventShowShortcuts()
    #If MSWD Then
        Set oDialog = frmShortcuts
        Application.OnTime TimeValue("00:00:10"), 5
        oDialog.Show
    #Else
        DialogLibraries.LoadLibrary ("IceLibrary")
        oDialog = CreateUnoDialog(DialogLibraries.IceLibrary.dlgShortcuts)
        oDialog.Execute
        oDialog.dispose
    #End If
End Sub


Sub subTimeEventHideForm()
    frmShortcuts.hide
    Unload frmShortcuts
End Sub


Function fnGetViewCursor()
    #If OOO Then
        oVC = ThisComponent.getCurrentController.getViewCursor()
        fnGetViewCursor = oVC
    #Else
        Set fnGetViewCursor = Selection.Range
    #End If
End Function


Function fnGetParaStyleName(Optional oCursor)
    If IsEmpty(oCursor) Or IsMissing(oCursor) Then
        Set oCursor = fnGetViewCursor()
        
    End If
    #If OOO Then
        fnGetParaStyleName = oCursor.paraStyleName
    #Else
        On Error GoTo MultipleRange
        fnGetParaStyleName = oCursor.ParagraphFormat.style
        Exit Function
MultipleRange:
        On Error GoTo errMsg
        Rem MsgBox Selection.Range.Paragraphs.count
        If oCursor.Paragraphs.count >= 1 Then
            fnGetParaStyleName = oCursor.Paragraphs(1).Range.ParagraphFormat.style
        Else
            fnGetParaStyleName = Selection.ParagraphFormat.style
        End If
    #End If
    Exit Function
errMsg:
    printMsgbox ("Error in getting paragraph style: Try deselecting")
        
End Function


Sub subSetParaStyleName(oCursor, sStyle)
Rem     On Error GoTo errHandler1:
    Dim isBold As Boolean, isItalic As Boolean
    Rem force them to have false in case the variable exist.
    isBold = False
    isItalic = False

    If Not fnHasStyle(sStyle) Then
        subCreateMissingStyle (sStyle)
    End If

    #If OOO Then
        Dim isStart, isEnd As Boolean
        Dim oTC
        isStart = False
        isEnd = False
        Rem move the cursor if it is in either end.

        If Not testmode Then
            If oCursor.supportsService("com.sun.star.text.Paragraph") Then
                oTC = ThisComponent.Text().createTextCursorByRange(ThisComponent.getCurrentSelection().getByIndex(0))
            ElseIf oCursor.supportsService("com.sun.star.text.TextTable") Then
                oTC = ThisComponent.Text().createTextCursorByRange(oCursor.Text().getByIndex(0))
            Else
                GoTo skip
            End If
            If oTC.isStartOFParagraph And oTC.isEndOfParagraph Then
                Rem if empty paragraph
                Rem do nothing
            ElseIf oTC.isStartOFParagraph() Then
                isStart = True
                oCursor.goRight(1,False)
            ElseIf oTC.isEndOfParagraph() Then
                isEnd = True
                oCursor.goLeft(1,False)
            End If
        End If
skip:
        sFamily = fnGetFamily(oCursor.paraStyleName)
        isBold = fnIsBold(oCursor) And sFamily <> "dt" And sFamily <> "h" And sFamily <> "Title"
        isItalic = fnIsItalic(oCursor) And sFamily <> "bq"
        
        If fnGetFamily(sStyle) = "li" And fnGetType(sStyle) <> "p" Then
            oCursor.NumberingStyleName = sStyle
        ElseIf fnGetFamily(sStyle) <> "h" Then
            oCursor.NumberingStyleName = ""
        ElseIf fnGetType(sStyle) <> "n" Then
            Rem in case it is not hn style.
            oCursor.NumberingStyleName = ""
        End If
        
        
        Rem Set the paragraph style
        oCursor.paraStyleName = sStyle

       

        Rem reset bold or italic
        If isBold Then
            oCursor.CharWeight = 150
        End If
        If isItalic Then
            oCursor.CharPosture = 2
        End If
        Rem Move the cursor back to where it was
        If isEnd Then
            oCursor.goRight(1,False)
         End If
        If isStart Then
            oCursor.goLeft(1,False)
        End If
    #Else
        Rem remember the cursor location
        Selection.Bookmarks.Add ("CurrentPos")
        If oCursor.Text = "" Then
            Rem if paragraph is not selected, then select it.
            Rem word does not apply bold if not selected.
            nIndex = fnGetCurrentParagraphNumber
            ActiveDocument.Paragraphs(nIndex).Range.Select
        End If
        On Error Resume Next
        sCurrentStyle = oCursor.style
        If sCurrentStyle = "" Or IsEmpty(sCurrentStyle) Then
            Rem just to avoid oCursor.style returning Nothing.
            sCurrentStyle = "p"
        End If
        sFamily = fnGetFamily(sCurrentStyle)
        'to do check if a list style is created in ooo. can it work in word?
        isBold = fnIsBold(Selection.Range) And sFamily <> "dt" And sFamily <> "h" And sFamily <> "Title"
        isItalic = fnIsItalic(Selection.Range) And sFamily <> "bq"
        
        oCursor.style = sStyle
        
        Rem reset the bold and italic.
        If isBold Then
            Rem has to be selection.range.
            Rem oCursor doesn't work in this case. don't know why.
            Selection.Range.Font.Bold = isBold
        End If
        If isItalic Then
            Rem has to be selection.range.
            Rem oCursor doesn't work in this case. don't know why.
            Selection.Range.Font.Italic = isItalic
        End If


         Rem reset the current position and then delete the bookmark
        Selection.GoTo what:=wdGoToBookmark, name:="CurrentPos"
        ActiveDocument.Bookmarks("CurrentPos").Delete
    #End If
    If fnGetFamily(sStyle) = "li" And Not (fnGetType(sStyle) = "b" Or fnGetType(sStyle) = "p") Then
        Set oVC = fnGetViewCursor()
            #If MSWD Then
                If fnNeedsRestart(sStyle, fnFindPrevStyleName(oVC)) Then
                    subRestartNumbering (True)
                End If
            #Else
                subRestartNumbering (fnNeedsRestart(sStyle, fnFindPrevStyleName(oVC)))
            #End If
    End If
    GoTo finish:

errHandler1:
    #If MSWD Then
        If fnGetFamily(sStyle) = "li" Then
            printMsgbox ("Style '" + sStyle + "' creation is completed with error. Try apply the style again.")
        Else
            printMsgbox ("Style '" + sStyle + "' could not be created. Try using the template.")
        End If
    #Else
        printMsgbox ("Style '" + sStyle + "' could not be applied. Try deselecting any objects.")
    #End If
finish:
End Sub


Function fnNeedsRestart(sStyle, sPrevStyle)
    fnNeedsRestart = fnGetFamily(sStyle) = "li" And _
                     Not (fnGetType(sStyle) = "p" Or fnGetType(sStyle) = "b") And _
                     fnGetLevel(sStyle) > fnGetLevel(sPrevStyle)
End Function

Sub toggleItalic()
    #If OOO Then
        oCurSelection = ThisComponent.getCurrentSelection()
        If oCurSelection.supportsService("com.sun.star.text.TextRanges") Then
            If oCurSelection.count = 1 Then
                oTextRange = oCurSelection.getByIndex(0)
            Else
                oTextRange = oCurSelection.getByIndex(1)
            End If
            dispatcher = createUnoService("com.sun.star.frame.DispatchHelper")
            Dim args1(0) As New com.sun.star.beans.PropertyValue
            args1(0).name = "Italic"
            args1(0).value = oTextRange.CharPosture <> 2
            dispatcher.executeDispatch(ThisComponent.CurrentController.Frame, ".uno:Italic", "", 0, args1())
        ElseIf oCurSelection.supportsService("com.sun.star.text.TextTableCursor") Then
            processTextTableCursor(oCurSelection, "i-i",Array())
        Else
            printMsgbox ("Error in getting selection range. Try deselecting.")

        End If

    #Else
        Selection.Font.Italic = wdToggle
    #End If
End Sub

Sub toggleBold()
    #If OOO Then
        oCurSelection = ThisComponent.getCurrentSelection()
        If oCurSelection.supportsService("com.sun.star.text.TextRanges") Then
            If oCurSelection.count = 1 Then
                oTextRange = oCurSelection.getByIndex(0)
            Else
                oTextRange = oCurSelection.getByIndex(1)
            End If
            dispatcher = createUnoService("com.sun.star.frame.DispatchHelper")
            Dim args1(0) As New com.sun.star.beans.PropertyValue
            args1(0).name = "Bold"
            args1(0).value = oTextRange.CharWeight <> 150
            dispatcher.executeDispatch(ThisComponent.CurrentController.Frame, ".uno:Bold", "", 0, args1())
        ElseIf oCurSelection.supportsService("com.sun.star.text.TextTableCursor") Then
            processTextTableCursor(oCurSelection, "i-b",Array())
        Else
            printMsgbox ("Error in getting selection range. Try deselecting.")
        End If
    #Else
        Selection.Font.Bold = wdToggle
    #End If
End Sub


Sub toggleCode()
    #If OOO Then
        subToggleCharacterStyles("i-code", array("CharFontCharSet","CharFontFamily","CharFontName","CharFontPitch"))
    #Else
        subToggleCustomCharStyle ("i-code")
    #End If
End Sub


Sub toggleSub()
    #If OOO Then
        subToggleCharacterStyles("i-sub", array("CharAutoEscapement","CharEscapement","CharEscapementHeight"))
    #Else
        subToggleCustomCharStyle ("i-sub")
    #End If
End Sub


Sub toggleSup()
    #If OOO Then
        subToggleCharacterStyles("i-sup", array("CharAutoEscapement","CharEscapement","CharEscapementHeight"))
    #Else
        subToggleCustomCharStyle ("i-sup")
    #End If
End Sub


Sub toggleLatex()
    #If OOO Then
        subToggleCharacterStyles("i-latex", array("CharFontCharSet","CharFontFamily","CharFontName","CharFontPitch"))
    #Else
        subToggleCustomCharStyle ("i-latex")
    #End If
End Sub


Sub subToggleCustomCharStyle(sCharStyle)
    If Not fnHasStyle(sCharStyle) Then
        subCreateMissingStyle (sCharStyle)
    End If
    For i = 1 To Selection.Paragraphs.count()
        s = Selection.Paragraphs(i)
        If s = sCharStyle Then
            s.style = ActiveDocument.Styles("Default Paragraph Font")
        Else
            s.style = ActiveDocument.Styles(sCharStyle)
        End If
    Next i
End Sub
Sub eventDemoteButton()
    Set oVC = fnGetViewCursor()
    sStyle = fnGetParaStyleName(oVC)
    sPrevStyle = fnFindPrevStyleName(oVC)
    If fnGetFamily(sStyle) = "h" Then
        sNewStyle = fnDemote(sStyle, fnFindPrevHeadingStyleName(oVC))
    Else
        sNewStyle = fnDemote(sStyle, fnFindPrevStyleName(oVC))
    End If
    If sNewStyle = sStyle Then
        printMsgbox ("Cannot demote any further.")
    Else
        If fnGetFamily(sNewStyle) = "li" And Not (fnGetType(sNewStyle) = "b" Or fnGetType(sNewStyle) = "p") Then
            subSetParaStyleName oVC, fnMakeStyleName("li", fnGetLevel(sNewStyle), "p")
            sNewStyle = fnNumberise(fnMakeStyleName("li", fnGetLevel(sNewStyle), "p"), fnFindPrevListStyleName(oVC))
        End If
        subSetParaStyleName oVC, sNewStyle
    End If
End Sub



Function fnDemote(sStyle, sPrevStyle)
    sFamily = fnGetFamily(sStyle)
    sPrevFamily = fnGetFamily(sPrevStyle)
    nLev = fnGetLevel(sStyle)
    If sFamily <> "h" And sPrevFamily = "h" Then
        nPrevLev = 0
    Else
        nPrevLev = fnGetLevel(sPrevStyle)
    End If
    sTyp = fnGetType(sStyle)
    sPrevTyp = fnGetType(sPrevStyle)


    If nLev >= 5 Then
        Rem no more than Level 5 allowed on any sStyle
        fnDemote = sStyle
        
    ElseIf sFamily = "h" Then
        If nLev <= nPrevLev Then
            fnDemote = fnMakeStyleName(sFamily, nLev + 1, sTyp)
        Else
            fnDemote = fnMakeStyleName(sFamily, nLev, sTyp)
        End If
    ElseIf sFamily = "Title" And sTyp = "chapter" Then
        fnDemote = fnMakeStyleName("h", 1, "n")
    ElseIf sFamily = "Title" Then
        fnDemote = "h1"
    ElseIf nLev > nPrevLev Then
        Rem Not allowed to fnDemote if you're already fnDemoted one or more than the previous
        fnDemote = sStyle
    ElseIf nLev < nPrevLev Then
        If sPrevFamily = "dt" Or sPrevFamily = "dd" Then
            fnDemote = fnMakeStyleName("dd", nPrevLev, sPrevTyp)
        ElseIf sPrevFamily = "li" Then
            If sFamily <> sPrevFamily Then
                fnDemote = fnMakeStyleName("li", nPrevLev, "p")
            Else
                fnDemote = fnMakeStyleName("li", nPrevLev, sPrevTyp)
            End If
        ElseIf sPrevFamily = "bq" And sPrevTyp <> "source" Then
            fnDemote = fnMakeStyleName(sPrevFamily, nPrevLev, "")
        ElseIf sPrevFamily = "bq" And sPrevTyp = "source" And sFamily = "p" Then
            If sStyle = "p" Then
                fnDemote = "p-indent"
            Else
                fnDemote = sStyle
            End If
        ElseIf sPrevFamily = "pre" Then
            fnDemote = fnMakeStyleName(sPrevFamily, nPrevLev, sPrevTyp)
        Else
            fnDemote = fnMakeStyleName("li", nLev + 1, "b")
        End If
    ElseIf sFamily = "li" Then
        If sPrevFamily <> "li" And sPrevFamily <> "dt" And sPrevFamily <> "dd" And sPrevFamily <> "pre" Then
            fnDemote = fnMakeStyleName(sFamily, nLev, sTyp)
        ElseIf sTyp <> "b" Then
            fnDemote = fnMakeStyleName(sFamily, nLev + 1, sPrevTyp)
        Else
            fnDemote = fnMakeStyleName(sFamily, nLev + 1, "b")
        End If
    ElseIf sStyle = "p" And sPrevFamily <> "dt" And sPrevFamily <> "li" And sPrevFamily <> "bq" And sPrevFamily <> "Pre" Then
        fnDemote = "p-indent"
    ElseIf sStyle = "p-indent" Or sStyle = "p-center" Or sStyle = "p-right" Then
        fnDemote = sStyle
    Else
        fnDemote = fnMakeStyleName(sFamily, nLev + 1, sTyp)
    End If
End Function

Sub eventPromoteButton()
    Set oVC = fnGetViewCursor()
    sStyle = fnGetParaStyleName(oVC)
    sPrevStyle = fnFindPrevParentStyleName(oVC)
    sPrevFamily = fnGetFamily(sPrevStyle)
    sTyp = fnGetType(sStyle)
    sPrevTyp = fnGetType(sPrevStyle)
    nLev = fnGetLevel(sPrevStyle)
    sNewStyle = fnPromote(sStyle, fnFindPrevParentStyleName(oVC))
    If sNewStyle = sStyle Then
        printMsgbox ("Cannot promote any further")
    ElseIf sPrevFamily = "li" And sTyp <> "p" Then
        subSetParaStyleName oVC, fnMakeStyleName("li", nLev, sPrevTyp)
    ElseIf sPrevFamily = "li" And sTyp = "p" Then
        subSetParaStyleName oVC, fnMakeStyleName("li", nLev, sTyp)
    ElseIf sPrevFamily = "bq" Then
        subSetParaStyleName oVC, fnMakeStyleName("bq", nLev, "")
    Else
        subSetParaStyleName oVC, sNewStyle
    End If
End Sub

Function fnPromote(sStyle, sPrevStyle)
    If sStyle = sPrevStyle Then
        fnPromote = sStyle
    End If
    sFamily = fnGetFamily(sStyle)
    sPrevFamily = fnGetFamily(sPrevStyle)
    nLev = fnGetLevel(sStyle)
    If sFamily <> "h" And sPrevFamily = "h" Then
        nPrevLev = 1
    Else
        nPrevLev = fnGetLevel(sPrevStyle)
    End If
    sTyp = fnGetType(sStyle)
    sPrevTyp = fnGetType(sPrevStyle)
    
    If sFamily = "h" And nLev = 1 And sTyp = "" Then
        fnPromote = fnMakeStyleName("Title", 0, "")
    ElseIf sFamily = "h" And nLev = 1 And sTyp = "n" Then
        fnPromote = fnMakeStyleName("Title", 0, "chapter")
    ElseIf (sFamily = "li" And nLev = 1) Or sTyp = "p" Then
        fnPromote = fnMakeStyleName("p", 0, "")
    ElseIf sFamily = "bq" And (sPrevFamily <> "bq" Or nLev = 1) Then
        fnPromote = fnMakeStyleName("p", 0, "")
    ElseIf sPrevFamily = "dd" Then
        fnPromote = fnMakeStyleName("dt", nPrevLev, sPrevTyp)
    Else
        If nLev > 1 Then
            nLevAdjust = 1
            If (nLev - nPrevLev) > 1 And sFamily = sPrevFamily Then
                nLevAdjust = nLev - nPrevLev - 1
            End If
            fnPromote = fnMakeStyleName(sFamily, nLev - nLevAdjust, sTyp)
        Else
            If nPrevLev = 0 Then
                fnPromote = sPrevStyle
            Else
                fnPromote = fnMakeStyleName(sFamily, nLev, sTyp)
            End If
        End If
    End If
End Function


Sub eventTitleButton()
    Set oVC = fnGetViewCursor()
    sStyle = fnGetParaStyleName(oVC)
    sStyle = fnTitle(sStyle, fnFindPrevStyleName(oVC))
    subSetParaStyleName oVC, sStyle
End Sub


Function fnTitle(sStyle, sPrevStyle)
    sFamily = fnGetFamily(sStyle)
    sPrevFamily = fnGetFamily(sPrevStyle)
    nLev = fnGetLevel(sStyle)
    nPrevLev = fnGetLevel(sPrevStyle)
    sTyp = fnGetType(sStyle)
    sPrevTyp = fnGetType(sPrevStyle)

    If sFamily <> "Title" Then
        If sPrevFamily <> "Title" Then
            fnTitle = fnMakeStyleName("Title", 0, "")
        End If
        If sTyp = "n" Then
            sPrevTyp = "chapter"
        End If
        If sPrevTyp <> "chapter" And sPrevTyp <> "book" Then
            Rem to prevent title other than chapter and book.
            sPrevTyp = ""
        End If
        fnTitle = fnMakeStyleName("Title", 0, sPrevTyp)
    Else
        fnTitle = fnMakeStyleName("p", 0, "")
    End If
End Function


Sub eventHeadingButton()
    Set oVC = fnGetViewCursor()
    sStyle = fnGetParaStyleName(oVC)
    sStyle = fnHeading(sStyle, fnFindPrevHeadingStyleName(oVC))
    Rem if the current style is li2  style, and set heading, this remove the previous Numbering style and allow the h-n style to continue from the previous list.
    subSetParaStyleName oVC, "h1"
    subSetParaStyleName oVC, sStyle
End Sub


Function fnHeading(sStyle, sPrevStyle)
    sFamily = fnGetFamily(sStyle)
    sPrevFamily = fnGetFamily(sPrevStyle)
    nLev = fnGetLevel(sStyle)
    nPrevLev = fnGetLevel(sPrevStyle)
    sTyp = fnGetType(sStyle)
    sPrevTyp = fnGetType(sPrevStyle)
    
    If sFamily <> "h" Then
        If sPrevFamily <> "h" Then
            fnHeading = fnMakeStyleName("h", 1, "")
        End If
        If nPrevLev < 1 Then
            nPrevLev = 1
        End If
        If sTyp = "n" Then
            sPrevTyp = "n"
        End If
        fnHeading = fnMakeStyleName("h", nPrevLev, sPrevTyp)
    Else
        fnHeading = fnMakeStyleName("p", 0, "")
    End If
End Function


Sub eventBlockQuoteButton()
    Set oVC = fnGetViewCursor()
    sStyle = fnGetParaStyleName(oVC)
    sStyle = fnBlockQuote(sStyle, fnFindPrevStyleName(oVC))
    subSetParaStyleName oVC, sStyle
End Sub


Function fnBlockQuote(sStyle, sPrevStyle)
    sFamily = fnGetFamily(sStyle)
    sPrevFamily = fnGetFamily(sPrevStyle)
    If sFamily = "h" Then
        nLev = 1
    Else
        nLev = fnGetLevel(sStyle)
        If nLev < 1 Then
            nLev = 1
        End If
    End If
    If sPrevFamily = "h" Then
        nPrevLev = 1
    Else
        nPrevLev = fnGetLevel(sPrevStyle)
    End If
    sTyp = fnGetType(sStyle)
    sPrevTyp = fnGetType(sPrevStyle)


    If sFamily = "bq" And sTyp = "" Then
        If sPrevFamily = "bq" And nLev = nPrevLev Then
            fnBlockQuote = fnMakeStyleName("bq", nLev, "source")
        Else
           If sPrevFamily = "h" Then
                fnBlockQuote = fnMakeStyleName("p", 0, "")
            Else
                fnBlockQuote = fnMakeStyleName(sPrevFamily, nPrevLev, sPrevTyp)
            End If
        End If
    ElseIf sFamily = "bq" And sTyp = "source" Then
        If sPrevFamily = "li" Or sPrevFamily = "dt" Or sPrevFamily = "dd" Or sPrevFamily = "pre" Then
            fnBlockQuote = fnMakeStyleName("bq", nPrevLev + 1, "")
        ElseIf nLev = nPrevLev Then
            fnBlockQuote = fnMakeStyleName("bq", nLev, "")
        ElseIf sPrevFamily = "h" Or sPrevFamily = "Title" Or sPrevFamily = "p" Then
'       If sPrevFamily = "h" or sPrevFamily = "Title" or sPrevFamily = "p" Then
            fnBlockQuote = fnMakeStyleName("bq", 1, "")
        Else
            fnBlockQuote = fnMakeStyleName(sPrevFamily, nPrevLev, sPrevTyp)
        End If
    ElseIf sPrevFamily = "li" Then
        fnBlockQuote = fnMakeStyleName("bq", nPrevLev + 1, "")
    Else
        If sPrevFamily = "bq" Then
            fnBlockQuote = fnMakeStyleName(sPrevFamily, nPrevLev, sPrevTyp)
        ElseIf sPrevFamily = "p" Or sPrevFamily = "h" Or sPrevFamily = "Title" Then
            fnBlockQuote = fnMakeStyleName("bq", 1, "")
        Else
            fnBlockQuote = fnMakeStyleName("bq", nLev, "")
        End If
    End If
End Function


Sub eventPreformmatedButton()
    Set oVC = fnGetViewCursor()
    sStyle = fnGetParaStyleName(oVC)
    sStyle = fnPreformatted(sStyle, fnFindPrevStyleName(oVC))
    subSetParaStyleName oVC, sStyle
End Sub


Function fnPreformatted(sStyle, sPrevStyle)
    sFamily = fnGetFamily(sStyle)
    sPrevFamily = fnGetFamily(sPrevStyle)
    If sFamily = "h" Then
        nLev = 0
    Else
        nLev = fnGetLevel(sStyle)
    End If
    If sPrevFamily = "h" Then
        nPrevLev = 0
    Else
        nPrevLev = fnGetLevel(sPrevStyle)
    End If
    sTyp = fnGetType(sStyle)
    sPrevTyp = fnGetType(sPrevStyle)

    If sFamily = "pre" Then
        If sPrevFamily = "h" Then
            fnPreformatted = fnMakeStyleName("p", 0, "")
        ElseIf sPrevFamily = "pre" Then
            If nPrevLev <= 1 Then
                fnPreformatted = fnMakeStyleName("p", 0, "")
            ElseIf sStyle = sPrevStyle Then
                fnPreformatted = fnfindThis("parentstyle")
            Else
                fnPreformatted = sPrevStyle
            End If
        Else
            fnPreformatted = fnMakeStyleName(sPrevFamily, nPrevLev, sPrevTyp)
        End If
    Else
        nLev = nPrevLev + 1
        If nLev > 5 Then
            nLev = 5
        End If
        If sPrevFamily = "h" Or sPrevFamily = "Title" Then
            nLev = 1
        End If
        fnPreformatted = fnMakeStyleName("pre", nLev, "")
    End If
End Function


Sub eventDefinitionButton()
    Set oVC = fnGetViewCursor()
    sStyle = fnGetParaStyleName(oVC)
    sStyle = fnDefinition(sStyle, fnFindPrevStyleName(oVC))
    subSetParaStyleName oVC, sStyle
End Sub


Function fnDefinition(sStyle, sPrevStyle)
    sFamily = fnGetFamily(sStyle)
    sPrevFamily = fnGetFamily(sPrevStyle)
    If sFamily = "h" Then
        nLev = 1
    Else
        nLev = fnGetLevel(sStyle)
    End If
    If sPrevFamily = "h" Then
        nPrevLev = 1
    Else
        nPrevLev = fnGetLevel(sPrevStyle)
    End If
    sTyp = fnGetType(sStyle)
    sPrevTyp = fnGetType(sPrevStyle)

    If sFamily = "dt" Then
        If sPrevFamily = "dd" Or sPrevFamily = "dt" Then
            fnDefinition = fnMakeStyleName("dd", nPrevLev, "")
        ElseIf sPrevFamily = "li" Or sPrevFamily = "pre" Then
            fnDefinition = fnMakeStyleName(sPrevFamily, nPrevLev, sPrevTyp)
        ElseIf (sPrevFamily = "h" Or sPrevFamily = "Title") And nLev <> 1 Then
            fnDefinition = fnMakeStyleName("dt", 1, "")
        Else
            fnDefinition = fnMakeStyleName("p", 0, "")
        End If
    ElseIf sFamily = "dd" Then
        If sPrevFamily = "dt" Then
            fnDefinition = fnMakeStyleName("dt", nPrevLev + 1, "")
        ElseIf sPrevFamily = "dd" Then
            fnDefinition = fnMakeStyleName("dt", nPrevLev, "")
        ElseIf sPrevFamily = "li" Or sPrevFamily = "pre" Then
            If nLev < nPrevLev Then
                fnDefinition = fnMakeStyleName("dt", nLev, "")
            Else
                fnDefinition = fnMakeStyleName("dt", nPrevLev + 1, "")
            End If
        Else
            If nPrevLev < 1 Then
                nPrevLev = 1
            End If
            fnDefinition = fnMakeStyleName("dt", nPrevLev, "")
        End If
    Else
        Rem if not definition list
        If nLev < 1 Then
            nLev = 1
        End If
        If sPrevFamily = "dt" Then
            fnDefinition = fnMakeStyleName("dd", nPrevLev, "")
        ElseIf sPrevFamily = "dd" Then
            fnDefinition = fnMakeStyleName("dt", nPrevLev, "")
        ElseIf sPrevFamily = "li" Or sPrevFamily = "pre" Then
            If sStyle <> sPrevStyle Then
                sParentStyle = fnfindThis("parentLevelStyle")
            Else
                sParentStyle = sPrevStyle
            End If
            sParentFamily = fnGetFamily(sParentStyle)
            sParentLev = fnGetLevel(sParentStyle)
            sParentTyp = fnGetType(sParentStyle)
            If sParentFamily = "dd" Or sParentFamily = "dt" Then
                fnDefinition = fnMakeStyleName("dd", sParentLev, "")
            Else
                nLev = nPrevLev + 1
                If nLev > 5 Then
                    nLev = 5
                End If
                fnDefinition = fnMakeStyleName("dt", nLev, "")
            End If
        ElseIf sPrevFamily <> "h" And sPrevFamily <> "Title" And sPrevFamily <> "p" Then
            fnDefinition = fnMakeStyleName("dt", nLev, "")
        Else
            fnDefinition = fnMakeStyleName("dt", 1, "")
        End If
    End If
End Function


Sub eventLeftButton()
    Set oVC = fnGetViewCursor()
    sStyle = fnGetParaStyleName(oVC)
    sStyle = fnLeft(sStyle, fnFindPrevStyleName(oVC))
    subSetParaStyleName oVC, sStyle
End Sub


Function fnLeft(sStyle, sPrevStyle)
    fnLeft = fnMakeStyleName("p", 0, "")
End Function

Sub eventIndentButton()
    Set oVC = fnGetViewCursor()
    sStyle = fnGetParaStyleName(oVC)
    sStyle = fnIndent(sStyle, fnFindPrevStyleName(oVC))
    subSetParaStyleName oVC, sStyle
End Sub


Function fnIndent(sStyle, sPrevStyle)
    sFamily = fnGetFamily(sStyle)
    sTyp = fnGetType(sStyle)
    If sFamily = "p" And sTyp = "indent" Then
        fnIndent = fnMakeStyleName("p", 0, "")
    Else
        fnIndent = fnMakeStyleName("p", 0, "indent")
    End If
End Function

Sub eventCenterButton()
    Set oVC = fnGetViewCursor()
    sStyle = fnGetParaStyleName(oVC)
    sStyle = fnCenter(sStyle, fnFindPrevStyleName(oVC))
    subSetParaStyleName oVC, sStyle
End Sub


Function fnCenter(sStyle, sPrevStyle)
    sFamily = fnGetFamily(sStyle)
    sTyp = fnGetType(sStyle)
    If sFamily = "p" And sTyp = "center" Then
        fnCenter = fnMakeStyleName("p", 0, "")
    Else
        fnCenter = fnMakeStyleName("p", 0, "center")
    End If
End Function


Sub eventRightButton()
    Set oVC = fnGetViewCursor()
    sStyle = fnGetParaStyleName(oVC)
    sStyle = fnRight(sStyle, fnFindPrevStyleName(oVC))
    subSetParaStyleName oVC, sStyle
End Sub


Function fnRight(sStyle, sPrevStyle)
    sFamily = fnGetFamily(sStyle)
    sTyp = fnGetType(sStyle)
    If sFamily = "p" And sTyp = "right" Then
        fnRight = fnMakeStyleName("p", 0, "")
    Else
        fnRight = fnMakeStyleName("p", 0, "right")
    End If
End Function


Function fnListerise(sFamily, sPrevFamily, nLev, nPrevLev, sTyp, sPrevTyp, sToggleTyp)
    Rem  The current item is a list item
    If sFamily = "li" Then
        Rem The current item does not match the togle type and is a child of the previous paragraph
        If sTyp <> sToggleTyp And nLev >= nPrevLev Then
            If sPrevTyp <> sToggleTyp Then
                If sToggleTyp = "n" And Not (sPrevTyp = "p" Or sPrevTyp = "b" Or sPrevTyp = "") Then
                    sToggleTyp = sPrevTyp
                ElseIf sPrevTyp <> "p" Then
                    nLev = nPrevLev + 1
                End If
            End If
            fnListerise = fnMakeStyleName("li", nLev, sToggleTyp)
        ElseIf sFamily = sPrevFamily And nLev >= nPrevLev And sTyp = sPrevTyp Then
            sPrevStyle = fnfindThis("prevparastyle")
            If fnGetFamily(sPrevStyle) = "li" Then
                fnListerise = fnMakeStyleName("li", fnGetLevel(sPrevStyle), "p")
            Else
                sParentStyle = fnfindThis("parentLevelStyle")
                If fnGetFamily(sParentStyle) = sPrevFamily And fnGetLevel(sParentStyle) = nLev And fnGetType(sParentStyle) = sTyp Then
                    fnListerise = fnMakeStyleName("li", nPrevLev, "p")
                Else
                    fnListerise = "p"
                End If
            End If
        ElseIf sTyp = sPrevTyp And sPrevFamily = "li" Then
            fnListerise = fnMakeStyleName(sPrevFamily, nLev, "p")
        ElseIf sPrevFamily = "h" Then
            Rem toggle off
            fnListerise = "p"
        Else
            Rem toggle off
            fnListerise = fnMakeStyleName(sPrevFamily, nPrevLev, sPrevTyp)
        End If
    Else
        Rem The current style is not a list item
        n = nPrevLev
        If n < 1 Then
            n = 1
        End If
        If sPrevFamily = "li" Then
            n = nPrevLev
            If n < 1 Then
                n = 1
            End If
            If sPrevTyp <> sToggleTyp Then
                If sToggleTyp = "n" And Not (sPrevTyp = "p" Or sPrevTyp = "b") Then
                    sToggleTyp = sPrevTyp
                Else
                    n = n + 1
                End If
            End If
        ElseIf sPrevFamily = "pre" Then
            sParentStyle = fnfindThis("parentLevelStyle")
            If fnGetType(sParentStyle) = sToggleTyp Then
                n = n - 1
                If n < 1 Then
                    Rem To force the level to have at least level 1
                    n = 1
                End If
            Else
                n = 1
            End If
            
        End If
        fnListerise = fnMakeStyleName("li", n, sToggleTyp)
    End If
End Function


Sub eventChangeListTypeDlg()
    #If MSWD Then
        Set oDialog = frmListType
        With oDialog.cmbListType
            .AddItem "n"
            .AddItem "i"
            .AddItem "a"
            .AddItem "I"
            .AddItem "A"
            .AddItem "b"
        End With
        Call oDialog.Show
    #Else
        DialogLibraries.LoadLibrary ("IceLibrary")
        oDialog = CreateUnoDialog(DialogLibraries.IceLibrary.dlgListType)
        If oDialog.Execute Then
            subChangeListType (oDialog.getControl("cmbListType").GetText)
        End If
    #End If
End Sub


Sub subChangeListType(sNewListType)
    If sNewListType = "" Then
        Rem in case it is empty, set it to p to create li-p style
        sNewListType = "p"
    End If
    Set oVC = fnGetViewCursor()
    sStyle = fnGetParaStyleName(oVC)
    sPrevStyle = fnFindPrevStyleName(oVC)

    sFamily = fnGetFamily(sStyle)
    sPrevFamily = fnGetFamily(sPrevStyle)
    nLev = fnGetLevel(sStyle)
    If sFamily <> "h" And sPrevFamily = "h" Then
        nPrevLev = 0
    Else
        nPrevLev = fnGetLevel(sPrevStyle)
    End If
    sTyp = fnGetType(sStyle)
    sPrevTyp = fnGetType(sPrevStyle)

    sStyle = fnListerise(sFamily, sPrevFamily, nLev, nPrevLev, sTyp, sPrevTyp, sNewListType)
    subSetParaStyleName oVC, sStyle
End Sub


Sub eventBulletButton()
    Set oVC = fnGetViewCursor()
    sStyle = fnGetParaStyleName(oVC)
    sStyle = fnBullet(sStyle, fnFindPrevStyleName(oVC))
    subSetParaStyleName oVC, sStyle
End Sub


Function fnBullet(sStyle, sPrevStyle)
    sFamily = fnGetFamily(sStyle)
    sPrevFamily = fnGetFamily(sPrevStyle)
    nLev = fnGetLevel(sStyle)
    If sFamily <> "h" And sPrevFamily = "h" Then
        nPrevLev = 0
    Else
        nPrevLev = fnGetLevel(sPrevStyle)
    End If
    sTyp = fnGetType(sStyle)
    sPrevTyp = fnGetType(sPrevStyle)
    fnBullet = ""

    fnBullet = fnListerise(sFamily, sPrevFamily, nLev, nPrevLev, sTyp, sPrevTyp, "b")

End Function


Sub eventNumberiseButton()
    Set oVC = fnGetViewCursor()
    sStyle = fnGetParaStyleName(oVC)
    If fnGetFamily(sStyle) = "h" Then
        sStyle = fnNumberise(sStyle, fnFindPrevHeadingStyleName(oVC))
    Else
        sStyle = fnCheckForOtherList(oVC, sStyle)
        sStyle = fnNumberise(sStyle, fnFindPrevListStyleName(oVC))
    End If
    subSetParaStyleName oVC, sStyle
End Sub

Function fnCheckForOtherList(oVC, sStyle)
    Rem check the style first
    sFamily = fnGetFamily(sStyle)
    nLev = fnGetLevel(sStyle)
    sType = fnGetType(sStyle)
    If nLev < 1 Then
        nLev = 1
    End If
    If sFamily = "li" And sType <> "b" And sType <> "p" Then
        Rem if toggle.
        fnCheckForOtherList = sStyle
        Exit Function
    End If

    Rem the paragraph above style data
    sPrevStyle = fnFindPrevStyleName(oVC)
    sPrevStyleFamily = fnGetFamily(sPrevStyle)
    sPrevStyleLevel = fnGetLevel(sPrevStyle)
    sPrevStyleType = fnGetType(sPrevStyle)
    Rem if prevStyleFamily is h or Title Then
    If sPrevStyleFamily = "h" Or sPrevStyleFamily = "Title" Or sPrevStyleFamily = "p" Then
        fnCheckForOtherList = sStyle
        Exit Function
    ElseIf sPrevStyle = sStyle Then
         Rem if the same e.g. li3b and li3b. then
         If sPrevStyleFamily = "li" And sPrevStyleType = "b" Then
            nLev = nLev + 1
         End If
    End If
    Rem the actual parent level style data
    sParentLevel = nLev
    If sParentLevel <> 1 Then
        sParentLevel = sParentLevel - 1
    End If
    sParentStyle = fnfindThis("thislevelliststyletype", sParentLevel, True)
    sParentFamily = fnGetFamily(sParentStyle)
    sParentType = fnGetType(sParentStyle)

    If (sPrevStyleFamily = "li" And sPrevStyleType = "b") Or (sParentFamily = "li" And sParentType = "b") Then
        If sParentLevel = nLev Then
            Rem if they are the same.ie. lev 1
             nLev = nLev + 1
         End If
        subSetParaStyleName oVC, fnMakeStyleName("li", nLev, "p")
        sStyle = fnMakeStyleName("li", nLev, "p")
    End If
    fnCheckForOtherList = sStyle
End Function

Function fnNumberise(sStyle, sPrevStyle)
    sFamily = fnGetFamily(sStyle)
    sPrevFamily = fnGetFamily(sPrevStyle)
    nLev = fnGetLevel(sStyle)
    If sFamily <> "h" And sPrevFamily = "h" Then
        nPrevLev = 0
    Else
        nPrevLev = fnGetLevel(sPrevStyle)
    End If
    sTyp = fnGetType(sStyle)
    sPrevTyp = fnGetType(sPrevStyle)

    If sFamily = "h" Then
        If sTyp = "n" Then
            sNewTyp = ""
        Else
            sNewTyp = "n"
        End If
        fnNumberise = fnMakeStyleName("h", nLev, sNewTyp)
    ElseIf sFamily = "Title" Then
        If sTyp = "chapter" Then
            sNewTyp = ""
        Else
            sNewTyp = "chapter"
        End If
        fnNumberise = fnMakeStyleName("Title", nLev, sNewTyp)
    Else
        If sTyp = "n" Or sTyp = "i" Or sTyp = "a" Or sTyp = "I" Or sTyp = "A" Then
            fnNumberise = fnListerise(sFamily, sPrevFamily, nLev, nPrevLev, sTyp, sPrevTyp, sTyp)
        Else
            fnNumberise = fnListerise(sFamily, sPrevFamily, nLev, nPrevLev, sTyp, sPrevTyp, "n")
        End If
    End If
End Function


Sub eventDefaultFormattingButton()
    #If OOO Then
        Dim Document   As Object
        Dim dispatcher As Object
        Document = ThisComponent.CurrentController.Frame
        dispatcher = createUnoService("com.sun.star.frame.DispatchHelper")

        dispatcher.executeDispatch(document, ".uno:ResetAttributes", "", 0, Array())
    #Else
        Selection.style = ActiveDocument.Styles("Default Paragraph Font")
        On Error Resume Next
        n = Selection.Hyperlinks.count
        Do While n > 0
           Selection.Hyperlinks(n).Delete
           n = Selection.Hyperlinks.count
        Loop
    #End If
End Sub


Sub eventRestartNumberingButton()
    subRestartNumbering (True)
End Sub


Sub subRestartNumbering(bRestart As Boolean)
    #If OOO Then
        Set oVC = fnGetViewCursor()
        oVC.ParaIsNumberingRestart = bRestart
    #Else
        nIndex = fnGetCurrentParagraphNumber()
        bRestart = Not bRestart
        ActiveDocument.Paragraphs(nIndex).Range.Select
        With Selection.Range.ListFormat
            .ApplyListTemplate .ListTemplate, False, wdListApplyToWholeList, 2
        End With
    #End If
End Sub


Function fnfindThis(criteria As String, Optional nLev, Optional IncludeBullet As Boolean)
    Rem return the value according to the criteria
    Rem just to clear the code
    Rem too many find program
    Set oVC = fnGetViewCursor()
    Select Case (LCase(criteria))
        Case "parastyle"
            fnfindThis = fnGetParaStyleName(oVC)
        Case "prevparastyle"
            fnfindThis = fnFindPrevStyleName(oVC)
        Case "parentstyle"
            Rem this one sometimes not return the correct style.
            Rem use for promote
            Rem
            fnfindThis = fnFindPrevParentStyleName(oVC)
        Case "parentlevelstyle"
            Rem to find the previous level above this style
            fnfindThis = fnFindPrevLevelStyleName(oVC)
        Case "prevheadingstyle"
            fnfindThis = fnFindPrevHeadingStyleName(oVC)
        Case "prevliststyle"
            fnfindThis = fnFindPrevListStyleName(oVC)
        Case "thislevelliststyletype"
            fnfindThis = fnFindThisListStyleType(oVC, nLev, IncludeBullet)
        Case Else
            Rem do nothing
    End Select
End Function

Function fnFindPrevHeadingStyleName(oCursor)
Rem find the last heading style about the current paragraph
    #If MSWD Then
        If Not Selection.Information(wdWithInTable) Then
            nIndex = fnGetCurrentParagraphNumber()
            sStyleName = "Title"
            Do While nIndex > 1
                sName = ActiveDocument.Paragraphs(nIndex - 1).style
                sFamily = fnGetFamily(sName)
                If sFamily = "h" Then
                    sStyleName = sName
                    Exit Do
                End If
                nIndex = nIndex - 1
            Loop
        Else
            Dim tableNum As Integer
            tableNum = fnGetCurrentTableNumber()
            nIndex = fnGetCurrentParagraphNumber()
            nFirstIndex = fnGetfirstParaNumberInTable(tableNum)
            Do While nIndex >= nFirstIndex
                sName = ActiveDocument.Paragraphs(nIndex - 1).style
                sFamily = fnGetFamily(sName)
                If sFamily = "h" Then
                    sStyleName = sName
                    Exit Do
                End If
                nIndex = nIndex - 1
            Loop
        End If
    #Else
        oTxtCursor = oCursor.Text.createTextCursorByRange(oCursor)
        Do
            If oTxtCursor.gotoPreviousParagraph(False) = False Then
                sStyleName = "Title"
                Exit Do
            End If
            sStyleName = oTxtCursor.paraStyleName
            sStyleName = str(sStyleName)
        Loop Until fnGetFamily(sStyleName) = "h"

    #End If
    fnFindPrevHeadingStyleName = sStyleName
End Function


Function fnFindPrevLevelStyleName(oCursor)
    Rem find the previous level style
    Rem if current level is level 3, find previous level 2 style.
    #If MSWD Then
        If Not Selection.Information(wdWithInTable) Then
            nIndex = fnGetCurrentParagraphNumber()
            sStartStyleName = ActiveDocument.Paragraphs(nIndex).style
            nStartLev = fnGetLevel(sStartStyleName)
            If nStartLev < 1 Then
                nStartLev = 1
            End If
            Do While nIndex > 1
                If Not ActiveDocument.Paragraphs(nIndex - 1).Range.Information(wdWithInTable) Then
                    sCurStyleName = ActiveDocument.Paragraphs(nIndex - 1).style
                    sCurFamily = fnGetFamily(sCurStyleName)
                    nCurLev = fnGetLevel(sCurStyleName)
                    sCurTyp = fnGetType(sCurStyleName)
                    If nCurLev = nStartLev - 1 Then
                        sStyleName = sCurStyleName
                        Exit Do
                    End If
                End If
                nIndex = nIndex - 1
            Loop
        Else
            Dim tableNum As Integer
            tableNum = fnGetCurrentTableNumber()
            nIndex = fnGetCurrentParagraphNumber()
            nFirstIndex = fnGetfirstParaNumberInTable(tableNum)
            sStartStyleName = ActiveDocument.Paragraphs(nIndex).style
            nStartLev = fnGetLevel(sStartStyleName)
            If nStartLev < 1 Then
                nStartLev = 1
            End If
            'sStyleName = fnMakeStyleName("li", nStartLev, mListType(nStartLev - 1))
            Do While nIndex >= nFirstIndex
            'For i = 1 To ActiveDocument.Tables(tableNum).Range.Paragraphs.count
                sCurStyleName = ActiveDocument.Paragraphs(nIndex - 1).style
                sCurFamily = fnGetFamily(sCurStyleName)
                nCurLev = fnGetLevel(sCurStyleName)
                sCurTyp = fnGetType(sCurStyleName)
                If nCurLev = nStartLev - 1 Then
                        sStyleName = sCurStyleName
                        Exit Do
                End If
                nIndex = nIndex - 1
            'Next
            Loop
        End If
    #Else
        oTxtCursor = oCursor.Text.createTextCursorByRange(oCursor)
        sStartStyleName = oTxtCursor.paraStyleName
        nStartFamily = fnGetFamily(sStartStyleName)
        nStartLev = fnGetLevel(sStartStyleName)
        If nStartLev < 1 Then
            nStartLev = 1
        End If
        nCurLev = nStartLev
        Do
            If oTxtCursor.gotoPreviousParagraph(False) = False Then
                sCurStyleName = "p"
                Exit Do
            End If
            sCurStyleName = oTxtCursor.paraStyleName
            sCurStyleName = str(sCurStyleName)
            sCurFamily = fnGetFamily(sCurStyleName)
            If sCurFamily = "p" Then
                Exit Do
            End If
            nCurLev = fnGetLevel(sCurStyleName)
            sCurTyp = fnGetType(sCurStyleName)
        Loop Until nCurLev = nStartLev - 1
    #End If
    If fnGetFamily(sCurStyleName) = "h" And nStartFamily <> "h" Then
        If nStartFamily <> "p" Then
            sCurStyleName = fnMakeStyleName(nStartFamily, 1, fnGetType(sStartStyleName))
        Else
            sCurStyleName = "p"
        End If
    End If
     
    fnFindPrevLevelStyleName = sCurStyleName
End Function


Function fnFindThisListStyleType(oCursor, nLev, Optional IncludeBullet As Boolean)
    Rem to find the list style type for the given list level.
    Rem maybe this can be used to see if there is a bullet or numbering list in front.
    Rem can we make it to return the numbering type jst as the fnFindPrevListStyleName??
    If IsEmpty(IncludeBullet) Or IsMissing(IncludeBullet) Then
        IncludeBullet = False
    End If
    If nLev < 1 Then
        nLev = 1
    End If
    mListType = Array("n", "i", "a", "I", "A")
    #If MSWD Then
        If Not Selection.Information(wdWithInTable) Then
            Rem if not within the table
            nIndex = fnGetCurrentParagraphNumber()
            sStyleName = fnGetParaStyleName()
            
            Do While nIndex > 1
                sCurStyleName = ActiveDocument.Paragraphs(nIndex - 1).style
                sCurFamily = fnGetFamily(sCurStyleName)
                nCurLev = fnGetLevel(sCurStyleName)
                sCurTyp = fnGetType(sCurStyleName)
                If IncludeBullet Then
                    If (sCurFamily = "li" And nCurLev = nLev And sCurTyp <> "p") Then
                        sStyleName = sCurStyleName
                        Exit Do
                    End If
                Else
                    If (sCurFamily = "li" And nCurLev = nLev And sCurTyp <> "b" And sCurTyp <> "p") Then
                        sStyleName = sCurStyleName
                        Exit Do
                    End If
                End If
                nIndex = nIndex - 1
            Loop
        Else
            Rem if within table
            Dim tableNum As Integer
            tableNum = fnGetCurrentTableNumber()
            nIndex = fnGetCurrentParagraphNumber()
            nFirstIndex = fnGetfirstParaNumberInTable(tableNum)
            sStyleName = fnGetParaStyleName()
            
            Do While nIndex >= nFirstIndex
                sCurStyleName = ActiveDocument.Paragraphs(nIndex - 1).style
                sCurFamily = fnGetFamily(sCurStyleName)
                nCurLev = fnGetLevel(sCurStyleName)
                sCurTyp = fnGetType(sCurStyleName)
                If IncludeBullet Then
                    If (sCurFamily = "li" And nCurLev = nLev And sCurTyp <> "p") Then
                        sStyleName = sCurStyleName
                        Exit Do
                    End If
                Else
                    If (sCurFamily = "li" And nCurLev = nLev And sCurTyp <> "b" And sCurTyp <> "p") Then
                        sStyleName = sCurStyleName
                        Exit Do
                    End If
                End If
                nIndex = nIndex - 1
            Loop
        End If
    #Else
        oTxtCursor = oCursor.Text.createTextCursorByRange(oCursor)
        sStyleName = oTxtCursor.paraStyleName
        sCurStyleName = sStyleName
        Do
            If oTxtCursor.gotoPreviousParagraph(False) = False Then
                sStyleName = sCurStyleName
                Exit Do
            End If
            sCurStyleName = oTxtCursor.paraStyleName
            sCurStyleName = str(sCurStyleName)
            sCurFamily = fnGetFamily(sCurStyleName)
            nCurLev = fnGetLevel(sCurStyleName)
            sCurTyp = fnGetType(sCurStyleName)
            If IncludeBullet Then
                 If (sCurFamily = "li" And nCurLev = nLev And sCurTyp <> "p") Then
                     sStyleName = sCurStyleName
                     Exit Do
                 End If
             Else
                 If (sCurFamily = "li" And nCurLev = nLev And sCurTyp <> "b" And sCurTyp <> "p") Then
                     sStyleName = sCurStyleName
                     Exit Do
                 End If
             End If
        Loop While True
        sStyleName = sCurStyleName
    #End If
    If fnGetFamily(sStyleName) <> "li" Or fnGetType(sStyleName) = "p" Then
        If nLev <= 0 Then
            nLev = 1
        End If
        sStyleName = fnMakeStyleName("li", nLev, mListType(nLev - 1))
    End If
    fnFindThisListStyleType = sStyleName
End Function

Function fnFindPrevListStyleName(oCursor)
    mListType = Array("n", "i", "a", "I", "A")
    #If MSWD Then
        If Not Selection.Information(wdWithInTable) Then
            nIndex = fnGetCurrentParagraphNumber()
            sStartStyleName = ActiveDocument.Paragraphs(nIndex).style
            nStartLev = fnGetLevel(sStartStyleName)
            If nStartLev < 1 Then
                nStartLev = 1
            End If
            sStyleName = fnMakeStyleName("li", nStartLev, mListType(nStartLev - 1))
            Do While nIndex > 1
                If Not ActiveDocument.Paragraphs(nIndex - 1).Range.Information(wdWithInTable) Then
                    sCurStyleName = ActiveDocument.Paragraphs(nIndex - 1).style
                    sCurFamily = fnGetFamily(sCurStyleName)
                    nCurLev = fnGetLevel(sCurStyleName)
                    sCurTyp = fnGetType(sCurStyleName)
                    If (sCurFamily = "li" And nCurLev = nStartLev And sCurTyp <> "b" And sCurTyp <> "p") Then
                        sStyleName = sCurStyleName
                        Exit Do
                    End If
                End If
                nIndex = nIndex - 1
            Loop
        Else
            Dim tableNum As Integer
            tableNum = fnGetCurrentTableNumber()
            nIndex = fnGetCurrentParagraphNumber()
            nFirstIndex = fnGetfirstParaNumberInTable(tableNum)
            sStartStyleName = ActiveDocument.Paragraphs(nIndex).style
            nStartLev = fnGetLevel(sStartStyleName)
            If nStartLev < 1 Then
                nStartLev = 1
            End If
            sStyleName = fnMakeStyleName("li", nStartLev, mListType(nStartLev - 1))
            Do While nIndex >= nFirstIndex
            'For i = 1 To ActiveDocument.Tables(tableNum).Range.Paragraphs.count
                sCurStyleName = ActiveDocument.Paragraphs(nIndex - 1).style
                sCurFamily = fnGetFamily(sCurStyleName)
                nCurLev = fnGetLevel(sCurStyleName)
                sCurTyp = fnGetType(sCurStyleName)
                If (sCurFamily = "li" And nCurLev = nStartLev And sCurTyp <> "b" And sCurTyp <> "p") Then
                    sStyleName = sCurStyleName
                    Exit Do
                End If
                nIndex = nIndex - 1
            'Next
            Loop
        End If
    #Else
        oTxtCursor = oCursor.Text.createTextCursorByRange(oCursor)
        sStartStyleName = oTxtCursor.paraStyleName
        nStartFamily = fnGetFamily(sStartStyleName)
        nStartLev = fnGetLevel(sStartStyleName)
        If nStartLev < 1 Then
            nStartLev = 1
        End If
        sCurStyleName = fnMakeStyleName("li", nStartLev, mListType(nStartLev - 1))
        Do
            If oTxtCursor.gotoPreviousParagraph(False) = False Then
                sCurStyleName = fnMakeStyleName("li", nStartLev, mListType(nStartLev - 1))
                Exit Do
            End If
            sCurStyleName = oTxtCursor.paraStyleName
            sCurStyleName = str(sCurStyleName)
            sCurFamily = fnGetFamily(sCurStyleName)
            nCurLev = fnGetLevel(sCurStyleName)
            sCurTyp = fnGetType(sCurStyleName)
        Loop Until sCurFamily = "li" And nCurLev = nStartLev And sCurTyp <> "b" And sCurTyp <> "p"
        sStyleName = sCurStyleName
    #End If
    fnFindPrevListStyleName = sStyleName
End Function


Function fnFindPrevParentStyleName(oCursor)
    #If MSWD Then
        nIndex = fnGetCurrentParagraphNumber()
        sCurrentStyleName = ActiveDocument.Paragraphs(nIndex).style
        nCurrentLev = fnGetLevel(sCurrentStyleName)
        If fnGetFamily(sCurrentStyleName) = "h" And fnGetLevel(sCurrentStyleName) = 1 Then
            sStyleName = "Title"
        ElseIf sCurrentStyleName = "p-center" Or sCurrentStyleName = "p-right" Then
            sStyleName = sCurrentStyleName
        ElseIf nCurrentLev <= 1 Then
            sStyleName = "p"
        Else
            sStyleFamily = fnGetFamily(sCurrentStyleName)
            sStyleType = fnGetType(sCurrentStyleName)
            If Not Selection.Information(wdWithInTable) Then
                Do While nIndex > 1
                    If Not ActiveDocument.Paragraphs(nIndex - 1).Range.Information(wdWithInTable) Then
                        sName = ActiveDocument.Paragraphs(nIndex - 1).style
                        sFamily = fnGetFamily(sName)
                        nLev = fnGetLevel(sName)
                        sType = fnGetType(sName)
                        If sStyleFamily = sFamily And nLev = nCurrentLev - 1 Then
                            sStyleName = sName
                            Exit Do
                        End If
                    End If
                    nIndex = nIndex - 1
                Loop
            Else
                Dim tableNum As Integer
                tableNum = fnGetCurrentTableNumber()
                nIndex = fnGetCurrentParagraphNumber()
                nFirstIndex = fnGetfirstParaNumberInTable(tableNum)
                Do While nIndex >= nFirstIndex
                    sName = ActiveDocument.Paragraphs(nIndex - 1).style
                    sFamily = fnGetFamily(sName)
                    nLev = fnGetLevel(sName)
                    sType = fnGetType(sName)
                    If sStyleFamily = sFamily And nLev = nCurrentLev - 1 Then
                        sStyleName = sName
                        Exit Do
                    End If
                    nIndex = nIndex - 1
                Loop
            End If
        End If
        If IsEmpty(sStyleName) Then
            If nCurrentLev > 1 Then
                sStyleName = fnMakeStyleName(fnGetFamily(sCurrentStyleName), nCurrentLev - 1, fnGetType(sCurrentStyleName))
            Else
                sStyleName = "p"
            End If
        End If
        sFamily = fnGetFamily(sStyleName)
        If sFamily <> "Title" And sFamily <> "h" And sFamily <> "p" And sFamily <> "bq" And _
            sFamily <> "dt" And sFamily <> "dd" And sFamily <> "li" And sFamily <> "pre" And _
            sFamily <> "i" And sFamily <> "xRef" Then
            Rem if not ice style then
            sStyleName = "p"
        End If
    #Else
        oTxtCursor = oCursor.Text.createTextCursorByRange(oCursor)
        sCurrentStyleName = oTxtCursor.paraStyleName
        sCurrentFamily = fnGetFamily(sCurrentStyleName)
        nCurrentLev = fnGetLevel(sCurrentStyleName)
        sCurrentType = fnGetType(sCurrentStyleName)
        sStyleName = ""
        Do
            If oTxtCursor.gotoPreviousParagraph(False) = False Then
                If sCurrentFamily = "h" Then
                    sStyleName = "Title"
                ElseIf sCurrentStyleName = "p-center" Or sCurrentStyleName = "p-right" Then
                    sStyleName = sCurrentStyleName
                ElseIf nCurrentLev > 1 Then
                    sStyleName = fnMakeStyleName(sCurrentFamily, nCurrentLev - 1, sCurrentType)
                Else
                    sStyleName = "p"
                End If
                Exit Do
            Else
                If sCurrentFamily = fnGetFamily(oTxtCursor.paraStyleName) And fnGetLevel(oTxtCursor.paraStyleName) = nCurrentLev - 1 Then
                        sStyleName = oTxtCursor.paraStyleName
                        sStyleName = str(sStyleName)
                        Exit Do
                    End If
            End If
        Loop Until sStyleName <> ""

    #End If
    fnFindPrevParentStyleName = sStyleName
End Function


Function fnFindPrevStyleName(oCursor)
    sStyleName = "p"
    #If MSWD Then
        nIndex = fnGetCurrentParagraphNumber()
        If nIndex = 1 Then
            sStyleName = "p"
        Else
            If ActiveDocument.Paragraphs(nIndex).Range.Information(wdWithInTable) Then
                Dim tableNum As Integer
                tableNum = fnGetCurrentTableNumber()
                nFirstIndex = fnGetfirstParaNumberInTable(tableNum)
                If nFirstIndex <= nIndex - 1 Then
                    sStyleName = ActiveDocument.Paragraphs(nIndex - 1).style
                Else
                    sStyleName = "p"
                End If
            Else
                sStyleName = ActiveDocument.Paragraphs(nIndex - 1).style
            End If
        End If
        sFamily = fnGetFamily(sStyleName)
        If sFamily <> "Title" And sFamily <> "h" And sFamily <> "p" And sFamily <> "bq" And _
            sFamily <> "dt" And sFamily <> "dd" And sFamily <> "li" And sFamily <> "pre" And _
            sFamily <> "i" And sFamily <> "xRef" Then
            Rem if not ice style then
            sStyleName = "p"
        End If
    #Else
        On Error GoTo finally
        If oCursor.supportsService("com.sun.star.style.ParagraphProperties") Then
            Rem xray oCursor
            oTxtCursor = oCursor.Text.createTextCursorByRange(oCursor)
            If oTxtCursor.gotoPreviousParagraph(False) Then
                sStyleName = oTxtCursor.paraStyleName
            Else
                sStyleName = "p" rem TODO: make this a constant "default paragraph style"
            End If
        End If
finally:
    #End If
    fnFindPrevStyleName = sStyleName
End Function

Function fnGetfirstParaNumberInTable(tableNum As Integer)
'get table number and get the para number
    #If MSWD Then
        fnGetfirstParaNumberInTable = ActiveDocument.Range(0, ActiveDocument.Tables(tableNum).Range.Paragraphs(1).Range.End).Paragraphs.count
    #End If
End Function

Function fnGetLastParaNumberInTable(tableNum As Integer)
'get table number and get the para number
    #If MSWD Then
        fnGetLastParaNumberInTable = ActiveDocument.Range(0, ActiveDocument.Tables(tableNum).Range.Paragraphs.Last.Range.End).Paragraphs.count
    #End If
End Function

Function fnGetCurrentTableNumber()
    #If MSWD Then
        fnGetCurrentTableNumber = ActiveDocument.Range(0, Selection.Paragraphs(1).Range.End).Tables.count
    #End If

End Function
Function fnGetCurrentParagraphNumber()
    #If MSWD Then
        fnGetCurrentParagraphNumber = ActiveDocument.Range(0, Selection.Paragraphs(1).Range.End).Paragraphs.count
    #End If
End Function


Function fnIsTextElementPara(oTextElement)
    fnIsTextElementPara = oTextElement.supportsService("com.sun.star.text.Paragraph")
End Function


Function fnIsTextElementTable(oTextElement)
    fnIsTextElementTable = oTextElement.supportsService("com.sun.star.text.TextTable")
End Function


Function fnGetSelectedItems()
    oCursorSelection = ThisComponent.getCurrentSelection()
    Rem  for debugging. will need xray tool.
    Rem If oCursorSelection.supportsService("com.sun.star.text.TextRanges") Then
    Rem    xray oCursorSelection
    Rem End If
End Function

Sub subToggleCharacterStyles(sStyle, mResetProps)
    #If OOO Then
        oCurSelection = ThisComponent.getCurrentSelection()
        If oCurSelection.supportsService("com.sun.star.text.TextRanges") Then
            nCount = oCurSelection.count
            If nCount = 1 Then
                Rem If nothing selected then select current word
                oVC = ThisComponent.CurrentController.ViewCursor
                oTextCursor = oVC.Text.createTextCursorByRange(oVC)
                If oVC.isCollapsed() Then
                    oTextCursor.gotoStartOfWord (False)
                    oTextCursor.gotoEndOfWord (True)
                End If
                subProcessTextRange(oTextCursor, sStyle, mResetProps)
            Else
                For i = 1 To nCount - 1
                    oTextRange = oCurSelection.getByIndex(i)
                    subProcessTextRange(oTextRange, sStyle, mResetProps)
                Next
            End If
        ElseIf oCurSelection.supportsService("com.sun.star.text.TextTableCursor") Then
            processTextTableCursor(oCurSelection, sStyle, mResetProps)
        Else
            printMsgbox ("Error in getting selection range. Try deselecting.")
        End If
    #End If
End Sub

Sub processTextTableCursor(oCurSelection, sStyle, mResetProps)
    cellRangeName = oCurSelection.getRangeName()

    startCellName = Split(cellRangeName, ":")(0)
    endCellName = Split(cellRangeName, ":")(1)
    
    startColumn = Asc(Left(startCellName, 1))
    startRow = CInt(Right(startCellName, Len(startCellName) - 1))


    endColumn = Asc(Left(endCellName, 1))
    endRow = CInt(Right(endCellName, Len(endCellName) - 1))
    
    oTable = ThisComponent.CurrentController.getViewCursor().TextTable
    
    For i = startRow To endRow
        For j = startColumn To endColumn
            If (j > 64 And j < 91) Or (j > 96 And j < 123) Then
                Rem only A-Z and a-z
                Rem only support upto52 .i.e until 'z' column
                Rem assume there won't be more than that. and getRangeName() does not support that as well.
                cellName = Chr(j) + CStr(i)
                oCell = oTable.getCellByName(cellName)
                oCellCursor = oTable.createCursorByCellName(cellName)
                If sStyle = "i-i" Then

                    If oCellCursor.CharPosture <> 2 Then
                        Rem switch on Italic
                        oCellCursor.CharPosture = 2
                    Else
                        oCellCursor.CharPosture = 0
                    End If
                ElseIf sStyle = "i-b" Then
                    If oCellCursor.CharWeight <> 150 Then
                        Rem switch on Bold
                        oCellCursor.CharWeight = 150
                    Else
                        oCellCursor.CharWeight = 100
                    End If
                Else
                    subProcessTextRange(oCell.text, sStyle, mResetProps)
                End If
            End If
        Next j
    Next i
End Sub

Sub subProcessTextRange(oTextRange, sStyle, mResetProps)
oTextElementEnum = oTextRange.createEnumeration
While oTextElementEnum.hasMoreElements()
    oTextElement = oTextElementEnum.nextElement()
    If oTextElement.supportsService("com.sun.star.text.Paragraph") Then
        subProcessParagraph(oTextElement, sStyle, mResetProps)
    Else Rem if oTextElement.supportsService("com.sun.star.text.TextTable") then
        subProcessTable(oTextElement, sStyle, mResetProps)
    End If
Wend
End Sub


Sub subProcessTable(oTextElement, sStyle, mResetProps)
mCells = oTextElement.getCellNames()
For i = 0 To UBound(mCells)
    oCell = oTextElement.getCellByName(mCells(i))
    subProcessTextRange(oCell.text, sStyle, mResetProps)
Next
End Sub


Sub subProcessParagraph(oTextElement, sStyle, mResetProps)
If Not fnHasStyle(sStyle, "Character") Then
    subCreateMissingStyle (sStyle)
End If
oPortionEnum = oTextElement.createEnumeration
While oPortionEnum.hasMoreElements()
    oPortion = oPortionEnum.nextElement()
    subResetProperties(oPortion, mResetProps)
    mCharStyleNames = oPortion.getPropertyValue("CharStyleNames")
    sCharStyleNames = ""
    If IsEmpty(mCharStyleNames) Then
        sCharStyleNames = sStyle
    ElseIf UBound(mCharStyleNames) < 0 Then
        sCharStyleNames = sStyle
    Else
        sCharStyleNames = Join(mCharStyleNames, ",") & ","
        nLoc = InStr(sCharStyleNames, sStyle & ",")
        If nLoc > 0 Then
            sCharStyleNames = Left(sCharStyleNames, nLoc - 1) & Right(sCharStyleNames, Len(sCharStyleNames) - (nLoc + Len(sStyle)))
            If Right(sCharStyleNames, 1) = "," Then sCharStyleNames = Left(sCharStyleNames, Len(sCharStyleNames) - 1)
        Else
            sCharStyleNames = sCharStyleNames & sStyle
        End If
    End If
    mCharStyleNames = Split(sCharStyleNames, ",")
    If IsEmpty(mCharStyleNames) Then
        oPortion.setPropertyToDefault ("CharStyleNames")
    ElseIf UBound(mCharStyleNames) < 0 Then
        oPortion.setPropertyToDefault ("CharStyleNames")
    Else
        oPortion.setPropertyToDefault ("CharStyleNames")
        oPortion.setPropertyValue("CharStyleNames", mCharStyleNames)
    End If
Wend
End Sub


Sub subResetProperties(oPortion, mResetProps)
For i = 0 To UBound(mResetProps)
    oPortion.setPropertyToDefault (mResetProps(i))
Next
End Sub

Function fnIsItalic(oCursor) As Boolean
    #If OOO Then
        If oCursor.CharPosture <> 2 Then
            fnIsItalic = False
        Else
            fnIsItalic = True
        End If
    #Else
        If oCursor.Italic Then
            Rem Word gives true if one word in the range is bold
            Rem so remove it
            Dim isItalic As Boolean
            isItalic = True
            nIndex = fnGetCurrentParagraphNumber
            For Each wd In ActiveDocument.Paragraphs(nIndex).Range.Words
                If Not wd.Italic Then
                    isItalic = False
                    Exit For
                End If
            Next
        
            fnIsItalic = isItalic
        Else
            fnIsItalic = False
        End If
    #End If
End Function

Function fnIsBold(oCursor) As Boolean
    #If OOO Then
        If oCursor.CharWeight = 150 Then
            fnIsBold = True
        Else
            fnIsBold = False
        End If
    #Else
        If oCursor.Bold Then
            Rem Word gives true if one word in the range is bold
            Rem so remove it
            Dim isBold As Boolean
            isBold = True
            nIndex = fnGetCurrentParagraphNumber
            For Each wd In ActiveDocument.Paragraphs(nIndex).Range.Words
                If Not wd.Bold Then
                    isBold = False
                    Exit For
                End If
            Next
            fnIsBold = isBold
        Else
            fnIsBold = False
        End If
    #End If
End Function


