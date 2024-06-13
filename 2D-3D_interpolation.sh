#!/bin/bash
# Bash script used to put 2d data in 3d keeping only the first row of each group in a h5 file
# IMPORTANT : Make a empty folder and launch the code inside
# ( Necessary because some files will be created and then destroyed )

file_name=/scratch/cfd/bergaud/Virtual-chemistry/AVBP_DEV/0D_NO_BOUND_3D_CELL/INIT/init_tr.sol.h5

i=1

# If some items are no wanted write "useless" in the following parameters to bypass them (the order of the item is important)
for item in /FictiveSpecies/CO /FictiveSpecies/V1 /FictiveSpecies/V2 /GaseousPhase/rho /GaseousPhase/rhoE /GaseousPhase/rhou /GaseousPhase/rhov /RhoSpecies/CH4 useless useless useless useless /RhoSpecies/I /RhoSpecies/N2 /RhoSpecies/O2 /RhoSpecies/P1 /RhoSpecies/P2 /RhoSpecies/P3 /RhoSpecies/P4

do
    python /scratch/cfd/bergaud/moulinettes/h5RSMDA.py $file_name --store --indices $i > /dev/null

    echo "file created" 
    ls > ../temp_created_file
    created_file=$(head -n 1 ../temp_created_file)
    first_line=$(head -n 1 $created_file)

    # At this step the group data has been store

    cat $created_file

    # Delete all existing lines and write the duplicated line 8 times
    printf "%s\n" "$first_line" > "$created_file"  # Write the first line
    
    for ((j=1; j<=5; j++))  # Loop 7 times to append the duplicated line
    do
        printf "%s\n" "$first_line" >> "$created_file"
    done

    echo After modification
    cat $created_file

    if [ "$item" != "useless" ]; then
    # This contition allows to bypass the item that are not wanted to be modified

    # Impossible to modify an array with a new one that has another dimension
    # New strategy : remove the chosen array, change it and then add it again into the h5 file 
    python /scratch/cfd/bergaud/moulinettes/h5RSMDA.py $file_name --remove $item
    echo Item removed

    python /scratch/cfd/bergaud/moulinettes/h5RSMDA.py $file_name --add $item $created_file #> /dev/null
    echo "item added to file"
    fi

    rm ../temp_created_file
    rm $created_file
    echo "files deleted"

    #Increment 1 to i
    ((i=i+1))
done


