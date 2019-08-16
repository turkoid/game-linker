import os
from typing import Optional

import win32api


def fix_path_case(path):
    return win32api.GetLongPathName(win32api.GetShortPathName(path))


def walkdir(directory):
    for dir_path, dirs, files in os.walk(directory):
        for filename in files:
            yield os.path.abspath(os.path.join(dir_path, filename))


def ask_yes_no(question: str, default: Optional[str] = None):
    default = (default or "").lower()
    yes_options = ["y", "yes"]
    no_options = ["n", "no"]
    yes = "Y" if default in yes_options else "y"
    no = "N" if default in no_options else "n"
    prompt = f"{question}? ({yes}/{no}) "
    while True:
        answer = input(prompt) or default
        if not answer:
            continue
        answer = answer.strip().lower()
        if answer in yes_options:
            return True
        elif answer in no_options:
            return False
