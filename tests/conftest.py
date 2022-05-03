import os
from dataclasses import dataclass

import pytest
from anki.decks import DeckId

from tests.tools.collection import (
    CardDescription,
    get_decks,
    create_model,
    create_deck,
    add_note,
)

from tests.tools.testing import (
    add_addon_to_copy_into_anki_addons_folder,
    reset_addon_configuration,
    close_all_dialogs_and_wait_for_them_to_run_closing_callbacks
)

# used fixtures and pytest hooks
# noinspection PyUnresolvedReferences
from tests.tools.testing import (
    pytest_addoption,
    pytest_report_header,
    session_scope_empty_session,
    session_scope_session_with_profile_loaded,
    session_with_profile_loaded,
)


addon_name = "anki_wallpaper"
addon_folder = os.path.join(os.path.split(__file__)[0], f"../{addon_name}")

add_addon_to_copy_into_anki_addons_folder(addon_name, addon_folder)


@dataclass
class Setup:
    anki_wallpaper: ...


def set_up_test_deck_and_test_model_and_one_note():
    deck_id = create_deck("test_deck")

    create_model(
        model_name="test_model",
        field_names=["field1", "field2"],
        card_descriptions=[CardDescription(name="card1", front="{{field1}}", back="{{field2}}")],
        css="red {color: red; background-color: red;}"
    )

    add_note(
        model_name="test_model",
        deck_name="test_deck",
        fields={"field1": "<red>note1 field1</red>", "field2": "note1 field2"},
        tags=["tag1"],
    )

    get_decks().set_current(DeckId(deck_id))

    reset_addon_configuration(addon_name)
    import anki_wallpaper
    anki_wallpaper.config.load()

    return Setup(anki_wallpaper=anki_wallpaper)


@pytest.fixture
def setup(session_with_profile_loaded):
    yield set_up_test_deck_and_test_model_and_one_note()
    close_all_dialogs_and_wait_for_them_to_run_closing_callbacks()
