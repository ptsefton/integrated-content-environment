Attribute VB_Name = "Hint"
#Const MSWD = True
#Const OOO = Not MSWD

Rem *********************************************************************
Rem    University of Southern Queensland
Rem    Author : Cynthia
Rem    Hint Image reference :
Rem    http://commons.wikimedia.org/wiki/File:Help-books-aj.svg_aj_ash_01.svg#file,  By Schmierer,  320x320(31KB),  22/March/2006 with GNU General Public Liciense
Rem *********************************************************************
Sub Hint()
    #If OOO Then
           Rem this function is to load the hint function menu. thus not for word
        Dim oAutoTextContainer As Object, oAutoGroup
        Dim count As Integer, n As Integer
        Dim AutoName As String
        oAutoTextContainer = createUnoService("com.sun.star.text.AutoTextContainer")
        Dim Flag As Boolean
        count = 0

        If Not oAutoTextContainer.hasByName("ICE Hint") Then
            printMsgbox ("Sorry.  Hint AutoText does not exist. Reinstall the ICE Hint.bau or Check the AutoText Path")
        Else
            For n = 0 To oAutoTextContainer.count - 1
                oAutoGroup = oAutoTextContainer.getByIndex(n)

                If oAutoGroup.Title = "ICE Hint" Then
                    If count = 0 Then
                        AutoName = oAutoGroup.name
                    End If
                    count = count + 1
                End If
            Next n
            If count > 1 Then

                oAutoTextContainer.removeByName (AutoName)
                Flag = False
            End If
            oAutoGroup = oAutoTextContainer.getByName("ICE Hint")
            For n = 0 To oAutoGroup.count - 1
                If oAutoGroup.Titles(n) = "Hint-empty" Then
                    DialogLibraries.LoadLibrary ("IceLibrary")
                    oDialog = CreateUnoDialog(DialogLibraries.IceLibrary.dlgHint)
                    oDialog.Execute
                    oDialog.dispose
                    Exit Sub
                Else
                    printMsgbox ("Sorry.  Hint AutoText does not exist. Reinstall the ICE Hint.bau or Check the AutoText Path")
                End If
            Next
        End If
    #End If
End Sub

Sub insertHint()
    Rem only for OOo
    Rem ----------------------------------------------------------------------
    #If OOO Then
        Dim Document   As Object
        Dim dispatcher As Object
        Dim oAutoTextContainer As Object, oAutoTextCursor, oAutoGroup
        Dim oAutoText As Object
        Dim Flag As Boolean
        Dim groupTitle As String
        Dim count As Integer, n As Integer, i As Integer
        groupTitle = ""
        Flag = False
        count = 0
        oAutoTextContainer = createUnoService("com.sun.star.text.AutoTextContainer")
        oAutoTextCursor = ThisComponent.Text.GetText().createTextCursor()
        For n = 0 To oAutoTextContainer.count - 1
           On Error GoTo noAutoText
            oAutoGroup = oAutoTextContainer.getByIndex(n)

            If oAutoGroup.Title = "ICE Hint" Then

                    For i = 0 To oAutoGroup.count - 1
                    If oAutoGroup.Titles(i) = "Hint-empty" Then
                        groupTitle = oAutoGroup.Title

                        Document = ThisComponent.CurrentController.Frame
                        dispatcher = createUnoService("com.sun.star.frame.DispatchHelper")

                        Rem ----------------------------------------------------------------------

                        Dim args4(0) As New com.sun.star.beans.PropertyValue
                        args4(0).name = "Group"
                        args4(0).value = groupTitle

                        dispatcher.executeDispatch(document, ".uno:SetActGlossaryGroup", "", 0, args4())

                        Rem --------    --------------------------------------------------------------
                        Dim args5(1) As New com.sun.star.beans.PropertyValue
                        args5(0).name = "Group"
                        args5(0).value = groupTitle
                        args5(1).name = "ShortName"
                        args5(1).value = "H"

                        dispatcher.executeDispatch(document, ".uno:InsertGlossary", "", 0, args5())
                        If Int(getOOoVersion()) = 2 Then
                            showHint()
                        End If
                        Exit Sub
                    End If
                Next i
            End If
        Next n
noAutoText:
        printMsgbox ("Hint AutoText does not exist. Please update the ICE AutoText file.")
    #End If

End Sub

Sub DeleteallHints()
Rem ==================================================================================
Rem  Loop through the tables in the document. If the table is Hint table, then delete the table
Rem ==================================================================================

    #If MSWD Then
        If fnIsThereAFile Then
            If ActiveDocument.Tables.count = 0 Then
                Rem Make sure there are tables in the doc...
                Exit Sub
            Else
    
                Dim aTable, subTable
                Dim aCell
    
                For Each aTable In ActiveDocument.Tables
                    Rem - Loop through the cells -----------------------
                    On Error GoTo notTrue
                    If aTable.Range.Cells.Item(2).ColumnIndex = 2 And aTable.Range.Cells.count = 3 Then
                        Set aCell = aTable.Cell(1, 2)
                        If aCell.Range.Paragraphs.count = 1 And aCell.Range.Paragraphs.style = "p-hint" Then
                           aTable.Delete
                        End If
                    Else
notTrue:
                        For Each subTable In aTable.Tables
                            On Error GoTo notTrue2
                            If subTable.Range.Cells.Item(2).ColumnIndex = 2 And subTable.Range.Cells.count = 3 Then
                                Set aCell = subTable.Cell(1, 2)
                                If aCell.Range.Paragraphs.count = 1 And aCell.Range.Paragraphs.style = "p-hint" Then
                                    subTable.Delete
                                End If
                            End If
notTrue2:
                            
                        Next subTable
                    End If
                Next aTable
            End If
        End If
    #Else
        Dim oTables, oTable, oCell
        Dim i, count
        Dim oTableCursor, oText, oCellCursor
        Dim sCellName
        Dim RowIndex, ColIndex
        Dim Rows, Cols
        Dim boo As Boolean

        oTables = ThisComponent.getTextTables()

        If Not oTables.hasElements() Then Exit Sub
        count = oTables.getCount() - 1
        For i = 0 To count
            oTable = oTables.getByIndex(i)
            Rows = oTable.getRows()
            Cols = oTable.getColumns()
            oTableCursor = oTable.createCursorByCellName("A1")
            oTableCursor.goRight(1,false)
            sCellName = oTableCursor.getRangeName()
            oCell = oTable.getCellByName(sCellName)
            oCellCursor = oCell.createTextCursor()
            If oCellCursor.paraStyleName = "p-hint" Then
                ThisComponent.GetText().removetextcontent (oTable)
                oTables = ThisComponent.getTextTables()
                If Not oTables.hasElements() Then Exit Sub
                count = oTables.getCount() - 1
                i = -1
             End If
        Next
    #End If
End Sub



Sub HideHints()
Rem ==================================================================================
Rem  Loop through the tables in the document. If the table contains cells with
Rem  one of our AuthorIT table styles then format it accordingly. Otherwise skip it.

Rem ==================================================================================
    #If MSWD Then
        If fnIsThereAFile() Then
            If ActiveDocument.Tables.count = 0 Then
                Rem Make sure there are tables in the doc...
                Exit Sub
            Else
    
                Dim aTable, subTable
                Dim aCell
    
                Rem - Loop through the tables -----------------------
                For Each aTable In ActiveDocument.Tables
                    Rem - Loop through the cells -----------------------
                    On Error GoTo notTrue
                    aTable.Range.Font.Hidden = False
                    If aTable.Range.Cells.count = 3 And aTable.Range.Cells.Item(2).ColumnIndex = 2 Then
                        Set aCell = aTable.Cell(1, 2)
                        If aCell.Range.Paragraphs.count = 1 And aCell.Range.Paragraphs.style = "p-hint" Then
                           aTable.Range.Font.Hidden = True
                        End If
                    Else
notTrue:
                        For Each subTable In aTable.Tables
                            On Error GoTo notTrue2
                            If subTable.Range.Cells.Item(2).ColumnIndex = 2 And subTable.Range.Cells.count = 3 Then
                                Set aCell = subTable.Cell(1, 2)
    
                                If aCell.Range.Paragraphs.count = 1 And aCell.Range.Paragraphs.style = "p-hint" Then
                                    Selection.Bookmarks.Add ("CurrentPos")
                                    subTable.Range.Select
                                    Selection.MoveEnd
                                    Selection.Range.InsertAfter vbNewLine
    
                                    subTable.Range.Font.Hidden = True
    
                                    Rem reset the current position and then delete the bookmark
                                    Selection.GoTo what:=wdGoToBookmark, name:="CurrentPos"
                                    ActiveDocument.Bookmarks("CurrentPos").Delete
                                End If
    
                            End If
notTrue2:
                        Next subTable
                    End If
                Next aTable
    
            End If
        End If
    #Else
        Dim oTables, oTable, oCell
        Dim i, count
        Dim oTableCursor, oText, oCellCursor
        Dim sCellName
        Dim RowIndex, ColIndex
        Dim Rows, Cols
        Dim boo As Boolean

        oTables = ThisComponent.getTextTables()

        If Not oTables.hasElements() Then Exit Sub

        For i = 0 To oTables.getCount() - 1
            oTable = oTables.getByIndex(i)
            Rows = oTable.getRows()
            Cols = oTable.getColumns()
            oTableCursor = oTable.createCursorByCellName("A1")
            oTableCursor.goRight(1,false)
            sCellName = oTableCursor.getRangeName()
            oCell = oTable.getCellByName(sCellName)
            oCellCursor = oCell.createTextCursor()
            If oCellCursor.paraStyleName = "p-hint" Then
                oTableCursor.goLeft(1,false)

                For RowIndex = 1 To Rows.getCount()
                    For ColIndex = 1 To Cols.getCount()
                        sCellName = Chr(64 + ColIndex) & RowIndex
                        oCell = oTable.getCellByName(sCellName)
                        oCellCursor = oCell.createTextCursorByRange(oCell)
                    Rem    boo = not(oCellCursor.charHidden)
                        oCellCursor.charHidden = True
                     Next
                Next
                hideTableBoundary()
             End If

        Next
    #End If
End Sub




Sub ShowHints()

Rem ==================================================================================
Rem  Loop through the tables in the document. If the table contains cells with
Rem  one of our AuthorIT table styles then format it accordingly. Otherwise skip it.

Rem ==================================================================================
    #If MSWD Then
        If fnIsThereAFile() Then
            If ActiveDocument.Tables.count = 0 Then
             Rem Make sure there are tables in the doc...
                Exit Sub
            Else
    
                Dim aTable, subTable
                Dim aCell
    
                Rem - Loop through the tables -----------------------
                For Each aTable In ActiveDocument.Tables
                    Rem - Loop through the cells -----------------------
                    On Error GoTo notTrue
                    If aTable.Range.Cells.Item(2).ColumnIndex = 2 And aTable.Range.Cells.count = 3 Then
                        Set aCell = aTable.Cell(1, 2)
                        If aCell.Range.Paragraphs.count = 1 And aCell.Range.Paragraphs.style = "p-hint" Then
                           aTable.Range.Font.Hidden = False
                        End If
                    Else
notTrue:
                        For Each subTable In aTable.Tables
                           On Error GoTo notTrue2
                            If subTable.Range.Cells.Item(2).ColumnIndex = 2 And subTable.Range.Cells.count = 3 Then
                                Set aCell = subTable.Cell(1, 2)
                                If aCell.Range.Paragraphs.count = 1 And aCell.Range.Paragraphs.style = "p-hint" Then
                                    subTable.Range.Font.Hidden = False
                                End If
                            End If
notTrue2:
                        Next subTable
                    End If
                Next aTable
    
            End If
        End If
    #Else

        Dim oTables, oTable, oCell
        Dim i, count
        Dim oTableCursor, oText, oCellCursor
        Dim sCellName
        Dim RowIndex, ColIndex
        Dim Rows, Cols
        Dim boo As Boolean
        oTables = ThisComponent.getTextTables()

        If Not oTables.hasElements() Then Exit Sub

        For i = 0 To oTables.getCount() - 1
            oTable = oTables.getByIndex(i)
            Rows = oTable.getRows()
            Cols = oTable.getColumns()
            oTableCursor = oTable.createCursorByCellName("A1")
            oTableCursor.goRight(1,false)
            sCellName = oTableCursor.getRangeName()
            oCell = oTable.getCellByName(sCellName)
            oCellCursor = oCell.createTextCursor()
            If oCellCursor.paraStyleName = "p-hint" Then
                oTableCursor.goLeft(1,false)

                For RowIndex = 1 To Rows.getCount()
                    For ColIndex = 1 To Cols.getCount()
                        sCellName = Chr(64 + ColIndex) & RowIndex
                        oCell = oTable.getCellByName(sCellName)
                        oCellCursor = oCell.createTextCursorByRange(oCell)
                        oCellCursor.charHidden = False
                     Next
                Next
                hideTableBoundary()
             End If

        Next

    #End If
End Sub

Sub hideTableBoundary()
    #If OOO Then
        Rem OOO only
        Rem this hide the table boundary property of the doucment
        Rem ----------------------------------------------------------------------
        Rem define variables
        Dim Document   As Object
        Dim dispatcher As Object
        Rem ----------------------------------------------------------------------
        Rem get access to the document
        Document = ThisComponent.CurrentController.ViewSettings
        document.setPropertyValue("ShowTableBoundaries",false)
    #End If
End Sub



