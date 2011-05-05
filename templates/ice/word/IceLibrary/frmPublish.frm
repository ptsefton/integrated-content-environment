VERSION 5.00
Begin {C62A69F0-16DC-11CE-9E98-00AA00574A4F} frmPublish 
   Caption         =   "ICE Publish To Blog"
   ClientHeight    =   5880
   ClientLeft      =   45
   ClientTop       =   330
   ClientWidth     =   6030
   OleObjectBlob   =   "frmPublish.frx":0000
   StartUpPosition =   1  'CenterOwner
End
Attribute VB_Name = "frmPublish"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False


Private Sub butViewLog_Click()
    subViewLog
End Sub

Private Sub butPreview_Click()
    subPublishPreview
End Sub

Private Sub butPublish_Click()
    subPublishExecute
End Sub

Private Sub butClose_Click()
    Me.hide
End Sub

Private Sub butCatHelp_Click()
    MsgBox "For multiple categories, separate the categories with "";""." & vbNewLine & "For Example, category1;category2", vbInformation, "Help"
End Sub
