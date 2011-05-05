VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
END
Attribute VB_Name = "ThisDocument"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = True
Private Sub Document_Open()
    Call loadInstaller
    ThisDocument.Saved = True
End Sub

Private Sub Document_New()
    Call loadInstaller
    
    ThisDocument.Saved = True
End Sub


Private Function fnGetAbsFilePath()
    Dim myDocname, InstalledValue, FullPathToSavedFile, Seperator, ThePath
    myDocname = "ice-toolbar"
    myDocname = myDocname & ".dot"

    ThePath = Options.DefaultFilePath(wdStartupPath)
    Seperator = ":"
    If InStr(ThePath, "\") > 0 Then Seperator = "\"
    If InStr(ThePath, "/") > 0 Then Seperator = "/"
    
    fnGetAbsFilePath = ThePath & Seperator & myDocname

End Function
Private Sub loadInstaller()
    FullPathToSavedFile = fnGetAbsFilePath()
    If InStr(LCase(ThisDocument.Name), "ice-toolbar-installer.dot") > 0 Or _
        InStr(LCase(ThisDocument.Name), "ice-toolbar-installer.doc") > 0 Then
        Rem if Installer file
        Rem If FileSystem.Dir(FullPathToSavedFile) = myDocname Then
        If Len(Dir$(FullPathToSavedFile)) > 0 Then
            Rem if file exists.
            frmInstaller.btnInstall.Visible = False
        Else
            Rem if new installation
            frmInstaller.btnUninstall.Visible = False
            frmInstaller.btnUpdate.Visible = False
        End If
        frmInstaller.Show
    End If
End Sub

Sub subEventEscKey()
    frmKeyShortcut.Left = "-1000"
    frmKeyShortcut.Top = "-1000"
    frmKeyShortcut.Show
End Sub

