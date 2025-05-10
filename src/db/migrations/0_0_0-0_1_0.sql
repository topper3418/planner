PRAGMA foreign_keys=off;

-- Add 'processed' column to notes
ALTER TABLE notes ADD COLUMN processed INTEGER DEFAULT 0;

-- Recreate todos to add parent_id
CREATE TABLE todos_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    target_start_time DATETIME DEFAULT NULL,
    target_end_time DATETIME DEFAULT NULL,
    todo_text TEXT NOT NULL,
    source_note_id INTEGER NOT NULL,
    parent_id INTEGER DEFAULT NULL,
    complete INTEGER NOT NULL DEFAULT 0,
    cancelled INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (source_note_id) REFERENCES notes(id),
    FOREIGN KEY (parent_id) REFERENCES todos_new(id)
);

INSERT INTO todos_new (id, target_start_time, target_end_time, todo_text, source_note_id, complete, cancelled)
SELECT id, target_start_time, target_end_time, todo_text, source_note_id, complete, cancelled FROM todos;

DROP TABLE todos;

ALTER TABLE todos_new RENAME TO todos;

-- Rename start_time to timestamp in actions
ALTER TABLE actions RENAME COLUMN start_time TO timestamp;

-- Recreate actions with source_note_id instead of source_annotation_id
CREATE TABLE actions_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    action_text TEXT NOT NULL,
    source_note_id INTEGER NOT NULL,
    todo_id INTEGER DEFAULT NULL,
    mark_complete INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (source_note_id) REFERENCES notes(id),
    FOREIGN KEY (todo_id) REFERENCES todos(id)
);

INSERT INTO actions_new (id, timestamp, action_text, source_note_id, todo_id, mark_complete)
SELECT a.id, a.timestamp, a.action_text, ann.note_id, a.todo_id, a.mark_complete
FROM actions a
JOIN annotations ann ON a.source_annotation_id = ann.id;

DROP TABLE actions;

ALTER TABLE actions_new RENAME TO actions;

-- Create new tables
CREATE TABLE tool_calls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_note_id INTEGER NOT NULL,
    target_table TEXT NOT NULL,
    target_id INTEGER NOT NULL,
    target TEXT,
    tool_call TEXT NOT NULL,
    FOREIGN KEY (source_note_id) REFERENCES notes(id)
);

CREATE TABLE curiosities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    curiosity_text TEXT NOT NULL,
    source_note_id INTEGER NOT NULL,
    FOREIGN KEY (source_note_id) REFERENCES notes(id)
);

CREATE TABLE version (
    db_version TEXT,
    commit_hash TEXT,
    branch TEXT
);

-- Drop categories table
DROP TABLE categories;

-- Drop commands table
DROP TABLE commands;

-- Drop annotations table
DROP TABLE annotations;

PRAGMA foreign_keys=on;

-- Check for foreign key violations
PRAGMA foreign_key_check;
