import os
import shutil

from tqdm import tqdm

from game_linker.util import fix_path_case
from game_linker.util import walkdir

_orig_copyfileobj = shutil.copyfileobj


class CopyProgress:
    def __init__(self, src, dst):
        self.src = src
        self.dst = dst
        self.show_current_file = False
        self._build_bar()

    def copyfileobj(self, fsrc, fdst, length=1000 * 1024):
        while True:
            buf = fsrc.read(length)
            if not buf:
                break
            fdst.write(buf)
            if self.show_current_file:
                self.bar.set_postfix(file=fix_path_case(fsrc.name), refresh=False)
            self.bar.update(len(buf))

    def _build_bar(self):
        total = 0
        if os.path.isdir(self.src):
            for filepath in tqdm(
                walkdir(self.src), unit="files", desc="Determining src size"
            ):
                total += os.stat(filepath).st_size
        else:
            total = os.stat(self.src).st_size
        self.bar = tqdm(total=total, unit="B", unit_scale=True, unit_divisor=1024)

    @staticmethod
    def copy(src, dst, follow_symlinks=True):
        p = CopyProgress(src, dst)
        try:
            shutil.copyfileobj = p.copyfileobj
            if os.path.isdir(src):
                dst = shutil.copytree(src, dst, symlinks=follow_symlinks)
            else:
                dst = shutil.copy(src, dst, follow_symlinks=follow_symlinks)
        finally:
            shutil.copyfileobj = _orig_copyfileobj
            p.bar.close()

        return dst

    @staticmethod
    def move(src, dst):
        p = CopyProgress(src, dst)
        try:
            shutil.copyfileobj = p.copyfileobj
            dst = shutil.move(src, dst)
        finally:
            shutil.copyfileobj = _orig_copyfileobj
            p.bar.close()

        return dst
