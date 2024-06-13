import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pandas as pd
import dask.dataframe as dd
import time
import json
import os

plt.style.use("/scratch/cfd/bergaud/CTPP/MPLSTYLE/cerfacs.mplstyle")

def load_csv(filename, x_idx, y_indices, labels):
    """
    Load CSV file using dask dataframe and provided headers for x and y data.
    """
    start_time = time.time()
    data = dd.read_csv(filename)

    end_time = time.time()
    loading_time = end_time - start_time
    print(f"Loading time = {loading_time:.2f} seconds")

    # Convert to pandas dataframe for further processing
    data = data.compute()

    # Prompt the user for labels for each set of data
    if not labels:
        print("Available headers:")
        for idx, header in enumerate(data.columns):
            print(f"{idx + 1}. {header}")
        labels = []
        for i in range(len(y_indices)):
            label = input(f"Enter label for Y data {i+1} in {filename}: ").strip()
            labels.append(label if label else f"Y data {i+1} in {filename}")

    x_data = data.iloc[:, x_idx-1].values
    y_data = [data.iloc[:, idx-1].values for idx in y_indices]

    # Optionally sort data based on x_data if needed for gradient calculation or plotting
    sorted_indices = np.argsort(x_data)
    x_data_sorted = x_data[sorted_indices]
    y_data_sorted = [y[sorted_indices] for y in y_data]

    return x_data_sorted, y_data_sorted, x_data, y_data, labels

def calculate_gradient(x_data, y_data):
    """
    Calculate the gradient of the y_data with respect to x_data.
    """
    gradient = np.gradient(y_data, x_data)  
    return gradient

def find_offset_by_gradient(x_data1, y_data1, x_data2, y_data2):
    """
    Find the optimal offset between two fields using the highest gradient.
    """
    gradient1 = calculate_gradient(x_data1, y_data1)
    gradient2 = calculate_gradient(x_data2, y_data2)

    max_grad_index1 = np.argmax(np.abs(gradient1))
    max_grad_index2 = np.argmax(np.abs(gradient2))
    
    offset = x_data2[max_grad_index2] - x_data1[max_grad_index1]
    
    return offset

def plot_fields(x_data_list, y_data_list, filenames, initial_offset=None, xlabel=None, ylabel=None, title=None, labels_list=None, save_path=None):
    """
    Plot multiple fields of data on the same figure.
    """
    named_colors = mcolors.CSS4_COLORS
    colors = ['b', 'r', 'k', 'grey']
    colors += list(named_colors.keys())

    for i, filename in enumerate(filenames):
        for j, y_data in enumerate(y_data_list[i]):
            # Apply initial_offset correctly
            x_data_shifted = x_data_list[i] + initial_offset if initial_offset is not None else x_data_list[i]
            
            # Check dimensions
            if len(x_data_shifted) != len(y_data):
                raise ValueError(f"Dimension mismatch between x_data and y_data for {filename}, field {j+1}")

            label = labels_list[i][j] if labels_list and len(labels_list[i]) > j else f"Field {j+1} in {filename}"
            plt.plot(x_data_shifted, y_data, label=label, linestyle='-', marker='', color=colors[i])

    plt.xlabel(xlabel if xlabel else 'Distance (m)', fontsize=12)  
    plt.ylabel(ylabel if ylabel else 'T (K)', fontsize=12)  
    plt.title(title if title else '', fontsize=14)  
    plt.legend(fontsize=10)  
    plt.grid(True)  
    plt.tight_layout()  

def load_config():
    """
    Load configuration from config.json if it exists.
    """
    config = {}
    if os.path.exists('config.json'):
        with open('config.json', 'r') as f:
            config = json.load(f)
    else:
        print("There isn't a config.json file in the current folder. Let's start the interactive mode.")
    return config

def main():
    # Load configuration from config.json or initialize empty dictionary
    config = load_config()

    # Check if at least two arguments are provided (assuming first argument is the script name)
    if len(sys.argv) < 3:
        print("At least two CSV files are required.")
        print("Usage: python script.py <csv_file1> <csv_file2> [<csv_file3> ...]")
        return

    # Extract filenames from command line arguments
    filenames = sys.argv[1:]

    # Initialize lists to store data for each file
    x_data_list = []
    y_data_list = []
    x_data_original_list = []
    y_data_original_list = []
    labels_list = []

    # Check if x_idx, y_indices, and labels are present in config or ask interactively for each file
    for filename in filenames:
        if filename in config.get('files', {}):
            file_config = config['files'][filename]
            x_idx = file_config.get('x_idx', None)
            y_indices = file_config.get('y_indices', [])
            labels = file_config.get('labels', [])
        else:
            x_idx = int(input(f"Enter the index of the header for X data in {filename}: ")) - 1
            y_indices = input(f"Enter the indices of the headers for Y data (comma-separated) in {filename}: ").split(',')
            y_indices = [int(idx.strip()) - 1 for idx in y_indices]
            labels = []

        print(f"Processing file: {filename}")
        x_data_sorted, y_data_sorted, x_data_original, y_data_original, labels = load_csv(filename, x_idx, y_indices, labels)
        x_data_list.append(x_data_sorted)
        y_data_list.append(y_data_sorted)
        x_data_original_list.append(x_data_original)
        y_data_original_list.append(y_data_original)
        labels_list.append(labels)

    # Find the initial offset using the highest gradient of the first file
    initial_offset = config.get('initial_offset', None)  # Get initial_offset from config

    # Get user input for axis labels and title if not in config
    xlabel = config.get('xlabel', '') if 'xlabel' in config else input("Enter X-axis label (or press Enter to use default): ").strip()
    ylabel = config.get('ylabel', '') if 'ylabel' in config else input("Enter Y-axis label (or press Enter to use default): ").strip()
    title = config.get('title', '') if 'title' in config else input("Enter plot title (or press Enter to use default): ").strip()

    # Save path with high resolution
    save_path = config.get('save_path', '') if 'save_path' in config else input("Enter the path to save the plot with high resolution (or press Enter to skip): ").strip()

    # Plotting parameters from config or defaults
    figsize = tuple(config.get('figsize', [6, 4])) if 'figsize' in config else (6, 4)
    linestyle_1 = config.get('linestyle_1', '-') if 'linestyle_1' in config else '-'
    marker_1 = config.get('marker_1', '') if 'marker_1' in config else ''
    xlim_a = config.get('xlim_a', -0.0035) if 'xlim_a' in config else 0.0035
    xlim_b = config.get('xlim_b', 0.0035) if 'xlim_b' in config else 0.0035
    xlabel_default = config.get('xlabel_default', 'Distance (m)') if 'xlabel_default' in config else 'Distance (m)'
    ylabel_default = config.get('ylabel_default', 'T (K)') if 'ylabel_default' in config else 'T (K)'
    title_default = config.get('title_default', '') if 'title_default' in config else ''
            # title_default in config else ''

    # Plot all the fields with the initial offset
    plt.figure(figsize=figsize)
    plot_fields(x_data_list, y_data_list, filenames, initial_offset, xlabel, ylabel, title, labels_list, save_path)

    # Save the plot if save_path is provided
    if save_path:
        plt.xlim(xlim_a, xlim_b)
        plt.savefig(save_path + ".pdf", dpi=300)
        print(f"Plot saved to {save_path}.pdf")

    # Interactive mode for adjusting offset and xlim
    while True:
        adjust_offset = input("Do you want to adjust the offset? (yes/no): ").strip().lower()
        if adjust_offset == 'yes':
            new_offset = float(input("Enter the new offset value: ").strip())
            plt.figure(figsize=figsize)
            plot_fields(x_data_list, y_data_list, filenames, new_offset,
                        xlabel, ylabel, title, labels_list, save_path)
            plt.show()
            if save_path:
                plt.xlim(xlim_a, xlim_b)
                plt.savefig(save_path + ".pdf", dpi=300)
                print(f"Plot saved to {save_path}.pdf")
        elif adjust_offset == 'no':
            break

    while True:
        adjust_xlim = input("Do you want to adjust xlim_a and xlim_b? (yes/no): ").strip().lower()
        if adjust_xlim == 'yes':
            new_xlim_a = float(input("Enter the new xlim_a value: ").strip())
            new_xlim_b = float(input("Enter the new xlim_b value: ").strip())
            plt.figure(figsize=figsize)
            plot_fields(x_data_list, y_data_list, filenames, initial_offset, xlabel, ylabel, title, labels_list, save_path)
            plt.xlim(new_xlim_a, new_xlim_b)
            plt.show()
            if save_path:
                plt.savefig(save_path + ".pdf", dpi=300)
                print(f"Plot saved to {save_path}.pdf")
        elif adjust_xlim == 'no':
            break

    print("End of the program")

if __name__ == "__main__":
    main()
