import argparse
import os
import yaml
import sys

from util import fix_path_case


class GameLinkerConfig:
    def __init__(self):
        self.config = None
        self.config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
        self.platform = None
        self.target = 'ssd'
        self.target_path = None
        self.source = 'hdd'
        self.source_path = None
        self.game = None
        self.reverse = False
        self._parse_arguments()

    def _build_arg_parser(self):
        parser = argparse.ArgumentParser(
            description='Moves a game folder to different location and creates a link to it')
        parser.add_argument('-c', '--config', help='location of config file')
        parser.add_argument('-p', '--platform', help='gaming platform')
        parser.add_argument('-s', '--source',
                            help='the original location of the game folder (where the link will be created)')
        parser.add_argument('-t', '--target', help='final location of game folder')
        parser.add_argument('-r', '--reverse', action='store_true', help='reverses the operation')
        parser.add_argument('game')
        return parser

    def _parse_arguments(self):
        parser = self._build_arg_parser()
        args = parser.parse_args()

        assert args.game
        self.game = args.game

        if args.config:
            self.config_path = args.config
        with open(self.config_path, 'r') as f:
            self.config = yaml.load(f)

        if args.platform:
            self.platform = args.platform
            assert self.platform in self.config
        else:
            current_dir = os.getcwd()
            self.platform = self._get_platform_from_dir(current_dir)
            assert self.platform

        if args.source:
            self.source = args.source
        assert self.source in self.config[self.platform]
        self.source_path = self.config[self.platform][self.source]
        assert os.path.exists(self.source_path)
        self.source_path = fix_path_case(self.source_path)

        if args.target:
            self.target = args.target
        assert self.target in self.config[self.platform]
        self.target_path = self.config[self.platform][self.target]
        assert os.path.exists(self.target_path)
        self.target_path = fix_path_case(self.target_path)

        assert self.source_path != self.target_path

        if args.reverse:
            self.reverse = True

    def _get_platform_from_dir(self, directory: str) -> str:
        directory = os.path.normpath(directory).lower()
        for platform, platform_dirs in self.config.items():
            for _, platform_dir in platform_dirs.items():
                platform_dir: directory = os.path.normpath(platform_dir).lower()
                if directory == platform_dir:
                    return platform
