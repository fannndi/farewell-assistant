@echo off
powershell -ExecutionPolicy Bypass -File "%~dp0scripts\owner.ps1"
if %ERRORLEVEL% neq 0 pause
