@echo off

set SCRIPT_PATH=..\src\main.py --configpath config\config.yml
set LOG_FILE=Log\log.txt

cd /d "%~dp0"
:start
if "%1" == "start" (
    call :start_cloudflare_ddns
) else if "%1" == "stop" (
    call :stop_cloudflare_ddns
) else if "%1" == "restart" (
    call :restart_cloudflare_ddns
) else (
    echo Usage: %0 {start|stop|restart}
    exit /b 1
)
goto :eof

:start_cloudflare_ddns
mkdir /p log 2>nul
mkdir /p config 2>nul
echo Starting the cloudflare_ddns...
start /B /MIN pythonw -u %SCRIPT_PATH% >> %LOG_FILE% 2>&1
echo cloudflare_ddns started.
goto :eof

:stop_cloudflare_ddns
echo Stopping the cloudflare_ddns...
set /p PID=<pid.txt
if defined PID (
   tasklist /FI "PID eq %PID%" | find /I "%PID%" > nul
   if not errorlevel 1 (
      goto :kill
   ) else (
      echo cloudflare_ddns is not running.
   )
)
goto :eof

:kill
taskkill /F /PID %PID%
echo cloudflare_ddns stopped.
goto :eof

:restart_cloudflare_ddns
call :stop_cloudflare_ddns
call :start_cloudflare_ddns
goto :eof
