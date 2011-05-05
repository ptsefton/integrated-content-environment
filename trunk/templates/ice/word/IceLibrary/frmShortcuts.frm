VERSION 5.00
Begin {C62A69F0-16DC-11CE-9E98-00AA00574A4F} frmShortcuts 
   Caption         =   "ICE toolbar shortcuts"
   ClientHeight    =   10995
   ClientLeft      =   45
   ClientTop       =   345
   ClientWidth     =   6585
   OleObjectBlob   =   "frmShortcuts.frx":0000
   StartUpPosition =   1  'CenterOwner
End
Attribute VB_Name = "frmShortcuts"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False


Private Sub CommandButton1_Click()
    frmShortcuts.hide
End Sub

Private Sub CommandButton2_Click()
    isFile = fnIsThereAFile()
    If isFile Then
        Call subCreateAllMissingStyles
    End If
End Sub

Private Sub CommandButton3_Click()
    frmShortcuts.hide
    frmAbout.Show
End Sub

Private Sub CommandButton4_Click()
    isFile = fnIsThereAFile()
    If isFile Then
        Call subSetupEscKeyHandler
    End If
End Sub

