@echo off
cd /d "%~dp0"
title Marcos Data Product - Editor de Artigos
echo ========================================================
echo   Iniciando o Editor de Artigos - Marcos Data Product
echo   Abrindo no navegador em: http://localhost:5000
echo ========================================================
python tools/editor.py
pause
