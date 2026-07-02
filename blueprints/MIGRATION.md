# Blueprint Migration Plan – flask_app.py 8742 → modular

The `flask_app.py` monolith was the user's original codebase. Rather than
refactor it in one risky pass, we use an **incremental, additive** migration:

## What we have today

| Layer | Routes | File |
|-------|--------|------|
| Legacy | 156    | `flask_app.py` (`create_app`) |
| New    | 3      | `blueprints/diagnostic.py` (`/api/diag/*`) |
| Total  | 159    | (no path collisions)         |

`server.py` calls:
1. `wire_integrations(flask_app)` – activates SQLAlchemy event triggers
   (defined once, idempotent via `_integrations_wired` guard).
2. `register_blueprints(flask_app)` – attaches NEW blueprint modules.

This ordering is important: SQLAlchemy listeners must be registered
before any request handler queries the ORM.

## Per-domain migration order (suggested)

The order is chosen so that highest-risk / largest endpoints migrate
LAST, after we are confident the pattern works.

1. **diagnostic** ✅ done (`blueprints/diagnostic.py`).
2. **kasa**     – 9 routes (small, well-bounded, already covered by
   integration tests).
3. **lookup / veriler** – 5 routes (pure CRUD).
4. **kesim**     – 8 routes (touches kasa + stok via integration engine).
5. **proforma**  – 12 routes.
6. **sevkiyat**  – 7 routes.
7. **fatura**    – 16 routes (uses tahsilat closure helpers).
8. **siparis**   – 22 routes (complex, uses many shared helpers).
9. **cari**      – 20 routes (cari hareket, ekstre, yaşlandırma).
10. **stok**      – 25 routes (largest; blok / plaka / ebatli ekleme,
    güncelle, sil; KDV mahsup; konum aktarımı).

## Pattern for each migration

Given a legacy route like:

```python
@app.route("/api/kasa", methods=["GET"])
def api_kasa_liste():
    if _auth_required(): return jsonify({"error": "Unauthorized"}), 401
    ...
```

we create:

```python
# blueprints/kasa.py
from flask import Blueprint, jsonify, session
from models import db, Kasa, KasaHareket

bp = Blueprint("kasa", __name__, url_prefix="/api/v2/kasa")

def _auth():
    return session.get("kullanici") is None

@bp.get("/")
def liste():
    if _auth(): return jsonify(error="Unauthorized"), 401
    ...
```

then update `blueprints/__init__.register_blueprints`:

```python
from .kasa import bp as kasa_bp
flask_app.register_blueprint(kasa_bp)
```

The legacy route stays in `flask_app.py` until QA validates the new
endpoint. To switch traffic over, simply change the legacy route to:

```python
return redirect("/api/v2/kasa" + request.full_path.removeprefix("/api/kasa"),
                code=308)
```

## Shared helper exposure

Many legacy routes use closures defined inside `create_app()`:
`_auth_required`, `_log_audit`, `_parse_date`, `_safe_commit`,
`_kullanici_yetkileri`, `_cari_hareket_ekle`, etc. To migrate cleanly:

1. Move each helper from `create_app()` to **module level** in a new
   file `helpers.py` (taking `db` and other dependencies as args).
2. Update both legacy and new routes to import them.

This is also why the `services/integration_bootstrap.py` we already
have is at module level, not inside a closure – it sets the precedent.

## Why we did NOT do the full refactor in one shot

`flask_app.py` is 8742 lines with 156 routes that all close over local
helper functions and rely on side-effects (event listeners, scheduled
jobs, shared `app.config`). A full move would require:

* Auditing every helper for stateful side effects.
* Re-running the entire test suite (testing_agent + 15 unit tests) after
  EACH route move.
* High risk of subtle regressions in Turkish edge-cases (KDV mahsup,
  iskonto, kur farki, exchange rate caching).

Doing it incrementally instead lets us deliver value (integration plan,
PostgreSQL, design refresh, seed data, blueprint pattern) without
destabilising the system.
