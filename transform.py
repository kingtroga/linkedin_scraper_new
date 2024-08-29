import os
import pandas as pd

def get_csv_files(directory):
    """Retrieve all CSV files from the specified directory."""
    return [f for f in os.listdir(directory) if f.endswith('.csv')]

def rename_file(filename):
    """Remove the 'dlp_' prefix from the filename if it exists."""
    if filename.startswith("dlp_"):
        return filename.replace("dlp_", "", 1)
    return filename

def convert_csv_to_xlsx(directory, csv_file):
    """Convert a CSV file to an XLSX file."""
    csv_path = os.path.join(directory, csv_file)
    xlsx_filename = rename_file(csv_file.replace('.csv', '.xlsx'))
    xlsx_path = os.path.join('xlsx', xlsx_filename)

    df = pd.read_csv(csv_path)
    df.to_excel(xlsx_path, index=False)
    print(f"Converted {csv_file} to {xlsx_filename}")

def main():
    csv_directory = 'csv'
    xlsx_directory = 'xlsx'

    # Ensure the xlsx directory exists
    os.makedirs(xlsx_directory, exist_ok=True)

    # Get all CSV files in the csv directory
    csv_files = get_csv_files(csv_directory)

    if not csv_files:
        print("No CSV files found in the 'csv' directory.")
        return

    # Allow the user to select files to convert
    print("Available CSV files:")
    for i, file in enumerate(csv_files, 1):
        print(f"{i}. {file}")

    choices = input("Enter the numbers of the files you want to convert, separated by commas (e.g., 1,3,5): ")
    selected_files = [csv_files[int(choice) - 1] for choice in choices.split(',') if choice.isdigit()]

    for csv_file in selected_files:
        convert_csv_to_xlsx(csv_directory, csv_file)

if __name__ == "__main__":
    main()
