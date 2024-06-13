#!/bin/bash

# Files to be read
mkdir Folder_recap

#for file in solut_29155001.h5 solut_29155002.h5 solut_29155003.h5 solut_29155004.h5 solut_29155005.h5 solut_29155006.h5 solut_29155007.h5 solut_29155008.h5 solut_29155009.h5 solut_29155010.h5 
for i in $(seq 29155000 1 29156003)

do    
    #namefile="${file::-3}"
    namefile=solut_${i}.h5
    mkdir Folder_$namefile
    # SI NON REACTIF
    # python /scratch/cfd/bergaud/moulinettes/h5RSMDA.py $file --store --indices 6,9,26,35,36,37,38,39,40,41,42 # P, T, rho, CH4, I, N2, O2, P1, P2, P3, P4
    # SI REACTIF 
    #python /scratch/cfd/bergaud/moulinettes/h5RSMDA.py $file --store --indices 7,10,24,25,26,27,40,41,42,43,44,45,46,47 # P, T, CO, V1, V2, rho, CH4, I, N2, O2, P1, P2, P3, P4
    # CAS CELLULE 3D - A SUPPRIMER ENSUITE
    #python /scratch/cfd/bergaud/moulinettes/h5RSMDA.py $file --store --indices 3,4,7,8,9,10,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34
    mv ${namefile}_* Folder_$namefile

    cd Folder_$namefile
    for param in Additionals_pressure Additionals_temperature /FictiveSpecies/CO /FictiveSpecies/V1 /FictiveSpecies/V2 GaseousPhase_rho /Reactions/rrate_1 /Reactions/rrate_2 /Reactions/rrate_pollut11 /Reactions/rrate_pollut12 /Reactions/rrate_pollut13 /Reactions/rrate_pollut14 /Reactions/rrate_r_1 /Reactions/rrate_r_2 RhoSpecies_CH4 RhoSpecies_I RhoSpecies_N2 RhoSpecies_O2 RhoSpecies_P1 RhoSpecies_P2 RhoSpecies_P3 RhoSpecies_P4
    do
        head -n 1 ${namefile}_${param}.csv >> ../Recap_${param}.csv
    done
    cd ..
done

mv Recap_*.csv Folder_recap


