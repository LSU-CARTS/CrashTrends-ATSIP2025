"""
Since there will likely be many directories that are empty at the end of the data collection process, this script
renames the ones that have no contents to have a suffix '-EMPTY'.
"""

import os
import sys


def is_in_skipped_path(dir_path, root):
    """
    Returns True if any component in the relative path (from root) starts with a period.
    """
    # Get the relative path from the root.
    rel_path = os.path.relpath(dir_path, root)
    # If it's the root directory itself, don't skip it.
    if rel_path == '.':
        return False
    # Split the relative path into its components.
    parts = rel_path.split(os.sep)
    return any(part.startswith('.') for part in parts)


def rename_empty_dirs(root):
    # Walk the directory tree bottom-up.
    for current_dir, dirs, files in os.walk(root, topdown=False):
        # Skip processing if this directory or any parent directory starts with a period.
        if is_in_skipped_path(current_dir, root):
            continue

        # Check if the directory is empty (no subdirectories and no files)
        if not dirs and not files:
            parent, dir_name = os.path.split(current_dir)
            new_name = dir_name + "-EMPTY"
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

    rename_empty_dirs(root_directory)

