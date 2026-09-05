@echo off
rem Build, commit and push. GitHub Pages publishes app/ about a minute later.
cd /d "%~dp0"
node build.js || exit /b 1
cd ..
git add -A
git commit -m "Build %date%"
git push
