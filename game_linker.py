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

    def _fix_paths(self, game):
        if os.path.exists(self.source_dir):
            self.source_dir = fix_path_case(self.source_dir)
        if os.path.exists(self.target_dir):
            self.target_dir = fix_path_case(self.target_dir)

        self.source_path = os.path.join(self.source_dir, game)
        self.target_path = os.path.join(self.target_dir, game)

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

    def _get_game(self):
        if not self.config.exact and not os.path.exists(self.source_path) and not os.path.exists(self.target_path):
            game = self.config.game.lower()
            games = []
            for entry in os.scandir(self.source_dir):
                if entry.is_dir() and game in entry.name.lower():
                    games.append(entry.name)
            for entry in os.scandir(self.target_dir):
                if entry.is_dir() and game in entry.name.lower() and entry.name not in games:
                    games.append(entry.name)

            if not games:
                sys.exit(f'No games found containing "{self.config.game}"')

            games.sort()
            game = None
            lower_game_index = 1
            display_count = 10
            print(f'Found {len(games)} containing "{self.config.game}"')
            while not game:
                valid_options = ['q']
                if lower_game_index > 1:
                    valid_options.append('<')
                    print('<: Previous')
                upper_game_index = min(lower_game_index + display_count, len(games))
                for game_index, game in enumerate(games[lower_game_index - 1:upper_game_index], start=1):
                    valid_options.extend(range(lower_game_index, upper_game_index + 1))
                    print(f'{game_index:<{len(str(upper_game_index))}}: {game}')
                if upper_game_index < len(games):
                    valid_options.append('>')
                    print('>: Next')
                print('q: Exit')
                while True:
                    option = input('What game? ')
                    if not option:
                        continue
                    if option in valid_options or lower_game_index <= int(option) <= upper_game_index:
                        if option == 'q':
                            sys.exit('Exiting...')
                        elif option == '<':
                            lower_game_index -= display_count
                        elif option == '>':
                            lower_game_index += display_count
                        else:
                            game = games[int(option) - 1]
                        break
        else:
            game = self.config.game

        return game

    def link(self):
        if self.config.create_dirs:
            if not os.path.exists(self.config.source_dir):
                os.makedirs(self.config.source_dir)
            if not os.path.exists(self.config.target_dir):
                os.makedirs(self.config.target_dir)

        game = self._get_game()
        print('testing=', game)
        quit(0)
        self._fix_paths(game)

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
