# =============================================================================
# check_table.py  -  tiny helper for the demo
# -----------------------------------------------------------------------------
# Prints whether the `todos` table currently exists in the database.
# Use it during the defense to show the table appear after `flask db upgrade`.
#
# Run it with:   python check_table.py
# (Avoids fragile python -c "..." one-liners that PowerShell mis-quotes.)
# =============================================================================

from app import create_app
from app.extensions import db

app = create_app()
with app.app_context():
    rows = db.session.execute(db.text("SHOW TABLES LIKE 'todos'")).fetchall()
    if rows:
        print("todos table EXISTS")
    else:
        print("todos table does NOT exist  ->  run:  flask db upgrade")
