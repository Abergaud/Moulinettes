#!/bin/bash

# Specify the path to your Python program (it can also be other than a python program)
python_program="/scratch/cfd/bergaud/moulinettes/readbin_file2csv.py"

# Loop through each file in the folder
for file in *; do
    # Check if the file is a regular file (not a directory)
    if [ -f "$file" ]; then
        readbin "$file" > "$file.txt"
        # Call your Python program with the file as an argument
        python "$python_program" "$file.txt"
        rm $file
    fi
done