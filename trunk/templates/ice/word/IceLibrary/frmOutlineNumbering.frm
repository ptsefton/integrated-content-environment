VERSION 5.00
Begin {C62A69F0-16DC-11CE-9E98-00AA00574A4F} frmOutlineNumbering 
   Caption         =   "Set outline numbering"
   ClientHeight    =   3690
   ClientLeft      =   45
   ClientTop       =   435
   ClientWidth     =   4560
   OleObjectBlob   =   "frmOutlineNumbering.frx":0000
   StartUpPosition =   1  'CenterOwner
End
Attribute VB_Name = "frmOutlineNumbering"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Private Sub cmdCancel_Click()
    frmOutlineNumbering.hide
    Rem Unload form if a mac otherwise it cause problems with the Enter key
    #If Mac Then
        Unload frmOutlineNumbering
    #End If
End Sub

Private Sub cmdOk_Click()
    Rem Based on SetHeadingOutline Macro
    Rem 27/10/2006 by Daniel de Byl
    Rem Set update syles on open to false otherwise outline numbering
    Rem will be lost when reopened
    ActiveDocument.UpdateStylesOnOpen = False
    
    Rem Check to see if we want to quite before we do anything.
    outlineStart = StartAt.value
    TitleText = SeparatorBefore.value
    If (outlineStart = "") Then
      printMsgbox ("No start value set")
      Rem Unload form if a mac otherwise it cause problems with the Enter key
        #If Mac Then
            Unload frmOutlineNumbering
        #End If
      Exit Sub
    End If
    Rem change the cursor to wait cursor
    System.Cursor = wdCursorWait
    Rem Let's start at H1n but remember what style we were in before
    Selection.MoveLeft unit:=wdCharacter, count:=1
    RememberedStyle = Selection.ParagraphFormat.style.NameLocal
    
    Rem Make sure we have all the relevant styles before starting
    CreateListOfAllStyles
    Call subCreateMissingStyle("Title-chapter")
    Call subCreateMissingStyle("h1n")
    Call subCreateMissingStyle("h2n")
    Call subCreateMissingStyle("h3n")
    Call subCreateMissingStyle("h4n")
    Call subCreateMissingStyle("h5n")
    Selection.style = ActiveDocument.Styles("p")
    Selection.style = ActiveDocument.Styles("h1n")
    CreateOutline ("SectOutline")

    Rem Note: Space after the number is set in NumberFormat not TrailingCharacter
    Rem If you use TrailingCharacter it is lost when opened in another word processor
    Selection.Range.ListFormat.ApplyListTemplate ListTemplate:=NewList, ContinuePreviousList:=True, _
        ApplyTo:=wdListApplyToWholeList
    With NewList.ListLevels(1)
        If (TitleChapter.value = False) Then
            .NumberFormat = "%1"
            .TrailingCharacter = wdTrailingTab
        Else
             .NumberFormat = TitleText + " %1" + SeparatorAfter.value
             .TrailingCharacter = wdTrailingNone
        End If
        .NumberStyle = wdListNumberStyleArabic
        .NumberPosition = CentimetersToPoints(0)
        .Alignment = wdListLevelAlignLeft
        .TextPosition = CentimetersToPoints(0)
        .TabPosition = CentimetersToPoints(0)
        .ResetOnHigher = True
        .StartAt = outlineStart
        .LinkedStyle = "Title-chapter"
    End With
    
    With NewList.ListLevels(2)
        If (TitleChapter.value = False) Then
            .NumberFormat = "%2 "
        Else
            .NumberFormat = "%1.%2 "
        End If
        .TrailingCharacter = wdTrailingNone
        .NumberStyle = wdListNumberStyleArabic
        .NumberPosition = CentimetersToPoints(0)
        .Alignment = wdListLevelAlignLeft
        .TextPosition = CentimetersToPoints(0)
        .TabPosition = CentimetersToPoints(0)
        .ResetOnHigher = True
        If (TitleChapter.value = False) Then
            .StartAt = outlineStart
        Else
             .StartAt = 1
        End If
        .LinkedStyle = "h1n"
    End With
  
    With NewList.ListLevels(3)
        If (TitleChapter.value = False) Then
            .NumberFormat = "%2.%3 "
        Else
            .NumberFormat = "%1.%2.%3 "
        End If
        .TrailingCharacter = wdTrailingNone
        .NumberStyle = wdListNumberStyleArabic
        .NumberPosition = CentimetersToPoints(0)
        .Alignment = wdListLevelAlignLeft
        .TextPosition = CentimetersToPoints(0)
        .TabPosition = CentimetersToPoints(0)
        .ResetOnHigher = True
        .StartAt = 1
        .LinkedStyle = "h2n"
    End With
  
    With NewList.ListLevels(4)
        If (TitleChapter.value = False) Then
            .NumberFormat = "%2.%3.%4 "
        Else
            .NumberFormat = "%1.%2.%3.%4 "
        End If
        .TrailingCharacter = wdTrailingNone
        .NumberStyle = wdListNumberStyleArabic
        .NumberPosition = CentimetersToPoints(0)
        .Alignment = wdListLevelAlignLeft
        .TextPosition = CentimetersToPoints(0)
        .TabPosition = CentimetersToPoints(0)
        .ResetOnHigher = True
        .StartAt = 1
        .LinkedStyle = "h3n"
    End With
   
    With NewList.ListLevels(5)
        If (TitleChapter.value = False) Then
            .NumberFormat = "%2.%3.%4.%5 "
        Else
            .NumberFormat = "%1.%2.%3.%4.%5 "
        End If
        .TrailingCharacter = wdTrailingNone
        .NumberStyle = wdListNumberStyleArabic
        .NumberPosition = CentimetersToPoints(0)
        .Alignment = wdListLevelAlignLeft
        .TextPosition = CentimetersToPoints(0)
        .TabPosition = CentimetersToPoints(0)
        .ResetOnHigher = True
        .StartAt = 1
        .LinkedStyle = "h4n"
    End With
    
    With NewList.ListLevels(6)
        If (TitleChapter.value = False) Then
            .NumberFormat = "%2.%3.%4.%5.%6 "
        Else
            .NumberFormat = "%1.%2.%3.%4.%5.%6 "
        End If
        .TrailingCharacter = wdTrailingNone
        .NumberStyle = wdListNumberStyleArabic
        .NumberPosition = CentimetersToPoints(0)
        .Alignment = wdListLevelAlignLeft
        .TextPosition = CentimetersToPoints(0)
        .TabPosition = CentimetersToPoints(0)
        .ResetOnHigher = True
        .StartAt = 1
        .LinkedStyle = "h5n"
    End With
    Selection.Range.ListFormat.ApplyListTemplate ListTemplate:=NewList, _
        ContinuePreviousList:=True, ApplyTo:=wdListApplyToWholeList

    Selection.style = ActiveDocument.Styles(RememberedStyle)
    System.Cursor = wdCursorNormal

    frmOutlineNumbering.hide
    Rem Unload form if a mac otherwise it cause problems with the Enter key
    #If Mac Then
        Unload frmOutlineNumbering
    #End If
    
    If (TitleChapter.value) Then
        Call setDocVar("outlineStart", outlineStart)
    Else
        Call setDocVar("outlineStart", 0)
    End If
    Rem update the fields
    ActiveDocument.Fields.Update
    
    
    Rem fix the autotext captions list  as well
    Rem Call fixCaptionAutoTextList
End Sub

Private Sub subToggle()
    If TitleChapter.value = True Then
        SeparatorBefore.Enabled = True
        SeparatorAfter.Enabled = True
    Else
        SeparatorBefore.Enabled = False
        SeparatorAfter.Enabled = False
    End If
End Sub
Private Sub TitleChapter_Click()
    Call subToggle
End Sub

Private Sub NumberedHeading_Click()
    Call subToggle
End Sub

Private Sub UserForm_Activate()
    isFile = fnIsThereAFile()
    If Not isFile Then
       Me.hide
    End If
End Sub

