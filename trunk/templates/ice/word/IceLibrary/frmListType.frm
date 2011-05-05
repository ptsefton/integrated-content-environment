VERSION 5.00
Begin {C62A69F0-16DC-11CE-9E98-00AA00574A4F} frmListType 
   Caption         =   "Change List Style"
   ClientHeight    =   915
   ClientLeft      =   45
   ClientTop       =   435
   ClientWidth     =   2250
   OleObjectBlob   =   "frmListType.frx":0000
   StartUpPosition =   1  'CenterOwner
End
Attribute VB_Name = "frmListType"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False


Private Sub butCancel_Click()
    Me.hide
    Me.cmbListType.Clear
End Sub

Private Sub butOK_Click()
    subChangeListType (Me.cmbListType.Text)
    butCancel_Click
End Sub

Rem Private Sub UserForm_Activate()
Rem     isFile = fnIsThereAFile()
Rem     If Not isFile Then
Rem        Me.hide
Rem     End If
Rem End Sub

