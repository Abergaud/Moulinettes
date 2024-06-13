# EASYPLOT
# Python tool to plot data easily using a csv file containg the x data and others csv files (at least one) for y data
# /!\ Csv files must have only one column and it is required not to have a header in the file
# 
#---------------------------------------------------------------------#
# Example of usage :                                                  #
# python EASYPLOT.py <csv_file1> <csv_file2> <csv_file3> ...          #
#                      (x-data)   (y-data1)   (y-data2)  ...          #
#---------------------------------------------------------------------#

import sys
import csv
import matplotlib.pyplot as plt

plt.style.use("/scratch/cfd/bergaud/CTPP/MPLSTYLE/cerfacs.mplstyle")

#---------------------------------------------------------------------#
#                      PARAMETERS TO CHANGE                           #
#---------------------------------------------------------------------#
xlabel = "Nombre_itérations"                                        
#ylabel = "Pression_[Pa]"
#ylabel = "Température_[K]"
# ylabel = "RhoSpecies"
ylabel = "Rho_[kg-m3]"
title = ""
name_fig = f"{xlabel}_vs_{ylabel}"
#---------------------------------------------------------------------#

def read_csv(filename):
    """
    Read data from a CSV file and return as a list.
    """
    data = []
    with open(filename, 'r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            data.append(row[0])
    return data

def plot_data(x_data, y_data_list, label="", xlabel='X', ylabel='Y', title='', name_fig='1'):
    """
    Plot the data using Matplotlib.
    """
    plt.plot(x_data, y_data_list, label=label)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.grid(True)

def main():
    # Check if correct number of arguments are provided
    if len(sys.argv) < 3:
        print("Usage: python script.py <x_csv_file> <y_csv_file1> [<y_csv_file2> ...]")
        sys.exit(1)

    # Get filenames from command line arguments
    x_filename = sys.argv[1]
    y_filenames = sys.argv[2:]

    # Read x data from CSV file
    x_data = read_csv(x_filename)

    # Read y data from CSV files
    y_data_dict = {}
    for y_filename in y_filenames:
        y_data = read_csv(y_filename)
        y_values = [float(y) for y in y_data]
        y_data_dict[y_filename] = y_values

    # Plot the data
    for filename in y_data_dict:
        plot_data(x_data, y_data_dict[filename], label=filename[:-4], xlabel= xlabel, ylabel= ylabel)
        
    plt.savefig(f"Figure_{name_fig}")

if __name__ == "__main__":
    main()
