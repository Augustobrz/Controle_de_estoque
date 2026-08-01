"""Basic tests to ensure models and DB initialization work."""
from __future__ import annotations

from database.engine import init_db
from models.base import Base


def test_init_db_creates_tables(tmp_path):
    # This test simply runs init_db to validate no exceptions are raised while creating tables
    init_db(Base)
    assert True
