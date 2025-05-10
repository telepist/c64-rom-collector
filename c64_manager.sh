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
    echo "  generate   - Generate the merge script for creating the best collection"
    echo "  merge      - Run the merge script to copy best versions to target directory"
    echo "  verify     - Verify the collection for completeness and consistency"
    echo "  count      - Run the check_counts.py script for additional verification"
    echo "  compare    - Run the compare_counts.py script to compare collections"
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
        python scripts/import_games.py
        ;;
    generate)
        echo "Generating merge script..."
        python scripts/generate_merge_script.py
        ;;
    merge)
        echo "Running merge script to create target collection..."
        ./merge_collection.sh
        ;;
    verify)
        echo "Verifying collection for completeness..."
        python scripts/check_missing.py
        ;;
    count)
        echo "Running count check..."
        python scripts/check_counts.py
        ;;
    compare)
        echo "Running collection comparison..."
        python scripts/compare_counts.py
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
