import argparse
from typing import List

from src import db


def pretty_print_notes(notes: List[db.Note]):
    """Prints a timestamp, new line, whether or not its processed,
        new line, and then the note text, no wider than 75 columns,
        then a blank line between notes."""
    for note in notes:
        print(f"{note.timestamp}\nprocessed: {note.processed}")
        if len(note.note_text) > 75:
            print(note.note_text[:75])
            remainder = note.note_text[75:]
            while remainder:
                if len(remainder) > 75:
                    print(remainder[:75])
                    remainder = remainder[75:]
                else:
                    print(remainder)
                    remainder = ""
        else:
            print(note.note_text)
        print("-" * 75 )

# Main CLI application
def main():
    parser = argparse.ArgumentParser(description="Notes management application")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Write subparser
    write_parser = subparsers.add_parser('write', help='Write a new note')
    write_group = write_parser.add_mutually_exclusive_group(required=True)
    write_group.add_argument('note_words', nargs='*', 
                           help='Note as consecutive words')

    # Read subparser with new options
    read_parser = subparsers.add_parser('read', help='Read notes with filters')
    read_parser.add_argument('-b', '--before', 
                            help='Show notes before this timestamp (YYYY-MM-DD HH:MM:SS)')
    read_parser.add_argument('-a', '--after', 
                            help='Show notes after this timestamp (YYYY-MM-DD HH:MM:SS)')
    read_parser.add_argument('-s', '--search', 
                            help='Search for notes containing this text')
    read_parser.add_argument('-l', '--limit', type=int, default=15,
                            help='Limit number of notes returned (default: 15)')

    args = parser.parse_args()
    db.Note.ensure_table()

    if args.command == 'write':
        note = ' '.join(args.note_words)
        db.Note.create(note)
        print("noted")

    elif args.command == 'read':
        notes = db.Note.read(
            before=args.before,
            after=args.after,
            search=args.search,
            limit=args.limit
        )
        if len(notes) == 0:
            print("No notes found matching the criteria")
        else:
            pretty_print_notes(notes)

if __name__ == "__main__":
    main()
