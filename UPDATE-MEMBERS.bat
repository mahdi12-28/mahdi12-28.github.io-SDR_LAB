@echo off
cd /d "%~dp0"
py -3 tools\update_members.py
pause
