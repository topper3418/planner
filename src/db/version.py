import os
import sqlite3
from typing import Optional
from pydantic import BaseModel, Field


from ..logging import get_logger
from ..errors import MigrationError

from .connection import get_connection

logger = get_logger(__name__)


class Version(BaseModel):
    """
    Represents a version of the application.
    """

    db_version: str = Field(..., description="Current version number")
    commit_hash: Optional[str] = Field(
        None, description="Git commit hash from when the db was created"
    )
    branch: Optional[str] = Field(
        None, description="Git branch name from when the db was created"
    )

    @classmethod
    def init(
        cls,
        db_version: str,
        commit_hash: Optional[str] = None,
        branch: Optional[str] = None,
    ) -> None:
        """
        Initializes the version information in the database.
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            # create the version table if it doesn't exist
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS version (db_version TEXT, commit_hash TEXT, branch TEXT)"
            )
            # check if the version table is empty
            cursor.execute("SELECT COUNT(*) FROM version")
            count = cursor.fetchone()[0]
            if count > 0:
                logger.info(
                    "Version table already contains data. Skipping insertion."
                )
                return
            cursor.execute(
                "INSERT INTO version (db_version, commit_hash, branch) VALUES (?, ?, ?)",
                (db_version, commit_hash, branch),
            )
            conn.commit()

    @classmethod
    def get(cls) -> "Version":
        """
        Retrieves the current version of the application from the database.
        """
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT db_version, commit_hash, branch FROM version"
                )
                row = cursor.fetchone()
            if row:
                return cls(
                    db_version=row[0], commit_hash=row[1], branch=row[2]
                )
            else:
                raise ValueError(
                    "Version information not found in the database."
                )
        except sqlite3.OperationalError as e:
            raise ValueError(
                "Version table does not exist. Please migrate to a newer version."
            ) from e

    @classmethod
    def migrate(cls, new_db_version: str) -> None:
        """
        Migrates the version information in the database to a new version.
        """
        # ensure the new version exists in the migrations folder
        try:
            current_db_version = cls.get().db_version
        except ValueError:
            logger.warning(
                "Version not found in the database, treating as 0.0.0"
            )
            current_db_version = "0.0.0"
        if current_db_version == new_db_version:
            logger.info(
                f"Version {new_db_version} is already set in the database."
            )
            return
        curr_str = current_db_version.replace(".", "_")
        new_str = new_db_version.replace(".", "_")
        migration_filepath = os.path.join(
            "src", "db", "migrations", f"{curr_str}-{new_str}.sql"
        )
        if not os.path.exists(migration_filepath):
            raise FileNotFoundError(
                f"Migration file {migration_filepath} does not exist."
            )
        # load the migration file
        with open(migration_filepath, "r") as file:
            migration_sql = file.read()
        # Split the migration SQL on blank lines
        statements = [
            stmt.strip()
            for stmt in migration_sql.split("\n\n")
            if stmt.strip()
        ]
        # execute the migration
        with get_connection() as conn:
            for statement in statements:
                try:
                    cursor = conn.cursor()
                    cursor.execute(statement)
                except sqlite3.OperationalError as e:
                    logger.error(
                        f"Migration failed: {e} for statement: {statement}"
                    )
                    # Rollback the transaction if an error occurs
                    conn.rollback()
                    raise MigrationError(
                        f"Migration failed: {e} for statement: {statement}"
                    ) from e
                except Exception as e:
                    logger.error(
                        f"Migration failed unexpectedly: {e} for statement: {statement}"
                    )
                    # Rollback the transaction if an error occurs
                    conn.rollback()
                    raise MigrationError(
                        f"Migration failed unexpectedly: {e} for statement: {statement}"
                    ) from e
