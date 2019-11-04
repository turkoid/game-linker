import argparse
import os
import re
import sys
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import yaml

from game_linker.choice_prompter import ChoicePrompter
from game_linker.util import ask_yes_no


class GameLinkerConfig:
    def __init__(self):
        self.config_path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
        self.platform: Optional[str] = None
        self.target = "ssd"
        self.source = "hdd"
        self.game: Optional[str] = None
        self.reverse = False
        self.create_dirs = False
        self.exact = False
        self._ignore_dirs = None
        self._parse_arguments()

    def _build_arg_parser(self):
        parser = argparse.ArgumentParser(
            description="Moves a game folder to different location and creates a link to it"
        )
        parser.add_argument("-c", "--config", help="location of config file")
        parser.add_argument("-p", "--platform", help="gaming platform")
        parser.add_argument(
            "-s",
            "--source",
            default="hdd",
            help="the original location of the game folder (where the link will be created)",
        )
        parser.add_argument(
            "-t", "--target", default="ssd", help="final location of game folder"
        )
        parser.add_argument(
            "-r", "--reverse", action="store_true", help="reverses the operation"
        )
        parser.add_argument(
            "-d",
            "--create-dirs",
            action="store_true",
            help="creates the directory if missing",
        )
        parser.add_argument(
            "-e",
            "--exact",
            action="store_true",
            help="finds the game using exact match",
        )
        parser.add_argument("game", nargs="?", help="full/partial game name")
        return parser

    def get_platform_dirs(self, platform: str) -> Dict[str, str]:
        return self.config[platform]["dirs"]

    def _parse_arguments(self):
        parser = self._build_arg_parser()
        args = parser.parse_args()

        self.game = args.game or ""
        self.exact = args.exact

        if args.config:
            self.config_path = args.config
        with open(self.config_path, "r") as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)

        if args.source:
            self.source = args.source
        if args.target:
            self.target = args.target

        if args.reverse:
            self.reverse = True
        if args.platform:
            self.platform = args.platform
            if self.platform not in self.config:
                sys.exit(f"{self.platform} not in config file")
        else:
            current_dir = os.getcwd()
            self.platform = self._get_platform_from_dir(current_dir)
        if not self.platform:
            if self.reverse:
                self.platform, self.game = self._prompt_for_all_games()
                self.exact = True
            else:
                self.platform = self._prompt_for_platform()
        platform_dirs = self.get_platform_dirs(self.platform)
        for location, directory in platform_dirs.items():
            if "windowsapps" in directory.lower():
                sys.exit(
                    "Currently linking microsoft store apps is not supported. Use the built-in windows app move under settings."
                )

        if self.source not in platform_dirs:
            sys.exit(f"{self.source} not in {self.platform} config")

        if self.target not in platform_dirs:
            sys.exit(f"{self.target} not in {self.platform} config")

        if self.source_path.lower() == self.target_path.lower():
            sys.exit("source path and target path cannot be the same")

        self.create_dirs = args.create_dirs
        if not self.create_dirs:
            for dir in [self.source_dir, self.target_dir]:
                if not os.path.exists(dir):
                    print(f'"{dir}" does not exist.')
                    if ask_yes_no("Do you want to create it?", default="y"):
                        os.makedirs(dir)
                    else:
                        sys.exit("Exiting...")

        if self.exact and not self.game:
            sys.exit("--exact used, but no game name supplied")

    def get_platform_dir(self, platform: str, location: str) -> str:
        platform_dir = os.path.normpath(self.config[platform]["dirs"][location])
        return platform_dir

    @property
    def source_dir(self) -> str:
        return self.get_platform_dir(self.platform, self.source)

    @property
    def source_path(self) -> str:
        return os.path.join(self.source_dir, self.game)

    @property
    def target_dir(self) -> str:
        return self.get_platform_dir(self.platform, self.target)

    @property
    def target_path(self) -> str:
        return os.path.join(self.target_dir, self.game)

    def get_ignore_dirs_for_platform(self, platform: str) -> List[str]:
        ignore_dirs = []
        if "ignore" in self.config[platform]:
            ignore_dirs = self.config[platform]["ignore"]
            ignore_dirs = [dir.lower() for dir in ignore_dirs if dir]
        return ignore_dirs

    @property
    def ignore_dirs(self) -> List[str]:
        if self._ignore_dirs is None:
            self._ignore_dirs = self.get_ignore_dirs_for_platform(self.platform)
        return self._ignore_dirs

    def _is_game_match(self, game: str) -> bool:
        if self.exact:
            return game.lower() == self.game.lower()
        elif self.game:
            return self.game.lower() in game.lower()
        else:
            return True

    def is_game_dir(
        self, entry: os.DirEntry, ignore_dirs: Optional[List[str]] = None
    ) -> bool:
        if ignore_dirs is None:
            ignore_dirs = self.ignore_dirs
        return (
            entry.is_dir()
            and self._is_game_match(entry.name)
            and entry.name.lower() not in ignore_dirs
        )

    def get_games_in_directory(
        self, directory: str, ignore_dirs: Optional[List[str]] = None
    ) -> List[str]:
        if not os.path.exists(directory):
            return []
        if ignore_dirs is None:
            ignore_dirs = self.ignore_dirs
        games = [
            entry.name
            for entry in os.scandir(directory)
            if self.is_game_dir(entry, ignore_dirs)
        ]
        return games

    def get_games_for_platform(self, platform: str, location: str) -> List[str]:
        location_dir = self.get_platform_dir(platform, location)
        ignore_dirs = self.get_ignore_dirs_for_platform(platform)
        return self.get_games_in_directory(location_dir, ignore_dirs)

    @property
    def source_games(self) -> List[str]:
        return self.get_games_in_directory(self.source_dir)

    @property
    def target_games(self) -> List[str]:
        return self.get_games_in_directory(self.target_dir)

    def get_games(self, platform: str) -> List[str]:
        target_games = set(self.get_games_for_platform(platform, self.target))
        if self.reverse:
            # only list games in the target directory
            games = target_games
        else:
            # list games in source or target, but not both
            source_games = set(self.get_games_for_platform(platform, self.source))
            games = source_games.symmetric_difference(target_games)
        games = list(games)
        games.sort(key=lambda g: g.lower())
        return games

    @property
    def games(self) -> List[str]:
        return self.get_games(self.platform)

    def _prompt_for_platform(self) -> str:
        platforms = list(self.config.keys())
        platforms.sort(key=lambda platform: platform.lower())
        prompter = ChoicePrompter("Choose a platform: ", platforms)
        platform = prompter.choose()
        return platform

    def _get_platform_from_dir(self, directory: str) -> str:
        directory = os.path.normpath(directory).lower()
        for platform, platform_dirs in self.config.items():
            for platform_dir in self.get_platform_dirs(platform).values():
                platform_dir = os.path.normpath(platform_dir)
                if directory == platform_dir:
                    return platform

    def _prompt_for_all_games(self) -> Tuple[str, str]:
        platforms = list(self.config.keys())
        platforms.sort(key=lambda p: p.lower())
        all_games = []
        for platform in platforms:
            platform_games = self.get_games(platform)
            platform_games = [f"[{platform}] {game}" for game in platform_games]
            all_games.extend(platform_games)
        prompter = ChoicePrompter("What game? ", all_games, 10)
        game = prompter.choose()
        match = re.match(r"\[(.+?)\] (.+)", game)
        platform = match.group(1)
        game = match.group(2)
        return platform, game
