"""
/api/diag/* - Diagnostic & integration introspection endpoints.

These endpoints help operators verify cross-module integration health
without poking into the database directly.  Read-only, JSON-only.
"""
from __future__ import annotations

from flask import Blueprint, jsonify, session
from sqlalchemy import func

from models import (
    db,
    Cari,
    CariHareket,
    Maliyet,
    Rezervasyon,
    Siparis,
    Sevkiyat,
    BlokStok,
    PlakaStok,
    EbatliStok,
    StokCikis,
    Fatura,
    KasaHareket,
    Kesim,
)


bp = Blueprint("diagnostic", __name__, url_prefix="/api/diag")


def _auth_required():
    return session.get("kullanici") is None


@bp.get("/health")
def health():
    """Lightweight health probe (no auth) - confirms the Flask app
    + the database are reachable.
    """
    try:
        db.session.execute(db.text("SELECT 1"))
        db_ok = True
    except Exception as e:  # pragma: no cover
        return jsonify(status="degraded", db=False, error=str(e)), 503
    return jsonify(status="ok", db=db_ok, app="milestone-erp")


@bp.get("/integration/summary")
def integration_summary():
    """One-shot snapshot of integration counters across modules.
    Used to verify the cross-module wiring is producing records.
    """
    if _auth_required():
        return jsonify(error="Unauthorized"), 401

    def _count(model):
        return db.session.query(func.count(model.id)).scalar() or 0

    by_kaynak = dict(
        db.session.query(CariHareket.kaynak, func.count(CariHareket.id))
        .group_by(CariHareket.kaynak)
        .all()
    )
    by_maliyet_tip = dict(
        db.session.query(Maliyet.maliyet_tip, func.count(Maliyet.id))
        .group_by(Maliyet.maliyet_tip)
        .all()
    )
    return jsonify(
        cariler=_count(Cari),
        cari_hareketleri=_count(CariHareket),
        cari_hareket_by_kaynak=by_kaynak,
        maliyetler=_count(Maliyet),
        maliyet_by_tip=by_maliyet_tip,
        stok={
            "blok": _count(BlokStok),
            "plaka": _count(PlakaStok),
            "ebatli": _count(EbatliStok),
        },
        siparisler=_count(Siparis),
        rezervasyonlar=_count(Rezervasyon),
        sevkiyatlar=_count(Sevkiyat),
        stok_cikislar=_count(StokCikis),
        faturalar=_count(Fatura),
        kasa_hareketleri=_count(KasaHareket),
        kesimler=_count(Kesim),
    )


@bp.get("/integration/trace/<string:baglanti_tip>/<string:baglanti_id>")
def integration_trace(baglanti_tip: str, baglanti_id: str):
    """Trace all downstream records auto-created by the integration engine
    for a given source (baglanti_tip, baglanti_id).

    Example:
        GET /api/diag/integration/trace/stok/PLK-DEMO01
        -> { cari_hareketleri: [...], maliyetler: [...] }
    """
    if _auth_required():
        return jsonify(error="Unauthorized"), 401

    ch_rows = (
        CariHareket.query.filter_by(
            baglanti_tip=baglanti_tip, baglanti_id=baglanti_id
        )
        .order_by(CariHareket.hareket_tarihi.asc(), CariHareket.id.asc())
        .all()
    )
    ml_rows = (
        Maliyet.query.filter_by(baglanti_tip=baglanti_tip, baglanti_id=baglanti_id)
        .order_by(Maliyet.maliyet_tarihi.asc(), Maliyet.id.asc())
        .all()
    )

    def _ch(h):
        return dict(
            id=h.id, tarih=h.hareket_tarihi.isoformat() if h.hareket_tarihi else None,
            cari=h.cari_unvan, islem_tip=h.islem_tip,
            borc=h.borc, alacak=h.alacak, doviz=h.doviz,
            kaynak=h.kaynak, kapatildi=h.kapatildi,
        )

    def _ml(m):
        return dict(
            id=m.id, tarih=m.maliyet_tarihi.isoformat() if m.maliyet_tarihi else None,
            tip=m.maliyet_tip, tutar=m.tutar, doviz=m.doviz, aciklama=m.aciklama,
        )

    return jsonify(
        baglanti_tip=baglanti_tip,
        baglanti_id=baglanti_id,
        cari_hareketleri=[_ch(h) for h in ch_rows],
        maliyetler=[_ml(m) for m in ml_rows],
    )
