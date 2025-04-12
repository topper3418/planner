


from src import db


def unprocess_note(note: db.Note):
# get the note's annotation
    annotation = db.Annotation.get_by_note_id(note.id)
    if not annotation:
        raise ValueError(f"Annotation with ID {note.id} not found")
# if a todo or action were created, they need to be deleted. 
    if annotation.category.name == "todo":
        todo = db.Todo.get_by_id(note.id)
        if todo:
            todo.delete()
    if annotation.category.name == "action":
        action = db.Action.get_by_id(note.id)
        if action:
            action.delete()
    # remove the annotation
    annotation.delete()



