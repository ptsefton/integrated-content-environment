VERSION 5.00
Begin {C62A69F0-16DC-11CE-9E98-00AA00574A4F} frmKeyShortcut 
   Caption         =   "ICE"
   ClientHeight    =   1620
   ClientLeft      =   -1995
   ClientTop       =   -1995
   ClientWidth     =   3000
   OleObjectBlob   =   "frmKeyShortcut.frx":0000
End
Attribute VB_Name = "frmKeyShortcut"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False









Private Sub Label1_Click()

End Sub

Private Sub UserForm_KeyPress(ByVal KeyAscii As _
    MSForms.ReturnInteger)
    Rem this form is needed for keypress event.
    Call toolbar.Capture_keyPressed(Chr(KeyAscii))
    frmKeyShortcut.hide
    Unload frmKeyShortcut
End Sub
