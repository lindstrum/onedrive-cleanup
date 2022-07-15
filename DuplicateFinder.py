import filecmp
import hashlib
import os
import pathlib
import shutil
from typing import Callable

src_root = "C:\\Users\\ethan\\OneDrive\\Documents\\school-work"
duplicate_search_root = "C:\\Users\\ethan\\OneDrive\\Documents\\AcerBackup20_05_2019_prev"
src_files_by_hash = dict()
src_duplicates = dict()
file_ignore = {".idea", ".git", ".metadata"}


def sort() -> None:
    def hash_file(path: str) -> str:
        return hashlib.md5(pathlib.Path(path).read_bytes()).hexdigest()

    def walk_file_tree(root: str, action: Callable[[str], None]) -> None:
        for path, _, files in os.walk(root):
            for name in files:
                filepath = os.path.join(path, name)
                action(filepath)

    def cache_original_files(filepath: str) -> None:
        filepath_components = os.path.normpath(filepath).split(os.sep)
        if len({ignore for ignore in filepath_components if ignore in file_ignore}) > 0:
            return
        folder_path = filepath_components[1:-1]
        name_no_ext = os.path.splitext(filepath_components[-1])[0]

        src_root_components = os.path.normpath(src_root).split(os.sep)
        root_path = src_root_components[1:-1]
        root_folder_name = src_root_components[-1]

        # new path is the same path but with "duplicates" before last folder name in root path
        duplicate_dest_path = os.path.join(
            os.path.sep,
            *root_path,
            "duplicates",
            root_folder_name,
            *folder_path[len(src_root_components):],
            name_no_ext
        )
        duplicate_dest_abs_path = os.path.abspath(duplicate_dest_path)
        filehash = hash_file(filepath)
        if filehash in src_duplicates:
            src_duplicates[filehash].append(filepath)
        elif filehash not in src_files_by_hash:
            src_files_by_hash[filehash] = (filepath, duplicate_dest_abs_path)
        else:
            src_duplicates[filehash] = [src_files_by_hash[filehash][0], filepath]
            src_files_by_hash.pop(filehash)

    def handle_duplicate(filepath: str) -> None:
        filehash = hash_file(filepath)
        if filehash in src_files_by_hash:
            (original_path, duplicate_dest_path) = src_files_by_hash[filehash]
            same_file = filecmp.cmp(filepath, original_path, shallow=False)
            if same_file:
                pathlib.Path(duplicate_dest_path).mkdir(parents=True, exist_ok=True)
                new_name = "-".join(os.path.normpath(filepath).split(os.sep)[1:])
                new_path = os.path.join(duplicate_dest_path, new_name)
                shutil.move(filepath, new_path)

    if len(src_files_by_hash) == 0 and src_root is not None:
        walk_file_tree(src_root, cache_original_files)
    if duplicate_search_root is not None:
        walk_file_tree(duplicate_search_root, handle_duplicate)


if __name__ == '__main__':
    sort()
