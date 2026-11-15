@echo off
setlocal

set "LaptopIP=192.168.1.180"
set "Port=8765"

if "%~1"=="" exit /b 1

set "Action=%~1"
set "URL=http://%LaptopIP%:%Port%/%Action%"

curl.exe -s --connect-timeout 3 --max-time 5 "%URL%" >nul

endlocal

@REM  ACTIONS
@REM
@REM  plex-control.cmd playpause
@REM  plex-control.cmd up
@REM  plex-control.cmd down
@REM  plex-control.cmd left
@REM  plex-control.cmd right
@REM  plex-control.cmd enter
@REM  plex-control.cmd mute
@REM  plex-control.cmd volumeup
@REM  plex-control.cmd volumedown
