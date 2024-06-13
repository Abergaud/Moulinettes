import numpy as np
import argparse
import csv

def read_csv(file_path):
    """
    Read data from a CSV file.

    Parameters:
        file_path (str): Path to the CSV file.

    Returns:
        numpy.ndarray: 1D array representing the data.
    """
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        data = np.array([float(row[0]) for row in reader])

    return data

def adjust_offset(data, mesh):
    """
    Adjusts the offset of the data to best fit the mesh.

    Parameters:
        data (numpy.ndarray): 1D array representing the temperature data.
        mesh (numpy.ndarray): 1D array representing the mesh.

    Returns:
        numpy.ndarray: Adjusted temperature data with the best-fit offset.
    """
    # Calculate the mean of the data and mesh
    data_mean = np.mean(data)
    mesh_mean = np.mean(mesh)

    # Calculate the offset
    offset = mesh_mean - data_mean

    # Adjust the data by adding the offset
    adjusted_data = data + offset

    return adjusted_data

def main():
    parser = argparse.ArgumentParser(description='Adjust the offset of data to best fit specified meshes.')
    parser.add_argument('--data-files', nargs='+', type=str, help='CSV files containing temperature data sets')
    parser.add_argument('--mesh-files', nargs='+', type=str, help='CSV files containing meshes corresponding to the data sets')
    args = parser.parse_args()

    data_sets = [read_csv(file) for file in args.data_files]
    meshes = [read_csv(file) for file in args.mesh_files]

    # Adjust offset for each data set
    adjusted_data_sets = [adjust_offset(data, mesh) for data, mesh in zip(data_sets, meshes)]

    # Print adjusted data sets (optional)
    for i, adjusted_data in enumerate(adjusted_data_sets):
        print(f"Adjusted Data Set {i+1}: {adjusted_data}")

if __name__ == "__main__":
    main()
