import pandas as pd
import sys

def read_csv_file(csv_file):
    try:
        df = pd.read_csv(csv_file)
        return df
    except Exception as e:
        print("An error occurred while reading the CSV file:", str(e))
        return None

def print_help():
    print("""
Usage: python script.py <csv_file> [-s|--store] [<header_index1>,<header_index2>,...]

Description:
    This script reads a CSV file and displays the data for selected headers.
    It also provides an option to store the data for selected headers in separate CSV files.

Arguments:
    <csv_file>          Path to the CSV file to be read.

Options:
    -s, --store         Store the data for selected headers in separate CSV files.

Optional Arguments:
    <header_index1>,<header_index2>,...
                        Indices of the headers to display, separated by commas.

If no header indices are provided, the script will prompt you to enter them interactively.
""")

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help']:
        print_help()
        sys.exit(0)

    csv_file = sys.argv[1]
    df = read_csv_file(csv_file)

    if df is None:
        sys.exit(1)

    print("Available headers:")
    for i, header in enumerate(df.columns):
        print(f"{i + 1}. {header}")

    store_csv = False
    if "-s" in sys.argv or "--store" in sys.argv:
        store_csv = True
        try:
            sys.argv.remove("-s")
        except ValueError:
            pass
        try:
            sys.argv.remove("--store")
        except ValueError:
            pass

    if len(sys.argv) == 2:  # Only file path provided
        header_indices_input = input("Enter the indices of the headers you want to display (comma-separated): ")
        header_indices = [int(idx.strip()) - 1 for idx in header_indices_input.split(',')]
        selected_headers = [df.columns[idx] for idx in header_indices]
    else:
        header_indices = []
        for arg in sys.argv[2:]:
            try:
                indices = map(int, arg.split(','))  # Split multiple indices and convert to int
                header_indices.extend(indices)
            except ValueError:
                print(f"Invalid argument: {arg}")
                sys.exit(1)
        header_indices = [idx - 1 for idx in header_indices]  # Adjust indices to zero-based
        selected_headers = [df.columns[idx] for idx in header_indices]

    print("Data for selected headers:")
    for header in selected_headers:
        print(f"\n{header}:")
        print(df[header])

        if store_csv:
            filename = f"{header.replace('/', '-').replace(' ', '_').replace(')', '').replace('(', '')}.csv"
            df[[header]].to_csv(filename, index=False, header=False)
            print(f"Data for {header} stored in {filename}")

if __name__ == "__main__":
    main()
