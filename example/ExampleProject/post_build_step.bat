@echo off

rem ===Architect===

pushd "%YYprojectDir%"
start /B /wait "" architect.exe -post -build
if %ERRORLEVEL% NEQ 0 (
	exit %ERRORLEVEL%
)
popd

rem ===Architect===

