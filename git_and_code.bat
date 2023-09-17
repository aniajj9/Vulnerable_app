@echo off

rem Check if there are changes to commit
git status | findstr /i "Changes not staged for commit" > nul
if errorlevel 1 (
    echo No changes to commit.
) else (
    git add * && git commit -m "%~1" && git push
)

rem Run the Flask app regardless of changes
"c:\Users\bduago\OneDrive - Bankdata\Skrivebord\git\Vuln-app\.venv\Scripts\python.exe" "c:\Users\bduago\OneDrive - Bankdata\Skrivebord\git\Vuln-app\main.py"
