VERSION 5.00
Begin {C62A69F0-16DC-11CE-9E98-00AA00574A4F} frmConvert 
   Caption         =   "ICE Convert To HTML"
   ClientHeight    =   3345
   ClientLeft      =   45
   ClientTop       =   330
   ClientWidth     =   6420
   OleObjectBlob   =   "frmConvert.frx":0000
   StartUpPosition =   1  'CenterOwner
End
Attribute VB_Name = "frmConvert"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False


Private Sub butViewLog_Click()
    subViewLog
End Sub

Private Sub butPreview_Click()
    subConvertPreview
End Sub

Private Sub butConvert_Click()
    subConvertExecute
End Sub

Private Sub butClose_Click()
    Me.hide
End Sub

Private Sub btBrowse_Click()
    Dim strFileName As String
    With Dialogs(wdDialogFileOpen)
        If .Display = -1 Then
            strFileName = .Application.Options.DefaultFilePath(wdDocumentsPath) & "\" & .name
        End If
    End With
    filTemplate.Text = strFileName
End Sub
