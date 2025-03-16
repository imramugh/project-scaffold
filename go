#!/bin/bash

# This is a wrapper script for scaffold.py that handles navigation and 
# virtual environment activation while keeping the .zshrc file simple

# Check if we're being sourced (as required for directory changes)
([[ -n $ZSH_EVAL_CONTEXT && $ZSH_EVAL_CONTEXT =~ :file$ ]] || 
 [[ -n $BASH_VERSION ]] && (return 0 2>/dev/null)) && SOURCED=1 || SOURCED=0

if [[ $SOURCED -eq 0 ]]; then
    echo "Error: This script must be sourced, not executed."
    echo "Please add this to your .zshrc or .bashrc:"
    echo "  alias go='source $HOME/Documents/Projects/scaffold/go'"
    exit 1
fi

# Handle debug mode and reorganize arguments
DEBUG=0
ARGS=()
HAS_COMMAND=false
COMMAND=""

# Check for verbose flag in any position
for arg in "$@"; do
    if [[ "$arg" == "--verbose" ]] || [[ "$arg" == "-v" ]]; then
        DEBUG=1
        break
    fi
done

# Special case for "go home" command (with or without verbose flag)
if [[ "$1" == "home" ]] || [[ "$2" == "home" && ("$1" == "-v" || "$1" == "--verbose") ]]; then
    if [[ $DEBUG -eq 1 ]]; then
        echo "Special case: 'go home' command detected with verbose flag"
        ARGS=("-v" "navigate" "home")
    else
        if [[ $DEBUG -eq 1 ]]; then
            echo "Special case: 'go home' command detected"
        fi
        ARGS=("navigate" "home")
    fi
    HAS_COMMAND=true
else
    # Build arguments array with verbose flag first if present
    if [[ $DEBUG -eq 1 ]]; then
        echo "Debug mode enabled"
        ARGS+=("-v")
    fi

    # Process arguments properly
    for arg in "$@"; do
        if [[ "$arg" == "--verbose" ]] || [[ "$arg" == "-v" ]]; then
            # Skip adding verbose flag again since we already added it
            continue
        elif [[ "$arg" == "create" ]] || [[ "$arg" == "delete" ]] || [[ "$arg" == "list" ]] || [[ "$arg" == "navigate" ]]; then
            COMMAND="$arg"
            ARGS+=("$arg")
            HAS_COMMAND=true
        else
            ARGS+=("$arg")
        fi
    done
    
    # If no command is specified but an argument is provided, treat it as a navigation
    if [[ $HAS_COMMAND == false && $# -ge 1 ]]; then
        COMMAND="navigate"
        
        # If we've already processed arguments but need to add the navigate command
        NEW_ARGS=()
        
        # Add verbose flag if present
        if [[ $DEBUG -eq 1 ]]; then
            NEW_ARGS+=("-v")
        fi
        
        # Add navigate command
        NEW_ARGS+=("navigate")
        
        # Add remaining args except verbose flag
        for arg in "$@"; do
            if [[ "$arg" != "--verbose" && "$arg" != "-v" ]]; then
                NEW_ARGS+=("$arg")
            fi
        done
        
        ARGS=("${NEW_ARGS[@]}")
    fi
fi

if [[ $DEBUG -eq 1 ]]; then
    echo "Command detected: $COMMAND"
    echo "Arguments array: ${ARGS[@]}"
fi

# Execute the scaffold.py script and capture its output
# Add 2>&1 to capture both stdout and stderr
OUTPUT=$(python3 $HOME/Documents/Projects/scaffold/scaffold.py "${ARGS[@]}" 2>&1)
EXIT_CODE=$?

if [[ $DEBUG -eq 1 ]]; then
    echo "Exit code: $EXIT_CODE"
    echo "Raw output from scaffold.py:"
    echo "$OUTPUT"
fi

# Check if we should handle special navigation instructions
echo "$OUTPUT" | while IFS= read -r line; do
    if [[ $line == NAVIGATE_TO:* ]]; then
        target_dir="${line#NAVIGATE_TO:}"
        if [[ $DEBUG -eq 1 ]]; then
            echo "Navigating to: $target_dir"
        fi
        cd "$target_dir" || return 1
    elif [[ $line == ACTIVATE_VENV:* ]]; then
        venv_path="${line#ACTIVATE_VENV:}"
        if [[ $DEBUG -eq 1 ]]; then
            echo "Activating virtual environment: $venv_path"
        fi
        source "$venv_path" || return 1
    else
        # Print regular output
        echo "$line"
    fi
done

# Return the exit code from the script
return $EXIT_CODE
