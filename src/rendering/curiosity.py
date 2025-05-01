from typing import List

from ..db import Annotation, Curiosity
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


def json_curiosity(curiosity: Curiosity) -> dict:
    """
    Converts an curiosity to a json object
    """
    # extract props for cleanliness
    note = curiosity.source_note
    annotation = note.annotation
    # attach the related objects to the json
    output_json = {}
    output_json['curiosity'] = curiosity.model_dump()
    output_json['annotation'] = annotation.model_dump() if annotation else None
    output_json["note"] = note.model_dump() if note else None
    return output_json
