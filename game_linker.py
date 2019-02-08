import os
import sys
import _winapi

from game_linker_config import GameLinkerConfig
from copy_progress import CopyProgress
from util import fix_path_case


class GameLinker:
    def __init__(self, config: GameLinkerConfig):
        self.config = config
        self.source_dir = self.config.source_dir
        self.source_path = self.config.source_path
        self.target_dir = self.config.target_dir
        self.target_path = self.config.target_path

    def _fix_paths(self):
        if os.path.exists(self.config.source_dir):
            self.source_dir = fix_path_case(self.config.source_dir)
        if os.path.exists(self.config.target_dir):
            self.target_dir = fix_path_case(self.config.target_dir)

        self.source_path = os.path.join(self.source_dir, self.config.game)
        self.target_path = os.path.join(self.target_dir, self.config.game)

        source_exists = os.path.exists(self.source_path)
        target_exists = os.path.exists(self.target_path)

        if source_exists:
            self.source_path = fix_path_case(self.source_path)
            if not target_exists:
                game = os.path.basename(self.source_path)
                self.target_path = os.path.join(self.target_dir, game)
        if target_exists:
            self.target_path = fix_path_case(self.target_path)
            if not source_exists:
                game = os.path.basename(self.target_path)
                self.source_path = os.path.join(self.source_dir, game)

    def link(self, create_dirs=False):
        if create_dirs:
            if not os.path.exists(self.config.source_dir):
                os.makedirs(self.config.source_dir)
            if not os.path.exists(self.config.target_dir):
                os.makedirs(self.config.target_dir)

        self._fix_paths()

        source_exists = os.path.exists(self.source_path)
        target_exists = os.path.exists(self.target_path)

        if not source_exists and not target_exists:
            sys.exit('Game folder does not exist in either location')
        if self.config.reverse:
            if source_exists and target_exists:
                # this remove directory will fail if not a link, unless the directory is empty
                # if the dir is empty, then it's not a big deal if the directory is accidentally deleted
                os.rmdir(self.source_path)
                CopyProgress.move(self.target_path, self.source_path)
                print(f'Junction removed: {self.source_path} <== {self.target_path}')
            elif not target_exists:
                sys.exit('Target does not exist')
            else:
                CopyProgress.move(self.target_path, self.source_path)
                print(f'Junction removed: {self.source_path} <== {self.target_path}')
        else:
            if source_exists and target_exists:
                sys.exit('Game folder exists in both locations')
            elif source_exists:
                assert os.path.isdir(self.source_path)
                CopyProgress.move(self.source_path, self.target_path)
            assert os.path.isdir(self.target_path)
            _winapi.CreateJunction(self.target_path, self.source_path)
            print(f'Junction created: {self.source_path} ==> {self.target_path}')


if __name__ == '__main__':
    config = GameLinkerConfig()
    linker = GameLinker(config)
    linker.link()
