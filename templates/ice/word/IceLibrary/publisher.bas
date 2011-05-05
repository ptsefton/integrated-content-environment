Attribute VB_Name = "publisher"
#Const MSWD = True
#Const OOO = Not MSWD
Rem *********************************************************************
Rem    Copyright (C) 2006  Distance and e-Learning Centre,
Rem    University of Southern Queensland
Rem
Rem    This program is free software; you can redistribute it and/or modify
Rem    it under the terms of the GNU General Public License as published by
Rem    the Free Software Foundation; either version 2 of the License, or
Rem    (at your option) any later version.
Rem
Rem    This program is distributed in the hope that it will be useful,
Rem    but WITHOUT ANY WARRANTY; without even the implied warranty of
Rem    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
Rem    GNU General Public License for more details.
Rem
Rem    You should have received a copy of the GNU General Public License
Rem    along with this program; if not, write to the Free Software
Rem    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
Rem
Rem *********************************************************************
Global udg_oDialogConvert
Global udg_oDialogPublish
Dim OSType As Integer
Dim sIceLoc As String

Function fnDialogStartup()
    Dim sloc As String
    fnDialogStartup = True
    sloc = "C:\Program Files\ICE 2\bin\Ice.exe"
    If fnFileExists(sloc) Then
        Rem if 32bits window OS
        Call subSetOSType(1)
        Call subSetIceLoc("C:\Program Files\ICE 2")
    Else
        sloc = "C:\Program Files (x86)\ICE 2\bin\Ice.exe"
        If fnFileExists(sloc) Then
            Rem If 64bits Window OS
            Call subSetOSType(1)
            Call subSetIceLoc("C:\Program Files (x86)\ICE 2")
        Else
            sloc = Trim(Environ("ICE_HOME")) + "bin\Ice.exe"
            If fnFileExists(sloc) Then
                Rem if Window but ICE is installed in other place than ProgramFile. Check if this is the case.
                Call subSetOSType(1)
                Call subSetIceLoc(Trim(Environ("ICE_HOME")))
            Else
                sloc = "/Applications/Ice2/Ice2.app/Contents/Resources/ice2.sh"
                If fnFileExists(sloc) Then
                    Rem if Mac OS
                    Call subSetOSType(3)
                    Call subSetIceLoc("sh " + sloc)
                Else
                    iceHome = Trim(Environ("ICE_HOME"))
                    If Right(iceHome, 1) = "/" Or Right(iceHome, 1) = "\" Then
                        iceHome = Left(iceHome, Len(iceHome) - 1)
                    End If
                    sloc = iceHome + "/ice.sh"
                    If fnFileExists(sloc) Then
                        Rem if Ubuntu
                        Call subSetOSType(4)
                        Call subSetIceLoc(sloc)
                    Else
                        GoTo FileNotFound
                    End If
                End If
            End If
        End If
    End If
    Call subAddProperties
    Exit Function
FileNotFound:
    Call subSetIceLoc("")
    fnDialogStartup = False
    printMsgbox ("Feature is unavailable for your operating system or ICE could not be found.")
End Function

Sub subAddProperties()
    #If OOO Then
        oDocInfo = ThisComponent.getDocumentInfo()
        If Not oDocInfo.PropertySetInfo.HasPropertyByName("chkTitle") Then
            oDocInfo.addProperty("chkTitle", 0, fnConvertToBoolean(1))
        End If
        If Not oDocInfo.PropertySetInfo.HasPropertyByName("chkTableOfContents") Then
            oDocInfo.addProperty("chkTableOfContents", 0, fnConvertToBoolean(0))
        End If
        If Not oDocInfo.PropertySetInfo.HasPropertyByName("chkPDF") Then
            oDocInfo.addProperty("chkPDF", 0, fnConvertToBoolean(0))
        End If
        If Not oDocInfo.PropertySetInfo.HasPropertyByName("filTemplate") Then
            oDocInfo.addProperty("filTemplate", 0, "")
        End If
        If Not oDocInfo.PropertySetInfo.HasPropertyByName("filSaveDir") Then
            oDocInfo.addProperty("filSaveDir", 0, "")
        End If
        If Not oDocInfo.PropertySetInfo.HasPropertyByName("txtTitle") Then
            oDocInfo.addProperty("txtTitle", 0, oDocInfo.Title)
        ElseIf fnGetDocProp("txtTitle") = "" Then
            subSetDocProp("txtTitle",oDocInfo.Title)
        End If
        If Not oDocInfo.PropertySetInfo.HasPropertyByName("txtSummary") Then
            oDocInfo.addProperty("txtSummary", 0, "")
        End If
        If Not oDocInfo.PropertySetInfo.HasPropertyByName("txtAuthor") Then
            oDocInfo.addProperty("txtAuthor", 0, "")
        End If
        If Not oDocInfo.PropertySetInfo.HasPropertyByName("txtAtomPubUrl") Then
            oDocInfo.addProperty("txtAtomPubUrl", 0, "")
        End If
        If Not oDocInfo.PropertySetInfo.HasPropertyByName("txtCategories") Then
            oDocInfo.addProperty("txtCategories", 0, "")
        End If
        If Not oDocInfo.PropertySetInfo.HasPropertyByName("optAuthType") Then
            oDocInfo.addProperty("optAuthType", 0, "Basic")
        End If
        If Not oDocInfo.PropertySetInfo.HasPropertyByName("txtUsername") Then
            oDocInfo.addProperty("txtUsername", 0, "")
        End If
        If Not oDocInfo.PropertySetInfo.HasPropertyByName("chkDraft") Then
            oDocInfo.addProperty("chkDraft", 0, fnConvertToBoolean(1))
        End If
        If Not oDocInfo.PropertySetInfo.HasPropertyByName("chkNewEntry") Then
            oDocInfo.addProperty("chkNewEntry", 0, fnConvertToBoolean(1))
        End If
    #Else
        On Error Resume Next
        ActiveDocument.CustomDocumentProperties.Add name:="chkTitle", LinkToContent:=False, value:=True, Type:=msoPropertyTypeNumber
        ActiveDocument.CustomDocumentProperties.Add name:="chkTableOfContents", LinkToContent:=False, value:=False, Type:=msoPropertyTypeNumber
        ActiveDocument.CustomDocumentProperties.Add name:="chkPDF", LinkToContent:=False, value:=False, Type:=msoPropertyTypeNumber
        ActiveDocument.CustomDocumentProperties.Add name:="filTemplate", LinkToContent:=False, value:="", Type:=msoPropertyTypeString
        ActiveDocument.CustomDocumentProperties.Add name:="filSaveDir", LinkToContent:=False, value:="", Type:=msoPropertyTypeString
        ActiveDocument.CustomDocumentProperties.Add name:="txtTitle", LinkToContent:=False, value:="", Type:=msoPropertyTypeString
        If fnGetDocProp("txtTitle") = "" Then
            Call subSetDocProp("txtTitle", ActiveDocument.BuiltInDocumentProperties(wdPropertyTitle))
        End If
        ActiveDocument.CustomDocumentProperties.Add name:="txtAuthor", LinkToContent:=False, value:="", Type:=msoPropertyTypeString
        ActiveDocument.CustomDocumentProperties.Add name:="txtSummary", LinkToContent:=False, value:="", Type:=msoPropertyTypeString
        ActiveDocument.CustomDocumentProperties.Add name:="txtAtomPubUrl", LinkToContent:=False, value:="", Type:=msoPropertyTypeString
        ActiveDocument.CustomDocumentProperties.Add name:="txtCategories", LinkToContent:=False, value:="", Type:=msoPropertyTypeString
        ActiveDocument.CustomDocumentProperties.Add name:="optAuthType", LinkToContent:=False, value:="Basic", Type:=msoPropertyTypeString
        ActiveDocument.CustomDocumentProperties.Add name:="txtUsername", LinkToContent:=False, value:="", Type:=msoPropertyTypeString
        ActiveDocument.CustomDocumentProperties.Add name:="chkDraft", LinkToContent:=False, value:=True, Type:=msoPropertyTypeNumber
        ActiveDocument.CustomDocumentProperties.Add name:="chkNewEntry", LinkToContent:=False, value:=True, Type:=msoPropertyTypeNumber
    #End If
End Sub

Function fnConvertToBoolean(value) As Boolean
    Rem this should fix the conversion
    fnConvertToBoolean = CBool(value)
End Function

Function fnConvertToInteger(value) As Integer
    Dim intValue  As Integer
    If VarType(value) = 11 Or VarType(value) = 2 Then
        intValue = CInt(value)
    Else
        Rem if string
        intValue = CInt(CBool(value))
    End If
    If intValue <> 0 Then
        intValue = 1
    End If
    fnConvertToInteger = intValue
End Function

Function fnConvertToString(value) As String
    fnConvertToString = CStr(CBool(value))
End Function

Sub PublishToBlog()
    #If MSWD Then
        If Not fnIsThereAFile() Then
            Exit Sub
        End If
    #End If
    Call subPublish
End Sub

Sub subPublish()
    If Not fnDialogStartup Then
        Exit Sub
    End If
    #If OOO Then
        DialogLibraries.LoadLibrary ("IceLibrary")
        udg_oDialogPublish = CreateUnoDialog(DialogLibraries.IceLibrary.dlgPublish)
        Rem this is needed for preview
        udg_oDialogConvert = CreateUnoDialog(DialogLibraries.IceLibrary.dlgConvert)
    #Else
        Set udg_oDialogPublish = frmPublish
        Set udg_oDialogConvert = frmConvert
    #End If

    Call subSetDlgCtrlText(udg_oDialogPublish, "txtTitle", fnGetDocProp("txtTitle"))
    Call subSetDlgCtrlText(udg_oDialogPublish, "txtAuthor", fnGetDocProp("txtAuthor"))
    Call subSetDlgCtrlText(udg_oDialogPublish, "txtSummary", fnGetDocProp("txtSummary"))
    Call subSetDlgCtrlText(udg_oDialogPublish, "txtAtomPubUrl", fnGetDocProp("txtAtomPubUrl"))
    Call subSetDlgCtrlText(udg_oDialogPublish, "txtCategories", fnGetDocProp("txtCategories"))
    Call subSetDlgCtrlState(udg_oDialogPublish, "opt" + fnGetDocProp("optAuthType"), 1)
    Call subSetDlgCtrlText(udg_oDialogPublish, "txtUsername", fnGetDocProp("txtUsername"))
    Call subSetDlgCtrlState(udg_oDialogPublish, "chkDraft", fnConvertToInteger(fnGetDocProp("chkDraft")))
    Call subSetDlgCtrlState(udg_oDialogPublish, "chkNewEntry", fnConvertToInteger(fnGetDocProp("chkNewEntry")))
    Call subSetDlgCtrlState(udg_oDialogConvert, "chkPDF", fnConvertToInteger(fnGetDocProp("chkPDF")))
    If Not CheckFile Then
        Exit Sub
    End If
    proxyFile = subGetProxyFile
    If fnFileExists(proxyFile) Then
        Call subSetDlgCtrlText(udg_oDialogPublish, "txtProxy", fnReadFile(proxyFile))
    End If

    subExecuteDialog (udg_oDialogPublish)

    If fnGetDlgCtrlText(udg_oDialogPublish, "txtProxy") = "" Then
        subKill (proxyFile)
    Else
        Call fnWriteFile(proxyFile, fnGetDlgCtrlText(udg_oDialogPublish, "txtProxy"))
    End If

    Call subSetDocProp("txtTitle", fnGetDlgCtrlText(udg_oDialogPublish, "txtTitle"))
    Call subSetDocProp("txtAuthor", fnGetDlgCtrlText(udg_oDialogPublish, "txtAuthor"))
    Call subSetDocProp("txtSummary", fnGetDlgCtrlText(udg_oDialogPublish, "txtSummary"))
    Call subSetDocProp("txtAtomPubUrl", fnGetDlgCtrlText(udg_oDialogPublish, "txtAtomPubUrl"))
    Call subSetDocProp("txtCategories", fnGetDlgCtrlText(udg_oDialogPublish, "txtCategories"))
    Select Case True
    Case fnGetDlgCtrlState(udg_oDialogPublish, "optNone")
        Call subSetDocProp("optAuthType", "None")
    Case fnGetDlgCtrlState(udg_oDialogPublish, "optBasic")
        Call subSetDocProp("optAuthType", "Basic")
    Case fnGetDlgCtrlState(udg_oDialogPublish, "optBlogger")
        Call subSetDocProp("optAuthType", "Blogger")
    End Select
    Call subSetDocProp("txtUsername", fnGetDlgCtrlText(udg_oDialogPublish, "txtUsername"))
    Call subSetDocProp("chkDraft", fnConvertToBoolean(fnGetDlgCtrlState(udg_oDialogPublish, "chkDraft")))
    Call subSetDocProp("chkNewEntry", fnConvertToBoolean(fnGetDlgCtrlState(udg_oDialogPublish, "chkNewEntry")))
    Call subSetDocProp("chkPDF", fnConvertToBoolean(fnGetDlgCtrlState(udg_oDialogConvert, "chkPDF")))
End Sub

Sub convertToHTML()
    #If MSWD Then
        If Not fnIsThereAFile() Then
            Exit Sub
        End If
    #End If
    Call subConvert
End Sub

Sub subConvert()
    If Not fnDialogStartup Then
        Exit Sub
    End If
    #If OOO Then
        DialogLibraries.LoadLibrary ("IceLibrary")
        udg_oDialogConvert = CreateUnoDialog(DialogLibraries.IceLibrary.dlgConvert)
    #Else
        Set udg_oDialogConvert = frmConvert
    #End If

    Call subSetDlgCtrlState(udg_oDialogConvert, "chkTitle", fnConvertToInteger(fnGetDocProp("chkTitle")))
    Call subSetDlgCtrlState(udg_oDialogConvert, "chkTableOfContents", fnConvertToInteger(fnGetDocProp("chkTableOfContents")))
    Call subSetDlgCtrlState(udg_oDialogConvert, "chkPDF", fnConvertToInteger(fnGetDocProp("chkPDF")))
    If Not CheckFile Then
        Exit Sub
    End If
    Call subSetDlgCtrlText(udg_oDialogConvert, "filTemplate", fnGetDocProp("filTemplate"))
    Call subSetDlgCtrlText(udg_oDialogConvert, "filSaveDir", docName)

    subExecuteDialog (udg_oDialogConvert)

    Call subSetDocProp("chkTitle", fnConvertToBoolean(fnGetDlgCtrlState(udg_oDialogConvert, "chkTitle")))
    Call subSetDocProp("chkTableOfContents", fnConvertToBoolean(fnGetDlgCtrlState(udg_oDialogConvert, "chkTableOfContents")))
    Call subSetDocProp("chkPDF", fnConvertToBoolean(fnGetDlgCtrlState(udg_oDialogConvert, "chkPDF")))
    Call subSetDocProp("filTemplate", fnGetDlgCtrlText(udg_oDialogConvert, "filTemplate"))
    Call subSetDocProp("filSaveDir", fnGetDlgCtrlText(udg_oDialogConvert, "filSaveDir"))
End Sub

Function CheckFile()
    docName = fnGetDocPath
    If docName = "" Then
        printMsgbox ("Please save current document first")
        CheckFile = False
        Exit Function
    End If
    docName = fnGetDocName
    fileParts = Split(docName, ".")
    If fileParts(UBound(fileParts)) <> "odt" And fileParts(UBound(fileParts)) <> "doc" And fileParts(UBound(fileParts)) <> "docx" Then
        printMsgbox ("Cannot support this file extension")
        CheckFile = False
        Exit Function
    End If
    CheckFile = True
End Function
Sub subConvertExecute()
    #If MSWD Then
        Set udg_oDialogConvert = frmConvert
    #End If
    Call subExecute(udg_oDialogConvert, "convert", False)
End Sub

Sub subConvertPreview()
    #If MSWD Then
        Set udg_oDialogConvert = frmConvert
    #End If
    Call subExecute(udg_oDialogConvert, "convert", True)
End Sub

Sub subPublishExecute()
    #If MSWD Then
        Set udg_oDialogPublish = frmPublish
    #End If
    Call subExecute(udg_oDialogPublish, "publish", False)
End Sub

Sub subPublishPreview()
    #If MSWD Then
        Set udg_oDialogPublish = frmPublish
    #End If
    Call subExecute(udg_oDialogPublish, "publish", True)
End Sub

Sub subExecute(oDialog, mode, preview)
    docName = fnGetDocName
    tempDir = fnGetTempDir
    If docName = "" Then
        printMsgbox ("Please save current document first")
        Exit Sub
    End If
    sIceLoc = fnGetIceLoc
    Select Case fnGetOSType
        Case 1
            iceCmd = "C: && cd """ + sIceLoc + """ && bin\ice.exe"
            Rem for testing purpose
            Rem iceCmd = "C: && cd ""C:\cynthia\workspace\ice\trunk\apps\ice"" && python ice2.py"
            s = "\"
        Case Else
            iceCmd = sIceLoc
            s = "/"
    End Select
    
    If fnGetOSType = 4 Then
        quote = "'"
    Else
        quote = """"
    End If

    checkBoxBool = Array("False", "True")

    If mode = "publish" Then
        includeTitle = " -includetitle " + checkBoxBool(0)
        includeToC = " -toc " + checkBoxBool(0)
        includePDF = " -pdfLink " + fnConvertToString(fnGetDlgCtrlState(oDialog, "chkPDF"))

        templateString = "<div><div class='ins pdf-rendition-link'></div><div class='ins page-toc'></div><div class='ins body'></div></div>"

        If fnGetOSType = 1 Then
            filTemplate = " -templateString " + quote + templateString + quote
        Else
            tempDir = fnGetTempDir
            tempFile = tempDir + "/template.txt"
            Call fnWriteFile(tempFile, templateString)
            filTemplate = " -template " + quote + tempFile + quote
        End If
        isDraft = fnConvertToBoolean(fnGetDlgCtrlState(oDialog, "chkDraft"))
        Draft = " -draft " + quote + fnConvertToString(isDraft) + quote
        newEntry = " -new " + quote + fnConvertToString(fnGetDlgCtrlState(oDialog, "chkNewEntry")) + quote
        saveDir = tempDir

        Rem authType
        Select Case True
        Case fnGetDlgCtrlState(oDialog, "optNone")
            authType = " -authType None"
        Case fnGetDlgCtrlState(oDialog, "optBasic")
            authType = " -authType Basic"
        Case fnGetDlgCtrlState(oDialog, "optBlogger")
            authType = " -authType Blogger"
        End Select

        Rem title
        If fnGetDlgCtrlText(oDialog, "txtTitle") = "" Then
            Rem title is an internal variable name and will cause it to crash badly. therefore use txtTitle
            txtTitle = ""
            If Not preview Then
                subDispErr ("Title")
                Exit Sub
            End If
        Else
            Dim Title As String
            Title = fnGetDlgCtrlText(oDialog, "txtTitle")
            If InStr(Title, "'") Or InStr(Title, """") Then
                Title = Replace(Title, "'", "%27")
                Title = Replace(Title, """", "%22")
                Title = Replace(Title, " ", "%20")
                txtTitle = " -title " + quote + quote + " -urlencodedtitle " + quote + Title + quote
            Else
                txtTitle = " -title " + quote + Title + quote
            End If
        End If

        Rem atomPubURL
        If fnGetDlgCtrlText(oDialog, "txtAtomPubUrl") = "" Then
            atomPubUrl = ""
            If Not preview Then
                subDispErr ("URL")
                Exit Sub
            End If
        Else
            Rem  for display later
            atomURL = fnGetDlgCtrlText(oDialog, "txtAtomPubUrl")
            If Left(atomURL, 4) <> "http" Then
                printMsgbox ("URL is invalid. Please check again.")
                Exit Sub
            End If
            atomPubUrl = " -atomPubUrl " + quote + atomURL + quote
        End If
        
        Rem Categories
        If fnGetDlgCtrlText(oDialog, "txtCategories") = "" Then
            categories = ""
        Else
            categories = fnGetDlgCtrlText(oDialog, "txtCategories")
            If Right(categories, 1) = ";" Then
                categories = Left(categories, Len(categories) - 1)
            End If
            categories = " -categories=" + quote + categories + quote
        End If
        
        Rem username
        If fnGetDlgCtrlText(oDialog, "txtUsername") = "" Then
            UserName = ""
            If Not (preview Or fnGetDlgCtrlState(oDialog, "optNone")) Then
                subDispErr ("Username")
                Exit Sub
            End If
        Else
            If fnGetOSType = 3 Then
               UserName = " -username " + fnGetDlgCtrlText(oDialog, "txtUsername")
            Else
               UserName = " -username " + quote + fnGetDlgCtrlText(oDialog, "txtUsername") + quote
            End If
        End If

        Rem password
        If fnGetDlgCtrlText(oDialog, "txtPassword") = "" Then
            Password = ""
            If Not (preview Or fnGetDlgCtrlState(oDialog, "optNone")) Then
                subDispErr ("Password")
                Exit Sub
            End If
        Else
            If fnGetOSType = 3 Then
                Password = " -password " + fnGetDlgCtrlText(oDialog, "txtPassword")
            Else
                Password = " -password " + quote + fnGetDlgCtrlText(oDialog, "txtPassword") + quote
            End If
        End If

        Rem authorl
        If fnGetDlgCtrlText(oDialog, "txtAuthor") = "" Then
            Author = ""
        Else
            Author = " -author " + quote + fnGetDlgCtrlText(oDialog, "txtAuthor") + quote
        End If

        Rem summary
        If fnGetDlgCtrlText(oDialog, "txtSummary") = "" Then
            summary = ""
        Else
            Dim varSummary As String
            varSummary = fnGetDlgCtrlText(oDialog, "txtSummary")
            If InStr(varSummary, "'") Or InStr(varSummary, """") Then
                varSummary = Replace(varSummary, "'", "%27")
                varSummary = Replace(varSummary, """", "%22")
                varSummary = Replace(varSummary, " ", "%20")
                summary = " -summary " + quote + quote + " -urlencodedsummary " + quote + varSummary + quote
            Else
                summary = " -summary " + quote + summary + quote
            End If
        End If


        Rem proxy
        If fnGetDlgCtrlText(oDialog, "txtProxy") = "" Then
            proxyCmd = ""
        Else
            If fnGetOSType = 1 Then
                proxyCmd = "set http_proxy=" + fnGetDlgCtrlText(oDialog, "txtProxy") + " && "
            ElseIf fnGetOSType = 4 Then
                printMsgbox ("Warning: Cannot set Proxy. Please set manually")
            Else
                Rem mac does not like to set http_proxy so hopefully the ice will do so.
                Rem proxyCmd = "export http_proxy=" + fnGetDlgCtrlText(oDialog, "txtProxy") + " && "
            End If
        End If
    Else
        Rem convert
        includeTitle = " -includetitle " + fnConvertToString(fnGetDlgCtrlState(oDialog, "chkTitle"))
        includeToC = " -toc " + fnConvertToString(fnGetDlgCtrlState(oDialog, "chkTableOfContents"))
        includePDF = " -pdfLink " + fnConvertToString(fnGetDlgCtrlState(oDialog, "chkPDF"))

        If fnGetDlgCtrlText(oDialog, "filTemplate") = "" Then
            filTemplate = ""
        Else
            filTemplate = " -template """ + fnGetDlgCtrlText(oDialog, "filTemplate") + """"
        End If

        If fnGetDlgCtrlText(oDialog, "filSaveDir") = "" Then
            Rem saveDir = docName
            saveDir = fnGetDocPath
        Else
            saveDir = fnGetDlgCtrlText(oDialog, "filSaveDir")
        End If
        If Right(saveDir, 1) = "/" Or Right(saveDir, 1) = "\" Then
            Rem if window, then the "/" or "\" at the end causes the error .
            saveDir = Left(saveDir, Len(saveDir) - 1)
        End If
        If Not fnDirExists(saveDir) Then
            MsgBox fnDirExists(saveDir)
            printMsgbox ("Output Location Directory is not found.")
            Exit Sub
        End If
        
    End If

    If preview Then
        saveDir = tempDir
    End If
    Rem  This is to keep the save path clean
    saveTempDir = saveDir
    
    Rem to prevent the ice from deleting source document
    sourceLink = " -sourceLink True"

    docName = " -f " + quote + docName + quote
    saveDir = " -d " + quote + saveDir + quote
    openCmdString = " -open"
    cmdString = iceCmd + " -convert" + docName + saveDir + includeTitle + includeToC + includePDF + sourceLink + filTemplate
    If preview Then
        cmdString = cmdString + openCmdString
    ElseIf mode = "publish" Then
        If isDraft Then
            openCmdString = ""
        End If
        If fnGetOSType = 4 Then
            cmdString = iceCmd + " -convert -atomConvertPub" + docName + saveDir + includeTitle + includeToC + sourceLink + includePDF + filTemplate + atomPubUrl + categories + txtTitle + authType + UserName + Password + Author + summary + Draft + newEntry + openCmdString
        Else
            cmdString = proxyCmd + iceCmd + " -convert -atomConvertPub" + docName + saveDir + includeTitle + sourceLink + includeToC + includePDF + filTemplate + atomPubUrl + categories + txtTitle + authType + UserName + Password + Author + summary + Draft + newEntry + openCmdString
        End If
    End If
    cmd = cmdString
    Rem execute the .bat files
    Select Case fnGetOSType
    Case 1:
        Rem window
        cmd = "cmd /c " + cmdString
    Case 3:
        Rem Mac
        cmd = cmdString
    Case 4:
        Rem Ubuntu
        cmd = "gnome-terminal -e """ + cmdString + """ --working-directory=""" + Environ("ICE_HOME") + """"
    End Select
   
    If Not preview And mode = "convert" Then
        Select Case fnGetOSType
            Case 1:
                cmd = cmd + " && cd """ + saveTempDir + """ && explorer ."
            Case 3:
                cmdString = "open " + saveTempDir
                Shell (cmdString)
                Rem Todo find if the command can be added like windows
                Rem open cannot be joined in Mac does not work with shell.
            Case 4:
                Rem Example command
                Rem cmd = "gnome-terminal -x bash -c ""/home/wongcyn/ice2/apps/ice/ice.sh -convert
                Rem -f '/home/wongcyn/Desktop/Untitled 1.odt' -d '/home/wongcyn/Desktop' -includetitle True -toc True
                Rem  -pdfLink True; nautilus /home/wongcyn/Desktop;""
                Rem  -working-directory=""/home/wongcyn/ice2/apps/ice"""
                cmd = "gnome-terminal -x bash -c """ + cmdString + " ; nautilus " + saveTempDir + """ --working-directory=""" + Environ("ICE_HOME") + """"
        End Select
        
    End If
    Shell (cmd)
    Rem testing remove comment for the following lines
    Rem oVC = fnGetViewCursor
    Rem oVC.String = cmd
    Rem if word
    Rem Selection.Range.Text = cmd
End Sub

Rem ############ These are added for workaround for GetGuiType function for now. ############
Sub subSetIceLoc(loc As String)
    sIceLoc = loc
End Sub

Function fnGetIceLoc()
    fnGetIceLoc = sIceLoc
End Function

Sub subSetOSType(t As Integer)
    OSType = t
End Sub

Function fnGetOSType()
    Rem return the os type as follow
    Rem Windows = 1
    Rem Mac OS = 3
    Rem Ubuntu = 4
    If OSType <> 0 Then
        Rem OSType variable is the work around for the GetGuiType for now.
        Rem This variable is assumed to be set on the form loads.
        fnGetOSType = OSType
    Else
        Rem Just in Case the OSType is never set
        #If OOO Then
            Rem     The following GetGuiType is not working for Mac OSX. It is defected in the OOo code.
            Rem     See http://www.openoffice.org/issues/show_bug.cgi?id=95717 .
            Rem     Need to work around for now.
            fnGetOSType = GetGuiType
        #Else
            If InStr(Application.System.OperatingSystem, "Windows") Then
               fnGetOSType = 1
            Else
               Rem this set the default as Mac.
               Rem I have assumed user will not use MS Word on Ubuntu.
               Rem of course if they are using WINE, then I am dead. :P.
               Rem thus to do. find out what word call Mac. in this variable.
               fnGetOSType = 3
            End If
        #End If
    End If
End Function
Rem #############################################################################
Function fnGetDocName()
    #If OOO Then
        fnGetDocName = ConvertFromURL(ThisComponent.URL)
    #Else
        fnGetDocName = ActiveDocument.FullName
    #End If
End Function

Function fnGetDocPath()
    #If OOO Then
        docName = fnGetDocName
        If docName <> "" Then
            For i = Len(docName) To 1 Step -1
                If InStr("/\", Mid(docName, i, 1)) Then
                    Exit For
                End If
            Next
            Rem  -1 to get rid of slash
            fnGetDocPath = Left(docName, i - 1)
        Else
            fnGetDocPath = ""
        End If
    #Else
        fnGetDocPath = ActiveDocument.Path
    #End If
End Function

Function fnGetTempDir()
    #If OOO Then
        fnGetTempDir = ConvertFromURL(createUnoService("com.sun.star.util.PathSettings").temp)
    #Else
        fnGetTempDir = CreateObject("Scripting.FileSystemObject").GetSpecialFolder(2)
    #End If
End Function

Function subGetProxyFile()
    #If OOO Then
        If fnGetOSType = 1 Then
            Rem the best path to use is storage since it is the most similar to the one we want.
            paths = createUnoService("com.sun.star.util.PathSettings")
            If Int(getOOoVersion()) = 2 Then
                Rem go up to common folder and back down to ice folder
                subGetProxyFile = ConvertFromURL(Left(paths.Storage, InStr(paths.Storage, "/OpenOffice.org2/user/store"))) + "Ice\http_proxy.txt"
            Else
                Rem go up to common folder and back down to ice folder
                subGetProxyFile = ConvertFromURL(Left(paths.Storage, InStr(paths.Storage, "/OpenOffice.org/3/user/store"))) + "Ice\http_proxy.txt"
            End If
        Else
           Rem  don't know why sam put this. will have to check later.
           Rem  subGetProxyFile = "/Users/knipes/Ice/http_proxy.txt"
           Rem do nothing at the moment
        End If
    #Else
        If fnGetOSType = 1 Then
            Rem sTempFilePath = Options.DefaultFilePath(wdTempFilePath)
            Rem subGetProxyFile = Left(sTempFilePath, InStr(sTempFilePath, "\locals~1\temp")) + "Applic~1\Ice\http_proxy.txt"
            If Right(Environ("USERPROFILE"), 1) <> "/" Or Right(Environ("USERPROFILE"), 1) <> "\" Then
                subGetProxyFile = Environ("USERPROFILE") + "\Applic~1\Ice\http_proxy.txt"
            Else
                subGetProxyFile = Environ("USERPROFILE") + "Applic~1\Ice\http_proxy.txt"
            End If
        Else
            Rem Don't do anything
        End If
    #End If
End Function

Function fnDirExists(sDirName)
    #If OOO Then
        
    #Else
        If (GetAttr(sDirName) And vbDirectory) = vbDirectory Then
            Rem Check if directory
            fnDirExists = True
        Else
            fnDirExists = False
        End If
    #End If
End Function


Function fnFileExists(sFileName)
    #If OOO Then
        fnFileExists = createUnoService("com.sun.star.ucb.SimpleFileAccess").Exists(ConvertToURL(sFileName))
    #Else
        fnFileExists = CreateObject("Scripting.FileSystemObject").FileExists(sFileName)
    #End If
End Function



Sub subKill(sFileName)
    If fnFileExists(sFileName) Then
        #If OOO Then
            createUnoService("com.sun.star.ucb.SimpleFileAccess").Kill (ConvertToURL(sFileName))
        #Else
            Call CreateObject("Scripting.FileSystemObject").DeleteFile(sFileName, True)
        #End If
    End If
End Sub


Function fnReadFile(sFileName)
    If Not fnFileExists(sFileName) Then
        Rem something's not right, we can't open a file that doesn't exist
        Exit Function
    End If
    #If OOO Then
        oInputStream = createUnoService("com.sun.star.ucb.SimpleFileAccess").openFileRead(ConvertToURL(sFileName))
        sFileContents = FileReadString(oInputStream)
        oInputStream.closeInput
    #Else
        If fnFileExists(sFileName) Then
            With CreateObject("Scripting.FileSystemObject").GetFile(sFileName).OpenAsTextStream(1, TristateUseDefault)
                sFileContents = .ReadAll
                .Close
            End With
        Else
            sFileContents = ""
        End If
    #End If
    fnReadFile = sFileContents
End Function


Function fnWriteFile(sFileName, sFileContents, Optional bKillFile)
    If IsMissing(bKillFile) Then
        bKillFile = True
    End If
    If bKillFile Then
        subKill (sFileName)
    End If
    #If OOO Then
        On Error Resume Next
        oOutputStream = createUnoService("com.sun.star.ucb.SimpleFileAccess").openFileWrite(ConvertToURL(sFileName))
        FileWriteString(oOutputStream, sFileContents)
        oOutputStream.closeOutput
    #Else
        With CreateObject("Scripting.FileSystemObject").CreateTextFile(sFileName, bKillFile)
            .Write (sFileContents)
            .Close
        End With
    #End If
    fnWriteFile = sFileName
End Function


Sub FileWriteString(oOS, ByVal cString As String)
    #If OOO Then
        oOutputStream = oOS
        Rem Convert the string into an array of bytes.
        aBytesToWrite = StringToByteArray(cString)

        Rem Write the bytes to the output file.
        oOutputStream.writeBytes (aBytesToWrite)
    #End If
End Sub


Function StringToByteArray(ByVal cString As String)
    nNumBytes = Len(cString)
    If nNumBytes = 0 Then
        StringToByteArray() = 0
        Exit Function
    End If
    Rem ToDo: Resolve error on OS X
    Rem On Error Resume Next
    Dim aBytes(nNumBytes - 1) As Integer
    For i = 1 To nNumBytes
        cChar = Mid(cString, i, 1)
        nByte = Asc(cChar)
        nByte = IntegerToByte(nByte)
        aBytes(i - 1) = nByte
    Next
    StringToByteArray() = aBytes()
End Function

Function IntegerToByte(ByVal nByte As Integer) As Integer
    If nByte > 127 Then
        nByte = nByte - 256
    End If
    IntegerToByte = nByte
End Function

Function FileReadString(oIS, Optional nNumBytesToRead As Integer) As String
    #If OOO Then
        oInputStream = oIS
        aBytesToRead = Array()
        If IsMissing(nNumBytesToRead) Then
            nNumBytesToRead = oInputStream.Length()
        End If
        Rem  Read the bytes from the output file.
        oInputStream.readBytes(aBytesToRead, nNumBytesToRead)
        Rem Return the array of bytes as a string.
        FileReadString = ByteArrayToString(aBytesToRead)
    #End If
End Function

Function ByteArrayToString(aByteArray)
    cBytes = ""
    For i = LBound(aByteArray) To UBound(aByteArray)
        nByte = aByteArray(i)
        nByte = ByteToInteger(nByte)
        cBytes = cBytes + Chr(nByte)
    Next i
    ByteArrayToString() = cBytes
End Function

Function ByteToInteger(ByVal nByte As Integer) As Integer
    If nByte < 0 Then
        nByte = nByte + 256
    End If
    ByteToInteger() = nByte
End Function

Sub subDispErr(sMissingInfo)
    printMsgbox ("Please fill in the " + sMissingInfo + " field.")
End Sub

Sub subViewLog()
    tempDir = fnGetTempDir
    If fnGetOSType = 1 Then
        s = "\"
        sLogCmd = "notepad "
    ElseIf fnGetOSType = 4 Then
        s = "/"
        sLogCmd = "gedit "
    Else
        s = "/"
        sLogCmd = "open "
    End If
    cmdString = sLogCmd + tempDir + s + "ice.log"
    Shell (cmdString)
End Sub

Function fnGetDocProp(sPropertyName)
    #If OOO Then
        fnGetDocProp = ThisComponent.getDocumentInfo().getPropertyValue(sPropertyName)
    #Else
        fnGetDocProp = ActiveDocument.CustomDocumentProperties(sPropertyName)
    #End If
End Function

Function convertToSuitableType(vVarType, vValue)
Rem vbEmpty     0   Empty (Empty: The state of an uninitialized Variant variable (which returns a VarType of 0). Not to be confused with Null (a variable state indicating invalid data), variables with zero-length strings (" "), or numeric variables equal zero.)  (uninitialized)
Rem vbNull  1   Null (Null: A value you can enter in a field or use in expressions or queries to indicate missing or unknown data. In Visual Basic, the Null keyword indicates a Null value. Some fields, such as primary key fields, can't contain Null.) (no valid data)
Rem vbInteger   2   Integer
Rem vbLong  3   Long integer
Rem vbSingle    4   Single-precision floating-point number
Rem vbDouble    5   Double-precision floating-point number
Rem vbCurrency  6   Currency value
Rem vbDate  7   Date value
Rem vbString    8   String
Rem vbObject    9   Object
Rem vbError     10  Error value
Rem vbBoolean   11  Boolean value
Rem vbVariant   12  Variant (used only with arrays (array: A variable that contains a finite number of elements that have a common name and data type. Each element of an array is identified by a unique index number. Changes made to one element of an array don't affect the other elements.) of variants)
Rem vbDataObject    13  A data access object
Rem vbDecimal   14  Decimal value
Rem vbByte  17  Byte value
Rem vbUserDefinedType   36  Variants that contain user-defined types
Rem vbArray     8192    Array

    If vVarType = 2 Then
        convertToSuitableType = CInt(vValue)
    ElseIf vVarType = 3 Then
        convertToSuitableType = CLng(vValue)
    ElseIf vVarType = 5 Then
        convertToSuitableType = CDbl(vValue)
    ElseIf vVarType = 8 Then
        convertToSuitableType = CStr(vValue)
    ElseIf vVarType = 11 Then
        convertToSuitableType = CBool(vValue)
    Else
        convertToSuitableType = "Error in storing the form data: Unsupported Data Type. This will cause the lost of form data"
    End If
End Function

Sub subSetDocProp(sPropertyName, vNewValue)
    #If OOO Then
        On Error GoTo wrongType
        thisComponent.getDocumentInfo().setPropertyValue(sPropertyName, vNewValue)
        Exit Sub
wrongType:
        Rem fix the wrong type error
        value = convertToSuitableType(VarType(fnGetDocProp(sPropertyName)), vNewValue)
        On Error GoTo otherError
        If VarType(value) <> 8 Then
            thisComponent.getDocumentInfo().setPropertyValue(sPropertyName, value)
        Else
            If InStr(value, "Error in storing the form data:") = 0 Then
                thisComponent.getDocumentInfo().setPropertyValue(sPropertyName, value)
            End If
        End If
        Exit Sub
otherError:
        Rem This is for the last solution for the error. Hope there is no more error
        ThisComponent.getDocumentInfo().removeProperty (sPropertyName)
        thisComponent.getDocumentInfo().addProperty(sPropertyName, 0,vNewValue)
    #Else
        ActiveDocument.CustomDocumentProperties(sPropertyName) = vNewValue
    #End If
End Sub

Function fnGetDlgCtrlText(oDialog, sControlName)
On Error GoTo noData
    #If OOO Then
        fnGetDlgCtrlText = oDialog.getControl(sControlName).GetText
    #Else
        Select Case sControlName
        Case "filTemplate"
            fnGetDlgCtrlText = oDialog.filTemplate
        Case "filSaveDir"
            fnGetDlgCtrlText = oDialog.filSaveDir
        Case "txtTitle"
            fnGetDlgCtrlText = oDialog.txtTitle
        Case "txtAuthor"
            fnGetDlgCtrlText = oDialog.txtAuthor
        Case "txtSummary"
            fnGetDlgCtrlText = oDialog.txtSummary
        Case "txtAtomPubUrl"
            fnGetDlgCtrlText = oDialog.txtAtomPubUrl
        Case "txtUsername"
            fnGetDlgCtrlText = oDialog.txtUsername
        Case "txtPassword"
            fnGetDlgCtrlText = oDialog.txtPassword
        Case "txtProxy"
            fnGetDlgCtrlText = oDialog.txtProxy
        Case "txtCategories"
            fnGetDlgCtrlText = oDialog.txtCategories
        End Select
        Exit Function
noData:
        fnGetDlgCtrlText = ""
    #End If
End Function

Function fnGetDlgCtrlState(ByVal oDialog, sControlName)
On Error GoTo noData
    #If OOO Then
        fnGetDlgCtrlState = oDialog.getControl(sControlName).GetState
    #Else
        Select Case sControlName
        Case "chkTitle"
            fnGetDlgCtrlState = oDialog.chkTitle
        Case "chkTableOfContents"
            fnGetDlgCtrlState = oDialog.chkTableOfContents
        Case "chkPDF"
            fnGetDlgCtrlState = oDialog.chkPDF
        Case "optNone"
            fnGetDlgCtrlState = oDialog.optNone
        Case "optBasic"
            fnGetDlgCtrlState = oDialog.optBasic
        Case "optBlogger"
            fnGetDlgCtrlState = oDialog.optBlogger
        Case "chkDraft"
            fnGetDlgCtrlState = oDialog.chkDraft
        Case "chkNewEntry"
            fnGetDlgCtrlState = oDialog.chkNewEntry
        End Select
        If fnGetDlgCtrlState <> 0 Then
            fnGetDlgCtrlState = 1
        End If
        Exit Function
noData:
        fnGetDlgCtrlState = 1
    #End If
End Function

Sub subSetDlgCtrlText(oDialog, sControlName, sNewText)
    #If OOO Then
        oDialog.getControl(sControlName).SetText (sNewText)
    #Else
        Select Case sControlName
        Case "filTemplate"
            oDialog.filTemplate = sNewText
        Case "filSaveDir"
            oDialog.filSaveDir = sNewText
        Case "txtTitle"
            oDialog.txtTitle = sNewText
        Case "txtAuthor"
            oDialog.txtAuthor = sNewText
        Case "txtSummary"
            oDialog.txtSummary = sNewText
        Case "txtAtomPubUrl"
            oDialog.txtAtomPubUrl = sNewText
        Case "txtUsername"
            oDialog.txtUsername = sNewText
        Case "txtPassword"
            oDialog.txtPassword = sNewText
        Case "txtProxy"
            oDialog.txtProxy = sNewText
        Case "txtCategories"
            oDialog.txtCategories = sNewText
        End Select
    #End If
End Sub

Sub subSetDlgCtrlState(oDialog, sControlName, bNewState)
    #If OOO Then
        oDialog.getControl(sControlName).SetState (bNewState)
    #Else
        If bNewState <> 0 Then
            bNewState = True
        End If
        Select Case sControlName
        Case "chkTitle"
            oDialog.chkTitle = bNewState
        Case "chkTableOfContents"
            oDialog.chkTableOfContents = bNewState
        Case "chkPDF"
            oDialog.chkPDF = bNewState
        Case "optNone"
            oDialog.optNone = bNewState
        Case "optBasic"
            oDialog.optBasic = bNewState
        Case "optBlogger"
            oDialog.optBlogger = bNewState
        Case "chkDraft"
            oDialog.chkDraft = bNewState
        Case "chkNewEntry"
            oDialog.chkNewEntry = bNewState
        End Select
    #End If
End Sub

Sub subExecuteDialog(ByVal oDialog)
    #If OOO Then
        oDialog.Execute
    #Else
        oDialog.Show
    #End If
End Sub
