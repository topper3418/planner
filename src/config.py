import os


NOTES_DB_FILENAME = os.environ.get("PLANNER_NOTES_DB_FILENAME", "notes.db")
NOTES_DATABASE_FILEPATH = os.path.join("data", NOTES_DB_FILENAME)
SERVER_PORT = int(os.environ.get("PLANNER_REST_SERVER_PORT", 9000))
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
CHAT_SERVICE = os.environ.get("PLANNER_CHAT_SERVICE", "grok")
