from typing import Sequence, List

from aqt import mw, gui_hooks
from aqt.browser import Column
from aqt.browser import ItemId, CellRow
from anki.collection import BrowserColumns
from anki.utils import pointVersion


config = mw.addonManager.getConfig(__name__)

SEPARATOR = config["Separator"]
HIERARCHY_SEPARATOR = config["Hierarchy separator"]
HIERARCHY_LEVELS_TO_SHOW = config["Number of hierarchy levels to show"]
ALIGNMENT = config["Alignment"]
COLUMN_NAME = config["Column name"]


COLUMN_KEY = "abbreviatedTag"   # camelCase used for column keys - see browser.py
COLUMN_LABEL = COLUMN_NAME


def add_column(columns: dict[str, Column]) -> None:

    # Set alignment.
    if ALIGNMENT == "Center":
        alignment = BrowserColumns.ALIGNMENT_CENTER
    else:
        alignment = BrowserColumns.ALIGNMENT_START

    if pointVersion() >= 231000:
        columns[COLUMN_KEY] = Column(
            key=COLUMN_KEY,
            cards_mode_label=COLUMN_LABEL,
            notes_mode_label=COLUMN_LABEL,
            sorting_notes=BrowserColumns.SORTING_NONE,
            sorting_cards=BrowserColumns.SORTING_NONE,
            uses_cell_font=False,
            alignment=alignment,
        )

    else:
        columns[COLUMN_KEY] = Column(
            key=COLUMN_KEY,
            cards_mode_label=COLUMN_LABEL,
            notes_mode_label=COLUMN_LABEL,
            sorting=BrowserColumns.SORTING_NONE,
            uses_cell_font=False,
            alignment=alignment,
        )


def fill_rows(item_id: ItemId, is_note: bool, row: CellRow, columns: Sequence[str]) -> None:
    try:
        idx = columns.index(COLUMN_KEY)
    except ValueError:
        # Column may not be presently displayed.
        return

    if is_note:
        nid = item_id
    else:
        nid = mw.col.db.scalar(
            "select nid from cards where id = ?", item_id
        )
    # Tags for each card are stored as a single string of individual tags separated by spaces.
    tag = mw.col.db.scalar("select tags from notes where id = ?", nid)
    text_list = []
    construct_text_list(text_list, tag)
    text = SEPARATOR.join(text_list)
    row.cells[idx].text = text.strip(SEPARATOR)


def construct_text_list(text_list: List[str], full_tag: str) -> None:
    tag_list = full_tag.split(" ")
    for tag in tag_list:
        tag_parts = tag.split("::")
        if HIERARCHY_LEVELS_TO_SHOW > len(tag_parts):
            text_list.append(tag)
            continue
        else:
            num_to_remove = abs(len(tag_parts) - HIERARCHY_LEVELS_TO_SHOW)
            for i in range(num_to_remove-1, -1, -1):
                del tag_parts[i]
            if len(tag_parts) == 1:
                text_list.append(tag_parts[0])
            else:
                text_list.append(HIERARCHY_SEPARATOR.join(tag_parts))


# Hooks
def setup_hooks() -> None:
    gui_hooks.browser_did_fetch_columns.append(add_column)
    gui_hooks.browser_did_fetch_row.append(fill_rows)


setup_hooks()
