@echo off
echo Checking for update files.
c:
xcopy c:\temp\ice\update . /y /s /q > nul
rd c:\temp\ice\update /s /q > nul
echo Starting ICE.
cmd /c bin\ice.exe -webserver:Paste
pause