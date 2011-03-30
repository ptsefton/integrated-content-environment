@echo

@echo This will move the dist directory and commit it to the svn repository
@echo  (press Ctrl+c to abort!)
pause 

del dist\config.xml
svn update ..\..\..\builds\windows\2.0
svn rm ..\..\..\builds\windows\2.0 --force
svn commit ..\..\..\builds\windows -m "removing 2.0 directory during build"
mkdir ..\..\..\builds\windows\2.0
xcopy dist ..\..\..\builds\windows\2.0 /s /i /y
svn add ..\..\..\builds\windows\2.0
svn commit ..\..\..\builds\windows\2.0 -m "adding new contents for ICE2.0 build" 

@echo Done.
