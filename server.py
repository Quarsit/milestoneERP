"""
Milestone ERP - FastAPI WSGI bridge.

Mounts the Flask application (flask_app.py) under FastAPI so that both
the existing /api/* JSON endpoints and the Jinja2 HTML page routes
(/giris, /dashboard, /stok, ...) are all served on port 8001.

The kubernetes ingress sends /api/* to port 8001 directly (works).
The frontend container on port 3000 is a thin reverse-proxy that
forwards every non-/api request back to this FastAPI process so page
routes work too.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

# Make sure PostgreSQL is reachable before Flask tries to connect.
from a2wsgi import WSGIMiddleware  # noqa: E402
from fastapi import FastAPI  # noqa: E402
from fastapi.responses import RedirectResponse  # noqa: E402

from flask_app import app as flask_app  # noqa: E402
from blueprints import register_blueprints  # noqa: E402

# NOT: wire_integrations() DEVRE DIŞI bırakıldı.
# flask_app.py artık tüm cross-module entegrasyonu (Cari/Stok/Sipariş/Fatura/
# Kasa/Sevkiyat/Kesim) kendi içinde yapıyor. integration_bootstrap paralel/eski
# bir katmandı ve aynı kayıtları İKİNCİ kez oluşturarak mükerrer cari hareketi +
# maliyet kaydına yol açıyordu. Bu yüzden kapatıldı.
# from integration_bootstrap import wire_integrations
# wire_integrations(flask_app)

# Register new blueprint-based endpoints (/api/diag/*, /api/v2/*).
register_blueprints(flask_app)

app = FastAPI(title="Milestone ERP", docs_url=None, redoc_url=None)


@app.get("/")
def _root():
    # Friendly redirect to the login page served by Flask.
    return RedirectResponse(url="/giris", status_code=302)


# Mount the entire Flask app at root - it already owns /api/* and page routes.
app.mount("/", WSGIMiddleware(flask_app.wsgi_app))
