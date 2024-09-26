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

def get_valid_int(prompt, min_val=None, max_val=None):
    while True:
        try:
            value = int(input(prompt).strip())
            if (min_val is not None and value < min_val) or (max_val is not None and value > max_val):
                print(f"Please enter a value between {min_val} and {max_val}.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter an integer.")

def get_valid_float(prompt, min_val=None, max_val=None):
    while True:
        try:
            value = float(input(prompt).strip())
            if (min_val is not None and value < min_val) or (max_val is not None and value > max_val):
                print(f"Please enter a value between {min_val} and {max_val}.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter a floating-point number.")

def get_valid_list_of_ints(prompt, delimiter=','):
    while True:
        try:
            values = input(prompt).strip().split(delimiter)
            return [int(value.strip()) for value in values]
        except ValueError:
            print(f"Invalid input. Please enter a list of integers separated by '{delimiter}'.")

def get_yes_no(prompt):
    while True:
        response = input(prompt).strip().lower()
        if response in ['yes', 'no']:
            return response
        print("Invalid input. Please enter 'yes' or 'no'.")

def load_csv(filename, x_idx, y_indices, labels):
    data = dd.read_csv(filename,assume_missing=True,dtype='float64')
    data = data.compute()

    if not labels:
        labels = []
        for i in range(len(y_indices)):
            label = input(f"Enter label for Y data {i+1} in {filename}: ").strip()
            labels.append(label if label else f"Y data {i+1} in {filename}")

    x_data = data.iloc[:, x_idx-1].values
    y_data = [data.iloc[:, idx-1].values for idx in y_indices]

    sorted_indices = np.argsort(x_data)
    x_data_sorted = x_data[sorted_indices]
    y_data_sorted = [y[sorted_indices] for y in y_data]

    return x_data_sorted, y_data_sorted, x_data, y_data, labels

def calculate_gradient(x_data, y_data):
    gradient = np.gradient(y_data, x_data)
    return gradient

def find_offset_by_gradient(x_data1, y_data1, x_data2, y_data2):
    gradient1 = calculate_gradient(x_data1, y_data1)
    gradient2 = calculate_gradient(x_data2, y_data2)

    max_grad_index1 = np.argmax(np.abs(gradient1))
    max_grad_index2 = np.argmax(np.abs(gradient2))
    
    offset = x_data2[max_grad_index2] - x_data1[max_grad_index1]
    
    return offset

def plot_fields(x_data_list, y_data_list, filenames, initial_offset=None, xlabel=None, ylabel=None, title=None, labels_list=None, save_path=None):
    named_colors = mcolors.CSS4_COLORS
    colors = ['b', 'r', 'k', 'green']
    colors += list(named_colors.keys())
    linestyle = ['solid', 'dashed', '']

    for i, filename in enumerate(filenames):
        for j, y_data in enumerate(y_data_list[i]):
            x_data_shifted = x_data_list[i] + initial_offset if initial_offset is not None else x_data_list[i]

            if len(x_data_shifted) != len(y_data):
                raise ValueError(f"Dimension mismatch between x_data and y_data for {filename}, field {j+1}")

            label = labels_list[i][j] if labels_list and len(labels_list[i]) > j else f"Field {j+1} in {filename}"
            
            if i == 2 : 
                plt.plot(x_data_shifted, y_data, label=label, linestyle=linestyle[i], marker='o', color=colors[j])
            else :
                plt.plot(x_data_shifted, y_data, label=label, linestyle=linestyle[i], marker='', color=colors[j])

    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.title(title, fontsize=14)
    #plt.legend(fontsize=10)
    plt.grid(True)
    plt.tight_layout()

def load_config():
    config = {}
    if os.path.exists('config.json'):
        with open('config.json', 'r') as f:
            config = json.load(f)
    else:
        print("There isn't a config.json file in the current folder. Let's start the interactive mode.")
    return config

def main():
    config = load_config()

    if len(sys.argv) < 3:
        print("At least two CSV files are required.")
        print("Usage: python script.py <csv_file1> <csv_file2> [<csv_file3> ...]")
        return

    filenames = sys.argv[1:]

    x_data_list = []
    y_data_list = []
    x_data_original_list = []
    y_data_original_list = []
    labels_list = []

    for filename in filenames:
        if filename in config.get('files', {}):
            file_config = config['files'][filename]
            x_idx = file_config.get('x_idx', None)
            y_indices = file_config.get('y_indices', [])
            labels = file_config.get('labels', [])
        else:
            print(f"Loading headers for file: {filename}")
            temp_data = dd.read_csv(filename,assume_missing=True).head()
            print("Available headers:")
            for idx, header in enumerate(temp_data.columns):
                print(f"{idx + 1}. {header}")

            x_idx = get_valid_int(f"Enter the index of the header for X data in {filename}: ", min_val=1, max_val=len(temp_data.columns))
            y_indices = get_valid_list_of_ints(f"Enter the indices of the headers for Y data (comma-separated) in {filename}: ")
            labels = []

        x_data_sorted, y_data_sorted, x_data_original, y_data_original, labels = load_csv(filename, x_idx, y_indices, labels)
        x_data_list.append(x_data_sorted)
        y_data_list.append(y_data_sorted)
        x_data_original_list.append(x_data_original)
        y_data_original_list.append(y_data_original)
        labels_list.append(labels)

    initial_offset = config.get('initial_offset', None)

    xlabel = config.get('xlabel', '') if 'xlabel' in config else input("Enter X-axis label (or press Enter to use default): ").strip()
    ylabel = config.get('ylabel', '') if 'ylabel' in config else input("Enter Y-axis label (or press Enter to use default): ").strip()
    title = config.get('title', '') if 'title' in config else input("Enter plot title (or press Enter to use default): ").strip()

    save_path = config.get('save_path', '') if 'save_path' in config else input("Enter the path to save the plot with high resolution (or press Enter to skip): ").strip()

    figsize = tuple(config.get('figsize', [6, 4])) if 'figsize' in config else (6, 4)
    linestyle_1 = config.get('linestyle_1', '-') if 'linestyle_1' in config else '-'
    marker_1 = config.get('marker_1', '') if 'marker_1' in config else ''
    xlim_a = config.get('xlim_a', 0) if 'xlim_a' in config else 0
    xlim_b = config.get('xlim_b', 1) if 'xlim_b' in config else 3
    xlabel_default = config.get('xlabel_default') if 'xlabel_default' in config else 'X_coordinate'
    ylabel_default = config.get('ylabel_default') if 'ylabel_default' in config else 'Y_coordinate'
    title_default = config.get('title_default') if 'title_default' in config else ''

    plt.figure(figsize=figsize)
    plot_fields(x_data_list, y_data_list, filenames, initial_offset, xlabel, ylabel, title, labels_list, save_path)

    if save_path:
        plt.xlim(xlim_a, xlim_b)
        plt.savefig(save_path + ".pdf", dpi=300)
        print(f"Plot saved to {save_path}.pdf")

    while True:
        adjust_offset = get_yes_no("Do you want to adjust the offset? (yes/no): ")
        if adjust_offset == 'yes':
            new_offset = get_valid_float("Enter the new offset value: ")
            plt.figure(figsize=figsize)
            plot_fields(x_data_list, y_data_list, filenames, new_offset, xlabel, ylabel, title, labels_list, save_path)
            plt.show()
            if save_path:
                plt.xlim(xlim_a, xlim_b)
                plt.savefig(save_path + ".pdf", dpi=300)
                print(f"Plot saved to {save_path}.pdf")
        elif adjust_offset == 'no':
            break

    while True:
        adjust_xlim = get_yes_no("Do you want to adjust xlim_a and xlim_b? (yes/no): ")
        if adjust_xlim == 'yes':
            new_xlim_a = get_valid_float("Enter the new xlim_a value: ")
            new_xlim_b = get_valid_float("Enter the new xlim_b value: ")
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
