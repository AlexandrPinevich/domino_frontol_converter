@echo off
setlocal enabledelayedexpansion

rem gpedit.msc Конфигурация компьютера → Конфигурация Windows → Сценарии (запуск/завершение) → Завершение работы.


rem ========== SETTINGS ==========
set "source_folder=C:\domino_frontol_converter\data\FROM_KAS"
set "destination_folder=\\Server\Domino\MAIL\FROM_KAS"
set "log_folder=\\Server\Domino\MAIL\FROM_KAS\Frontol_extract_log"
set "kas_number=kas_3"
set "log_file=%log_folder%\%kas_number%.log"

rem ========== PATH VALIDATION ==========
if not exist "%source_folder%\" (
    echo [FAIL] Source folder missing: %source_folder%
    pause & exit /b 1
)

if not exist "%destination_folder%\" (
    echo [FAIL] Destination folder missing: %destination_folder%
    pause & exit /b 2
)

if not exist "%log_folder%\" (
    echo [FAIL] Log folder missing: %log_folder%
    pause & exit /b 3
)

rem === MAIN OPERATION ===

echo [INFO] Starting script 
echo [INFO] Starting script >> "%log_file%"

rem --- File count ---
set "file_count=0"
for /f %%i in ('dir /b /a-d "%source_folder%" 2^>nul ^| find /c /v ""') do set file_count=%%i
echo [%date% %time%] [DEBUG] file_count="!file_count!" 
echo [%date% %time%] [DEBUG] file_count="!file_count!" >> "%log_file%"

rem --- File move ---
if !file_count! equ 0 (
    echo [%date% %time%] [WARN] No files to process in %source_folder%
    echo [%date% %time%] [WARN] No files to process in %source_folder%  >> "%log_file%"      
) else (
    echo [%date% %time%] [INFO] moving !file_count! files from %source_folder% to %destination_folder%
    echo [%date% %time%] [INFO] moving !file_count! files from %source_folder% to %destination_folder% >> "%log_file%"        
    robocopy "%source_folder%" "%destination_folder%" *.* /MOV /NJH /NJS /NDL /NC /NS /NP
    set "robocopy_errorlevel=!errorlevel!"
    if !robocopy_errorlevel! geq 8 (
        echo [%date% %time%] [ERROR] Critical Robocopy error (code: !robocopy_errorlevel!^)
        echo [%date% %time%] [ERROR] Critical Robocopy error (code: !robocopy_errorlevel!^) >> "%log_file%"            
    ) 
    if !robocopy_errorlevel! leq 7 (
        echo [%date% %time%] [OK] Success Robocopy error level (code: !robocopy_errorlevel!^) less then 8 is ok
        echo [%date% %time%] [OK] Success Robocopy error level (code: !robocopy_errorlevel!^) >> "%log_file%"            
    )
)

rem ========== FINAL OUTPUT ==========
echo [OK] Script finished
echo [OK] Script finished >> "%log_file%"
rem pause
timeout 3 >nul
exit /b 0

