# =============================================================================
# app/routes.py  -  THE API ROUTES (controller layer)
# -----------------------------------------------------------------------------
# This file maps each URL + HTTP method to a Python function and implements the
# full CRUD cycle for a Todo:
#
#   CREATE  ->  POST   /api/todos
#   READ    ->  GET    /api/todos          (all)
#               GET    /api/todos/<id>     (one)
#   UPDATE  ->  PUT    /api/todos/<id>     (replace every field)
#               PATCH  /api/todos/<id>     (change only the fields sent)
#   DELETE  ->  DELETE /api/todos/<id>
#
# Routes live on a BLUEPRINT (a reusable group of routes) instead of directly on
# `app`. The app factory registers the blueprint, which keeps app setup and
# route logic in separate files.
# =============================================================================

from flask import Blueprint, request, jsonify

from .extensions import db
from .models import Todo

# All routes here share the /api/todos prefix, set once on the blueprint.
todos_bp = Blueprint("todos", __name__, url_prefix="/api/todos")


# Quick HTTP status-code reference used below:
#   200 OK            request succeeded
#   201 Created       a new record was created
#   400 Bad Request   the client sent invalid/missing data
#   404 Not Found     the requested record does not exist


def _validate_payload(data, *, require_title):
    """Check an incoming JSON body and return an error string, or None if valid.

    Centralising validation here means CREATE and UPDATE share the SAME rules
    instead of duplicating checks. `require_title` is True for POST/PUT (where a
    title must be present) and False for PATCH (where every field is optional).
    """
    if "title" in data:
        # If title is supplied, it must be a non-empty string.
        if not isinstance(data["title"], str) or not data["title"].strip():
            return "title must be a non-empty string"
    elif require_title:
        # POST/PUT must include a title.
        return "title is required"

    if "description" in data and data["description"] is not None:
        if not isinstance(data["description"], str):
            return "description must be a string"

    if "completed" in data and not isinstance(data["completed"], bool):
        return "completed must be true or false"

    return None   # no problems found


# --- CREATE ------------------------------------------------------------------
@todos_bp.route("", methods=["POST"])
def create_todo():
    """Create a new todo from a JSON body: {"title": "...", "description": "..."}"""
    # silent=True -> return None (not crash) if the body is missing/not JSON;
    # `or {}` then gives a safe empty dict to read from.
    data = request.get_json(silent=True) or {}

    error = _validate_payload(data, require_title=True)
    if error:
        return jsonify({"error": error}), 400

    todo = Todo(
        title=data["title"].strip(),
        description=(data.get("description") or None),
        completed=data.get("completed", False),
    )
    db.session.add(todo)     # stage the new row
    db.session.commit()      # write to MySQL; todo.id is filled in afterwards
    # 201 Created + the new record so the client learns its generated id.
    return jsonify(todo.to_dict()), 201


# --- READ (all) --------------------------------------------------------------
@todos_bp.route("", methods=["GET"])
def list_todos():
    """Return every todo, newest first."""
    todos = Todo.query.order_by(Todo.created_at.desc()).all()
    return jsonify([t.to_dict() for t in todos])


# --- READ (one) --------------------------------------------------------------
@todos_bp.route("/<int:todo_id>", methods=["GET"])
def get_todo(todo_id):
    """Return a single todo by id, or 404 if it doesn't exist."""
    todo = db.session.get(Todo, todo_id)     # look up by primary key
    if todo is None:
        return jsonify({"error": "Todo not found"}), 404
    return jsonify(todo.to_dict())


# --- UPDATE (full replace) ---------------------------------------------------
@todos_bp.route("/<int:todo_id>", methods=["PUT"])
def replace_todo(todo_id):
    """Replace ALL editable fields of a todo. Title is required (full replace)."""
    todo = db.session.get(Todo, todo_id)
    if todo is None:
        return jsonify({"error": "Todo not found"}), 404

    data = request.get_json(silent=True) or {}
    error = _validate_payload(data, require_title=True)
    if error:
        return jsonify({"error": error}), 400

    # Overwrite every field; missing optional fields reset to their defaults.
    todo.title = data["title"].strip()
    todo.description = data.get("description") or None
    todo.completed = data.get("completed", False)
    db.session.commit()      # SQLAlchemy detects the changes and saves them
    return jsonify(todo.to_dict())


# --- UPDATE (partial) --------------------------------------------------------
@todos_bp.route("/<int:todo_id>", methods=["PATCH"])
def update_todo(todo_id):
    """Change only the fields that are sent (e.g. just flip `completed`)."""
    todo = db.session.get(Todo, todo_id)
    if todo is None:
        return jsonify({"error": "Todo not found"}), 404

    data = request.get_json(silent=True) or {}
    error = _validate_payload(data, require_title=False)
    if error:
        return jsonify({"error": error}), 400

    # Update each field ONLY if the client included it in the body.
    if "title" in data:
        todo.title = data["title"].strip()
    if "description" in data:
        todo.description = data["description"] or None
    if "completed" in data:
        todo.completed = data["completed"]
    db.session.commit()
    return jsonify(todo.to_dict())


# --- DELETE ------------------------------------------------------------------
@todos_bp.route("/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    """Delete a todo by id, or 404 if it doesn't exist."""
    todo = db.session.get(Todo, todo_id)
    if todo is None:
        return jsonify({"error": "Todo not found"}), 404
    db.session.delete(todo)  # stage the deletion
    db.session.commit()      # apply it
    return jsonify({"message": f"Todo {todo_id} deleted"})
