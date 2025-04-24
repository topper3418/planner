from typing import List

from ..db import Annotation
from ..util import format_paragraph

def strf_curiosity(curiosity: Annotation) -> str:
    pretty_text = f"{curiosity.note.timestamp}\n{format_paragraph(curiosity.note.note_text, indents=0)}\n{format_paragraph(curiosity.annotation_text)}"
    return pretty_text


def strf_curiosities(curiosities: List[Annotation]) -> str:
    """
    Pretty prints an observation like: 

    2023-04-12
    original-note
        observation-text
    """
    if not curiosities:
        return "No curiosities found"
    curiosities.reverse()
    pretty_curiosities = ""
    for curiosity in curiosities:
        pretty_text = strf_curiosity(curiosity)
        pretty_curiosities += pretty_text + "-" * 75 + "\n"
    return pretty_curiosities


def json_curiosity(curiosity: Annotation) -> dict:
    """
    Converts an curiosity to a json object
    """
    output_json = {}
    output_json['annotation'] = curiosity.model_dump()
    # find the related objects
    note = curiosity.note
    # attach the related objects to the json
    output_json["note"] = note.model_dump() if note else None
    return output_json
