@echo off
rem Serves the site/ folder at http://localhost:8000
rem Browsers block loading local JSON from file://, so a small local server is needed.
cd /d "%~dp0"
python pipeline\build_site.py || exit /b 1
cd site
start "" http://localhost:8000
python -m http.server 8000
