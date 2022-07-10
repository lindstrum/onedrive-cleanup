import filecmp
import hashlib
import os
import pathlib
from typing import Callable, Iterable


class DuplicateFinder:

    def __init__(self, src_root: str, search_roots: Iterable[str]):
        self.src_root = src_root
        self.search_roots = search_roots

    def sort(self) -> None:
        src_files_by_hash = dict()

        def hash_file(path: str) -> str:
            return hashlib.md5(pathlib.Path(path).read_bytes()).hexdigest()

        def walk_file_tree(roots: Iterable[str], action: Callable[[str], None]) -> None:
            for root in roots:
                for path, _, files in os.walk(root):
                    for name in files:
                        filepath = os.path.join(path, name)
                        action(filepath)

        def cache_original_files(filepath: str) -> None:
            src_root_components = os.path.normpath(self.src_root).split(os.sep)
            root_path = src_root_components[1:-1]
            root_folder_name = src_root_components[-1]
            filepath_components = os.path.normpath(filepath).split(os.sep)
            folder_path = filepath_components[1:-1]
            name_no_ext = os.path.splitext(filepath_components[-1])[0]
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
            if filehash not in src_files_by_hash:
                src_files_by_hash[filehash] = (filepath, duplicate_dest_abs_path)
            else:
                raise AssertionError(f"Duplicates in src root: {duplicate_dest_abs_path} is duplicate of {filepath}")

        def handle_duplicate(filepath: str) -> None:
            filehash = hash_file(filepath)
            if filehash in src_files_by_hash:
                (original_path, duplicate_dest_path) = src_files_by_hash[filehash]
                same_file = filecmp.cmp(filepath, original_path, shallow=False)
                if same_file:
                    pathlib.Path(duplicate_dest_path).mkdir(parents=True, exist_ok=True)
                    new_name = "-".join(os.path.normpath(filepath).split(os.sep)[1:])
                    new_path = os.path.join(duplicate_dest_path, new_name)
                    os.rename(filepath, new_path)

        if self.search_roots is not None and self.src_root is not None:
            walk_file_tree([self.src_root], cache_original_files)
            walk_file_tree(self.search_roots, handle_duplicate)
        else:
            raise ValueError(f"Either src_root ({self.src_root}) or search roots ({self.search_roots}) are None")
