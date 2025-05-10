from src import db


if __name__ == "__main__":
    db.backup_db()
    db.migrate()
