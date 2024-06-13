import os
import pandas as pd
import argparse

def add_column_from_csv(input_file, column_file, column_header):
    """
    Add a column from a CSV file to another CSV file.

    Parameters:
        input_file (str): Path to the input CSV file.
        column_file (str): Path to the CSV file containing the column data.
        column_header (str): Header for the new column.
    """
    # Read the original CSV file into a DataFrame
    df = pd.read_csv(input_file)

    # Read the column data from the other CSV file
    column_data = pd.read_csv(column_file, header=None)

    # Add the column data to the original DataFrame
    df[column_header] = column_data

    # Get the base name of the input file
    base_name = os.path.splitext(os.path.basename(input_file))[0]

    # Construct the output file name
    output_file = f"{base_name}_with_{column_header}.csv"

    # Write the DataFrame back to a CSV file
    df.to_csv(output_file, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Add a column from a CSV file to another CSV file.')
    parser.add_argument('input_file', type=str, help='Path to the input CSV file')
    parser.add_argument('column_file', type=str, help='Path to the CSV file containing the column data')
    parser.add_argument('column_header', type=str, help='Header for the new column')
    args = parser.parse_args()

    add_column_from_csv(args.input_file, args.column_file, args.column_header)
    
    print("File has been generated")
