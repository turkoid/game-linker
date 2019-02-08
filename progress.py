import os
import shutil
from tqdm import tqdm

_orig_copyfileobj = shutil.copyfileobj


class Progress:
    def __init__(self, src, dst):
        self.src = src
        self.dst = dst
        self.total = 0
        self.bar = None

    def copyfileobj(self, fsrc, fdst, length=16 * 1024):
        while True:
            buf = fsrc.read(length)
            if not buf:
                break
            fdst.write(buf)
            self.bar.set_postfix(file=str(fsrc.name), refresh=False)
            self.bar.update(len(buf))

    def _build_bar(self):
        self.total = 0
        if os.path.isdir(self.src):
            for filepath in tqdm(os.walk(src), unit="files"):
                self.total += os.stat(filepath).st_size
        else:
            self.total = os.stat(src).st_size
        self.bar = tqdm(total=self.total, unit='B', unit_scale=True, unit_divisor=1024)

    def copy(self, follow_symlinks=True):
        self._build_bar()
        try:
            shutil.copyfileobj = self.copyfileobj
            if os.path.isdir(self.src):
                dst = shutil.copytree(self.src, self.dst, symlinks=follow_symlinks)
            else:
                dst = shutil.copy(self.src, self.dst, follow_symlinks=follow_symlinks)
        finally:
            shutil.copyfileobj = _orig_copyfileobj
        return dst

    def move(self):
        self._build_bar()
        try:
            shutil.copyfileobj = self.copyfileobj
            dst = shutil.move(self.src, self.dst)
        finally:
            shutil.copyfileobj = _orig_copyfileobj
        return dst
