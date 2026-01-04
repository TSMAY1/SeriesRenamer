import re
import os
from pathlib import Path

directory_path = Path("DIRECTORY_PATH_HERE")
# Initialize an empty list
old_name_list = []
new_name_list = []

pattern = "REGEX_PATTERN_HERE"

# Get the names of each of the files
def get_names(dir_path):
    for file_path in dir_path.iterdir():
        old_name_list.append(file_path.name)
    return old_name_list

# Create a new name list by regexing the information in the old name list
def update_names(old_name_list):
    for name in old_name_list:
        result = re.search(pattern, name)
        series_name = result[1]
        season_number = result[2]
        episode_number = result[3]
        new_name_list.append(f"{series_name} - S{season_number} - E{episode_number}")
    return new_name_list

# Rename the files by iterating through the directory and the new name list
def rename_files(old_name_list, new_name_list):
    for old_name, new_name in zip(old_name_list, new_name_list):
        old_name_path = directory_path / old_name
        new_name_path = directory_path / new_name
        try:
            os.rename(old_name_path, new_name_path)
            print(f"Renamed '{old_name}' to '{new_name}'")
        except FileNotFoundError:
            print(f"Error: The file '{old_name}' was not found.")
        except FileExistsError:
            print(f"Error: The destination file '{new_name}' already exists.")
        except PermissionError:
            print("Error: Permission denied. Unable to rename the file.")
    print("Files renamed successfully.")


old_names = get_names(directory_path)
new_names = update_names(old_names)
rename_files(old_names, new_names)