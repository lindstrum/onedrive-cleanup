import filecmp
import hashlib
import os
import pathlib
from typing import Callable, Iterable


class DuplicateFinder:

    def __init__(self, src_root: str, search_roots: Iterable[str] = None):
        self.src_root = src_root
        self.search_roots = search_roots if search_roots is not None else src_root

    def sort(self) -> None:
        src_files_by_hash = dict()

        def hash_file(path: str) -> str:
            return hashlib.md5(pathlib.Path(path).read_bytes()).hexdigest()

        def walk_file_tree(roots: Iterable[str], action: Callable[[str, str], None]) -> None:
            for root in roots:
                for root_path, _, files in os.walk(root):
                    for name in files:
                        action(root_path, name)

        def cache_original_files(folder_path: str, name: str) -> None:
            filepath = os.path.join(folder_path, name)
            src_root_components = os.path.splitext(self.src_root)
            root_path = list(src_root_components[:-1])
            root_folder_name = src_root_components[-1]
            name_no_ext = os.path.splitext(name)[0]

            duplicates_dest_path = os.path.join(*root_path, "duplicates", root_folder_name, folder_path, name_no_ext)
            filehash = hash_file(filepath)
            if filehash not in src_files_by_hash:
                src_files_by_hash[filehash] = (filepath, duplicates_dest_path)
            else:
                raise AssertionError(f"Duplicates in src root: {duplicates_dest_path} is duplicate of {filepath}")

        def handle_duplicates(duplicate_path: str, name: str) -> None:
            filepath = os.path.join(duplicate_path, name)
            filehash = hash_file(filepath)
            if filehash in src_files_by_hash:
                (original_path, duplicate_dest_path) = src_files_by_hash[filehash]
                same_file = filecmp.cmp(filepath, original_path, shallow=False)
                if same_file:
                    pathlib.Path(duplicate_dest_path).mkdir(parents=True, exist_ok=True)
                    new_path = os.path.join(duplicate_dest_path, name)
                    os.rename(filepath, new_path)

        walk_file_tree(self.src_root, cache_original_files)
        walk_file_tree(self.search_roots, handle_duplicates)
