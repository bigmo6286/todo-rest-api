# =============================================================================
# app/models.py  -  THE DATABASE MODEL (ORM layer)
# -----------------------------------------------------------------------------
# A "model" is a Python class that mirrors a database TABLE:
#   * the class          -> the table
#   * each db.Column     -> a column
#   * each object/instance -> a single row
# SQLAlchemy (the ORM) translates between these Python objects and SQL, so we
# never write raw SQL by hand for normal CRUD work.
# =============================================================================

from datetime import datetime

from .extensions import db    # the shared SQLAlchemy instance from extensions.py


class Todo(db.Model):
    # The exact table name in MySQL. Without this, SQLAlchemy would guess one.
    __tablename__ = "todos"

    # --- Columns -------------------------------------------------------------
    # Primary key: a unique id MySQL auto-increments for every new row.
    id = db.Column(db.Integer, primary_key=True)

    # The task text. Required (nullable=False) and capped at 200 characters.
    title = db.Column(db.String(200), nullable=False)

    # Optional longer notes. Text = unlimited length; nullable so it can be empty.
    description = db.Column(db.Text, nullable=True)

    # Done / not done. Boolean with a default so new todos start as "not done".
    # default applies in Python; server_default writes the default in MySQL too.
    completed = db.Column(db.Boolean, nullable=False, default=False,
                          server_default=db.text("0"))

    # When the row was created. Set automatically to "now" the moment we insert.
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        """Convert this row into a plain dict so jsonify() can return it as JSON.

        jsonify cannot serialize a Todo object or a datetime directly, so we
        hand-build the dict and turn created_at into an ISO-8601 string.
        """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        # A readable label shown when debugging/printing a Todo object.
        return f"<Todo {self.id} {self.title!r} completed={self.completed}>"
