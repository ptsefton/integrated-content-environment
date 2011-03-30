@echo off
echo Updating ICE, please note this may take a while...
c:
bin\ice.exe -svn:export -path:http://ice.usq.edu.au/svn/ice/builds/windows/2.0 -dir:c:\temp\ice\update
echo Note: You will need to restart ICE for changes to take affect.
pause