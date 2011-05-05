VERSION 5.00
Begin {C62A69F0-16DC-11CE-9E98-00AA00574A4F} frmAbout 
   Caption         =   "ICE Style Toolbar"
   ClientHeight    =   3180
   ClientLeft      =   45
   ClientTop       =   435
   ClientWidth     =   6450
   OleObjectBlob   =   "frmAbout.frx":0000
   StartUpPosition =   1  'CenterOwner
End
Attribute VB_Name = "frmAbout"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Private Sub cmdAdvancedToolbar_Click()
    If Application.CommandBars("ICE Advanced Toolbar").Visible Then
        Application.CommandBars("ICE Advanced Toolbar").Visible = False
        cmdAdvancedToolbar.Caption = "Show Advanced Toolbar"
    Else
        Application.CommandBars("ICE Advanced Toolbar").Visible = True
        cmdAdvancedToolbar.Caption = "Hide Advanced Toolbar"
    End If
    Me.hide
End Sub

Private Sub CommandButton1_Click()
    Me.hide
End Sub

Private Sub Label2_Click()

End Sub

Private Sub UserForm_Initialize()
    Rem to show and hide the advanced toolbar
    Rem Application.Version == 11 is Word 2003
    Rem Application.Version == 12 is Word 2007
    Rem Application.Version == 13 is Word 2010
    If CInt(Application.Version) >= 12 Then
        cmdAdvancedToolbar.Visible = True
        If Application.CommandBars("ICE Advanced Toolbar").Visible Then
            cmdAdvancedToolbar.Caption = "Hide Advanced Toolbar"
        Else
            cmdAdvancedToolbar.Caption = "Show Advanced Toolbar"
        End If
    Else
        cmdAdvancedToolbar.Visible = False
    End If
End Sub
