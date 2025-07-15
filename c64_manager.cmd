@echo off
REM C64 ROM Collection Manager
REM A batch script to easily run different management functions

REM Check if a command was provided
if "%1"=="" goto :show_help

REM Process commands
if "%1"=="import" goto :import
if "%1"=="generate" goto :generate
if "%1"=="merge" goto :merge
if "%1"=="run" goto :run
if "%1"=="count" goto :count
if "%1"=="version" goto :version
if "%1"=="test" goto :test
if "%1"=="help" goto :show_help

REM Unknown command
echo Error: Unknown command '%1'
goto :show_help

:import
echo Importing games from source collections (will clear existing database)...
python -m src.cli import --src roms
exit /b %errorlevel%

:generate
echo Generating merge script...
python -m src.cli generate --target target
exit /b %errorlevel%

:merge
echo Running merge script to create target collection...
python -m src.cli merge --target target
exit /b %errorlevel%

:run
echo Running complete workflow: import, generate, and merge...
echo Step 1/3: Importing games from source collections...
python -m src.cli import --src roms
if errorlevel 1 exit /b %errorlevel%
echo Step 2/3: Generating merge script...
python -m src.cli generate --target target
if errorlevel 1 exit /b %errorlevel%
echo Step 3/3: Running merge script to create target collection...
python -m src.cli merge --target target
if errorlevel 1 exit /b %errorlevel%
echo Complete workflow finished successfully!
exit /b 0

:count
echo Running count check...
python -m src.cli count
exit /b %errorlevel%

:version
echo Showing version information...
python -m src.cli version
exit /b %errorlevel%

:test
if "%2"=="unit" goto :test_unit
if "%2"=="integration" goto :test_integration
goto :test_all

:test_unit
echo Running unit tests...
set "PYTHONPATH=src" && python -m pytest tests/unit/ -v %3 %4 %5 %6 %7 %8 %9
exit /b %errorlevel%

:test_integration
echo Running integration tests...
set "PYTHONPATH=src" && python -m pytest tests/integration/ -v %3 %4 %5 %6 %7 %8 %9
exit /b %errorlevel%

:test_all
echo Running all tests...
set "PYTHONPATH=src" && python -m pytest tests/ -v %2 %3 %4 %5 %6 %7 %8 %9
exit /b %errorlevel%

:show_help
echo C64 ROM Collection Manager
echo ==========================
echo.
echo Usage: c64_manager.cmd [command]
echo.
echo Available Commands:
echo   import     - Import and normalize game information from source collections
echo   generate   - Generate the merge script for creating the target collection
echo   merge      - Run the merge script to copy best versions to target directory
echo   run        - Execute import, generate, and merge commands in sequence
echo   count      - Run the check_counts.py script for additional verification
echo   version    - Show version information
echo   test       - Run tests using pytest (supports 'unit' or 'integration' as second argument)
echo   help       - Display this help message
echo.
echo Note: Multi-part games are automatically organized into subdirectories.
echo.
exit /b 1
