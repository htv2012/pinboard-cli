import itertools
import logging
import os
import shutil

logging.basicConfig(level=os.getenv("LOGLEVEL", "WARNING"))


def rows_split(li: list[str], count: int) -> list[list[str]]:
    rows = [[] for _ in range(count)]
    for element, row_index in zip(li, itertools.cycle(range(count))):
        rows[row_index].append(element)
    return rows


def columnize(elements: list[str], total_width: int = None):
    total_width = total_width or shutil.get_terminal_size().columns - 1
    max_width = max(len(e) for e in elements) + 2

    columns_count = total_width // max_width
    logging.debug("columns_count=%r", columns_count)

    for row in rows_split(elements, columns_count):
        logging.debug("row=%r", row)
        for cell in row:
            print(cell.ljust(max_width), end="")
        print()
