@echo off
rem ============================================================
rem  start_shutdown_listener.bat
rem  Запускает shutdown_listener.py в фоне, без окна консоли.
rem  Файл должен лежать в одной папке с shutdown_listener.py.
rem  Журнал работы: shutdown_listener.log (в той же папке).
rem
rem  Если автозагрузка не срабатывает, замените слово pythonw
rem  ниже на полный путь к вашему pythonw.exe, например:
rem  "C:\Users\Даня\AppData\Local\Programs\Python\Python312\pythonw.exe"
rem  (свой путь узнайте командой: where python)
rem ============================================================

start "" /min pythonw "%~dp0shutdown_listener.py"
