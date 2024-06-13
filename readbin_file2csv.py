# Anthony BERGAUD - 2024

import csv
import argparse
import os

def convert_txt_to_csv(input_file):
    # Derive the output file name
    base_name = os.path.basename(input_file)
    output_file = f"{os.path.splitext(base_name)[0]}.csv"

    # Read the text file from Readbin
    with open(input_file, 'r') as file:
        lines = file.readlines()

    # Extract headers
    headers = [line.strip()[1:] for line in lines if line.startswith('#')]

    # Extract data
    data = [line.strip().split() for line in lines if not line.startswith('#')]

    # Write to CSV
    with open(output_file, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        
        # Write headers
        csvwriter.writerow(headers)
        
        # Write data
        csvwriter.writerows(data)

    print(f"Conversion to CSV completed successfully. Output file: {output_file}")

def main():
    parser = argparse.ArgumentParser(
        description="Convert a readbin text file to CSV.",
        epilog="This script reads a text file with headers starting with # "
               "and data rows separated by spaces. The output CSV file will "
               "have the same base name as the input file, with a .csv extension."
    )
    parser.add_argument('input_file', type=str, help="The input text file to be converted")

    args = parser.parse_args()

    convert_txt_to_csv(args.input_file)

if __name__ == "__main__":
    main()
