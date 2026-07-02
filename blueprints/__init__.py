"""
Milestone ERP - Blueprint package.

This is the scaffolding for the long-term migration of the 8700-line
``flask_app.py`` monolith into per-domain Flask blueprints.

Current state (Jun 2026):
    • flask_app.py still owns 155 routes inside ``create_app()``.
    • This package adds NEW routes via blueprints registered from
      ``flask_app.create_app`` AFTER the legacy routes load. They live
      under the namespace ``/api/diag/*`` and ``/api/v2/*`` to avoid
      colliding with the legacy endpoints.

How to add a new blueprint:

    1. Create ``blueprints/<domain>.py``:
       .. code-block:: python

           from flask import Blueprint, jsonify, request, session
           bp = Blueprint("<domain>", __name__, url_prefix="/api/v2/<domain>")

           @bp.get("/")
           def liste():
               if session.get("kullanici") is None:
                   return jsonify(error="Unauthorized"), 401
               ...

    2. Register inside ``register_blueprints(app)`` below.

    3. (Optional) Once the legacy route in flask_app.py is stable, replace
       it with a 308 redirect to the v2 endpoint:
       ``return redirect("/api/v2/<domain>" + request.full_path, code=308)``

Helpers exposed for blueprints (importable from flask_app at request time):
    • ``g.db``        - the global SQLAlchemy instance
    • ``session``     - Flask session (yetki bilgisi)
"""
from __future__ import annotations

from flask import Flask


def register_blueprints(flask_app: Flask) -> None:
    """Register all blueprint modules onto the running Flask app.

    Called from ``integration_bootstrap.wire_integrations`` AFTER all
    legacy routes from ``create_app`` are loaded, so blueprint paths
    never accidentally shadow them.
    """
    # Idempotency guard (uvicorn reload safety).
    if getattr(flask_app, "_blueprints_registered", False):
        return
    flask_app._blueprints_registered = True

    from .diagnostic import bp as diagnostic_bp
    flask_app.register_blueprint(diagnostic_bp)
