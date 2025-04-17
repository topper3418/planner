

def render():



if __name__ == "__main__":
    from src import db, pretty_printing

    # Get all notes
    notes = db.Note.get_all(limit=75)
    pretty_notes = pretty_printing.strf_notes(notes, show_processed_text=True)
    # clear the console
    print("\033[H\033[J")
    print("===================================")
    print("Notes:                            ||")
    print("===================================")
    print(pretty_notes)
