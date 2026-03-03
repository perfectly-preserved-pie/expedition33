from sqlite3 import Connection, connect
from pathlib import Path
from typing import Optional

def load_sqlite_database(db_path: Optional[Path] = None) -> Connection:
    """Open the bundled Xenosaga SQLite database.

    Args:
        db_path: An optional path override for the SQLite database file. When
            omitted, the bundled ``xenosaga.db`` next to this module is used.

    Returns:
        An open SQLite connection to the requested database file.

    Raises:
        FileNotFoundError: If the resolved database path does not exist.
    """

    if db_path is None:
        db_path = Path(__file__).parent / "xenosaga.db"

    if not db_path.exists():
        raise FileNotFoundError(f"Database file not found at {db_path}")

    connection = connect(db_path)
    return connection
