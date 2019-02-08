import os
import shutil
from tqdm import tqdm

_orig_copyfileobj = shutil.copyfileobj


class Progress:
    def __init__(self, src, dst):
        self.src = src
        self.dst = dst
        self._build_bar()

    def copyfileobj(self, fsrc, fdst, length=16 * 1024):
        while True:
            buf = fsrc.read(length)
            if not buf:
                break
            fdst.write(buf)
            self.bar.set_postfix(file=str(fsrc.name), refresh=False)
            self.bar.update(len(buf))

    def _build_bar(self):
        total = 0
        if os.path.isdir(self.src):
            for filepath in tqdm(os.walk(self.src), unit="files"):
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
