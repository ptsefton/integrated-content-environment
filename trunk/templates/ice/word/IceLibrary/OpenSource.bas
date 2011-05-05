Attribute VB_Name = "OpenSource"
#Const MSWD = True
#Const OOO = Not MSWD

'REM THIS MODULE IS COPYRIGHT USQ 2005 - other modules need to be re-written before we can GPL license the lot
Rem this module is not available in OOo Version. Cynthia
Rem This is used to reformat the list style so that they can be opened in OOO

Function MakeOutlineName(shortListType)
   Select Case shortListType
        Case "A"
          listType = "UppercaseAlpha"
        Case "a"
          listType = "LowercaseAlpha"
        Case "I"
          listType = "UppercaseRoman"
        Case "i"
          listType = "LowercaseRoman"
        Case Else
          listType = shortListType
  End Select
  MakeOutlineName = "L" + listType
End Function
Sub RepairLists()
    Rem for word hover.
    Call repairListInstances
End Sub
Sub repairListInstances()
    'added by cynthia on 29/jun/2009
    If Not fnIsThereAFile() Then
        Exit Sub
    End If
    If Not fnHasStyle("p") Then
        subCreateMissingStyle ("p") ' in case p style not exist.
    End If
    '######## cynthia ######

    Rem Fix outlines first
    Call outline.SetListOutlines
    Call outline.CreateListOfAllStyles
    
    Rem Loops through every paragraph in the document and re-applies styles, restarts lists as appropriate
    
    'TODO rewrite the following two modules so we can GPL license this code
    Dim varPageBreakBefore As Long, varKeepTogether As Long, varKeepWithNext As Long
    Dim style, listType, previousListType, outlineName As String
    Dim listLevel, previousListLevel As Integer
    Dim para As Object
    ' Move to beginning of document.
    Selection.HomeKey unit:=wdStory
      
     For Each para In ActiveDocument.Paragraphs
         para.Range.Select
         style = para.style
         family = Left(style, 2)
         If family = "li" Or family = "dl" Or family = "dt" Then
            listLevel = Int(Mid(style, 3, 1))
            listType = Right(style, 1)
            'Test if list paragraph eg li1p
            If Right(style, 1) = "p" Then
                listType = "lip"
            End If
        Else
            listLevel = 0
            listType = ""
            
         End If
         
         'remembering pagination
        varPageBreakBefore = Selection.ParagraphFormat.PageBreakBefore
        varKeepTogether = Selection.ParagraphFormat.KeepTogether
        varKeepWithNext = Selection.ParagraphFormat.KeepWithNext
        
        Rem reapply style
        para.style = style
         
        listOutlineName = MakeOutlineName(listType)
        
        'TODO make this a function: 'outlineExists'
        'Continue numbering is the previous list item is an li#p and on the same level
        'MsgBox AllOutlines
        If InStr(AllOutlines, ":::" + listOutlineName + ":::") > 0 Then
            If (listLevel > previousListLevel) Or (listLevel = previousListLevel And listType <> previousListType And previousListType <> "lip") Then
                Selection.Range.ListFormat.ApplyListTemplate ListTemplate:=ActiveDocument.ListTemplates(listOutlineName), ContinuePreviousList:=False, _
                        ApplyTo:=wdListApplyToWholeList, DefaultListBehavior:=2
            End If
           
        End If
        
        'reset the pagination
        Selection.ParagraphFormat.PageBreakBefore = varPageBreakBefore
        Selection.ParagraphFormat.KeepTogether = varKeepTogether
        Selection.ParagraphFormat.KeepWithNext = varKeepWithNext
        
        previousListLevel = listLevel
        previousListType = listType
        
         
      Next para
   End Sub
Sub UpdateLinks()
    If fnIsThereAFile() Then
        frmUpdateLinks.Show
    End If
    frmUpdateLinks.Show
End Sub

Sub SetOutlineNumbering()
    frmOutlineNumbering.Show
End Sub


Sub getListTemplate()
Rem For tesing only
For Each outl In ActiveDocument.ListTemplates
On Error Resume Next
   Selection.Range.InsertParagraph
   Selection.Range.Text = outl.name + ":" + outl.ListLevels(2).LinkedStyle + ":" + outl.ListLevels(2).NumberFormat
Next outl
End Sub

Function getDocVar(name)
Rem for autotext Numbering
    getTitleNumber = ActiveDocument.Variables(name).value
End Function


Sub setDocVar(name, value)
Rem for autotext Numbering
    On Error GoTo addNew
    ActiveDocument.Variables(name).value = value
    Exit Sub
addNew:
    ActiveDocument.Variables.Add name:=name, value:=value
End Sub

Function findInArray(list, value)
Rem This is never used. But may be it is useful function
   On Error GoTo newArray
   For Each Item In list
        If Item = value Then
            findInArray = True
            Exit Function
        End If
    Next Item
newArray:
    findInArray = False
End Function

Function fngetTitleStart()
    On Error GoTo Default
    If ActiveDocument.ListTemplates("SectOutline").ListLevels(1).LinkedStyle = "Title-chapter" Then
        fngetTitleStart = ActiveDocument.ListTemplates("SectOutline").ListLevels(1).StartAt
        Exit Function
    End If
Default:
    fngetTitleStart = 1

End Function




Sub fixCaptionAutoTextList()


End Sub
