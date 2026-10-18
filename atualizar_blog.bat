@echo off
cd /d "%~dp0"
title Marcos Data Product - Compilar Blog e Home
echo ========================================================
echo   Compilando posts do Blog e sincronizando a HOME...
echo ========================================================
python tools/build_blog.py
echo ========================================================
echo   Concluido! Todos os artigos e a Home estao sincronizados.
echo ========================================================
pause
