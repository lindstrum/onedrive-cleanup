from DuplicateFinder import DuplicateFinder

if __name__ == '__main__':
    src_root = "C:\\Users\\ethan\\OneDrive\\Documents\\test\\original"
    duplicate_search_root = "C:\\Users\\ethan\\OneDrive\\Documents\\test\\other"

    duplicate_finder = DuplicateFinder(src_root, [duplicate_search_root])
    duplicate_finder.sort()
