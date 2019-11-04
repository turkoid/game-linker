import pytest

from game_linker.choice_prompter import ChoicePrompter


@pytest.fixture
def no_choices():
    return []


@pytest.fixture
def one_choice():
    return ["one"]


@pytest.fixture
def two_choices():
    return ["one", "two"]


def test_no_choices_raises_error(no_choices):
    with pytest.raises(ValueError):
        _ = ChoicePrompter("select", no_choices)


def test_init_display_count_does_not_use_choices_length(two_choices):
    prompter = ChoicePrompter("select", two_choices, display_count=1)
    assert prompter.display_count != len(two_choices)


def test_no_init_display_count_use_choices_length(two_choices):
    prompter = ChoicePrompter("select", two_choices)
    assert prompter.display_count == len(two_choices)


def test_one_choice_does_not_prompt(one_choice):
    prompter = ChoicePrompter("select", one_choice)
    choice = prompter.choose()
    assert choice == "one"
