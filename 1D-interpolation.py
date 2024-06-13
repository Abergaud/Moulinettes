import numpy as np
from scipy.interpolate import interp1d
import pandas as pd
import sys
import os

def read_csv_file(csv_file):
    try:
        df = pd.read_csv(csv_file)
        if len(df.columns) != 1:
            print("Error: Input CSV file must have exactly one column.")
            return None
        return df.iloc[:, 0].values  # Extract the values of the single column
    except Exception as e:
        print("An error occurred while reading the CSV file:", str(e))
        return None

def interpolate_data(data, new_size):
    # Original data size
    original_size = len(data)

    # Generate indices for the original and new data
    x_original = np.arange(original_size)
    x_new = np.linspace(0, original_size - 1, new_size)

    # Perform linear interpolation
    f = interp1d(x_original, data, kind='linear')
    interpolated_data = f(x_new)

    return interpolated_data

def save_to_csv(data, input_csv_file):
    try:
        base_name, extension = os.path.splitext(input_csv_file)
        output_csv_file = f"{base_name}_interpolated{extension}"
        df = pd.DataFrame(data, columns=['Interpolated_Data'])
        df.to_csv(output_csv_file, index=False, header=False)
        print(f"Interpolated data saved to {output_csv_file}")
    except Exception as e:
        print("An error occurred while saving the interpolated data to CSV:", str(e))

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <csv_file> <new_size>")
        sys.exit(1)

    csv_file = sys.argv[1]
    new_size = int(sys.argv[2])

    # Read the dataset from the CSV file
    data = read_csv_file(csv_file)
    if data is None:
        sys.exit(1)

    # Interpolate the data to the new size
    interpolated_data = interpolate_data(data, new_size)

    # Save the interpolated data to a new CSV file
    save_to_csv(interpolated_data, csv_file)

if __name__ == "__main__":
    main()
