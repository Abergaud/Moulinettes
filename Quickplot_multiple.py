import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pandas as pd

plt.style.use("/scratch/cfd/bergaud/CTPP/MPLSTYLE/cerfacs.mplstyle")

##################### PARAMETERS EASY TO MODIFY ####################
figsize=(6,4)
linestyle_1='-'
linestyle_2='-'
marker_1=''
marker_2='.'
xlim_a=0; xlim_b=0.025
#ylim=(0,0)
######################################################################

def load_csv(filename):
    """
    Load CSV file and prompt user to select headers for x and y data.
    """
    data = pd.read_csv(filename)
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

def calculate_gradient(x_data, y_data):
    """
    Calculate the gradient of the y_data with respect to x_data.
    """
    gradient = np.gradient(y_data, x_data)  # Add edge_order parameter to handle edges
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
    colors += named_colors.keys()

    for i in range(len(filenames)):
        for j in range(len(y_data_list[i])):
            label = labels_list[i][j] if labels_list and len(labels_list[i]) > j else f"Field {j+1} ({filenames[i]})"
            plt.plot(x_data_list[i] + initial_offset, y_data_list[i][j], label=label, linestyle=linestyle_1, marker=marker_1, color=colors[i])

    plt.xlabel(xlabel if xlabel else 'X Data', fontsize=12)  # X-axis label
    plt.ylabel(ylabel if ylabel else 'Y Data', fontsize=12)  # Y-axis label
    plt.title(title if title else 'Comparison of Fields', fontsize=14)  # Plot title
    plt.legend(fontsize=10)  # Legend
    plt.grid(True)  # Enable grid
    plt.tight_layout()  # Adjust layout

def main():
    # Check if at least two arguments are provided
    if len(sys.argv) < 3:
        print("At least two CSV files are required.")
        print("Usage: python script.py <csv_file1> <csv_file2> [<csv_file3> ...]")
        return

    # Extract filenames from command line arguments
    filenames = sys.argv[1:]

    # Initialize lists to store data for each file
    x_data_list = []
    y_data_list = []
    x_data_non_sorted_list = []
    y_data_non_sorted_list = []
    labels_list = []

    # Load X and Y data for each file
    for filename in filenames:
        print(f"Processing file: {filename}")
        x_data, y_data, x_data_non_sorted, y_data_non_sorted, labels = load_csv(filename)
        x_data_list.append(x_data)
        y_data_list.append(y_data)
        x_data_non_sorted_list.append(x_data_non_sorted)
        y_data_non_sorted_list.append(y_data_non_sorted)
        labels_list.append(labels)

    # Find the initial offset using the highest gradient of the first file
    initial_offset = None
    if len(filenames) > 1:
        initial_offset = find_offset_by_gradient(x_data_non_sorted_list[0], y_data_non_sorted_list[0][0], x_data_non_sorted_list[1], y_data_non_sorted_list[1][0])
        print(f"Initial offset computed: {initial_offset}")

    # Get user input for axis labels and title
    xlabel = input("Enter X-axis label (or press Enter to use default): ").strip()
    ylabel = input("Enter Y-axis label (or press Enter to use default): ").strip()
    title = input("Enter plot title (or press Enter to use default): ").strip()

    # Save path with high resolution
    save_path = input("Enter the path to save the plot with high resolution (or press Enter to skip): ").strip()

    # Plot all the fields with the initial offset
    plt.figure(figsize=figsize)  # Set figure size
    plot_fields(x_data_list, y_data_list, filenames, initial_offset, xlabel, ylabel, title, labels_list, save_path)

    # Save the plot
    if save_path:
        plt.xlim(xlim_a, xlim_b)
        plt.savefig(save_path + ".pdf", dpi=300)  # Save figure with high resolution (300 dpi)
        print(f"Plot saved to {save_path}.pdf")

    while True:
        # Ask the user if they want to adjust the offset
        adjust_offset = input("Do you want to adjust the offset? (yes/no): ").strip().lower()
        if adjust_offset == 'yes':
            new_offset = float(input("Enter the new offset value: ").strip())
            # Re-plot with the new offset
            plt.figure(figsize=figsize)  # Set figure size
            plot_fields(x_data_list, y_data_list, filenames, new_offset, xlabel, ylabel, title, labels_list, save_path)
            plt.show()
            if save_path:
                plt.xlim(xlim_a, xlim_b)
                plt.savefig(save_path + ".pdf", dpi=300)  # Save figure with high resolution (300dpi)
                print(f"Plot saved to {save_path}.pdf")
            else:
                break
        if adjust_offset == 'no':
            new_offset = 0.0
            break
            
    initial_offset = new_offset

    while True:
        # Ask the user if they want to adjust the offset
        adjust_xlim = input("Do you want to adjust xlim_a and xlim_b? (yes/no): ").strip().lower()
        if adjust_xlim == 'yes':
            new_xlim_a = float(input("Enter the new xlim_a value: ").strip())
            new_xlim_b = float(input("Enter the new xlim_b value: ").strip())
            # Re-plot with the new offset
            plt.figure(figsize=figsize)  # Set figure size
            plot_fields(x_data_list, y_data_list, filenames, new_offset, xlabel, ylabel, title, labels_list, save_path)
            plt.show()
            if save_path:
                plt.xlim(new_xlim_a, new_xlim_b)
                plt.savefig(save_path + ".pdf", dpi=300)  # Save figure with high resolution (300dpi)
                print(f"Plot saved to {save_path}.pdf")
            else:
                break
        if adjust_xlim == 'no':
            break

if __name__ == "__main__":
    main()
    print("End of the program")