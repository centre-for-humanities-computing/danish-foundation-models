import curses
import os
from functools import partial
from nis import cat
from typing import Iterable


class ExampleRater:
    def __init__(self, examples: Iterable, output_path: str):
        self.examples = examples
        self.output_path = output_path

        self.items_to_process = []
        self.processed_items = []
        self.n_items_processed = 0

    def rate_examples(self):
        while self.examples or self.items_to_process:
            if self.items_to_process:
                item = self.items_to_process.pop()
                self.rate_str(
                    example_str=item["example_str"],
                    is_porn=item["is_porn"],
                    is_offensive=item["is_offensive"],
                )
            else:
                self.rate_str(self.examples.pop())

    def rate_str(self, example_str, is_porn=False, is_offensive=False):
        curses.wrapper(
            self.main_window,
            example_str=example_str,
            is_porn=is_porn,
            is_offensive=is_offensive,
        )

    def main_window(self, win, example_str, is_porn=False, is_offensive=False):
        win.nodelay(False)
        key = ""
        win.clear()
        win.scrollok(False)

        cat_dict = {
            "n": "not_language",
            "w": "wrong_language",
            "c": "correct_language",
            "s": "skipped",
        }

        is_porn = is_porn
        is_offensive = is_offensive

        left_spacing = " " * 2

        while True:
            win.clear()
            win.addstr("\n" * 2)

            win.addstr(f"{example_str}")
            win.addstr("\n" * 2)

            win.addstr(f"Tags (non-exclusive):\n")
            win.addstr(f"{left_spacing*2}[P]orn: {self.sign_from_bool(is_porn)} \n")
            win.addstr(
                f"{left_spacing*2}[O]ffensive: {self.sign_from_bool(is_offensive)}"
            )
            win.addstr("\n" * 2)

            win.addstr(f"Category (exclusive):\n")
            win.addstr(
                f"{left_spacing*2}[N]ot language | [W]rong language | [C]orrect language | [S]kip \n"
            )
            win.addstr(f"{left_spacing*2}[U]ndo")
            win.addstr("\n" * 2)

            win.addstr(f"Processed: {self.n_items_processed} 🎉")
            win.addstr("\n" * 2)

            key = win.getkey()

            if key in cat_dict:
                self.process_example(
                    category=cat_dict[key],
                    example_str=example_str,
                    is_porn=is_porn,
                    is_offensive=is_offensive,
                )
                return

            if key == "p":
                is_porn = not is_porn
            elif key == "o":
                is_offensive = not is_offensive
            elif key == "u":
                self.undo_one_item(
                    current_item_str=example_str,
                    is_porn=is_porn,
                    is_offensive=is_offensive,
                )

                return

    def undo_one_item(self, current_item_str, is_porn, is_offensive):
        self.items_to_process.append(
            {
                "example_str": current_item_str,
                "is_porn": is_porn,
                "is_offensive": is_offensive,
            }
        )

        # Remove the line from the .csv
        with open(self.output_path, "r") as f:
            lines = f.readlines()
            lines_to_write = lines[:-1]
            with open(self.output_path, "w") as f:
                str = "\n".join(lines_to_write)
                f.write(str)

        prev_item = self.processed_items.pop()

        self.n_items_processed -= 1

        self.rate_str(
            example_str=prev_item["example_str"],
            is_porn=prev_item["is_porn"],
            is_offensive=prev_item["is_offensive"],
        )

    def process_example(self, category, is_porn, is_offensive, example_str):
        self.processed_items.append(
            {
                "example_str": example_str,
                "is_porn": is_porn,
                "is_offensive": is_offensive,
            }
        )

        self.write_example_to_csv(
            category=category,
            is_porn=is_porn,
            is_offensive=is_offensive,
            example_str=example_str,
        )

        self.n_items_processed += 1

    def write_example_to_csv(self, category, is_porn, is_offensive, example_str):
        # Create file and add header if it doesn't
        if not os.path.exists(self.output_path):
            with open(self.output_path, "w") as f:
                f.write("category,is_porn,is_offensive,text\n")

        with open(self.output_path, "a") as f:
            row = ""

            for var in [category, is_porn, is_offensive, example_str]:
                row += f"{var},"

            f.write(f"{row}\n")

    @staticmethod
    def sign_from_bool(boolean):
        if boolean:
            return "✓"
        else:
            return "False"
