import argparse
import os
import sys
from typing import Dict

import yaml


class GameLinkerConfig:
    def __init__(self):
        self.config_path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
        self.platform: str = None
        self.target = "ssd"
        self.source = "hdd"
        self.game: str = None
        self.ignore_games = []
        self.reverse = False
        self.create_dirs = False
        self.exact = False
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

        if args.config:
            self.config_path = args.config
        with open(self.config_path, "r") as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)

        if args.platform:
            self.platform = args.platform
            if self.platform not in self.config:
                sys.exit(f"{self.platform} not in config file")
        else:
            current_dir = os.getcwd()
            self.platform = self._get_platform_from_dir(current_dir)
            if not self.platform:
                sys.exit("unable to retrieve platform from current directory")

        if "ignore" in self.config[self.platform]:
            self.ignore_games = self.config[self.platform]["ignore"]
            if not isinstance(self.ignore_games, list):
                sys.exit("ignore needs to be a list")
            self.ignore_games = [g.lower() for g in self.ignore_games if g]

        if args.source:
            self.source = args.source
        platform_dirs = self.get_platform_dirs(self.platform)
        if self.source not in platform_dirs:
            sys.exit(f"{self.source} not in {self.platform} config")
        self.source_dir = os.path.normpath(platform_dirs[self.source])
        self.source_path = os.path.join(self.source_dir, self.game)

        if args.target:
            self.target = args.target
        if self.target not in platform_dirs:
            sys.exit(f"{self.target} not in {self.platform} config")
        self.target_dir = os.path.normpath(platform_dirs[self.target])
        self.target_path = os.path.join(self.target_dir, self.game)

        if self.source_path.lower() == self.target_path.lower():
            sys.exit("source path and target path cannot be the same")

        self.create_dirs = args.create_dirs
        self.exact = args.exact
        if self.exact and not self.game:
            sys.exit("--exact used, but no game name supplied")

        if args.reverse:
            self.reverse = True

    def _get_platform_from_dir(self, directory: str) -> str:
        directory = os.path.normpath(directory).lower()
        for platform, platform_dirs in self.config.items():
            for platform_dir in self.get_platform_dirs(platform).values():
                platform_dir = os.path.normpath(platform_dir)
                if directory == platform_dir:
                    return platform
