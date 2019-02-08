import os
import sys
import _winapi

from game_linker_config import GameLinkerConfig
from progress import Progress


class GameLinker:
    def __init__(self, config: GameLinkerConfig):
        self.config = config
        self.source_path = os.path.join(self.config.source_path, self.config.game)
        self.target_path = os.path.join(self.config.target_path, self.config.game)

    def link(self):
        source_exists = os.path.exists(self.source_path)
        target_exists = os.path.exists(self.target_path)
        if source_exists:
            self.source_path = Progress.fix_path_case(self.source_path)
        if target_exists:
            self.target_path = Progress.fix_path_case(self.target_path)

        if not source_exists and not target_exists:
            sys.exit('Game folder does not exist in either location')
        if self.config.reverse:
            if source_exists and target_exists:
                # this remove directory will fail if not a link, unless the directory is empty
                # if the dir is empty, then it's not a big deal if the directory is accidentally deleted
                os.rmdir(self.source_path)
                Progress.move(self.target_path, self.source_path)
                print(f'Junction removed: {self.source_path} <== {self.target_path}')
            elif source_exists:
                sys.exit('Target does not exist')
            else:
                Progress.move(self.target_path, self.source_path)
                print(f'Junction removed: {self.source_path} <== {self.target_path}')
        else:
            if source_exists and target_exists:
                sys.exit('Game folder exists in both locations')
            elif source_exists:
                assert os.path.isdir(self.source_path)
                Progress.move(self.source_path, self.target_path)
            assert os.path.isdir(self.target_path)
            _winapi.CreateJunction(self.target_path, self.source_path)
            print(f'Junction created: {self.source_path} ==> {self.target_path}')


if __name__ == '__main__':
    config = GameLinkerConfig()
    linker = GameLinker(config)
    linker.link()
