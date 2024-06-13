# Anthony BERGAUD 2024
# This tool allows one to translate 1D data until reaching a strong gradient/slope 
# -> useful to change values of entry gas in 1D flame until reaching the combustion zone

import argparse
import pandas as pd
import numpy as np

def main(file_path, translation_value):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(file_path)

    # Convert the DataFrame column to a numpy array for analysis
    data = df.iloc[:, 0].values  # Assuming the data is in the first column

    # Calculate the gradient
    gradient = np.gradient(data)

    # Find the index of the maximum gradient (positive or negative) -> that's where the translation should be stopped because we reach the flame
    max_gradient_index = np.argmax(np.abs(gradient))

    # Get the corresponding value from the original data
    max_gradient_value = data[max_gradient_index]

    # Translate the data until the location of the maximum gradient with the user defined value
    translated_data = np.copy(data)
    translated_data[:max_gradient_index] += translation_value

    # Write the translated data to a new CSV file
    translated_df = pd.DataFrame(translated_data)
    translated_df = translated_df.drop(translated_df.index[1])
    translated_file_path = "translated_data.csv"
    translated_df.to_csv(translated_file_path, index=False)

    # Print a message to inform the user about the created file and translation value
    print(f"Translation value: {translation_value}")
    print(f"Translated data saved to: {translated_file_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Translate data in a CSV file.")
    parser.add_argument("file_path", type=str, help="Path to the CSV file")
    parser.add_argument("-t", "--translate", type=float, default=0.0, help="Value for translation")
    args = parser.parse_args()
    main(args.file_path, args.translate)