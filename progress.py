import os
import shutil
from tqdm import tqdm
import win32api

_orig_copyfileobj = shutil.copyfileobj


class Progress:
    def __init__(self, src, dst):
        self.src = src
        self.dst = dst
        self._build_bar()

    @staticmethod
    def fix_path_case(file):
        return win32api.GetLongPathName(path)

    def copyfileobj(self, fsrc, fdst, length=16 * 1024):
        while True:
            buf = fsrc.read(length)
            if not buf:
                break
            fdst.write(buf)
            self.bar.set_postfix(file=Progress.fix_path_case(fsrc.name), refresh=False)
            self.bar.update(len(buf))

    @staticmethod
    def walkdir(directory):
        for dir_path, dirs, files in os.walk(directory):
            for filename in files:
                yield os.path.abspath(os.path.join(dir_path, filename))

    def _build_bar(self):
        total = 0
        if os.path.isdir(self.src):
            for filepath in tqdm(Progress.walkdir(self.src), unit="files"):
                total += os.stat(filepath).st_size
        else:
            total = os.stat(self.src).st_size
        self.bar = tqdm(total=total, unit='B', unit_scale=True, unit_divisor=1024)

    @staticmethod
    def copy(src, dst, follow_symlinks=True):
        p = Progress(src, dst)
        try:
            shutil.copyfileobj = p.copyfileobj
            if os.path.isdir(src):
                dst = shutil.copytree(src, dst, symlinks=follow_symlinks)
            else:
                dst = shutil.copy(src, dst, follow_symlinks=follow_symlinks)
        finally:
            shutil.copyfileobj = _orig_copyfileobj
        return dst

    @staticmethod
    def move(src, dst):
        p = Progress(src, dst)
        try:
            shutil.copyfileobj = p.copyfileobj
            dst = shutil.move(src, dst)
        finally:
            shutil.copyfileobj = _orig_copyfileobj
        return dst
