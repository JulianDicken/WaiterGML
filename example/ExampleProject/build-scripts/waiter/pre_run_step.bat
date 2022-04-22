@echo off
if "%IGOR_DEPENDENCIES%" == "1" (
    echo "[pre_run_step.bat] Called recursively; skipping."
    exit 0
)
set IGOR_DEPENDENCIES=1

build-scripts\waiter\main.exe -p %YYprojectDir% -v