import csv
import sys

def display_headers(file_path):
    with open(file_path, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader)
        print("Headers:")
        for i, header in enumerate(headers):
            print(f"{i + 1}. {header}")

def display_data(file_path, header_index):
    with open(file_path, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader)
        try:
            header = headers[header_index - 1]
            print(f"Data for header '{header}':")
            for row in reader:
                print(row[header_index - 1])
        except IndexError:
            print("Invalid header index.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <csv_file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    display_headers(file_path)
    header_index = int(input("Enter the index of the header you want to display data for: "))
    display_data(file_path, header_index)
