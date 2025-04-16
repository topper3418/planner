import argparse
import time
from typing import List

from src import db, pretty_printing, engine


def add_date_filters(parser):
    """Add before and after date filter arguments to the given parser."""
    parser.add_argument('-b', '--before',
                        help='Show items before this timestamp (YYYY-MM-DD HH:MM:SS)')
    parser.add_argument('-a', '--after',
                        help='Show items after this timestamp (YYYY-MM-DD HH:MM:SS)')


# Main CLI application
def main():
    parser = argparse.ArgumentParser(description="Notes management application")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Write subparser
    write_parser = subparsers.add_parser('write', help='Write a new note')
    write_parser.add_argument('note_words', nargs='*',
                            help='Note as consecutive words')

    # Cycle subparser
    cycle_parser = subparsers.add_parser('cycle', help='cycles the engine once')
    cycle_parser.add_argument('-c', '--continuous', action='store_true', help='cycles in a loop until interrupted')
    cycle_parser.add_argument('-a', '--all', action='store_true', help='cycles all notes and reprocess annotations until all are processed')
    cycle_parser.add_argument('-i', '--iterations', type=int)

    # Read subparser with type-specific subcommands
    read_parser = subparsers.add_parser('read', help='Read notes with filters')
    read_subparsers = read_parser.add_subparsers(dest='type', help='Type of item to read')

    # Note subparser
    note_parser = read_subparsers.add_parser('note', help='Read notes')
    add_date_filters(note_parser)
    note_parser.add_argument('-s', '--search',
                            help='Search for notes containing this text')
    note_parser.add_argument('-l', '--limit', type=int, default=25,
                            help='Limit number of notes returned (default: 15)')

    # Todo subparser
    todo_parser = read_subparsers.add_parser('todo', help='Read todos')
    add_date_filters(todo_parser)
    todo_parser.add_argument('-s', '--search',
                            help='Search for todos containing this text')
    todo_parser.add_argument('-l', '--limit', type=int, default=25,
                            help='Limit number of todos returned (default: 15)')
    todo_status_group = todo_parser.add_mutually_exclusive_group()
    todo_status_group.add_argument('-i', '--incomplete-only', action='store_true',
                                  help='Show only incomplete todos')
    todo_status_group.add_argument('-c', '--complete-only', action='store_true',
                                  help='Show only complete todos')
    todo_parser.add_argument('-x', '--cancelled-only', action='store_true',)

    # Action subparser
    action_parser = read_subparsers.add_parser('action', help='Read actions')
    add_date_filters(action_parser)
    action_parser.add_argument('-s', '--search',
                              help='Search for actions containing this text')
    action_parser.add_argument('-l', '--limit', type=int, default=25,
                              help='Limit number of actions returned (default: 25)')

    # Observation subparser
    observation_parser = read_subparsers.add_parser('observation', help='Read observations')
    add_date_filters(observation_parser)
    observation_parser.add_argument('-s', '--search',
                                   help='Search for observations containing this text')
    observation_parser.add_argument('-l', '--limit', type=int, default=25,
                                   help='Limit number of observations returned (default: 25)')

    # Curiosity subparser
    curiosity_parser = read_subparsers.add_parser('curiosity', help='Read curiosities')
    add_date_filters(curiosity_parser)
    curiosity_parser.add_argument('-s', '--search',
                                 help='Search for curiosities containing this text')
    curiosity_parser.add_argument('-l', '--limit', type=int, default=25,
                                 help='Limit number of curiosities returned (default: 25)')

    args = parser.parse_args()

    if args.command == 'write':
        note = ' '.join(args.note_words)
        db.Note.create(note)  # Note: You might want to update this for other types
        print("noted")

    if args.command == 'cycle':
        # Call the cycle function from the engine module
        if args.continuous:
            try:
                while True:
                    engine.cycle()
                    time.sleep(5)
            except KeyboardInterrupt:
                print("Stopping the engine.")
        if args.all:
            return_value = True
            while return_value:
                return_value = engine.cycle()
        if args.iterations:
            for i in range(args.iterations):
                engine.cycle()
                print(f"Cycle {i + 1}/{args.iterations} completed")
        else:
            engine.cycle()
            print("Cycle completed")

    elif args.command == 'read':
        # Default to note if no type is specified
        if args.type == 'todo':
            if args.incomplete_only and args.complete_only:
                parser.error("Cannot use both --incomplete-only and --complete-only.")
            if args.incomplete_only:
                complete = False
            elif args.complete_only:
                complete = True
            else:
                complete = None
            if args.cancelled_only:
                complete = None
                cancelled = True
            else:
                cancelled = False
            notes = db.Todo.read(
                before=args.before,
                after=args.after,
                limit=args.limit,
                complete=complete,
                cancelled=cancelled,
            )
            pretty_todos = pretty_printing.strf_todos(notes)
            print(pretty_todos)
        elif args.type == 'action':
            actions = db.Action.read(
                before=args.before,
                after=args.after,
                search=args.search,
                limit=args.limit
            )
            actions.reverse()
            pretty_actions = pretty_printing.strf_actions(actions)
            print(pretty_actions)
        elif args.type == 'observation':
            annotations = db.Annotation.get_by_category_name('observation')
            if annotations is None:
                print("No observations found")
                return
            notes = [annotation.note for annotation in annotations]
            pretty_notes = pretty_printing.strf_notes(notes)
            print(pretty_notes)
        elif args.type == 'curiosity':
            annotations = db.Annotation.get_by_category_name(
                'curiosity',
                before=args.before,
                after=args.after,
                search=args.search,
                limit=args.limit
            )
            if annotations is None:
                print("No curiosities found")
                return
            pretty_curiosities = pretty_printing.strf_curiosities(annotations)
            print(pretty_curiosities)
        else:
            notes = db.Note.read(
                before=getattr(args, 'before', None),
                after=getattr(args, 'after', None),
                search=getattr(args, 'search', None),
                limit=getattr(args, 'limit', 15)
            )
            notes.reverse()
            pretty_notes = pretty_printing.strf_notes(notes, show_processed_text=True)
            print(pretty_notes)

if __name__ == "__main__":
    main()
