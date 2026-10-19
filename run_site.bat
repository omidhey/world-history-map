@echo off
rem Serves the site/ folder at http://localhost:8000
rem Browsers block loading local JSON from file://, so a small local server is needed.
cd /d "%~dp0site"
start "" http://localhost:8000
python -m http.server 8000
