VERSION 5.00
Begin {C62A69F0-16DC-11CE-9E98-00AA00574A4F} frmUpdateLinks 
   Caption         =   "Update links"
   ClientHeight    =   4290
   ClientLeft      =   45
   ClientTop       =   345
   ClientWidth     =   4650
   OleObjectBlob   =   "frmUpdateLinks.frx":0000
   StartUpPosition =   1  'CenterOwner
End
Attribute VB_Name = "frmUpdateLinks"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False


' Called when the cancel button is clicked
Private Sub cmdCancel_Click()
    ' Hide the form
    frmUpdateLinks.hide
    'Unload form if a mac otherwise it cause problems with the Enter key
    #If Mac Then
        Unload frmUpdateLinks
    #End If
End Sub

' Called when the ok button is clicked
Private Sub cmdOk_Click()
    
    Dim i As Long, n As Long, URL
    Dim currentDocument As String
    FixPos = 1
    currentDocument = ActiveDocument.FullName
    
    ' Check for empty fields
    If FindStr.Text = "" Then
        printMsgbox ("Error - The text to display was not specified")
    Else
        System.Cursor = wdCursorWait
        
        Dim strFind As String, strReplace As String, strStart As String
        strFind = FindStr.Text
        strReplace = ReplaceStr.Text
        strStart = StartsWithStr.Text
        
        ' Hide the form otherwise cause the error on opening other files
         frmUpdateLinks.hide
        'Unload form if a mac otherwise it cause problems with the Enter key
        #If Mac Then
            Unload frmUpdateLinks
        #End If
        
        If strFind <> "" And UpdateAll.value = False Then
            processDocument fileName:=currentDocument, curDoc:=currentDocument, strFind:=strFind, strReplace:=strReplace, strStart:=strStart
        ElseIf strFind <> "" And UpdateAll.value = True And DirectoryStr.Text <> "" Then
    '   File search is no longer working in word 2007.
            processFolder dirName:=DirectoryStr.Text, curdocument:=currentDocument, strFind:=strFind, strReplace:=strReplace, strStart:=strStart
        End If
           
         System.Cursor = wdCursorNormal
         
    End If
End Sub
Private Sub processFolder(dirName As String, curdocument As String, strFind As String, strReplace As String, strStart As String)
    'get the first name
    Dim strName As String
    Dim dirNames() As String, directories As String
    dirFileName = FileSystem.Dir(dirName + "/*", vbDirectory)
    nDir = 0
    ReDim dirNames(nDir)
    On Error GoTo catchErr
    Do While dirFileName <> ""
        
        If Right(dirName, 1) = "/" Or Right(dirName, 1) = "\" Then
            dirFileName = dirName + dirFileName
        Else
            If InStr(dirName, "/") > 0 Then
                dirFileName = dirName + "/" + dirFileName
            ElseIf InStr(dirName, "\") > 0 Then
                dirFileName = dirName + "\" + dirFileName
            End If
        End If
       ' open the file based on its index position
'        Documents.Open FileName:=.FoundFiles(i)
        'see whether it get the subfolder or not
        If Right(dirFileName, 1) <> "." And Right(dirFileName, 4) <> ".ice" Then
            ' if the folder is not "." or ".." or ".ice"
            strName = dirFileName
            If (GetAttr(dirFileName) And vbDirectory) = vbDirectory Then
                dirNames(nDir) = dirFileName
                nDir = nDir + 1
                'extend the array
                ReDim Preserve dirNames(nDir)
                'For the subFolder
                'processSubFolder dirName:=strName, curdocument:=curdocument, strFind:=strFind, strReplace:=strReplace, strStart:=strStart
                
            Else
                If Right(dirFileName, 4) = ".doc" Or Right(dirFileName, 5) = ".docx" Then
                    ' process only if it is word document
                    'strName = dirName + "/" + dirFileName
                    processDocument fileName:=strName, curDoc:=curdocument, strFind:=strFind, strReplace:=strReplace, strStart:=strStart
                    dirFileName = curDirFileName
                End If
            End If
        End If
        'go to next file or directory.
        dirFileName = Dir()
                                       
    Loop
    
GoTo finally
catchErr:
    dirFileName = ""
    Resume Next
finally:
    If nDir <> 0 Then
       For i = 0 To nDir - 1
            processFolder dirName:=dirNames(i), curdocument:=curdocument, strFind:=strFind, strReplace:=strReplace, strStart:=strStart
        Next
    End If
End Sub


Private Sub processSubFolder(dirName As String, curdocument As String, strFind As String, strReplace As String, strStart As String)
    'get the first name
    Dim strName As String
    dirFileName = FileSystem.Dir(dirName + "/*", vbDirectory)
    On Error GoTo catchErr
    Do While dirFileName <> ""
        
        If Right(dirName, 1) = "/" Or Right(dirName, 1) = "\" Then
            dirFileName = dirName + dirFileName
        Else
            If InStr(dirName, "/") > 0 Then
                dirFileName = dirName + "/" + dirFileName
            ElseIf InStr(dirName, "\") > 0 Then
                dirFileName = dirName + "\" + dirFileName
            End If
        End If
       ' open the file based on its index position
'        Documents.Open FileName:=.FoundFiles(i)
        'see whether it get the subfolder or not
        If Right(dirFileName, 1) <> "." And Right(dirFileName, 4) <> ".ice" Then
            ' if the folder is not "." or ".." or ".ice"
            strName = dirFileName
            If (GetAttr(dirFileName) And vbDirectory) = vbDirectory Then
                'strName = dirName + dirFileName
            
                'For the subFolder
                processFolder dirName:=strName, curdocument:=curdocument, strFind:=strFind, strReplace:=strReplace, strStart:=strStart
                dirFileName = Dir(dirFileName)
            Else
                If Right(dirFileName, 4) = ".doc" Or Right(dirFileName, 5) = ".docx" Then
                    ' process only if it is word document
                    'strName = dirName + "/" + dirFileName
                    processDocument fileName:=strName, curDoc:=curdocument, strFind:=strFind, strReplace:=strReplace, strStart:=strStart
                    dirFileName = curDirFileName
                End If
            End If
        End If
        'go to next file or directory.
        dirFileName = Dir()
                                       
    Loop
    
GoTo finally
catchErr:
    dirFileName = ""
    Resume Next
finally:
End Sub

Private Sub processDocument(fileName As String, curDoc As String, strFind As String, strReplace As String, strStart As String)
    If fileName <> curDoc Then
        'if not the current document, open the document
        
        Documents.Open fileName:=fileName
    End If
                        
    'modify the url
    For n = ActiveDocument.Hyperlinks.count To 1 Step -1
        If InStr(ActiveDocument.Hyperlinks(n).Address, strStart) Then
            URL = ActiveDocument.Hyperlinks(n).Address
            If URL = ActiveDocument.Hyperlinks(n).TextToDisplay Then
                'if url is displayed in the document. modify it.
                 changeName = True
            End If
            pos = InStr(URL, strFind)
            If pos > 0 Then
                'if findstr can be found in URL. change it.
                'without this condition, it will cause the error.
                StrLeft = Left(URL, pos - 1)
                RightPos = pos + Len(strFind)
                RightStr = Mid(URL, RightPos)
                URL = StrLeft + strReplace + RightStr
                                        
                ActiveDocument.Hyperlinks(n).Address = URL
                If changeName Then
                    'Change the text in the document.
                    ActiveDocument.Hyperlinks(n).TextToDisplay = URL
                End If
                        
            End If
                                    
        End If
    Next n
    
    
    ' save and close the opened documents
    ' Keep current document open
    If ActiveDocument.FullName <> curDoc Then
        ActiveDocument.Close wdSaveChanges
    End If
                
End Sub

Private Sub DirectoryStr_Change()

End Sub


' Initialise the form when the macro is run
Private Sub UserForm_Activate()
    isFile = fnIsThereAFile()
    If Not isFile Then
        OS = Application.System.OperatingSystem
        ' Set the focus + Clear the fields
        FindStr.SetFocus
        ReplaceStr.Text = ""
        'Unable to use the Application.Filesearch on Macintosh
        If OS <> "Macintosh" Then
            UpdateAll.Visible = True
            DirectoryStr.Visible = True
            pos = InStr(ActiveDocument.FullName, ActiveDocument.name) - 1
            DirectoryStr.Text = Left(ActiveDocument.FullName, pos)
        Else
            UpdateAll.Visible = False
            DirectoryStr.Visible = False
        End If
    End If
End Sub
