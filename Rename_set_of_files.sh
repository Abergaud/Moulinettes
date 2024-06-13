#!/bin/bash

# Help function
show_help() {
    echo "Usage: $(basename "$0") [old_prefix] [new_prefix]"
    echo "Rename files with the specified prefix."
    echo "Arguments:"
    echo "  old_prefix   The prefix to be replaced in the filenames."
    echo "  new_prefix   The new prefix to replace the old prefix."
    echo "Example:"
    echo "  $(basename "$0") name newname"
}

# Check if the number of arguments is correct
if [ "$#" -ne 2 ]; then
    show_help
    exit 1
fi

# Assign the arguments to variables
old_prefix="$1"
new_prefix="$2"

# Loop through files with the old prefix
for file in "${old_prefix}"*; do
    # Extract the number part of the filename
    number="${file#${old_prefix}}"
    # Rename the file with the new prefix
    mv "$file" "${new_prefix}${number}"
done

ls


