import _winapi
import os
import sys
from typing import Union

from game_linker.config import GameLinkerConfig
from game_linker.copy_progress import CopyProgress
from game_linker.util import fix_path_case


class GameLinker:
    def __init__(self, config: GameLinkerConfig):
        self.config = config
        self.source_dir = self.config.source_dir
        self.source_path = self.config.source_path
        self.target_dir = self.config.target_dir
        self.target_path = self.config.target_path
        self.game = self.config.game

    def _fix_paths(self):
        if os.path.exists(self.source_dir):
            self.source_dir = fix_path_case(self.source_dir)
        if os.path.exists(self.target_dir):
            self.target_dir = fix_path_case(self.target_dir)

        self.source_path = os.path.join(self.source_dir, self.game)
        self.target_path = os.path.join(self.target_dir, self.game)

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

    def _get_padded_option(
        self, option: Union[int, str], description: str, pad: int
    ) -> str:
        return f"{option:>{pad}}: {description}"

    def _get_game(self):
        if self.config.exact:
            return self.game
        game = self.game.lower()
        games = []
        for entry in os.scandir(self.source_dir):
            if entry.is_dir() and game in entry.name.lower():
                games.append(entry.name)
        for entry in os.scandir(self.target_dir):
            if (
                entry.is_dir()
                and game in entry.name.lower()
                and entry.name not in games
            ):
                games.append(entry.name)
        games = [g for g in games if g.lower() not in self.config.ignore_games]
        if not games:
            if self.config.game:
                sys.exit(f'No games found containing "{self.config.game}"')
            else:
                sys.exit(f'No games found for "{self.config.platform}" platform')
        if len(games) == 1:
            return games[0]

        games.sort(key=lambda g: g.lower())
        game = None
        lower_game_index = 1
        display_count = 10
        if self.config.game:
            print(f'Found {len(games)} games containing "{self.config.game}"')
        else:
            print(f'Found {len(games)} games for "{self.config.platform}" platform')
        while not game:
            upper_game_index = min(lower_game_index + display_count - 1, len(games))
            pad = len(str(upper_game_index))
            valid_options = [str(n) for n in range(1, upper_game_index + 1)]
            for game_index, game in enumerate(
                games[lower_game_index - 1 : upper_game_index], start=lower_game_index
            ):
                print(self._get_padded_option(game_index, game, pad))
            if lower_game_index > 1:
                valid_options.append("<")
                print(self._get_padded_option("<", "Previous", pad))
            if upper_game_index < len(games):
                valid_options.append(">")
                print(self._get_padded_option(">", "Next", pad))
            valid_options.append("q")
            print(self._get_padded_option("q", "Exit", pad))
            game = None
            while True:
                option = input("What game? ")
                option = option.strip().lower()
                if option in valid_options:
                    if option == "q":
                        sys.exit("Exiting...")
                    elif option == "<":
                        lower_game_index -= display_count
                    elif option == ">":
                        lower_game_index += display_count
                    else:
                        return games[int(option) - 1]
                    break

    def link(self):
        if self.config.create_dirs:
            if not os.path.exists(self.config.source_dir):
                os.makedirs(self.config.source_dir)
            if not os.path.exists(self.config.target_dir):
                os.makedirs(self.config.target_dir)

        self.game = self._get_game()
        assert self.game
        self._fix_paths()
        while True:
            link_msg = "unlink" if self.config.reverse else "link"
            confirm = input(f'Are you sure you want to {link_msg} "{self.game}"? ')
            if not confirm:
                continue
            confirm = confirm.strip().lower()
            if confirm in ["y", "yes"]:
                break
            elif confirm in ["n", "no"]:
                sys.exit("Exiting...")

        source_exists = os.path.exists(self.source_path)
        target_exists = os.path.exists(self.target_path)

        if not source_exists and not target_exists:
            sys.exit("Game folder does not exist in either location")
        if self.config.reverse:
            if source_exists and target_exists:
                # this remove directory will fail if not a link, unless the directory is empty
                # if the dir is empty, then it's not a big deal if the directory is accidentally deleted
                os.rmdir(self.source_path)
                CopyProgress.move(self.target_path, self.source_path)
                print(f"Junction removed: {self.source_path} <== {self.target_path}")
            elif not target_exists:
                sys.exit("Target does not exist")
            else:
                CopyProgress.move(self.target_path, self.source_path)
                print(f"Junction removed: {self.source_path} <== {self.target_path}")
        else:
            if source_exists and target_exists:
                sys.exit("Game folder exists in both locations")
            elif source_exists:
                assert os.path.isdir(self.source_path)
                CopyProgress.move(self.source_path, self.target_path)
            assert os.path.isdir(self.target_path)
            _winapi.CreateJunction(self.target_path, self.source_path)
            print(f"Junction created: {self.source_path} ==> {self.target_path}")


if __name__ == "__main__":
    config = GameLinkerConfig()
    linker = GameLinker(config)
    linker.link()
