Attribute VB_Name = "StyleUnitTest"
Rem  To Test the style
#Const MSWD = True
#Const OOO = Not MSWD

Sub test()
   Call testStyle
End Sub


Sub testStyle()
    Dim oTables, oTable
    Dim i
    Dim oTableCursor, oText
    Dim RowIndex, ColIndex
    Dim Rows, Cols
    Dim boo As Boolean
    Dim keywords As Variant
    
    errMsg = ""
    testmode = True
    setTestmode (True)
    
    
    #If OOO Then
        oTables = ThisComponent.getTextTables()
    
        If Not oTables.hasElements() Then
            MsgBox "Cannot find the test tables. Use 'toolbat_test.odt' file for Testing"
            Exit Sub
        End If
        
    
        For i = 0 To oTables.getCount() - 1
            oTable = oTables.getByIndex(i)
            oPars = oTable.getCellByName("A1").GetText().createEnumeration()
            oOldSelection = ThisComponent.CurrentSelection
            Do While oPars.hasMoreElements()
                oPar = oPars.nextElement()
                Rem select the paragraph
                ThisComponent.CurrentController.Select (oPar)
                oVC = fnGetViewCursor
                If oPar.getString = "" Then
                    Exit Do
                End If
                
                keywords = Split(oPar.getString, " ")
                If LCase(keywords(0)) <> "given" And LCase(keywords(0)) <> "test" Then
                    If InStr(LCase(keywords(0)), "given") <> 0 Then
                        pos = InStr(LCase(keywords(0)), "given")
                    Else
                        pos = InStr(LCase(keywords(0)), "test")
                    End If
                    pos = pos - 1
                    keywords(0) = Right(keywords(0), Len(keywords(0)) - pos)
                End If
                If LCase(keywords(0)) = "given" Then
                    If keywords(1) <> oPar.paraStyleName Then
                        Rem if the given statement doesnot have the style. then apply the style.
                        subSetParaStyleName(oVC, keywords(1))
                    End If
                End If
                
                If LCase(keywords(0)) = "test" Then
                    If keywords(1) <> oPar.paraStyleName Then
                        Rem if the test statement doesn't have the prestyle then apply it.
                        subSetParaStyleName(oVC, keywords(1))
                    End If
                    If processEvent(CStr(keywords(2)), CStr(Trim(keywords(3)))) Then
                        errMsg = fnGetErrMsg()
                        If CStr(keywords(3)) = oPar.paraStyleName Then
                                If errMsg <> "" Then
                                    message = "RESULT: " + "PASSED with error Message shown '" + errMsg + "'"
                                    errMsg = ""
                                Else
                                    message = "RESULT: " + "PASSED"
                                End If
                                
                            Else
                                If errMsg = "" Then
                                    message = "RESULT: FAILED : Paragraph Style (" + oPar.paraStyleName + ") is not PosStyle : " + keywords(3) + "'"
                                Else
                                    message = "RESULT: FAILED : Paragraph Style (" + oPar.paraStyleName + ") is not PosStyle : " + keywords(3) + "." + "with error message '" + errMsg + "'"
                                End If
                            End If
                        End If
                        Rem oVC.goToEndofParagraph(1,False)
                        printResult (message)
                        subSetErrMsg ("")
                End If
            Loop
        Next
        
    #Else
        Selection.Bookmarks.Add ("CurrentCursorPosition")
        If ActiveDocument.Tables.count = 0 Then
            MsgBox "Cannot find the test tables. Use 'toolbat_test.doc' file for Testing"
            Exit Sub
        End If
         For i = 1 To ActiveDocument.Tables.count
         
            With ActiveDocument.Tables(i)
                For j = 1 To .Cell(1, 1).Range.Paragraphs.count
                    .Cell(1, 1).Range.Paragraphs(j).Range.Select
                    keywords = Split(CStr(.Cell(1, 1).Range.Paragraphs(j).Range.Text))

                  
                    If LCase(keywords(0)) = "given" Then
                        If keywords(1) <> .Cell(1, 1).Range.Paragraphs(j).style Then
                            .Cell(1, 1).Range.Paragraphs(j).style = keywords(1)
                        End If
                        
                    End If
                    If LCase(keywords(0)) = "test" Then
                         keywords(3) = Left(keywords(3), Len(keywords(3)) - 1)
                        If StrComp(keywords(1), .Cell(1, 1).Range.Paragraphs(j).Format.style) <> 0 Then
                            Rem in case style is not the pre style
                            .Cell(1, 1).Range.Paragraphs(j).style = keywords(1)
                        End If
                        
                        
                        
                        If processEvent(CStr(keywords(2)), CStr(Trim(keywords(3)))) Then
                            Rem check the result style
                           
                           errMsg = fnGetErrMsg()
                           If StrComp(CStr(keywords(3)), Trim(.Cell(1, 1).Range.Paragraphs(j).style), vbTextCompare) = 0 Then
                            
                           Rem  If strCompare(CStr(Trim(Keywords(3))), .Cell(1, 1).Range.Paragraphs(j).style) Then
                                If errMsg <> "" Then
                                    message = "RESULT: " + "PASSED with error Message shown '" + errMsg + "'"
                                    errMsg = ""
                                Else
                                    message = "RESULT: " + "PASSED"
                                End If
                                
                            Else
                                If errMsg = "" Then
                                    message = "RESULT: FAILED : Paragraph Style (" + .Cell(1, 1).Range.Paragraphs(j).style + ") is not PosStyle : " + keywords(3) + "'"
                                Else
                                    message = "RESULT: FAILED : Paragraph Style (" + .Cell(1, 1).Range.Paragraphs(j).style + ") is not PosStyle : " + "." + "with error message '" + errMsg + "'"
                                End If
                            End If
                        End If
                         Selection.Collapse (wdCollapseEnd)
                        printResult (message)
                        subSetErrMsg ("")
                    End If
                    
                    
                Next
           End With
        Next
      
       
        
        Rem reset the current position and then delete the bookmark
        If Selection.Bookmarks.Exists("CurrentCursorPosition") Then
            Selection.GoTo what:=wdGoToBookmark, name:="CurrentCursorPosition"
            ActiveDocument.Bookmarks("CurrentCursorPosition").Delete
        End If
    #End If
    
    setTestmode (False)
    MsgBox "done testing"
    Exit Sub
End Sub


Function processEvent(fnName As String, posStyle As String)
    Select Case fnName
        Case "DemoteButton"
            Call toolbar.eventDemoteButton
            processEvent = True
        Case "PromoteButton"
            Call toolbar.eventPromoteButton
            processEvent = True
        Case "TitleButton"
            Call toolbar.eventTitleButton
            processEvent = True
        Case "HeadingButton"
            Call toolbar.eventHeadingButton
            processEvent = True
        Case "LeftAlignedButton"
            Call toolbar.LeftAlignedParagraph
            processEvent = True
        Case "IndentButton"
            Call toolbar.IndentParagraph
            processEvent = True
        Case "CenterAlignedButton"
            Call toolbar.CenterAlignedParagraph
            processEvent = True
        Case "RightAlignedButton"
            Call toolbar.RightAlignedParagraph
            processEvent = True
        Case "BlockQuoteButton"
            Call toolbar.eventBlockQuoteButton
            processEvent = True
        Case "DefinitionButton"
            Call toolbar.Definition
            processEvent = True
        Case "PreformattedButton"
            Call toolbar.Preformatted
            processEvent = True
        Case "BulletButton"
            Call toolbar.eventBulletButton
            processEvent = True
        Case "NumberiseButton"
            Call toolbar.eventNumberiseButton
            processEvent = True
        Case Else
            #If MSWD Then
                Selection.Range.Collapse (wdCollapseEnd)
            #End If
            MsgBox fnName
            printResult ("This function is not yet implemented")
            processEvent = False
    End Select
End Function



Sub restore()
    Dim oTables As Object, oTable As Object
    Dim i As Integer
    Dim oText As Object
    Rem set the require field
    errMsg = ""
    
    setTestmode (True)
    #If OOO Then
        oTables = ThisComponent.getTextTables()
    
        If Not oTables.hasElements() Then
            If MsgBox("This document is not the test document.  This process will delete all paragraphs.  Are you sure you want to continue?", 4, "ICE Warning") = 7 Then
                Exit Sub
            End If
        ElseIf oTables.getByIndex(0).Columns.count <> 1 Then
            If MsgBox("This document is not the test document.  This process will delete all paragraphs.  Are you sure you want to continue?", 4, "ICE Warning") = 7 Then
                Exit Sub
            End If
        End If

        For i = 0 To oTables.getCount() - 1
            oTable = oTables.getByIndex(i)
            oPars = oTable.getCellByName("A1").GetText().createEnumeration()
            oOldSelection = ThisComponent.CurrentSelection
            Do While oPars.hasMoreElements()
                oPar = oPars.nextElement()
                Rem select the paragraph
                ThisComponent.CurrentController.Select (oPar)
                oVC = fnGetViewCursor

                If oPar.getString = "" Then
                    Exit Do
                End If
                
                keywords = Split(oPar.getString, " ")

                
                If LCase(keywords(0)) = "given" Then
                    If keywords(1) <> oPar.paraStyleName Then
                        Rem if the given statement doesnot have the style. then apply the style.
                        subSetParaStyleName(oVC, keywords(1))
                    End If
                End If
                
                If LCase(keywords(0)) = "test" Then
                    If keywords(1) <> oPar.paraStyleName Then
                        Rem if the test statement doesn't have the prestyle then apply it.
                        subSetParaStyleName(oVC, keywords(1))
                    End If
                End If
                
                If LCase(keywords(0)) = "result:" Then
                    oCursor = oVC.GetText().createTextCursorByRange(oPar)

                    oCursor.setString ("here")
                    If oCursor.gotoPreviousParagraph(False) Then
                        oCursor.gotoEndOfParagraph (False)
                        oCursor.gotoNextParagraph (True)
                        oCursor.gotoEndOfParagraph (True)
                        oCursor.setString ("")
                    End If
                End If
            Loop
        Next
        Call removeStylesResult
    #Else
        Selection.Bookmarks.Add ("CurrentCursorPosition")
        If ActiveDocument.Tables.count = 0 Then
            MsgBox "Cannot find the test tables. Use 'toolbat_test.doc' file for Testing"
            Exit Sub
        End If
         For i = 1 To ActiveDocument.Tables.count
            With ActiveDocument.Tables(i)
                For j = 1 To .Cell(1, 1).Range.Paragraphs.count
                    On Error Resume Next
                    With .Cell(1, 1).Range.Paragraphs(j)
                        .Range.Select
                      If InStr(.Range.Text, "RESULT") <> 0 Then
                          .Range.Text = ""
                      Else
                          If .Range.Text <> "" Then
                            keywords = Split(CStr(.Range.Text))
                            If keywords(0) = "GIVEN" Or keywords(0) = "TEST" Then
                                If UBound(keywords) > 1 Then
                                    .style = keywords(1)
                                Else
                                    .style = "p"
                                End If
                            End If
                        End If
                      End If
                       Selection.Collapse (wdCollapseEnd)
                       
                     End With
                Next
           End With
        Next
        On Error GoTo 0
       
        
        Rem reset the current position and then delete the bookmark
        If Selection.Bookmarks.Exists("CurrentCursorPosition") Then
            Selection.GoTo what:=wdGoToBookmark, name:="CurrentCursorPosition"
            ActiveDocument.Bookmarks("CurrentCursorPosition").Delete
        End If
    #End If
    setTestmode (False)
    MsgBox "done restoring"
    Exit Sub

End Sub

Sub removeStylesResult()
    Dim oPars As Object, oPar As Object
    Dim str As String
    Dim pos As Integer
    oOldSelection = ThisComponent.CurrentSelection
    oPars = ThisComponent.GetText().createEnumeration()
    Do While oPars.hasMoreElements()
        oPar = oPars.nextElement()
        Rem if paragraph is a text paragraph, then delete it.
        If oPar.supportsService("com.sun.star.text.Paragraph") Then
            oPar.setString ("")
        End If
    Loop

    Rem restore the selection. or deselect the paragraph
    ThisComponent.CurrentController.Select (oOldSelection)

End Sub
