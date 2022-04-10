import hashlib
import os
import pathlib

pictures_root = 'C:\\Users\\ethan\\OneDrive\\Pictures'
new_pictures_root = os.path.join(pictures_root, 'result')


def new_filename(path: str) -> str:
    return path.replace('\\', '_').removeprefix('C:')


def dest_directory(file_hash: str) -> str:
    return os.path.join(new_pictures_root, file_hash)


def new_path(original_path: str, file_hash: str) -> str:
    return os.path.join(dest_directory(file_hash), new_filename(original_path))


def hash_file(path: str) -> str:
    return hashlib.md5(pathlib.Path(path).read_bytes()).hexdigest()


def group_pictures(root: str, file_hashes: set[str]) -> None:
    for name in os.listdir(root):
        path = os.path.join(root, name)
        if path == new_pictures_root:
            continue
        elif os.path.isdir(path):
            group_pictures(path, file_hashes)
        else:
            parts = path.split('.')
            if len(parts) > 1 and parts[1] == 'ini':
                continue
            h = hash_file(path)
            if h not in file_hashes:
                file_hashes.add(h)
                os.makedirs(dest_directory(h))
            dest = new_path(path, h)
            os.rename(path, new_path(path, h))


if __name__ == '__main__':
    if os.path.exists(new_pictures_root):
        existing_hashes = {h for h in os.listdir(new_pictures_root)}
    else:
        existing_hashes = set()
    group_pictures(pictures_root, existing_hashes)
