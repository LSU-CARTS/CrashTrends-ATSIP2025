"""
If processes are rerun and directories might now have content, this script removes the -EMPTY suffix.
"""


import os
import sys


def remove_empty_suffix(root):
    # Walk the directory tree bottom-up to safely rename directories.
    for current_dir, dirs, files in os.walk(root, topdown=False):
        parent, dir_name = os.path.split(current_dir)
        # Check if the directory's name ends with '-EMPTY'
        if dir_name.endswith("-EMPTY"):
            # Remove the '-EMPTY' suffix
            new_name = dir_name[:-len("-EMPTY")]
            new_path = os.path.join(parent, new_name)
            try:
                os.rename(current_dir, new_path)
                print(f"Renamed: {current_dir} -> {new_path}")
            except Exception as e:
                print(f"Error renaming {current_dir}: {e}")


if __name__ == "__main__":

    root_directory = "/Path/To/Root/Directory"
    if not os.path.isdir(root_directory):
        print(f"Error: {root_directory} is not a valid directory.")
        sys.exit(1)

    remove_empty_suffix(root_directory)
