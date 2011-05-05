Attribute VB_Name = "Xrefmod"
Option Explicit
#Const MSWD = True
#Const OOO = Not MSWD

' Revised: 2007-08-30

Rem To present a custom dialog for the creation of cross references

Rem This is the main module sheet.
Rem Subroutines that I have written, the name starts with sub, and for functions fn
Rem If they are called by an event then the routine name starts with subEvent

Rem *********************************************************************
Rem     Copyright (C) 2006  Distance and e-Learning Centre,
Rem     University of Southern Queensland
Rem
Rem     This program is free software; you can redistribute it and/or modify
Rem     it under the terms of the GNU General Public License as published by
Rem     the Free Software Foundation; either version 2 of the License, or
Rem     (at your option) any later version.
Rem
Rem     This program is distributed in the hope that it will be useful,
Rem     but WITHOUT ANY WARRANTY; without even the implied warranty of
Rem     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
Rem     GNU General Public License for more details.
Rem
Rem     You should have received a copy of the GNU General Public License
Rem     along with this program; if not, write to the Free Software
Rem     Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
Rem
Rem *********************************************************************

Rem ************************************************************
Rem   Author Ian Laurenson
Rem ************************************************************

Rem -----------------------------------------------------------------
Rem  Constants
Rem -----------------------------------------------------------------
Const nIndent = 3               'Number spaces at left of item in listbox acting as tree control
Const HIDDEN_SECTION_NAME = "XRefSection"


Rem -----------------------------------------------------------------
Rem  Variables common to functions in this library (library variables)
Rem -----------------------------------------------------------------
Private oDialog As Object       'Points to the dialog dlgCrossRef
Private oDoc As Object          'Points to the current document
Private oCurSelection As Object 'Points to the current selection
Private mOutlines()             'Holds the text of the headings, the level, and name of reference
Private mLinks()                'For each item in listbox mLinks holds the index of the corresponding
                                'entry in mOutlines
Private nHeadCount As Long      'The number of heading paragraphs in the document
Private mDocs()
Global mXRefDialogSettings(0)  'Holds the current settings of the dialog. Global so settings are still
                                'available for next time dialog is called.

Rem =====================================================
Rem     Main entry point.
Rem     Procedure to initialise and display the dialog box
Rem =====================================================
Sub CrossReference()
    #If MSWD Then
        If Not fnIsThereAFile() Then
            Exit Sub
        End If
        #If Mac Then
            MsgBox "Sorry, this feature is not available in Word on the Mac."
            End
        #End If
    #End If
    Rem A routine to present a custom dialog for the creation of cross references to
    Rem outlined heading levels
    #If MSWD Then
        Set oDoc = ActiveDocument
        Set oDialog = Xref
    #Else
        oDoc = thisComponent REM stardesktop.currentComponent
        Rem Check that we are in a text document and that text is selected
        If Not oDoc.supportsService("com.sun.star.text.GenericTextDocument") Then
            MsgBox "Sorry - only text documents can have cross references to outlined headings", 16, "Error"
            Exit Sub
        End If

        oCurSelection = oDoc.CurrentSelection

        If Not oCurSelection.supportsService("com.sun.star.text.TextRanges") Then
            MsgBox "Sorry - I can't handle anything being selected except text.", 16, "Error"
            Exit Sub
        End If

        DialogLibraries.LoadLibrary ("IceLibrary")
        oDialog = CreateUnoDialog(DialogLibraries.IceLibrary.dlgCrossRef)
    #End If


    Rem Set-up other module variables
    Call subBuildHeadingArray(oDoc)

    subLoadType

    Rem Set-up the dialog

Rem      subLoadDialogSettings
    subCurrentWriterDocuments


Rem  Present the dialog
    #If MSWD Then
        oDialog.ComboBoxLevel.list = Array("1", "2", "3", "4", "5")
     oDialog.ComboBoxLevel.value = "1"
        Call subShowLevel(oDialog.ListBoxHeadings, 1)

        oDialog.Show
    #Else
        oDialog.getControl("ListBoxLevel").selectItemPos(0, true)
        subShowLevel(oDialog.getControl("ListBoxHeadings"), oDialog.getControl("ListBoxLevel").selectedItemPos + 1)
        oDialog.model.Step = 1
        oDialog.Execute
        oDialog.dispose
    #End If
End Sub


Sub subEventType(oObject)
    subChangeType
End Sub


Sub subChangeType()
    Dim oListbox, mDependentTextFields, oAnchor, oCursor, i As Integer
    Dim sType As String, nLevel As Integer, bShowHidden As Boolean

    #If MSWD Then
        sType = oDialog.ComboBoxType.value
        Set oListbox = oDialog.ListBoxHeadings
    #Else
        sType = oDialog.getControl("ListBoxType").SelectedItem
        oListbox = oDialog.getControl("ListBoxHeadings")
    #End If

    Select Case sType
    Case "Headings"
        #If MSWD Then
            oDialog.ComboBoxLevel.Visible = True
            nLevel = Val(oDialog.ComboBoxLevel.value)
            oDialog.CheckBoxRef.Visible = True
            oDialog.CheckBoxLeft.Visible = False
            oDialog.CheckBoxRight.Visible = False
        #Else
            oDialog.model.Step = 1
            nLevel = oDialog.getControl("ListBoxLevel").selectedItemPos + 1
        #End If
        Call subBuildHeadingArray(oDoc)
        Call subShowLevel(oListbox, nLevel)
    Case "Bookmarks"
        #If MSWD Then
            oDialog.ComboBoxLevel.Visible = False
            oDialog.CheckBoxRef.Visible = True
            oDialog.CheckBoxLeft.Visible = False
            oDialog.CheckBoxRight.Visible = False
            bShowHidden = oDoc.Bookmarks.ShowHidden
            oDoc.Bookmarks.ShowHidden = True
        #Else
            oDialog.model.Step = 2
        #End If
        Call subRemoveListboxItems(oListbox)
        For i = 0 To oDoc.Bookmarks.count - 1
            Rem oListbox.addItems(oDoc.Bookmarks.ElementNames, 0)
            #If MSWD Then
                Call subListBoxAddItem(oListbox, oDoc.Bookmarks(i + 1).name & " - " & oDoc.Bookmarks(i + 1).Range.Text, i)

            #Else
                Call subListBoxAddItem(oListbox, oDoc.Bookmarks.getByIndex(i).name & " - " & oDoc.Bookmarks.getByIndex(i).Anchor.String, i)
            #End If
            Rem oListbox.addItem(oDoc.Bookmarks.getByIndex(i).name & " - " & oDoc.Bookmarks.getByIndex(i).anchor.string, i)
        Next
        #If MSWD Then
            oDoc.Bookmarks.ShowHidden = bShowHidden
        #End If
    Case Else
        #If MSWD Then
            oDialog.ComboBoxLevel.Visible = False
            oDialog.CheckBoxRef.Visible = False
            oDialog.CheckBoxLeft.Visible = True
            oDialog.CheckBoxRight.Visible = True
        #Else
            oDialog.model.Step = 3
        #End If
        Call subRemoveListboxItems(oListbox)
        #If MSWD Then
            Dim oField
            i = 0
            For Each oField In oDoc.Fields
                If InStr(UCase(oField.Code), sType) > 0 Then
                    Call subListBoxAddItem(oListbox, oField.result.Paragraphs(1).Range.Text, i)
                    i = i + 1
                End If
            Next
        #Else
            mDependentTextFields = oDoc.TextFieldMasters.getByName("com.sun.star.text.FieldMaster.SetExpression." & sType).DependentTextFields
            For i = 0 To UBound(mDependentTextFields)
                oAnchor = mDependentTextFields(i).Anchor
                oCursor = oAnchor.Text.createTextCursorByRange(oAnchor)
                oCursor.gotoStartOfParagraph (False)
                oCursor.gotoEndOfParagraph (True)
                Call subListBoxAddItem(oListbox, oCursor.String, i)
            Next
        #End If
    End Select
End Sub


Sub subListBoxAddItem(oListbox, sItem, nIndex)
    #If MSWD Then
        oListbox.AddItem sItem, nIndex
    #Else
        oListbox.AddItem(sItem, nIndex)
    #End If
End Sub


Sub subRemoveListboxItems(oListbox)
    #If MSWD Then
        Dim i As Integer
        For i = 1 To oListbox.ListCount
            oListbox.RemoveItem 0
        Next
        Rem oListbox.List = Array() rem Works in Windows but not Mac
    #Else
        oListbox.removeItems(0, oListBox.getItemCount)
    #End If
End Sub


Sub subLoadType()
    Dim oType, mTextFieldMasterNames, mElementNames(), i As Integer
    Rem Note whileTextFieldMasters are document specific in OOo Writer
    'they are "application" specific in Word.

    #If MSWD Then
        'The following commented code does not pickup the names of Seq fields in use in the document
        'ReDim Preserve mElementNames(CaptionLabels.Count + 1)
        'For i = 1 To CaptionLabels.Count
        '    mElementNames(i + 1) = CaptionLabels(i).Name
        'Next
        Dim oField, sFieldCode As String, nSpacePosn1 As Integer, nSpacePosn2 As Integer
        Dim nLen As Integer, sName As String, sFieldNames As String, ch As String

        sFieldNames = ""
        For Each oField In oDoc.Fields
            sFieldCode = UCase(LTrim(oField.Code))
            nSpacePosn1 = InStr(sFieldCode, " ")
            If Left(sFieldCode, nSpacePosn1 - 1) = "SEQ" Then
                'skip to name
                For i = nSpacePosn1 + 1 To Len(sFieldCode)
                    ch = Mid(sFieldCode, i, 1)
                    If ch >= "A" And ch <= "Z" Then Exit For
                Next
                'Build name
                sName = ""
                For i = i To Len(sFieldCode)
                    ch = Mid(sFieldCode, i, 1)
                    If Not (ch >= "A" And ch <= "Z") Or (ch >= "0" And ch <= "9") Then Exit For
                    sName = sName & ch
                Next
                If InStr(sFieldNames, sName) = 0 Then
                    sFieldNames = sFieldNames & "~" & sName
                End If
            End If
        Next
        sFieldNames = "Headings~Bookmarks" & sFieldNames
        'mElementNames = Split(sFieldNames, "~")
        oDialog.ComboBoxType.list = fnSplit(sFieldNames, "~")
        oDialog.ComboBoxType.value = "Headings"
    #Else
        mElementNames = Array("Headings", "Bookmarks")
        mTextFieldMasterNames = fnGetFieldMastersOfType(oDoc, ".SetExpression.")
        'xray mTextFieldMasterNames
        ReDim Preserve mElementNames(UBound(mTextFieldMasterNames) + 2)
        For i = 0 To UBound(mTextFieldMasterNames)
            mElementNames(i + 2) = mTextFieldMasterNames(i)
        Next
        oType = oDialog.getControl("ListBoxType")
        oType.addItems( mElementNames ,0)
        oType.selectItemPos(0, true)
    #End If
End Sub


Function fnGetFieldMastersOfType(oDoc, sType)
    Dim mTextFieldMasterNames, i As Integer, j As Integer, mElementNames(), nPosn As Integer

    mTextFieldMasterNames = oDoc.TextFieldMasters.ElementNames
    j = -1
    ReDim Preserve mElementNames(UBound(mTextFieldMasterNames) + 2)
    For i = 0 To UBound(mTextFieldMasterNames)
        nPosn = InStr(mTextFieldMasterNames(i), sType)
        If nPosn > 0 Then
            j = j + 1
            mElementNames(j) = Right(mTextFieldMasterNames(i), Len(mTextFieldMasterNames(i)) - (nPosn + Len(sType) - 1))
        End If
    Next
    If j > 0 Then
        ReDim Preserve mElementNames(j)
        fnGetFieldMastersOfType = mElementNames
    Else
        fnGetFieldMastersOfType = Array()
    End If
End Function


Sub subInsertReference(sRefName As String, nPart As Integer, oCurText, oCursor, sStyleName)
    #If MSWD Then
        Dim oCrossRef, oField
        oCursor.InsertCrossReference ReferenceType:="Bookmark", ReferenceKind:=nPart, _
            ReferenceItem:=sRefName, InsertAsHyperlink:=True, IncludePosition:=False
        If oDoc.name = ActiveDocument.name Then
            If Not fnHasStyle(sStyleName, "Character") Then
                subCreateMissingStyle (sStyleName)
            End If
            sStyleName = ActiveDocument.Styles.Item(sStyleName)
            On Error GoTo 0
            oCursor.MoveStart wdWord, -1
            oCursor.style = sStyleName
            oCursor.Collapse wdCollapseEnd
        Else
            oCursor.MoveEnd wdWord, 1
            Set oField = oCursor.Fields(1)
            oCursor.Collapse
            oField.ShowCodes = True
            oCursor.Move wdCharacter, Len(oField.Code.Text) + 2
            oField.ShowCodes = False
            oField.Update 'Not sure if this is necessary
        End If
        Exit Sub
NoStyle:
        subCreateMissingStyle (sStyleName)
        Resume Next
    #Else
        'Inserts a reference into the OOo document at the location of oViewCursor
        Dim oRefField As Object

        oRefField = oDoc.createInstance("com.sun.star.text.TextField.GetReference")
        oRefField.ReferenceFieldSource = 2 'com.sun.star.text.ReferenceFieldSource.BOOKMARK
        oRefField.SourceName = sRefName
        oRefField.ReferenceFieldPart = nPart
        oCurText.insertTextContent(oCursor, oRefField, false)
        If oDoc.URL = ThisComponent.URL Then
            If Not ThisComponent.styleFamilies.getByName("CharacterStyles").hasByName(sStyleName) Then
                subCreateMissingStyle (sStyleName)
            End If
            oRefField.Anchor.CharStyleName = sStyleName
        End If
        oRefField.Update
    #End If
End Sub

Sub subInsertText(sTextString As String, oCurText, oCursor, sStyleName)
    #If MSWD Then
        oCursor.InsertAfter sTextString
        If oDoc.name = ActiveDocument.name Then
            If Not fnHasStyle(sStyleName, "Character") Then
                subCreateMissingStyle (sStyleName)
            End If
            oCursor.style = sStyleName
        End If
        oCursor.Collapse wdCollapseEnd
        Exit Sub
    #Else
        If oDoc.URL = ThisComponent.URL Then
            If Not fnHasStyle(sStyleName, "Character") Then
                subCreateMissingStyle (sStyleName)
            End If
            oCursor.CharStyleName = sStyleName
        End If
         oCurText.insertString(oCursor, sTextString, false)
    #End If
End Sub


Sub subCreateDDEFieldWithHyperLink(sURL, sDDEBookmarkName, sRefBookmarkname, oRange)
    'Allows creation of a DDE field that gets text from another writer document bookmark,
    'And creates a hyperlink out of the field to a possibly different bookmark in the same document.
    Dim sFullURL As String, oDoc, oText, oMasterField, oDDEField

    sFullURL = sURL & "#" & sRefBookmarkname
    oDoc = ThisComponent
    oText = oRange.Text

    'Check if a master field has already been created for a DDE field to the DDE bookmark
    'if not create one
    If oDoc.TextFieldMasters.hasByName("com.sun.star.text.FieldMaster.DDE." & sDDEBookmarkName) Then
        oMasterField = oDoc.TextFieldMasters.getByName("com.sun.star.text.FieldMaster.DDE." & sDDEBookmarkName)
    Else
        oMasterField = oDoc.createInstance("com.sun.star.text.FieldMaster.DDE")
        oMasterField.DDECommandFile = sURL
        oMasterField.DDECommandType = "soffice"
        oMasterField.DDECommandElement = sDDEBookmarkName
        oMasterField.IsAutomaticUpdate = True
        oMasterField.name = sDDEBookmarkName 'Must have a name and it must be unique!
    End If

    'Insert the DDEfield
    oDDEField = ThisComponent.createInstance("com.sun.star.text.TextField.DDE")
    oDDEField.attachTextFieldMaster (oMasterField)
    oDDEField.attach (ThisComponent.CurrentController.ViewCursor)

    'Create the hyperlink
    oRange = oDDEField.Anchor
    oRange.HyperLinkURL = sFullURL
    oRange.HyperLinkName = sFullURL
End Sub


Function fnGetHiddenSection(oDoc, sSectionName)

    #If MSWD Then
        Dim oEndOfDoc, oBookmark
        'Sections in Word can be neither named nor hidden.
        'Thus using a bookmark to get desired region if already set.
        'The text can not be hidden as the DDE field only displays visible text.
        On Error GoTo NoBookmark
            Set oBookmark = oDoc.Bookmarks.Item(sSectionName)
        On Error GoTo 0
        Set fnGetHiddenSection = oBookmark.Range
        Exit Function
NoBookmark:
        Set oEndOfDoc = oDoc.Bookmarks("\EndOfDoc").Range
        oEndOfDoc.InsertBreak Type:=wdSectionBreakNextPage
        Set oBookmark = oDoc.Bookmarks.Add(Range:=oEndOfDoc, name:=sSectionName)
        Resume Next
    #Else
        'Warning: There is a bug in OOo (2.2) that if a section has been deleted by selecting the text
        'and deleting it, the section still sort of exists, as hasByName returns true, but getByName fails.
        'Also, if the newly created section has the same name then hiding the section via the API
        'doesn't work.

        Dim oText, oCursor, oSections, oSection, oAnchor
        If oDoc.Bookmarks.hasByName(sSectionName) Then
            fnGetHiddenSection = oDoc.Bookmarks.getByName(sSectionName)
            oSections = oDoc.getTextSections
            'If oSections.hasByName(sSectionName) Then
            oSection = oSections.getByName(sSectionName)
            oSection.setPropertyValue("IsVisible", true) 'This doesn't always work - see comment above.
        Else
            oText = oDoc.Text
            oCursor = oText.createTextCursorByRange(oText.End)
            oText.insertControlCharacter(oCursor, com.sun.star.text.ControlCharacter.PARAGRAPH_BREAK, true)
            oSection = oDoc.createInstance("com.sun.star.text.TextSection")
            oSection.setName (sSectionName)
            oText.insertTextContent(oCursor, oSection, true)
            oSection.setPropertyValue("IsVisible", true) 'This doesn't always work - see comment above.
        End If
        fnGetHiddenSection = oSection
    #End If
End Function


Sub subEventCommandButtonInsert_Initiate()
    'Creates a reference for the selected item if one doesn't already exist
    'Inserts the references and text
    Dim oCursor, sRefName As String, i As Long, nPosn As Long, oRefField As Object
    Dim oCharStyle As Object, mDependentTextFields, oDependentTextField
    Dim oVC, oCurText, sType As String, oField, oSection, oAnchor, sCurCharStyle As String
    Dim l As Integer, k As Long, sDDEBookmarkName As String, sSlash As String

    #If MSWD Then
        nPosn = Xref.ListBoxHeadings.ListIndex
    #Else
        nPosn = oDialog.getControl("ListBoxHeadings").selectedItemPos
    #End If

    If nPosn < 0 Then   'Nothing selected so can't insert anything
        Beep
        Exit Sub
    End If

    'Create the reference if it doesn't already exist
    #If MSWD Then
        sType = oDialog.ComboBoxType.value
    #Else
        sType = oDialog.getControl("ListBoxType").SelectedItem
    #End If

    Select Case sType
    Case "Headings"
        #If MSWD Then
            Set oCursor = oDoc.Paragraphs(mOutlines(2, mLinks(nPosn))).Range
            'Don't include the paragraph mark
            oCursor.End = oCursor.End - 1
        #Else
            oCursor = oDoc.Text.createTextCursor
            For i = 1 To mOutlines(2, mLinks(nPosn))
                oCursor.gotoNextParagraph (False)
            Next
            oCursor.gotoEndOfParagraph (True)
        #End If
        sRefName = fnBookmarkRange(oCursor)
    Case "Bookmarks"
        #If MSWD Then
            sRefName = oDoc.Bookmarks(nPosn + 1).name
        #Else
            sRefName = oDoc.Bookmarks.getByIndex(nPosn).name
        #End If
    Case Else
        #If MSWD Then
            i = -1
            For Each oField In oDoc.Fields
                If InStr(UCase(oField.Code), sType) > 0 Then
                    i = i + 1
                    If i = nPosn Then Exit For
                End If
            Next
            Set oCursor = oField.result '.Copy
            oCursor.Collapse wdCollapseEnd
            If oDialog.CheckBoxLeft.value Then
                oCursor.MoveStart wdParagraph, -1
            End If
            If oDialog.CheckBoxRight.value Then
                oCursor.MoveEnd wdParagraph, 1
                oCursor.End = oCursor.End - 1
            End If
        #Else
            mDependentTextFields = oDoc.TextFieldMasters.getByName("com.sun.star.text.FieldMaster.SetExpression." & oDialog.getControl("ListBoxType").SelectedItem).DependentTextFields
            oDependentTextField = mDependentTextFields(nPosn)
            oCursor = oDependentTextField.Anchor.Text.createTextCursorByRange(oDependentTextField.Anchor)
            If oDialog.getControl("CheckBoxLeft").State = 1 Then
                oCursor.gotoStartOfParagraph (False)
                oCursor.gotoRange(oDependentTextField.anchor.end, true)
                If oDialog.getControl("CheckBoxRight").State = 1 Then
                    oCursor.gotoEndOfParagraph (True)
                End If
            ElseIf oDialog.getControl("CheckBoxRight").State = 1 Then
                oCursor.collapseToEnd
                oCursor.gotoEndOfParagraph (True)
            End If
        #End If
        sRefName = fnBookmarkRange(oCursor)
    End Select

    'Insert the cross references and text as per the dialog.
    'Setting character styles if the reference is in the cirrent document.
    #If MSWD Then
        If oDoc.name <> ActiveDocument.name Then
            Set oSection = fnGetHiddenSection(oDoc, HIDDEN_SECTION_NAME)
            oSection.InsertParagraphBefore
            Set oCursor = oSection
        Else
            Set oCursor = Selection
        End If
        Call subInsertText(oDialog.TextBox0.Text, "", oCursor, "xRef-ChapterText")
        If oDialog.CheckBoxChapter.value Then
            Call subInsertReference(sRefName, wdNumberNoContext, "", oCursor, "xRef-Chapter")
        End If
        Call subInsertText(oDialog.TextBox1.Text, "", oCursor, "xRef-RefText")
        If (sType = "Headings" Or sType = "bookmarks") And oDialog.CheckBoxRef.value Or _
           Not (sType = "Headings" Or sType = "bookmarks") And (oDialog.CheckBoxLeft.value Or _
            oDialog.CheckBoxRight.value) Then
            Call subInsertReference(sRefName, wdContentText, "", oCursor, "xRef-Ref")
        End If
        Call subInsertText(oDialog.TextBox2.Text, "", oCursor, "xRef-PageText")
        If oDialog.CheckBoxpage.value Then
            Call subInsertReference(sRefName, wdPageNumber, "", oCursor, "xRef-Page")
        End If
        If ActiveDocument.name = oDoc.name Then
            Call subInsertText(oDialog.TextBox3.Text, "", oCursor, "xRef-DirectionText")
            If oDialog.CheckBoxDirection.value Then
                Call subInsertReference(sRefName, wdPosition, "", oCursor, "xRef-Direction")
            End If
        Else
            sDDEBookmarkName = "DDE" & sRefName & "_"
            oDoc.Bookmarks.Add Range:=oCursor.Paragraphs(1).Range, name:=sDDEBookmarkName
            sSlash = Application.PathSeparator
            Set oField = ActiveDocument.Fields.Add(Selection.Range, wdFieldDDEAuto, _
                "winword " & _
                Join(Split(oDoc.FullName, sSlash), sSlash & sSlash) & " " & _
                sDDEBookmarkName & " \t", True)
            ActiveDocument.Hyperlinks.Add Anchor:=oField.result, Address:= _
                oDoc.name, SubAddress:=sRefName


            'Not current documnt so need to insert dde field and hyperlink
'            'msgbox oCursor.string
'            Dim l, k, sDDEBookmarkName
'            oCursor.gotoStartOfParagraph (True)
'            'Create dde bookmark Instance("com.sun.star.text.Bookmark")
'            oRefField = oDoc.createInstance("com.sun.star.text.Bookmark")
'            sDDEBookmarkName = "DDE" & sRefName & "_"
'            oRefField.setName (sDDEBookmarkName)
'            sDDEBookmarkName = oRefField.Name 'This allows for the name to already exist and to have a number added
'            oCursor.text.insertTextContent(oCursor, oRefField, True)

'            'Loop until the fields get expanded or timeout
'            l = Len(oCursor.String)
'            While l = Len(oCursor.String) And k < 100000 'Timeout
'                k = k + 1
'            Wend
'            Call subCreateDDEFieldWithHyperLink(oDoc.URL, sDDEBookmarkName, sRefName, oCursor)
        End If
    #Else

        If oDoc.URL <> ThisComponent.URL Then
            oSection = fnGetHiddenSection(oDoc, HIDDEN_SECTION_NAME)
            oAnchor = oSection.getAnchor
            oCursor = oAnchor.Text.createTextCursorByRange(oAnchor.End)
            'Insert new paragraph
            oCursor.text.insertControlCharacter(oCursor, 0, false) '0=com.sun.star.text.ControlCharacter.PARAGRAPH_BREAK
        Else
            oCursor = ThisComponent.CurrentController.ViewCursor
            sCurCharStyle = oCursor.CharStyleName
        End If

        oCurText = oCursor.Text

        subInsertText(oDialog.getControl("TextField0").text, oCurText, oCursor, "xRef-ChapterText")

        If oDialog.getControl("CheckBoxChapter").State = 1 Then
            subInsertReference(sRefname, com.sun.star.text.ReferenceFieldPart.CHAPTER, oCurText, oCursor, "xRef-Chapter")
        End If

        subInsertText(oDialog.getControl("TextField1").text, oCurText, oCursor, "xRef-RefText")

        If oDialog.getControl("ListBoxType").SelectedItem = "Headings" And oDialog.getControl("CheckBoxRefh").State = 1 Or _
           oDialog.getControl("ListBoxType").SelectedItem = "Bookmarks" And oDialog.getControl("CheckBoxRefb").State = 1 Or _
           (oDialog.getControl("ListBoxType").selectedItemPos > 1 And (oDialog.getControl("CheckBoxLeft").State = 1 Or _
            oDialog.getControl("CheckBoxRight").State = 1)) Then
            subInsertReference(sRefname, com.sun.star.text.ReferenceFieldPart.TEXT, oCurText, oCursor, "xRef-Ref")
        End If

        subInsertText(oDialog.getControl("TextField2").text, oCurText, oCursor, "xRef-PageText")

        If oDialog.getControl("CheckBoxPage").State = 1 Then
            subInsertReference(sRefname, com.sun.star.text.ReferenceFieldPart.PAGE_DESC, oCurText, oCursor, "xRef-Page")
        End If

        subInsertText(oDialog.getControl("TextField3").text, oCurText, oCursor, "xRef-DirectionText")

        If oDialog.getControl("CheckBoxDirection").State = 1 And ThisComponent.URL = oDoc.URL Then
            subInsertReference(sRefname, com.sun.star.text.ReferenceFieldPart.UP_DOWN, oCurText, oCursor, "xRef-Direction")
        End If

        If oDoc.URL <> ThisComponent.URL Then
            'msgbox oCursor.string

            oCursor.gotoStartOfParagraph (True)
            'Create dde bookmark Instance("com.sun.star.text.Bookmark")
            oRefField = oDoc.createInstance("com.sun.star.text.Bookmark")
            sDDEBookmarkName = "DDE" & sRefName & "_"
            oRefField.setName (sDDEBookmarkName)
            sDDEBookmarkName = oRefField.name 'This allows for the name to already exist and to have a number added
            oCursor.text.insertTextContent(oCursor, oRefField, True)

            'Loop until the fields get expanded or timeout
            l = Len(oCursor.String)
            While l = Len(oCursor.String) And k < 100000 'Timeout
                k = k + 1
            Wend
            subCreateDDEFieldWithHyperLink(oDoc.url, sDDEBookmarkName, sRefName, oCursor)
            oSection.setPropertyValue("IsVisible", false)
        Else
            If sCurCharStyle = "" Then
                oCursor.setPropertyToDefault ("CharStyleName")
            Else
                oCursor.CharStyleName = sCurCharStyle
            End If
        End If
        subSaveDialogSettings
    #End If

End Sub


Function fnBookmarkRange(oRange) As String
    Dim oRefField, sRefName As String, oBookmark
    Dim oBookmarks, i, oText, oBookmarkRange

    #If MSWD Then
        For Each oBookmark In oRange.Bookmarks
            If oRange.IsEqual(oBookmark.Range) Then
                fnBookmarkRange = oBookmark.name
                Exit Function
            End If
        Next
    #Else
        oBookmarks = oDoc.Bookmarks
        oText = oRange.Text
        For i = 0 To oBookmarks.count - 1
            oBookmark = oBookmarks.getByIndex(i)
            oBookmarkRange = oBookmark.Anchor
            If EqualUnoObjects(oText, oBookmarkRange.Text) Then
                If oText.compareRegionStarts(oRange, oBookmarkRange) = 0 Then
                    If oText.compareRegionEnds(oRange, oBookmarkRange) = 0 Then
                        fnBookmarkRange = oBookmark.name
                        Exit Function
                    End If
                End If
            End If
        Next
    #End If

    'No bookmark corresponds to specified range so create one
    sRefName = fnNewRefName()
    #If MSWD Then
        oDoc.Bookmarks.Add Range:=oRange, name:=sRefName
    #Else
        oRefField = oDoc.createInstance("com.sun.star.text.Bookmark")
        oRefField.setName (sRefName)
        oRange.text.insertTextContent(oRange, oRefField, True)
    #End If
    fnBookmarkRange = sRefName
End Function

'Function thanks to http://www.tek-tips.com/faqs.cfm?fid=1824 with modifications
Public Function Replace(sString As Variant, sFind As String, sReplace As String)

    Dim iStart As Integer, iLength As Integer
    If IsNull(sString) Then
        Replace = Null
    Else
        iStart = InStr(1, sString, sFind)
        Do While iStart > 0
            sString = Left(sString, iStart - 1) _
                    & sReplace & Mid(sString, iStart + Len(sFind), Len(sString) - iStart - Len(sFind) + 1)
            iStart = InStr(iStart, sString, sFind)
        Loop
        Replace = sString
    End If

End Function


Function fnNewRefName() As String
    #If MSWD Then
    Rem Temporarily create a new hidden doc, a heading and a cross ref to it.
    Rem This creates a bookmark and so get that bookmark name.
        Dim oTemp

        Set oTemp = Documents.Add(DocumentType:=wdNewBlankDocument, Visible:=True)
        oTemp.Bookmarks.ShowHidden = True
        oTemp.Paragraphs(1).Range.Text = "Sample heading"
        oTemp.Paragraphs(1).style = ActiveDocument.Styles("Heading 1")
        oTemp.Paragraphs(1).Range.InsertParagraphAfter
        oTemp.Paragraphs(2).Range.InsertCrossReference ReferenceType:="Heading", ReferenceKind:= _
            wdContentText, ReferenceItem:="1"
        fnNewRefName = oTemp.Bookmarks(1).name
        oTemp.Close (False)
    #Else
    Rem Returns a REM uniqueREM  reference name using UNOREM s generateUuid.
    Rem So that it looks similar to MSWD the absolute value of the 15 numbers returned
    Rem concatenated and then the first 9 digits selected

        Dim sId, nId, oUuid, mUuid, sUuid As String, i As Integer

Rem        Removed need to use Uuid via Python due to problems loading the extension
Rem         oUuid = createUnoService("com.sun.star.task.Uuid")
Rem         mUuid = oUuid.Execute(Array())
Rem         For i = 0 To UBound(mUuid)
Rem             sUuid = sUuid & Abs(mUuid(i))
Rem         Next

Rem         fnNewRefName = "_Ref" & Left(sUuid, 9)

        Rem Todo: remove hack which uses the date plus time since midnight not an unique ID
        sId = Date + Timer()
        nId = Replace(sId, "/", "")
        nId = Replace(nId, ":", "")
        nId = Replace(nId, " ", "")

        fnNewRefName = "_Ref" + nId

    #End If
Rem      If oDoc.Bookmarks.hasByName(sBaseName) Then
Rem          i = oDoc.ReferenceMarks.Count
Rem          While oDoc.Bookmarks.hasByName(sBaseName & "_" & i)
Rem              i = i + 1
Rem          Wend
Rem          fnNewRefName = sBaseName & "_" & i
Rem      Else
Rem          fnNewRefName = sBaseName
Rem      End If
End Function


Sub subBuildHeadingArray(oDoc)
    Rem Uses module level variables: oText
    Rem Set values for module level variables: mOutlines, nHeadCount
    Rem Redimensions mOutlines to the number of found headings (nHeadCount)
    Rem Stores the heading text, heading level, then the paragraph number
    Dim oTextEnum As Object, oTextElement As Object
    Dim oPortionEnum As Object, oPortion As Object
    Dim i As Long, nHeadsFound As Long, nHeadingLevel As Integer, nParagraphCount As Long

    #If MSWD Then
        nParagraphCount = oDoc.Paragraphs.count
    #Else
        nParagraphCount = oDoc.ParagraphCount
    #End If

    ReDim mOutlines(2, nParagraphCount)

    nHeadsFound = -1
    Rem Fill the array with the headings, heading level and the paragraph number
    i = -1

    #If MSWD Then
        For i = 1 To oDoc.Paragraphs.count
            nHeadingLevel = fnHeadingLevel(oDoc.Paragraphs(i))
            If nHeadingLevel > 0 Then
                nHeadsFound = nHeadsFound + 1
                mOutlines(0, nHeadsFound) = oDoc.Paragraphs(i).Range.ListFormat.ListString & " " & _
                    oDoc.Paragraphs(i).Range.Text
                mOutlines(1, nHeadsFound) = nHeadingLevel
                mOutlines(2, nHeadsFound) = i
            End If
        Next
    #Else
        oTextEnum = oDoc.Text.createEnumeration
        While oTextEnum.hasMoreElements
            oTextElement = oTextEnum.nextElement
            If oTextElement.supportsService("com.sun.star.text.Paragraph") Then
                i = i + 1
                nHeadingLevel = fnHeadingLevel(oTextElement)
                If nHeadingLevel > 0 Then Rem oTextElement.ParaChapterNumberingLevel >= 0 then
                    nHeadsFound = nHeadsFound + 1
                    mOutlines(0, nHeadsFound) = oTextElement.String
                    mOutlines(1, nHeadsFound) = nHeadingLevel REM oTextElement.ParaChapterNumberingLevel + 1
                    mOutlines(2, nHeadsFound) = i
                End If
            End If
        Wend
    #End If
    nHeadCount = nHeadsFound
    ReDim Preserve mOutlines(2, nHeadCount + 1)
    ReDim mLinks(nHeadCount + 1)
End Sub


Function fnHeadingLevel(oParagraph)
    Dim sStyleName As String

    #If OOO Then
        sStyleName = fnGetParaStyleName(oParagraph)
    #Else
        sStyleName = oParagraph.style.NameLocal
    #End If
    If fnGetFamily(sStyleName) = "h" Then
        Rem left(sStyleName,1) = "h" and instr("12345", mid(sStylename,2,1))>0
        fnHeadingLevel = fnGetLevel(sStyleName)
    Else
        fnHeadingLevel = 0
    End If
End Function


Sub subEventListBoxLevels_Initiate(oEvent)
    subShowLevel(oDialog.getControl("ListBoxHeadings"), oEvent.Source.SelectedItemPos + 1)
End Sub


Sub subShowLevel(oListbox, nDisplayLevel As Integer)
    Rem Called by:subMyCrossRef,  subEventListBoxLevels_Initiate
    Rem Displays the headings in the listbox up to the specified level
    Rem E.g.  subShowLevel(oListBox,2) would display headings with levels of 1 and 2
    Dim i As Long, nPosn As Long

    Call subRemoveListboxItems(oListbox)
    nPosn = -1
    For i = 0 To nHeadCount
        If mOutlines(1, i) <= nDisplayLevel Then
            nPosn = nPosn + 1
            Call subAddItem(oListbox, i, nPosn, nDisplayLevel)
            mLinks(nPosn) = i
        End If
    Next
End Sub


Sub subAddSubLevel(oListbox, nPosn As Long)
    Rem Display the sublevel of the heading at nPosn in the listbox
    Dim i As Long, nLevel As Integer, nCurPosn As Long, nDiff As Long, j As Long
    Dim nTotal As Long

    nLevel = mOutlines(1, mLinks(nPosn)) + 1
    nCurPosn = nPosn
    i = mLinks(nPosn) + 1
    While mOutlines(1, i) >= nLevel
        If mOutlines(1, i) = nLevel Then
            nCurPosn = nCurPosn + 1
            Call subAddItem(oListbox, i, nCurPosn, nLevel)
            #If MSWD Then
                nTotal = oDialog.ListBoxHeadings.ListCount
                Rem oListBox.ListCount
            #Else
                nTotal = oListbox.getItemCount
            #End If
            For j = nTotal - 1 To nCurPosn + 1 Step -1
                mLinks(j) = mLinks(j - 1)
            Next
            mLinks(nCurPosn) = i
        End If
        i = i + 1
    Wend
End Sub


Sub subAddItem(oListbox, i As Long, nPosn As Long, nDisplayLevel As Integer)
    Rem Insert an item into the listbox
    Dim sInitial As String, nLevel As Integer

    nLevel = mOutlines(1, i)
    sInitial = String((Abs(nLevel) - 1) * nIndent, " ")
    If mOutlines(1, i + 1) > nLevel And nDisplayLevel = nLevel And nDisplayLevel < 10 Then
        sInitial = sInitial & "+"
    Else
        sInitial = sInitial & "-"
    End If
    oListbox.AddItem sInitial & mOutlines(0, i), nPosn
End Sub


Sub subRemoveSubLevels(oListbox As Object, nPosn As Long)
    Rem Remove from the listbox the sublevel headings of the heading at nPosn
    Dim i As Integer, nCurLevel As Integer, nCurPosn As Long, nDiff As Long, nCount As Integer

    nCurPosn = nPosn + 1
    nCurLevel = mOutlines(1, mLinks(nPosn))
    i = nCurPosn
    While nPosn < fnListboxItemCount(oListbox) And mOutlines(1, mLinks(nCurPosn)) > nCurLevel
        #If MSWD Then
            oListbox.RemoveItem i
        #Else
            oListBox.removeItems(i, 1)
        #End If
        nCurPosn = nCurPosn + 1
    Wend

    Rem Shift the link array back
    nDiff = nCurPosn - nPosn - 1

    For i = nPosn + 1 To fnListboxItemCount(oListbox) - 1
        mLinks(i) = mLinks(i + nDiff)
    Next
End Sub


Function fnListboxItemCount(oListbox)
    #If MSWD Then
        fnListboxItemCount = oListbox.ListCount
    #Else
        fnListboxItemCount = oListbox.getItemCount
    #End If
End Function

Sub subEventListBoxheadings_Initiate()
    Rem Called when the listbox is double clicked
    Dim oListBoxHeadings As Object, nSelectedItemPos As Long

    Rem Check that headings are displayed
    #If MSWD Then
        If oDialog.ComboBoxType.value <> "Headings" Then
            Exit Sub
        End If
        Rem set oListBoxHeadings = oDialog.ListBoxHeadings
        Rem nSelectedItemPos = oListBoxHeadings.selectedItemPos
        subAddRemoveNextLevel oDialog.ListBoxHeadings
        Rem oListBoxHeadings.selectItemPos(oListBoxHeadings.itemCount -1, true)
        Rem oListBoxHeadings.selectItemPos(nSelectedItemPos, true)
    #Else
        If oDialog.getControl("ListBoxType").selectedItemPos <> 0 Then
            Exit Sub
        End If

        oListBoxHeadings = oDialog.getControl("ListBoxHeadings")
        nSelectedItemPos = oListBoxHeadings.selectedItemPos
        subAddRemoveNextLevel (oListBoxHeadings)
        oListBoxHeadings.selectItemPos(oListBoxHeadings.itemCount -1, true)
        oListBoxHeadings.selectItemPos(nSelectedItemPos, true)
    #End If
End Sub


Sub subAddRemoveNextLevel(oListbox As Object)
    Rem Called by: subEventListBoxheadings_Initiate
    Dim nPosn As Long
    Dim sSelection As String

    #If MSWD Then
        sSelection = oDialog.ListBoxHeadings.value
        nPosn = oDialog.ListBoxHeadings.ListIndex
    #Else
        sSelection = oListbox.SelectedItem
        nPosn = oListbox.selectedItemPos
    #End If
    If nPosn < 0 Then   'Don't think this could happen but just in case
        Exit Sub
    End If

    If fnLevel(sSelection) > 0 Then
        Call subSetPlusMinus(oListbox, nPosn, "+", "-")
        Call subAddSubLevel(oListbox, nPosn)
    Else
        Call subSetPlusMinus(oListbox, nPosn, "-", "+")
        Call subRemoveSubLevels(oListbox, nPosn)
    End If
End Sub


Sub subSetPlusMinus(oListbox As Object, nPosn As Long, sCur As String, sTo As String)
    Rem Called by: subAddRemoveNextLevel
    Rem Toggless the + and - in the currently selected item
    Dim sSelection As String, nSignPos As Integer

    #If MSWD Then
        sSelection = oDialog.ListBoxHeadings.list(nPosn)
        nSignPos = InStr(sSelection, sCur)
        sSelection = Left(sSelection, nSignPos - 1) & sTo & _
            Right(sSelection, Len(sSelection) - nSignPos)
        oDialog.ListBoxHeadings.list(nPosn) = sSelection
    #Else
        sSelection = oListbox.getItem(nPosn)
        oListBox.removeItems(nPosn, 1)
        Mid(sSelection,instr(sSelection, sCur), 1, sTo)
        oListBox.addItem(sSelection, nPosn)
        oListBox.selectItemPos(nPosn, true)
    #End If
End Sub


Function fnLevel(sSelection As String) As Integer
    Rem Called by: fnGetListboxLevel,fnGetItem, subAddRemoveNextLevel
    Rem Determines the level of the string by looking at the leading spaces and first symbol (highest level = 1)
    Dim i As Integer, iLen As Integer
    iLen = Len(sSelection)
    i = 1
    While i < iLen And Mid(sSelection, i, 1) = " "
        i = i + nIndent
    Wend
    If Mid(sSelection, i, 1) = "+" Then
        fnLevel = Int((i - 1) / nIndent) + 1
    Else
        fnLevel = -1 * (Int((i - 1) / nIndent) + 1)
    End If
End Function


Function fnGetListboxLevel(oListbox As Object) As Integer
    Rem Returns the level of the currently selected item
    fnGetListboxLevel = Abs(fnLevel(oListbox.SelectedItem))
End Function


Sub subCurrentWriterDocuments()
    Dim oEnum As Object, oPosDoc As Object, i As Integer, j As Integer, nCurIndex As Integer
    Dim oListboxDocs As Object, mDocNames() As String

    #If MSWD Then
        ReDim mDocNames(Documents.count)
        j = 0
        For i = 1 To Documents.count
            If Documents(i).Path <> "" And Documents(i).name <> ActiveDocument.name Then
                mDocNames(j) = Documents(i).name
                j = j + 1
            End If
        Next
        mDocNames(j) = ActiveDocument.name
        ReDim Preserve mDocNames(j)
        oDialog.ComboBoxDocs.list = mDocNames
        oDialog.ComboBoxDocs.value = ActiveDocument.name
    #Else
        oEnum = StarDesktop.getComponents.createEnumeration

        Rem Count doc windows
        i = 0
        While oEnum.hasMoreElements
            oPosDoc = oEnum.nextElement
            If HasUnoInterfaces(oPosDoc, "com.sun.star.frame.XModel") Then Rem Thanks to DannyB for this line
                If oPosDoc.supportsService("com.sun.star.text.TextDocument") Then
                    i = i + 1
                End If
            End If
        Wend

        ReDim mDocs(i)

        i = 0
        oListboxDocs = oDialog.getControl("ListBoxDocs")
        oEnum = StarDesktop.getComponents.createEnumeration
        While oEnum.hasMoreElements
            oPosDoc = oEnum.nextElement
            If HasUnoInterfaces(oPosDoc, "com.sun.star.frame.XModel") Then
                If oPosDoc.supportsService("com.sun.star.text.TextDocument") Then
                    If oPosDoc.URL <> "" Or oPosDoc.CurrentController.Frame.Title = ThisComponent.CurrentController.Frame.Title Then
                        mDocs(i) = oPosDoc
                        oListboxDocs.addItem(oPosDoc.currentController.frame.title, i)
                        If oPosDoc.URL = ThisComponent.URL Then
                            nCurIndex = i
                        End If
                        i = i + 1
                    End If
                End If
            End If
        Wend
        oListboxDocs.selectItemPos(nCurIndex, true)
    #End If
End Sub


Sub subEventChangeDoc()
    Dim oListboxDocs As Object, oDocTemp As Object

    #If MSWD Then
        Set oDoc = Documents.Item(oDialog.ComboBoxDocs.value)
        oDialog.CheckBoxDirection.Enabled = ActiveDocument.name = oDoc.name
    #Else
        oListboxDocs = oDialog.getControl("ListBoxDocs")
        oDoc = mDocs(oListboxDocs.selectedItemPos)
        oDialog.getControl("CheckBoxDirection").Enable = (oDoc.URL = ThisComponent.URL)
    #End If

    Call subChangeType
End Sub


Sub subSaveDialogSettings()
    Rem Uses module level variable: oDialog
    Rem Uses global variable: mXRefDialogSettings
    Dim i As Integer, mControls

    mControls = oDialog.Controls
    ReDim mXRefDialogSettings(UBound(mControls) + 1)
    mXRefDialogSettings(0) = True

    For i = 0 To UBound(mControls)
        Select Case mControls(i).ImplementationName
        Case "stardiv.Toolkit.UnoEditControl"
            mXRefDialogSettings(i + 1) = mControls(i).Text
        Rem case "stardiv.Toolkit.UnoListBoxControl"
        Rem     mXRefDialogSettings(i+1) = mControls(i).SelectedItemPos
        Case "stardiv.Toolkit.UnoCheckBoxControl"
            mXRefDialogSettings(i + 1) = mControls(i).State
        End Select
    Next
    oDialog.endExecute
End Sub

Sub subLoadDialogSettings()
    Rem Uses module level variable: oDialog
    Rem Uses global variable: mXRefDialogSettings
    Dim i As Integer, mControls

    mControls = oDialog.Controls
    If mXRefDialogSettings(0) Then
        For i = 0 To UBound(mControls)
            Select Case mControls(i).ImplementationName
            Case "stardiv.Toolkit.UnoEditControl"
                mControls(i).Text = mXRefDialogSettings(i + 1)
            Rem case "stardiv.Toolkit.UnoListBoxControl"
            Rem     mControls(i).SelectItemPos(mXRefDialogSettings(i+1), true)
            Case "stardiv.Toolkit.UnoCheckBoxControl"
                mControls(i).State = mXRefDialogSettings(i + 1)
            End Select
        Next
    End If
End Sub

Function fnSplit(sStrIn As String, sStrDelim As String, Optional lCount As Long)

#If OOO Then
    fnSplit = Split(sStrIn, sStrDelim)
    Exit Function
#End If
#If Win16 Then
    fnSplit = Split(sStrIn, sStrDelim)
    Exit Function
#End If

Dim vOut() As Variant
Dim strSubString As String
Dim k As Integer
Dim lDelimPos As Long
Dim StrIn As String

StrIn = sStrIn
k = 0
lDelimPos = InStr(StrIn, sStrDelim)

Do While (lDelimPos)
    Rem Get everything to the left of the delimiter
    strSubString = Left(StrIn, lDelimPos - 1)
    Rem Make the return array one element larger
    ReDim Preserve vOut(k)
    Rem Add the new element
    vOut(k) = strSubString
    k = k + 1
    If lCount <> -1 And k = lCount Then
    fnSplit = vOut
    Exit Function
    End If
    Rem Only interested in what's right of delimiter
    StrIn = Right(StrIn, (Len(StrIn) - _
    (lDelimPos + Len(sStrDelim) - 1)))
    Rem See if delimiter occurs again
    lDelimPos = InStr(StrIn, sStrDelim)
Loop

Rem  No more delimiters in string.
Rem  Add what's left as last element
ReDim Preserve vOut(k)
vOut(k) = StrIn

fnSplit = vOut
End Function

