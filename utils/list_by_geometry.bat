@echo off
set "BAT_DIR=%~dp0"

python %BAT_DIR%list_by_geometry.py %1 %2 %3
