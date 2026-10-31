@echo off
cd /d "%~dp0"
title Marcos Data Product - Site Local
echo ========================================================
echo   Iniciando Servidor Local - Marcos Data Product
echo   Abrindo no navegador em: http://localhost:8000
echo   Pressione Ctrl+C para encerrar.
echo ========================================================
start http://localhost:8000
python -m http.server 8000
pause

