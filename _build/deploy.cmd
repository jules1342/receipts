@echo off
rem Build, then deploy app/ to the claimed Netlify site. Run "netlify login" once first.
cd /d "%~dp0"
node build.js || exit /b 1
cd ..\app
netlify deploy --prod --dir .
