@echo off

rem ========== Configuration ==========
rem Указываем номер кассы (менять только здесь)
set KAS_NUM=1

rem Указываем путь к скрипту
set "SCRIPT_PATH=C:\domino_frontol_converter\src\domino_frontol_for_kas_converter.py"

rem Формируем пути на основе номера кассы
set "INPUT_DIR=\\Server\Domino\MAIL\FOR_KAS\%KAS_NUM%"
set "OUTPUT_DIR=c:\domino_frontol_converter\data\FOR_KAS\%KAS_NUM%_FRONTOL"
set "LOG_DIR=\\Server\Domino\MAIL\FOR_KAS\%KAS_NUM%_CONVERT_LOG"

rem ========== Initialization ==========
for /f %%A in ('powershell -Command "(Get-Date).ToString('yyyy-MM-dd')"') do set "LOG_DATE=%%A"
set "LOG_FILE=%LOG_DIR%\execution_%LOG_DATE%.log"

rem ========== Python detection ==========
set "PYTHON_PATH="
for /f "delims=" %%P in ('where python 2^>nul') do if not defined PYTHON_PATH set "PYTHON_PATH=%%P"

rem ========== Script validation ==========

if not exist "%PYTHON_PATH%" (
    echo [%date% %time%] [FAIL] Python not found in system PATH >> "%LOG_FILE%"
    echo [%date% %time%] [FAIL] ERROR: Python interpreter not found. Contact support.
    pause
)

if not exist "%SCRIPT_PATH%" (
    echo [%date% %time%] [FAIL] Script not found at %SCRIPT_PATH% >> "%LOG_FILE%"
    echo [%date% %time%] [FAIL] FATAL: Conversion script missing. Contact support.
    pause
)

rem ========== Execution block ==========
echo [SYSTEM] Starting conversion process >> "%LOG_FILE%"
echo [SYSTEM] Starting document conversion...

rem Запуск python скрипта с передачей путей
"%PYTHON_PATH%" "%SCRIPT_PATH%" "%INPUT_DIR%" "%OUTPUT_DIR%" "%LOG_DIR%" >> "%LOG_FILE%" 2>&1
set PYTHON_EXITCODE=%errorlevel%

if %PYTHON_EXITCODE% equ 0 (
    echo [%date% %time%] [OK] Conversion successful >> "%LOG_FILE%"
    echo [%date% %time%] [OK] Conversion completed successfully
) else (
    echo [%date% %time%] [WARNING] Conversion failed with code %errorlevel% >> "%LOG_FILE%"
    echo [%date% %time%] [WARNING] ERROR: Conversion failed. Check logfile: %LOG_FILE%
)

exit /b %PYTHON_EXITCODE%






