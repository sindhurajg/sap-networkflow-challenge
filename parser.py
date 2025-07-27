"""
Parser zip files into single csv
"""

import os
import zipfile
import pandas as pd


def load_and_merge_zipped_csvs(folder_path):
    """
    Load and parses the csvs into single csv
    """
    all_dfs = []

    # List all .zip files in the folder
    zip_files = \
        [f for f in os.listdir(folder_path) if f.lower().endswith('.zip')]
    if not zip_files:
        raise FileNotFoundError("No ZIP files found in the folder.")

    for zip_file in zip_files:
        zip_path = os.path.join(folder_path, zip_file)
        with zipfile.ZipFile(zip_path) as z:
            csv_files = [f for f in z.namelist() if f.endswith('.csv')]
            for csv_file in csv_files:
                print(csv_file)
                with z.open(csv_file) as f:
                    df = pd.read_csv(f, encoding='latin1')
                    all_dfs.append(df)

    # Concatenate all dataframes
    combined_df = pd.concat(all_dfs, ignore_index=True, sort=False)
    return combined_df


folder = r"C:\Users\Admin\Downloads\NSG_Flow_Logs_files"
merged_df = load_and_merge_zipped_csvs(folder)
print(f"Total records loaded: {len(merged_df)}")
print(merged_df.head())
