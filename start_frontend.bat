@echo off
echo =====================================
echo  Starting Pridicto Frontend (React)
echo =====================================

cd /d "%~dp0frontend"

if not exist "node_modules" (
    echo [*] Installing npm packages...
    npm install
)

echo [*] Starting React on http://localhost:3000 ...
npm run dev
