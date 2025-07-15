#!/bin/bash

# C64 ROM Collection Manager
# A shell script to easily run different management functions

# Find the appropriate Python command
get_python_cmd() {
    # Check for py launcher (Windows) first
    if command -v py &> /dev/null; then
        if py --version 2>&1 | grep -q "Python 3"; then
            echo "py"
            return
        fi
    fi
    # Check for python if it's available and is Python 3
    if command -v python &> /dev/null; then
        if python --version 2>&1 | grep -q "Python 3"; then
            echo "python"
            return
        fi
    fi
    # Check for python3 (common on Unix systems)
    if command -v python3 &> /dev/null; then
        echo "python3"
        return
    fi
    echo "Error: Python 3 not found" >&2
    exit 1
}

# Get Python command
PYTHON_CMD=$(get_python_cmd)

# Display help message
show_help() {
    echo "C64 ROM Collection Manager"
    echo "=========================="
    echo ""
    echo "Usage: ./c64_manager.sh [command]"
    echo ""
    echo "Available Commands:"
    echo "  import     - Import and normalize game information from source collections"
    echo "  generate   - Generate the merge script for creating the target collection"
    echo "  merge      - Run the merge script to copy best versions to target directory"
    echo "  run        - Execute import, generate, and merge commands in sequence"
    echo "  count      - Run the check_counts.py script for additional verification"
    echo "  version    - Show version information"
    echo "  test       - Run unit tests"
    echo "  help       - Display this help message"
    echo ""
    echo "Note: Multi-part games are automatically organized into subdirectories."
    echo ""
}

# Check if a command was provided
if [ $# -eq 0 ]; then
    show_help
    exit 1
fi

# Process commands
case "$1" in
    import)
        echo "Importing games from source collections (will clear existing database)..."
        BASEDIR="$(pwd)"
        cd src && $PYTHON_CMD cli.py import --src "$BASEDIR/roms"
        ;;
    generate)
        echo "Generating merge script..."
        BASEDIR="$(pwd)"
        cd src && $PYTHON_CMD cli.py generate --target "$BASEDIR/target"
        ;;
    merge)
        echo "Running merge script to create target collection..."
        BASEDIR="$(pwd)"
        cd src && $PYTHON_CMD cli.py merge --target "$BASEDIR/target"
        ;;
    run)
        echo "Running complete workflow: import, generate, and merge..."
        echo "Step 1/3: Importing games from source collections..."
        BASEDIR="$(pwd)"
        cd src && $PYTHON_CMD cli.py import --src "$BASEDIR/roms" || exit 1
        echo "Step 2/3: Generating merge script..."
        $PYTHON_CMD cli.py generate --target "$BASEDIR/target" || exit 1
        echo "Step 3/3: Running merge script to create target collection..."
        $PYTHON_CMD cli.py merge --target "$BASEDIR/target" || exit 1
        echo "Complete workflow finished successfully!"
        ;;
    count)
        echo "Running count check..."
        cd src && $PYTHON_CMD cli.py count
        ;;
    version)
        echo "Showing version information..."
        cd src && $PYTHON_CMD cli.py version
        ;;
    test)
        # Handle test type and optional arguments
        if [ "$2" = "unit" ] || [ "$2" = "integration" ]; then
            echo "Running $2 tests..."
            cd src && $PYTHON_CMD cli.py test "$2" "${@:3}"
        else
            echo "Running all tests..."
            cd src && $PYTHON_CMD cli.py test "${@:2}"
        fi
        ;;
    help)
        show_help
        ;;
    *)
        echo "Error: Unknown command '$1'"
        show_help
        exit 1
        ;;
esac

exit 0
