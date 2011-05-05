VERSION 5.00
Begin {C62A69F0-16DC-11CE-9E98-00AA00574A4F} Xref 
   Caption         =   "Cross reference"
   ClientHeight    =   5835
   ClientLeft      =   0
   ClientTop       =   0
   ClientWidth     =   6405
   OleObjectBlob   =   "Xref.frx":0000
   StartUpPosition =   1  'CenterOwner
End
Attribute VB_Name = "Xref"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Private Sub ComboBoxDocs_Change()
    subEventChangeDoc
End Sub

Private Sub ComboBoxLevel_Change()
    Dim oListbox
    Set oListbox = Xref.ListBoxHeadings
    Call subShowLevel(oListbox, Xref.ComboBoxLevel.ListIndex + 1)
End Sub

Private Sub ComboBoxType_Change()
    subChangeType
End Sub

Private Sub CommandButtonClose_Click()
    Xref.hide
    'Should also call save settings
End Sub

Private Sub CommandButtonInsert_Click()
    subEventCommandButtonInsert_Initiate
End Sub

Private Sub ListBoxHeadings_DblClick(ByVal bCancel As MSForms.ReturnBoolean)
    subEventListBoxheadings_Initiate
End Sub
