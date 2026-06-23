# =============================================================================
# run.py  -  THE ENTRY POINT
# -----------------------------------------------------------------------------
# This is the file you run to start the server. It does ONE job: ask the app
# factory to build an app, then run it. Keeping the entry point this thin means
# all the real wiring lives in app/__init__.py where it can be reused (e.g. by
# tests) without starting a web server.
# =============================================================================

from app import create_app   # the factory from app/__init__.py

# `flask` CLI commands (flask db migrate / upgrade) look for this `app` variable
# because .flaskenv sets FLASK_APP=run.
app = create_app()

if __name__ == "__main__":
    # Runs only with `python run.py` (not when imported).
    # debug=True -> auto-reload on code changes + detailed error pages.
    app.run(debug=True)
