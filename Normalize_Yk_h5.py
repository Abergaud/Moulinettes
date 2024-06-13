# In the case an init file containing only one cell (4 nodes) doesn't have the sum of Yk = 0
# This code corrects it by normalizing the Yk by the total sum


import h5py
import numpy as np


#data = h5py.File('filename')
data = h5py.File('init_cell_3D_modified_energy_rho.h5')

dict_YK = {}
# sum_Yk = np.array([0,0,0,0]) # For length = 4 
sum_Yk = np.array([0,0,0,0,0,0,0,0]) # For length = 8 
for species in data['RhoSpecies']:
	dict_YK[species] = data['RhoSpecies'][species][...]/data['GaseousPhase']['rho'][...] # [...] implies using np.arrays
	sum_Yk = sum_Yk + data['RhoSpecies'][species][...]/data['GaseousPhase']['rho'][...]

for species in dict_YK:
	dict_YK[species] = dict_YK[species]/sum_Yk
	del data['RhoSpecies'][species]
	data['RhoSpecies'].create_dataset(species,data=dict_YK[species]*data['GaseousPhase']['rho'][...])
 
