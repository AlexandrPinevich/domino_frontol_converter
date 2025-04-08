@echo off
rem Указываем путь к Python
rem Get-Command python
set "PYTHON_PATH=C:\Python313\python.exe"

rem Указываем путь к скрипту
set "SCRIPT_PATH=C:\Users\A.Pinevich\YandexDisk\domino_frontol_converter\src\domino_frontol_for_kas_converter.py"

rem Извлекаем день, месяц и год из текущей даты
set day=%date:~0,2%
set month=%date:~3,2%
set year=%date:~6,4%

rem Формируем дату в формате ГГГГ-ММ-ДД
set LOG_DATE=%year%-%month%-%day%

set "LOG_FILE=C:\Users\A.Pinevich\YandexDisk\domino_frontol_converter\data\FOR_KAS\2_CONVERT_LOG\execution_%LOG_DATE%.log"

rem Проверяем, существует ли Python
if exist "%PYTHON_PATH%" (
    echo [%date% %time%] Запуск скрипта... >> "%LOG_FILE%"
    "%PYTHON_PATH%" "%SCRIPT_PATH%" >> "%LOG_FILE%" 2>&1
    if %errorlevel% equ 0 (
        echo [%date% %time%] Скрипт выполнен успешно. >> "%LOG_FILE%"
    ) else (
        echo [%date% %time%] Ошибка при выполнении скрипта. Код ошибки: %errorlevel% >> "%LOG_FILE%"
    )
) else (
    echo [%date% %time%] Python не найден по пути: "%PYTHON_PATH%" >> "%LOG_FILE%"
)



