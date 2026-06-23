# =============================================================================
# app/extensions.py  -  SHARED EXTENSION INSTANCES
# -----------------------------------------------------------------------------
# Flask extensions are created here as "unbound" objects (no app attached yet)
# and later wired to the real app inside create_app() with .init_app(app).
#
# WHY a separate file?
#   * models.py needs `db`, and the app factory also needs `db`. If we created
#     `db` inside the factory, models could not import it without a circular
#     import. Defining the extensions in their own neutral module breaks that
#     cycle: everyone imports from here, and here imports from no one.
# =============================================================================

from flask_sqlalchemy import SQLAlchemy   # the ORM (Python objects <-> SQL rows)
from flask_migrate import Migrate         # schema migrations (wraps Alembic)

# The ORM database handle. Models subclass db.Model; queries go through db.session.
db = SQLAlchemy()

# Migrate compares the models against the real database and generates migration
# scripts so the schema can evolve safely. Workflow after changing a model:
#   flask db migrate -m "describe change"   # autogenerate the migration
#   flask db upgrade                         # apply it to the database
migrate = Migrate()
