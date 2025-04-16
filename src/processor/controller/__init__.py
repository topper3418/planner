from datetime import datetime
from src import db, config

from .note_buffer import NoteProcessBuffer
from .unprocess_note import unprocess_note


def route_command(command: db.Command):
    """
    Routes the command to the appropriate function based on its type.
    """

    if command.command_text == "update_note_text":
        # update the note text
        note = db.Note.get_by_id(command.target_id)
        if not note:
            raise ValueError(f"Note with ID {command.target_id} not found")
        note.note_text = command.desired_value
        note.save()
        unprocess_note(note)
        buffer = NoteProcessBuffer(note)
    if command.command_text == "update_note_category":
        # update the note category
        note = db.Note.get_by_id(command.target_id)
        if not note:
            raise ValueError(f"Note with ID {command.target_id} not found")
        buffer = NoteProcessBuffer(note)
        category = db.Category.find_by_name(command.desired_value)
        if not category:
            raise ValueError(f"Category with name {command.desired_value} not found")
        buffer.category = category
        # get the annotation
        annotation = db.Annotation.get_by_note_id(command.target_id)
        if not annotation:
            raise ValueError(f"Annotation with ID {command.source_annotation_id} not found")
        # remove objects that might have been created, depending on the category
        if annotation.category.name == "command":
            # commands cannot be undone
            raise ValueError("Commands cannot be undone")
        if annotation.category.name == "todo":
            # delete the todo
            todo = db.Todo.get_by_id(note.id)
            if todo:
                todo.delete()
        if annotation.category.name == "action":
            # delete the action
            action = db.Action.get_by_id(note.id)
            if action:
                action.delete()
        # update the category
        annotation.category = category
        annotation.reprocess = True
        annotation.save()
        buffer.annotation = annotation
    elif "todo" in command.command_text:
        todo = db.Todo.get_by_id(command.target_id)
        if not todo:
            raise ValueError(f"Todo with ID {command.target_id} not found")
        if command.command_text == "update_todo_text":
            # update the todo
            todo.todo_text = command.desired_value
            todo.save()
        if command.command_text == "update_todo_start_time":
            # update the todo start time
            todo.target_start_time= datetime.strptime(command.desired_value, config.TIMESTAMP_FORMAT)
            todo.save()
        if command.command_text == "update_todo_end_time":
            # update the todo end time
            todo.target_end_time = datetime.strptime(command.desired_value, config.TIMESTAMP_FORMAT)
            todo.save()
        if command.command_text == "cancel_todo":
            # cancel the todo
            todo.cancelled = True
            todo.save()
    elif "action" in command.command_text:
        action = db.Action.get_by_id(command.target_id)
        if not action:
            raise ValueError(f"Action with ID {command.target_id} not found")
        if command.command_text == "update_action_text":
            # update the action
            action.action_text = command.desired_value
            action.save()
        if command.command_text == "update_action_start_time":
            # update the action start time
            action.start_time = datetime.strptime(command.desired_value, config.TIMESTAMP_FORMAT)
            action.save()
    else:
        raise ValueError(f"Unknown command: {command.command_text}")
