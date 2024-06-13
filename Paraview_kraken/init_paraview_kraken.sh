#!/bin/bash
# This bash file is used to launch local Paraview connected to Kraken 
# It avoids to use Nice Visu and allows also postprocessing parallelizing.


# Prompt the user with a question
echo "Have you allocated a node ? (y/n): "

# Read the user's response
read response

# Check the user's response
if [ "$response" == "y" ]; then
    echo "" # Empty line
    echo "Great! Proceeding with the code."
    echo "" # Empty line

    ssh -Y krakenv6
    ssh -L 11111:localhost:11111 krakenv6
    module load visu/paraview/5.10.1_ompi315_gcc83-mesa
    DISPLAY=:0 __GLX_VENDOR_LIBRARY_NAME=nvidia mpiexec -np 4 pvserver --mpi --force-offscreen-rendering

    echo "Now you can open Paraview"

elif [ "$response" == "n" ]; then
    echo "" # Empty line
    echo "Please allocate a node before lauching this code."
    echo "You can use the following command :"
    echo "" # Empty line
    echo "salloc -N 1 -n 4 --partition=batchvisu --time=01:00:00"
    echo "" # Empty line
    # Exit the script or add further instructions as needed
else
    echo "Invalid response. Please enter 'y' or 'n'."
    echo "Program exit ..."
fi



