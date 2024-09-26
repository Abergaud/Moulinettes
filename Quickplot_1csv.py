import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pandas as pd
import dask.dataframe as dd
import time

plt.style.use("/scratch/cfd/bergaud/CTPP/MPLSTYLE/cerfacs.mplstyle")

def get_yes_no(prompt):
    while True:
        response = input(prompt).strip().lower()
        if response in ['yes', 'no']:
            return response
        print("Invalid input. Please enter 'yes' or 'no'.")

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

def load_csv(filename):
    """
    Load CSV file and prompt user to select headers for x and y data.
    """
    # Load CSV file using dask dataframe
    start_time=time.time()
    data = dd.read_csv(filename,assume_missing=True,dtype='float64')
    end_time=time.time()
    
    loading_time = end_time - start_time
    
    print(f"Loading time : {loading_time:.2f}")
    
    # Convert to pandas dataframe for compatibility with current code
    data = data.compute()
    
    print("Available headers:")
    for idx, header in enumerate(data.columns):
        print(f"{idx + 1}. {header}")
    
    x_idx = int(input("Enter the index of the header for X data: ")) - 1
    y_indices = input("Enter the indices of the headers for Y data (comma-separated): ").split(',')
    y_indices = [int(idx.strip()) - 1 for idx in y_indices]
    
    x_data_non_sorted = data.iloc[:, x_idx].values
    y_data_non_sorted = [data.iloc[:, idx].values for idx in y_indices]

    # Sort data based on x_data
    sorted_indices = np.argsort(x_data_non_sorted)
    x_data = x_data_non_sorted[sorted_indices]
    y_data = [y[sorted_indices] for y in y_data_non_sorted]

    # Prompt the user for labels for each set of data
    labels = []
    for i in range(len(y_data)):
        label = input(f"Enter label for Y data {i+1}: ").strip()
        labels.append(label if label else f"Y data {i+1}")
    
    return x_data, y_data, x_data_non_sorted, y_data_non_sorted, labels

def plot_fields(x_data, y_data, filename, offset=None, xlabel=None, ylabel=None, title=None, labels=None, save_path=None):
    """
    Plot fields of data and save the figure.
    """
    
    named_colors = mcolors.XKCD_COLORS
    colors = ['b', 'r', 'k', 'c']
    colors += list(named_colors.keys())
    for i in range(len(y_data)):
        plt.plot(x_data, y_data[i], label=labels[i], linestyle='-', color=colors[i])  # Field 1

def main():
    # Check if one argument is provided: script.py <csv_file>
    if len(sys.argv) != 2:
        print("Usage: python script.py <csv_file>")
        return

    # Extract filename from command line argument
    filename = sys.argv[1]

    # Load X and Y data for the field
    x_data, y_data, x_data_non_sorted, y_data_non_sorted, labels = load_csv(filename)

    # Get user input for axis labels and title
    xlabel = input("Enter X-axis label (or press Enter to use default): ").strip()
    ylabel = input("Enter Y-axis label (or press Enter to use default): ").strip()
    title = input("Enter plot title (or press Enter to use default): ").strip()

    # Save path with high resolution
    save_path = input("Enter the path to save the plot with high resolution (or press Enter to skip): ").strip()

    # Plot the field
    plt.figure(figsize=(6, 4))  # Set figure size
    plot_fields(x_data, y_data, filename, xlabel=xlabel, ylabel=ylabel, title=title, labels=labels, save_path=save_path)

    plt.xlabel(xlabel if xlabel else 'X Data', fontsize=12)  # X-axis label
    plt.ylabel(ylabel if ylabel else 'Y Data', fontsize=12)  # Y-axis label
    plt.title(title if title else 'Field Data', fontsize=14)  # Plot title
    plt.legend(fontsize=10)  # Legend
    plt.grid(True)  # Enable grid
    plt.tight_layout()  # Adjust layout

    # Save the plot
    if save_path:
        plt.savefig(save_path + ".pdf", dpi=300)  # Save figure with high resolution (300 dpi)
        print(f"Plot saved to {save_path}" + ".pdf")
        
        while True:
            adjust_xlim = get_yes_no("Do you want to adjust xlim_a and xlim_b? (yes/no): ")
            if adjust_xlim == 'yes':
                new_xlim_a = get_valid_float("Enter the new xlim_a value: ")
                new_xlim_b = get_valid_float("Enter the new xlim_b value: ")
                plt.figure(figsize=(6, 4))  # Set figure size
                plot_fields(x_data, y_data, filename, xlabel=xlabel, ylabel=ylabel, title=title, labels=labels, save_path=save_path)
                plt.xlabel(xlabel if xlabel else 'X Data', fontsize=12)  # X-axis label
                plt.ylabel(ylabel if ylabel else 'Y Data', fontsize=12)  # Y-axis label
                plt.title(title if title else 'Field Data', fontsize=14)  # Plot title
                plt.legend(fontsize=10,loc=0)  # Legend
                plt.grid(True)  # Enable grid
                plt.tight_layout()  # Adjust layout
                plt.xlim(new_xlim_a, new_xlim_b)
                if save_path:
                    plt.savefig(save_path + ".pdf", dpi=300)
                    print(f"Plot saved to {save_path}.pdf")
            elif adjust_xlim == 'no':
                break

    # Display the plot
    plt.show()

if __name__ == "__main__":
    main()
