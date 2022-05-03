from dataclasses import dataclass
from typing import Sequence

import aqt
from anki.collection import Collection
from anki.decks import DeckManager
from anki.models import ModelManager
from anki.notes import Note
from aqt.main import MainWindowState


anki_version = tuple(int(segment) for segment in aqt.appVersion.split("."))


def get_collection() -> Collection:
    return aqt.mw.col

def get_models() -> ModelManager:
    return get_collection().models

def get_decks() -> DeckManager:
    return get_collection().decks

def get_all_deck_ids() -> "list[int]":
    return [item.id for item in get_decks().all_names_and_ids()]

def get_all_model_ids() -> "list[int]":
    return [item.id for item in get_models().all_names_and_ids()]


def move_main_window_to_state(state: MainWindowState):
    aqt.mw.moveToState(state)


########################################################################### create stuff


@dataclass
class CardDescription:
    name: str
    front: str
    back: str


def create_model(
    model_name: str,
    field_names: Sequence[str],
    card_descriptions: Sequence[CardDescription],
    css: str = None,
) -> int:
    models = get_models()
    model = models.new(model_name)

    for field_name in field_names:
        field = models.new_field(field_name)
        models.add_field(model, field)

    for card_description in card_descriptions:
        template = models.new_template(card_description.name)
        template["qfmt"] = card_description.front
        template["afmt"] = card_description.back
        models.add_template(model, template)

    if css is not None:
        model["css"] = css

    return models.add(model).id


def create_deck(deck_name: str) -> int:
    return get_decks().id(deck_name)


def add_note(model_name: str, deck_name: str, fields: "dict[str, str]",
             tags: Sequence[str] = None) -> int:
    model_id = get_models().id_for_name(model_name)
    deck_id = get_decks().id_for_name(deck_name)
    note = Note(get_collection(), model_id)

    for field_name, field_value in fields.items():
        note[field_name] = field_value

    if tags is not None:
        note.tags = list(tags)

    get_collection().add_note(note, deck_id)
    return note.id
