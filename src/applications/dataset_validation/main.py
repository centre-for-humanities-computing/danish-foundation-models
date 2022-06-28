import curses
import os
from functools import partial
from typing import Iterable


def rate_str(str):
    curses.wrapper(main_window, str)


def write_example(filepath, category, is_porn, is_offensive, example_str):
    # Create file and add header if it doesn't
    if not os.path.exists(filepath):
        with open(filepath, "w") as f:
            f.write("category,is_porn,is_offensive,text\n")

    with open(filepath, "a") as f:
        row = ""

        for var in [category, is_porn, is_offensive, example_str]:
            row += f"{var},"

        f.write(f"{row}\n")


def sign_from_bool(boolean):
    if boolean:
        return "✓"
    else:
        return "False"


def main_window(win, str_to_rate):
    win.nodelay(False)
    key = ""
    win.clear()
    win.scrollok(False)

    filepath = "test.csv"

    process_language_with_path = partial(
        write_example, filepath=filepath, example_str=str_to_rate
    )

    cat_dict = {
        "n": "not_language",
        "w": "wrong_language",
        "c": "correct_language",
        "u": "unknown",
    }

    is_porn = False
    is_offensive = False

    left_spacing = " " * 4

    while True:
        win.clear()
        win.addstr("\n" * 2)
        win.addstr(f"{left_spacing}{str_to_rate}")
        win.addstr("\n" * 2)
        win.addstr(f"{left_spacing}Tags (non-exclusive):\n")
        win.addstr(f"{left_spacing*2}[p]orn: {sign_from_bool(is_porn)} \n")
        win.addstr(f"{left_spacing*2}[o]ffensive: {sign_from_bool(is_offensive)}")
        win.addstr("\n" * 2)
        win.addstr(f"{left_spacing}Category (exclusive):\n")
        win.addstr(
            f"{left_spacing*2}[n]ot language | [w]rong language | [c]orrect language | [u]nknown\n"
        )

        try:
            key = win.getkey()

            if key in cat_dict:
                process_language_with_path(
                    category=cat_dict[key], is_porn=is_porn, is_offensive=is_offensive
                )
                return

            if key == "p":
                is_porn = not is_porn
            elif key == "o":
                is_offensive = not is_offensive

        except Exception as e:
            raise e


def rate_examples(examples: Iterable[str]):
    for example in examples:
        rate_str(example)


if __name__ == "__main__":
    str_iterable = ["I'm a true string!", "Je suis un string", "fidosajfiodsaj"]

    rate_examples(str_iterable)
