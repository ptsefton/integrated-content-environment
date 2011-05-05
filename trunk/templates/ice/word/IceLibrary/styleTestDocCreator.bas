Attribute VB_Name = "styleTestDocCreator"
#Const MSWD = True
#Const OOO = Not MSWD

Sub createTestDocument()
    Rem create text document
    Rem this is mainly to create the test document. thus should not visible to general users.
    
    ans = MsgBox("Are you sure you want to use this current document? This process will delete all document content", 1, "Create Text Document")
    If ans = 1 Then
        #If MSWD Then
            ActiveDocument.Select
            ActiveDocument.Range.InsertParagraph
        #Else
            oVC = fnGetViewCursor()
            oVC.goToStart (False)
        #End If
        
        Rem  make sure we have all the styles
        subCreateAllMissingStyles
        
        Rem create the test cases
        addThisTestCases ("PromoteButton")
        addThisTestCases ("DemoteButton")
        addThisTestCases ("TitleButton")
        addThisTestCases ("HeadingButton")
        addThisTestCases ("LeftAlignedButton")
        addThisTestCases ("IndentButton")
        addThisTestCases ("CenterAlignedButton")
        addThisTestCases ("RightAlignedButton")
        addThisTestCases ("BlockQouteButton")
        addThisTestCases ("DefinitionButton")
        addThisTestCases ("PreformattedButton")
        addThisTestCases ("BulletButton")
        addThisTestCases ("NumberiseButton")
        
        Rem saving the document Word only. OOo needs to add Test and restore button
        Rem so i haven't adding the saving part of it.
        #If MSWD Then
          '  ActiveDocument.SaveAs fileName:="Test Document.doc"
        #End If
        MsgBox "Done creating test document"
    End If

End Sub



Sub addThisTestCases(sBtnName As String)
    Rem this add testcases for each button
    testCases = fnGetTestCases(sBtnName)
    For Each testCase In testCases
        createTable (testCase)
    Next
End Sub

Sub createTable(testCase As Variant)
Rem Create each test as table
Rem param : testCase(ButtonName,sStyle,sPrevStyle,sResultStyle)

Rem get the style names
sBtnName = Split(testCase(0), " : ")(0)
Rem if you want to see the test number comment the above and uncomment the following
Rem sBtnName = testCase(0)
sStyle = testCase(1)
sPrevStyles = testCase(2)
sResultStyle = testCase(3)

#If MSWD Then
    'move to end
    Selection.Move unit:=wdStory
    
    'add paragraph
    Selection.TypeParagraph
    
    'now add a table
    Set tbl = ActiveDocument.Tables.Add(Selection.Range, 1, 1)
    
    Rem now add the data
    With tbl.Cell(1, 1).Range
        .Text = "Case : " + testCase(0)
        .style = "p"
        For Each sPrevStyle In sPrevStyles
            If sPrevStyle <> "" Then
                .InsertParagraphAfter
                .InsertAfter ("GIVEN " + sPrevStyle)
                .Paragraphs(.Paragraphs.count).Range.style = sPrevStyle
            End If
        Next
        .InsertParagraphAfter
        .InsertAfter ("TEST " + sStyle + " " + sBtnName + " " + sResultStyle)
        .Paragraphs(.Paragraphs.count).Range.style = sStyle
        .InsertParagraphAfter
        .Paragraphs(.Paragraphs.count).Range.style = "p"
    End With
#Else
    ' create table
    oTextTable = ThisComponent.createInstance("com.sun.star.text.TextTable")
    oTextTable.initialize(1,1)
    
    Rem create text cursor
    oCursor = ThisComponent.GetText().createTextCursor()
    oCursor.goToEnd (False)
    Rem insert table
    oCursor.getText().insertTextContent(oCursor,oTextTable,false)
    Rem get the cell cursor
    oCell = oTextTable.getCellByName("A1")
    oCellCursor = oCell.createTextCursor()

    Rem Insert Text seemly paragraph
    oCellCursor.String = "Case : " + testCase(0)
    subSetParaStyleName(oCellCursor, "p")
    oCellCursor.gotoEndofParagraph(1,False)
    oCellCursor.getText().insertControlCharacter(oCellCursor, com.sun.star.text.ControlCharacter.PARAGRAPH_BREAK, False)
    For Each sPrevStyle In sPrevStyles
        If sPrevStyle <> "" Then
            oCellCursor.String = "GIVEN " + sPrevStyle
            subSetParaStyleName(oCellCursor, sPrevStyle)
            oCellCursor.gotoEndofParagraph(1,False)
            oCellCursor.getText().insertControlCharacter(oCellCursor, com.sun.star.text.ControlCharacter.PARAGRAPH_BREAK, False)
        End If
    Next
    oCellCursor.String = "TEST " + sStyle + " " + sBtnName + " " + sResultStyle

    subSetParaStyleName(oCellCursor, sStyle)
    oCellCursor.gotoEndOfParagraph (False)

    Rem insert line break
    oPar = ThisComponent.createInstance("com.sun.star.text.Paragraph")
    
    ThisComponent.getText().insertTextContentAfter(oPar,oTextTable)
    oCursor.goToEnd (False)

#End If

End Sub

