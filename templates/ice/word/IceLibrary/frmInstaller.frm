VERSION 5.00
Begin {C62A69F0-16DC-11CE-9E98-00AA00574A4F} frmInstaller 
   Caption         =   "ICE Toolbar Installer"
   ClientHeight    =   4710
   ClientLeft      =   45
   ClientTop       =   435
   ClientWidth     =   6480
   OleObjectBlob   =   "frmInstaller.frx":0000
   StartUpPosition =   1  'CenterOwner
End
Attribute VB_Name = "frmInstaller"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False

Private Sub btnInstall_Click()
    Call InstallTemplate
    Me.hide
End Sub

Private Sub btnUninstall_Click()
    Call unInstallTemplate
    Me.hide
End Sub

Private Sub btnUpdate_Click()
    Call UpdateTemplate
    Me.hide
End Sub


Sub InstallTemplate(Optional showMsg)
    If IsMissing(showMsg) Then
        showMsg = True
    End If
    FullPathToSavedFile = fnGetAbsFilePath()
            
    'assign key to capture key strokes for short cuts
    subSetupEscKeyHandler
    'Set AddIn to False for this template
    On Error Resume Next
    AddIns.Add fileName:= _
        FullPathToSavedFile _
        , Install:=False
    'Install template
    Call ThisDocument.SaveAs(fileName:=FullPathToSavedFile)
    
    Rem hide the advanced toolbar when installed
    Application.CommandBars("ICE Advanced Toolbar").Visible = False
    
    'Set Addin to True
    On Error Resume Next
    AddIns.Add fileName:= _
        FullPathToSavedFile _
        , Install:=True
    Rem hide the advanced toolbar.
    Application.CommandBars("ICE Advanced Toolbar").Visible = False
    Rem Give the message regarding the ice-toolbar.dot
    If showMsg Then
        Dim theMessage
        theMessage = "Template saved to: " & FullPathToSavedFile & vbCrLf & vbCrLf
        theMessage = theMessage & "NOTE: This template has been installed as a Word Add-In."
        MsgBox theMessage
        
        On Error Resume Next
        ActiveDocument.Close SaveChanges:=False
        ThisDocument.Close SaveChanges:=True
        On Error GoTo 0
    End If
End Sub
Sub UpdateTemplate()
Rem remove the older version of the template
Rem then install  a new version
    FullPathToSavedFile = fnGetAbsFilePath()
    Call unInstallTemplate(False)
    If Len(Dir$(FullPathToSavedFile)) > 0 Then
        MsgBox "Error in replacing the file. Try Uninstall and Install", vbOKOnly, "ICE"
        Exit Sub
    End If
    ThisDocument.Close SaveChanges:=True
    
    Call InstallTemplate(False)
    MsgBox "ICE Toolbar is updated.", vbOKOnly, "ICE Toolbar"
    On Error Resume Next
    ActiveDocument.Close SaveChanges:=False
    ThisDocument.Close SaveChanges:=True
    On Error GoTo 0
End Sub

Sub OpenFolder()
Rem open the startup path for the user to delete the file
    cmdString = "explorer """ + Options.DefaultFilePath(wdStartupPath) + """"
    Shell (cmdString)
End Sub

Sub unInstallTemplate(Optional showMsg)
'
' unInstallTemplate Macro
' Macro recorded and modified by Cynthia on 2/02/2010
'
    If IsMissing(showMsg) Then
        showMsg = True
    End If
    FullPathToSavedFile = fnGetAbsFilePath()
    Rem file = Application.StartupPath
    Rem If Right(file, 1) <> "/" And Right(file, 1) <> "/" Then
    Rem     file = file + "/"
    Rem End If
    Rem file = file + "ice-toolbar.dot"
    On Error Resume Next
    AddIns(FullPathToSavedFile).Installed = False
    
    Rem delete the actual file
    'Check that file exists
    If Len(Dir$(FullPathToSavedFile)) > 0 Then
        'First remove readonly attribute, if set
        SetAttr FullPathToSavedFile, vbNormal
        'Then delete the file
         Kill FullPathToSavedFile
    End If
    
     Rem uninstall the file from the add in list first so that we can proceed.
    Rem AddIns(file).Installed = False
    On Error GoTo finally
    AddIns(FullPathToSavedFile).Delete
    With ActiveDocument
        .UpdateStylesOnOpen = False
        .AttachedTemplate = "Normal"
        .XMLSchemaReferences.AutomaticValidation = True
        .XMLSchemaReferences.AllowSaveAsXMLWithoutValidation = False
    End With
finally:
    If showMsg Then
        If Len(Dir$(FullPathToSavedFile)) > 0 Then
            MsgBox "Error in uninstalling: please delete the file"
            Call OpenFolder
        Else
            MsgBox "ICE toolbar is uninstalled.", vbOKOnly, "ICE Toolbar"
        End If
        On Error Resume Next
        ActiveDocument.Close SaveChanges:=False
        ThisDocument.Close SaveChanges:=True
        On Error GoTo 0
    End If
End Sub

Sub subSetupEscKeyHandler()
    CustomizationContext = ActiveDocument
    KeyBindings.Add KeyCode:=wdKeyEsc, KeyCategory:=wdKeyCategoryMacro, _
        Command:="subEventEscKey"
End Sub

Sub removeAdvancedToolbar()
    Rem hide the advanced toolbar
    On Error Resume Next
    Rem Application.CommandBars("ICE Advanced Toolbar").Visible = False
    Application.CommandBars("ICE Advanced Toolbar").Delete
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

Private Sub cmdClose_Click()
    Me.hide
End Sub

Private Sub UserForm_Click()

End Sub
