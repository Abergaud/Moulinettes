import h5py
import sys
import os
import numpy as np
import shutil
import csv

def read_h5_group(group, group_name="", data_dict=None):
    for name, item in group.items():
        if isinstance(item, h5py.Dataset):
            dataset_path = group_name + "/" + name
            try:
                data = item[:]
                if isinstance(data, np.ndarray):
                    data_dict[dataset_path] = data
                elif isinstance(data, h5py.Empty):
                    data_dict[dataset_path] = None
                else:
                    # Decode byte strings to regular strings
                    if isinstance(data, bytes):
                        data = data.decode("utf-8")
                    data_dict[dataset_path] = data
            except Exception as e:
                print("Error accessing dataset values:", str(e))
        elif isinstance(item, h5py.Group):
            read_h5_group(item, group_name + "/" + name, data_dict)
        else:
            print("Unknown object type:", type(item))

def read_h5_file(file_path, modify=False, store_csv=False, new_data_file=None, remove_group=None, add_group=None, add_data_file=None, selected_indices=None, selected_group=None):
    if not os.path.isfile(file_path):
        print("Error: File not found:", file_path)
        return
    
    data_dict = {}
    try:
        with h5py.File(file_path, 'r+') as file:  # Open file in read/write mode
            if remove_group:  # Check if remove option is specified
                if remove_group in file:
                    del file[remove_group]  # Remove the specified group
                    print(f"Group '{remove_group}' removed successfully from the HDF5 file.")
                else:
                    print(f"Error: Group '{remove_group}' not found in the HDF5 file.")
                return  # Exit after removing the group

            if add_group and add_data_file:
                if add_group in file:
                    print(f"Error: Group '{add_group}' already exists in the HDF5 file.")
                    return
                with open(add_data_file, 'r') as csvfile:
                    csv_reader = csv.reader(csvfile)
                    data = np.array([row for row in csv_reader], dtype=np.float64)  # Specify data type as np.float64
                    data_flat = data.flatten()  # Flatten the data array
                    file.create_dataset(add_group, data=data_flat)
                    print(f"Group '{add_group}' added successfully to the HDF5 file.")
                return


            read_h5_group(file, data_dict=data_dict)
    except Exception as e:
        print("An error occurred:", str(e))
        return

    if selected_group:
        if selected_group not in data_dict:
            print(f"Error: Group '{selected_group}' not found in the HDF5 file.")
            return
        selected_headers = [selected_group]
    else:
        headers = list(data_dict.keys())
        print("Available groups:")
        for i, header in enumerate(headers):
            print(f"{i + 1}. {header}")

        if selected_indices:
            selected_headers = [headers[i - 1] for i in selected_indices]
        else:
            selected_indices = input("Enter the indices of the groups you want to modify (separated by commas): ")
            selected_indices = [int(index.strip()) for index in selected_indices.split(",")]
            selected_headers = [headers[i - 1] for i in selected_indices]

    for selected_header in selected_headers:
        selected_data = data_dict[selected_header]
        print(f"Data for {selected_header}:")
        print(f"Number of elements: {len(selected_data)}")
        print(selected_data)

        if store_csv:
            filename = f"{selected_header.replace('/', '_')}.csv"
            csv_filename = file_path.split("/")[-1][:-3] + filename
            selected_data_list = [[elem] if not isinstance(elem, (list, tuple)) else elem for elem in selected_data]  # Convert NumPy array to list of lists or a single-element list
            with open(csv_filename, 'w', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                #csv_writer.writerow([selected_header]) # Commented so to avoid the writing of the header
                csv_writer.writerows(selected_data_list)

            print(f"Data for {selected_header} stored in {csv_filename}")

    if modify:
        if new_data_file is None:
            print("Error: No new data file provided after activating modification option.")
            sys.exit(1)
        if not os.path.isfile(new_data_file):
            print("Error: New data file not found.")
            return
        try:
            with open(new_data_file, 'r') as csvfile:
                csv_reader = csv.reader(csvfile)
                new_data = np.array([row for row in csv_reader], dtype='S')  # Convert data to string dtype
                new_data = new_data.squeeze()  # Remove singleton dimensions

                # Create a copy of the original file
                original_filename, original_file_extension = os.path.splitext(file_path)
                new_file_path = original_filename + "_modified" + original_file_extension
                shutil.copyfile(file_path, new_file_path)

                # Open the copied file for modification
                with h5py.File(new_file_path, 'a') as modified_file:
                    try:
                        dataset = modified_file[selected_header]
                        if 'chunks' not in dataset.attrs:
                            # If dataset is not chunked, create a new chunked dataset
                            del modified_file[selected_header]
                            modified_file.create_dataset(selected_header, data=new_data.astype(selected_data.dtype), chunks=True, maxshape=(None,))
                        else:
                            # If dataset is chunked, resize it to match the new data dimensions
                            if dataset.shape != new_data.shape:
                                dataset.resize(new_data.shape)
                        dataset[:] = new_data.astype(selected_data.dtype)  # Replace dataset with new data
                        print(f"Dataset modified successfully in: {new_file_path}.")
                    except Exception as e:
                        print("An error occurred while modifying the dataset:", str(e))
        except Exception as e:
            print("An error occurred while reading the new data file:", str(e))


def print_help():
    print("""
    NAME
        h5RSMDA - A utility for reading, modifying, and storing data in HDF5 files

    SYNOPSIS
        h5RSMDA [OPTIONS] <file_path>

    DESCRIPTION
        h5RSMDA is a Python script that provides functionalities for interacting with HDF5 files. 
        It allows users to read, modify, and store data stored in HDF5 format. The script provides 
        various options to perform these operations, including modifying existing datasets, storing 
        datasets as CSV files, removing groups, and adding new groups with data from CSV files.

    OPTIONS
        --modif, -m
            Activate modification mode. This allows the user to modify an existing dataset within 
            the HDF5 file.

        --store, -s
            Activate storing mode. This allows the user to store a dataset as a CSV file.

        --remove <data_file_path>, -r <group_name>
            Remove the specified group from the HDF5 file.

        --add <group_name> <data_file_path>, -a <group_name> <data_file_path>
            Add a new group to the HDF5 file. The group name and the path to the CSV file containing 
            the data for the group must be provided.

        --indices <index1,index2,...>, -i <index1,index2,...>
            Specify the indices of the headers to display, store, or modify.

        --group <group_name>, -g <group_name>
            Specify the name of the group to modify.

        --csv <file_path>, -c <file_path>
            Specify the path to the CSV file containing the new data for modification.

        <file_path>
            The path to the HDF5 file to be processed.

    EXAMPLES
        To display available headers in an HDF5 file:
            h5RSMDA data.h5

        To modify a dataset in an HDF5 file:
            h5RSMDA data.h5 --modif --indices 1,2,3 --csv new_data.csv

        To store a dataset as a CSV file:
            h5RSMDA data.h5 --store
        
        To specify indices of headers to display, store, or modify:
            h5RSMDA data.h5 --store --indices 1,3,5

        To specify the group to modify:
            h5RSMDA data.h5 --modif --group group_name 

        To remove a group from an HDF5 file:
            h5RSMDA data.h5 --remove group_name 

        To add a new group to an HDF5 file:
            h5RSMDA data.h5 --add new_group_name data.csv 
    """)
    sys.exit(0)

if __name__ == "__main__":
    
    print("""
                     _     _____ _____   _____ __  __ _____          
                    | |   | ____|  __ \ / ____|  \/  |  __ \   /\    
                    | |__ | |__ | |__) | (___ | \  / | |  | | /  \   
                    | '_ \|___ \|  _  / \___ \| |\/| | |  | |/ /\ \  
                    | | | |___) | | \ \ ____) | |  | | |__| / ____ \ 
                    |_| |_|____/|_|  \_\_____/|_|  |_|_____/_/    \_\                               
 """)                                                 

    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help']:
        print_help()

    file_path = sys.argv[1]
    modify = False
    store_csv = False
    new_data_file = None
    remove_group = None
    add_group = None
    add_data_file = None
    selected_indices = None
    selected_group = None

    # Parse command-line arguments
    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--modif" or arg == "-m":
            modify = True
        elif arg == "--store" or arg == "-s":
            store_csv = True
        elif arg == "--remove" or arg == "-r":
            remove_group = sys.argv[i + 1]
            i += 1
        elif arg == "--add" or arg == "-a":
            add_group = sys.argv[i + 1]
            add_data_file = sys.argv[i + 2]
            i += 2
        elif arg == "--indices" or arg == "-i":
            selected_indices = [int(index.strip()) for index in sys.argv[i + 1].split(",")]
            i += 1
        elif arg == "--group" or arg == "-g":
            selected_group = sys.argv[i + 1]
            i += 1
        elif arg == "--csv" or arg == "-c":
            new_data_file = sys.argv[i + 1]
            i += 1
        else:
            new_data_file = arg
        i += 1

    # Call read_h5_file with parsed arguments
    read_h5_file(file_path, modify, store_csv, new_data_file, remove_group, add_group, add_data_file, selected_indices, selected_group)
