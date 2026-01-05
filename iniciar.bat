@echo off
echo ============================================
echo  Sistema de Gestao de Pacientes
echo  Clinica Medica Laura Myrna
echo ============================================
echo.
echo Iniciando o sistema...
echo.

python main.py

if errorlevel 1 (
    echo.
    echo ============================================
    echo  ERRO: Nao foi possivel iniciar o sistema
    echo ============================================
    echo.
    echo Verifique se o Python esta instalado.
    echo.
    pause
)
