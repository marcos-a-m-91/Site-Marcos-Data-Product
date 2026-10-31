@echo off
cd /d "%~dp0"
title Marcos Data Product - Sincronizar e Compilar Todo o Site
echo ========================================================
echo   Sincronizando Blog, Biblioteca, Projetos,
echo   Sitemap XML e Compilando Tailwind CSS estatico...
echo ========================================================
python tools/build_site.py
echo ========================================================
echo   Concluido! Todo o site foi sincronizado com sucesso.
echo ========================================================
pause
