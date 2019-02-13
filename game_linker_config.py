import argparse
import os

import yaml


class GameLinkerConfig:
    def __init__(self):
        self.config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
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
        parser.add_argument(
            "game", nargs="?", default="", help="full/partial game name"
        )
        return parser

    def _parse_arguments(self):
        parser = self._build_arg_parser()
        args = parser.parse_args()

        self.game = args.game

        if args.config:
            self.config_path = args.config
        with open(self.config_path, "r") as f:
            self.config = yaml.load(f)

        if args.platform:
            self.platform = args.platform
            assert self.platform in self.config
        else:
            current_dir = os.getcwd()
            self.platform = self._get_platform_from_dir(current_dir)
            assert self.platform

        if self.config[self.platform]["ignore"]:
            self.ignore_games = self.config[self.platform]["ignore"]
            assert isinstance(self.ignore_games, list)
            self.ignore_games = [g.lower() for g in self.ignore_games if g]

        if args.source:
            self.source = args.source
        assert self.source in self.config[self.platform]
        self.source_dir = os.path.normpath(self.config[self.platform][self.source])
        self.source_path = os.path.join(self.source_dir, self.game)

        if args.target:
            self.target = args.target
        assert self.target in self.config[self.platform]
        self.target_dir = os.path.normpath(self.config[self.platform][self.target])
        self.target_path = os.path.join(self.target_dir, self.game)

        assert self.source_path.lower() != self.target_path.lower()

        self.create_dirs = args.create_dirs
        self.exact = args.exact
        if self.exact:
            assert self.game

        if args.reverse:
            self.reverse = True

    def _get_platform_from_dir(self, directory: str) -> str:
        directory = os.path.normpath(directory).lower()
        for platform, platform_dirs in self.config.items():
            for _, platform_dir in platform_dirs.items():
                platform_dir: directory = os.path.normpath(platform_dir).lower()
                if directory == platform_dir:
                    return platform
