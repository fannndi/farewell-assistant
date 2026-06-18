@echo off
powershell -ExecutionPolicy Bypass -File "%~dp0scripts\initial.ps1"
if %ERRORLEVEL% neq 0 pause
