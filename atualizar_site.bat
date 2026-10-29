@echo off
cd /d "%~dp0"
title Marcos Data Product - Sincronizar Todo o Site
echo ========================================================
echo   Sincronizando Blog, Biblioteca e Projetos na Home...
echo ========================================================
python tools/build_all.py
echo ========================================================
echo   Concluido! Todo o site foi sincronizado com sucesso.
echo ========================================================
pause
