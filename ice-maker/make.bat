@echo off
rd dist /s /q

python ../ice/plugins/required/plugin_info.py %* > version_info.txt
python setup.py py2exe
del ice.py
rd build /s /q

md dist\bin
move dist\library.zip dist\bin
move dist\*.exe dist\bin
move dist\*.dll dist\bin
move dist\*.pyd dist\bin
copy win32\MSVCP71.dll dist\bin
copy win32\msvcp90.dll dist\bin
copy win32\*.url dist
copy win32\*.bat dist
copy version_info.txt dist\version_info.txt

rem del dist\config.xml
rem svn update ..\..\..\builds\windows\2.0
rem svn rm ..\..\..\builds\windows\2.0 --force
rem svn commit ..\..\..\builds\windows -m "removing 2.0 directory during build"
rem mkdir ..\..\..\builds\windows\2.0
rem xcopy dist ..\..\..\builds\windows\2.0 /s /i /y
rem svn add ..\..\..\builds\windows\2.0
rem svn commit ..\..\..\builds\windows\2.0 -m "adding new contents for ICE2.0 build" 

@echo
@echo
@echo Now run svncommit.bat to commit this build
