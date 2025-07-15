@echo off
REM C64 ROM Collection Manager
REM A batch script to easily run different management functions

REM Display help message
:show_help
if "%1"=="" (
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
)

REM Process commands
if "%1"=="import" (
    echo Importing games from source collections (will clear existing database^)...
    python -m src.cli import %*
) else if "%1"=="generate" (
    echo Generating merge script...
    python -m src.cli generate %*
) else if "%1"=="merge" (
    echo Running merge script to create target collection...
    python -m src.cli merge %*
) else if "%1"=="run" (
    echo Running complete workflow: import, generate, and merge...
    echo Step 1/3: Importing games from source collections...
    python -m src.cli import
    if errorlevel 1 exit /b %errorlevel%
    echo Step 2/3: Generating merge script...
    python -m src.cli generate
    if errorlevel 1 exit /b %errorlevel%
    echo Step 3/3: Running merge script to create target collection...
    python -m src.cli merge
    if errorlevel 1 exit /b %errorlevel%
    echo Complete workflow finished successfully!
) else if "%1"=="count" (
    echo Running count check...
    python -m src.cli count %*
) else if "%1"=="version" (
    echo Showing version information...
    python -m src.cli version %*
) else if "%1"=="test" (
    if "%2"=="unit" (
        echo Running unit tests...
        set PYTHONPATH=src
        python -m pytest tests/unit/ -v %3 %4 %5
    ) else if "%2"=="integration" (
        echo Running integration tests...
        set PYTHONPATH=src
        python -m pytest tests/integration/ -v %3 %4 %5
    ) else (
        echo Running all tests...
        set PYTHONPATH=src
        python -m pytest tests/ -v %2 %3 %4
    )
) else if "%1"=="help" (
    goto :show_help
) else (
    echo Error: Unknown command '%1'
    goto :show_help
)

exit /b %errorlevel%
