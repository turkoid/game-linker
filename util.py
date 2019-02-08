import os
import win32api


def fix_path_case(path):
    return win32api.GetLongPathName(win32api.GetShortPathName(path))


def walkdir(directory):
    for dir_path, dirs, files in os.walk(directory):
        for filename in files:
            yield os.path.abspath(os.path.join(dir_path, filename))