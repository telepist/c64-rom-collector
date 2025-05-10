#!/bin/bash

# C64 ROM Collection Manager
# A shell script to easily run different management functions

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
    echo "  verify     - Verify the collection for completeness and consistency"
    echo "  count      - Run the check_counts.py script for additional verification"
    echo "  compare    - Run the compare_counts.py script to compare collections"
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
        python -m src.cli import
        ;;
    generate)
        echo "Generating merge script..."
        python -m src.cli generate
        ;;
    merge)
        echo "Running merge script to create target collection..."
        python -m src.cli merge
        ;;
    run)
        echo "Running complete workflow: import, generate, and merge..."
        echo "Step 1/3: Importing games from source collections..."
        python -m src.cli import
        echo "Step 2/3: Generating merge script..."
        python -m src.cli generate
        echo "Step 3/3: Running merge script to create target collection..."
        python -m src.cli merge
        echo "Complete workflow finished successfully!"
        ;;
    verify)
        echo "Verifying collection for completeness..."
        python -m c64collector.cli verify
        ;;
    count)
        echo "Running count check..."
        python -m c64collector.cli count
        ;;
    compare)
        echo "Running collection comparison..."
        python -m c64collector.cli compare
        ;;
    version)
        echo "Showing version information..."
        python -m c64collector.cli version
        ;;
    test)
        echo "Running unit tests..."
        if [ -n "$2" ]; then
            python -m c64collector.cli test --module "$2"
        else
            python -m c64collector.cli test
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
