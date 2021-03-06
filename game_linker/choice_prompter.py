import sys
from typing import List
from typing import Optional
from typing import Union


class ChoicePrompter:
    def __init__(
        self, prompt: str, choices: List[str], display_count: Optional[int] = None
    ):
        if not choices:
            raise ValueError("No choices given.")
        self.prompt = prompt
        self.choices = choices
        self.display_count = display_count or len(self.choices)

    def _get_padded_option(
        self, option: Union[int, str], description: str, pad: int
    ) -> str:
        return f"{option:>{pad}}: {description}"

    def choose(self):
        if len(self.choices) == 1:
            option = self.choices[0]
            print(f"Only one option available. Choosing {option}")
            return option
        lower_game_index = 1
        choice = None
        while not choice:
            upper_game_index = min(
                lower_game_index + self.display_count - 1, len(self.choices)
            )
            pad = len(str(upper_game_index))
            valid_options = [str(n) for n in range(1, upper_game_index + 1)]
            for game_index, game in enumerate(
                self.choices[lower_game_index - 1 : upper_game_index],
                start=lower_game_index,
            ):
                print(self._get_padded_option(game_index, game, pad))
            if lower_game_index > 1:
                valid_options.append("<")
                print(self._get_padded_option("<", "Previous", pad))
            if upper_game_index < len(self.choices):
                valid_options.append(">")
                print(self._get_padded_option(">", "Next", pad))
            valid_options.append("q")
            print(self._get_padded_option("q", "Exit", pad))
            choice = None
            while True:
                option = input(self.prompt)
                option = option.strip().lower()
                if option in valid_options:
                    if option == "q":
                        sys.exit("Exiting...")
                    elif option == "<":
                        lower_game_index -= self.display_count
                    elif option == ">":
                        lower_game_index += self.display_count
                    else:
                        return self.choices[int(option) - 1]
                    break
