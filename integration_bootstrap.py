"""
Milestone ERP - Cross-Module Integration Services.

Implements the integration plan:
    Cari ↔ Stok        : Stock entry/exit auto-creates cari hareket
    Cari ↔ Siparis     : Order open/complete auto-syncs cari
    Siparis ↔ Stok     : Stock_ids on order item auto-creates reservation
    Siparis ↔ Fatura   : Invoice from order auto-records cari + cost
    Fatura  ↔ Cari     : Invoice / payment auto-creates cari hareket
    Fatura  ↔ Maliyet  : Invoice auto-records cost (KDV / discount split)
    Kasa    ↔ Cari     : Payment auto-syncs cash + cari simultaneously
    Sevkiyat ↔ Siparis : Delivery auto-updates order status + stock out
    Kesim   ↔ Stok     : Cutting auto-creates new stock + fire cost

The module is designed to be IDEMPOTENT - every record uses a
(baglanti_tip, baglanti_id, kaynak) tuple so duplicate runs are safe.
"""
from __future__ import annotations

import json
import uuid
import logging
from datetime import datetime, date
from typing import Optional

from sqlalchemy import event

logger = logging.getLogger("milestone.integration")

# Will be populated by wire_integrations()
_db = None
_models = {}


# ──────────────────────────────────────────────────────────────────────
# CORE HELPERS
# ──────────────────────────────────────────────────────────────────────
def _yeni_id(prefix: str) -> str:
    """Generate a short prefixed id like ``CH-9F2A1B`` for cross-table refs."""
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"


def _q(value, ndigits: int = 3) -> float:
    if value is None or value == "":
        return 0.0
    try:
        return round(float(value), ndigits)
    except (TypeError, ValueError):
        return 0.0


def _find_cari_by_unvan(unvan: Optional[str]):
    """Lookup a cari record by exact `unvan` (case-insensitive trim)."""
    if not unvan:
        return None
    Cari = _models["Cari"]
    return Cari.query.filter(_db.func.lower(Cari.unvan) == unvan.strip().lower()).first()


def _hareket_var_mi(baglanti_tip: str, baglanti_id: str, kaynak: str) -> bool:
    """Idempotency check: cari hareket already created for this source?"""
    CH = _models["CariHareket"]
    return _db.session.query(
        _db.session.query(CH).filter_by(
            baglanti_tip=baglanti_tip, baglanti_id=baglanti_id, kaynak=kaynak
        ).exists()
    ).scalar()


def _maliyet_var_mi(baglanti_tip: str, baglanti_id: str, maliyet_tip: str) -> bool:
    M = _models["Maliyet"]
    return _db.session.query(
        _db.session.query(M).filter_by(
            baglanti_tip=baglanti_tip,
            baglanti_id=baglanti_id,
            maliyet_tip=maliyet_tip,
            aktif=True,
        ).exists()
    ).scalar()


def _kur_for_doviz_date(doviz: str, tarih=None) -> float:
    """Returns TRY-per-1-unit conversion rate for the given doviz on the
    given date.  Falls back to the latest TCMB rate, then to 1.0 for TRY.

    The DovizKur table stores rows {doviz, alis, satis, efektif, tarih}.
    """
    if not doviz or doviz == "TRY":
        return 1.0
    DovizKur = _models.get("DovizKur")
    if not DovizKur:
        return 0.0
    q = DovizKur.query.filter_by(doviz=doviz)
    if tarih:
        # Tarihe en yakin kuru bul (o tarih veya daha onceki, en yenisi)
        rec = q.filter(DovizKur.tarih <= tarih).order_by(DovizKur.tarih.desc()).first()
        if rec:
            return float(rec.satis or rec.alis or rec.efektif or 0)
    rec = q.order_by(DovizKur.tarih.desc()).first()
    if rec:
        return float(rec.satis or rec.alis or rec.efektif or 0)
    return 0.0


# ──────────────────────────────────────────────────────────────────────
# 1. STOK GİRİŞİ  →  CARİ HAREKET + MALİYET
# ──────────────────────────────────────────────────────────────────────
def stok_giris_kayit(stok, stok_tip: str, kullanici: Optional[str] = None) -> None:
    """Called after a Blok / Plaka / Ebatli stock record is inserted.

    Behaviour:
        - If supplier (uretici) matches a Cari (`unvan`) we create a *borç*
          movement (we owe the supplier) on that cari.
        - A matching "Alis Maliyeti" maliyet row is also created.
    """
    if not stok:
        return
    CariHareket = _models["CariHareket"]
    Maliyet = _models["Maliyet"]
    Cari = _models["Cari"]

    matrah = _q(getattr(stok, "matrah", 0) or 0)
    if matrah <= 0:
        # Fallback: alis_fiyati * (m3 / tonaj / metraj)
        f = _q(getattr(stok, "alis_fiyati", 0) or 0)
        if stok_tip == "BLOK":
            miktar = (
                _q(stok.tonaj)
                if (stok.alis_fiyat_birim or "ton") == "ton"
                else _q(stok.hacim_m3)
            )
        else:
            miktar = _q(getattr(stok, "metraj_m2", 0))
        matrah = _q(f * miktar)

    if matrah <= 0:
        return

    doviz = getattr(stok, "doviz", "USD") or "USD"
    cari = _find_cari_by_unvan(getattr(stok, "uretici", None))

    # ---- CARİ HAREKET (alacak: supplier'a borçluyuz) -----------------
    if cari and not _hareket_var_mi("stok", stok.id, "stok-giris"):
        ch = CariHareket(
            id=_yeni_id("CH"),
            hareket_tarihi=getattr(stok, "giris_tarihi", None) or date.today(),
            cari_unvan=cari.unvan,
            cari_id=cari.id,
            islem_tip="Alis (Stok Girisi)",
            evrak_no=(getattr(stok, "fatura_no", None) or stok.id),
            aciklama=f"{stok_tip} stok girisi - {stok.cins} ({stok.id})"
                + (f" | Fatura: {stok.fatura_no}" if getattr(stok, "fatura_no", None) else ""),
            borc=0,
            alacak=matrah,
            doviz=doviz,
            kaynak="stok-giris",
            baglanti_tip="stok",
            baglanti_id=stok.id,
            kullanici=kullanici or getattr(stok, "kullanici", None) or "sistem",
        )
        # Kur uygulanan: hareket tarihindeki kur
        try:
            ch.kur_uygulanan = _kur_for_doviz_date(doviz, ch.hareket_tarihi) or 0
            if doviz == "USD":
                ch.usd_kur = ch.kur_uygulanan
            elif doviz == "EUR":
                ch.eur_kur = ch.kur_uygulanan
            # TRY karşılığını da hesaplayıp sakla (ileri tarihte ekstre için)
            if ch.kur_uygulanan and ch.kur_uygulanan > 0:
                ch.borc_try = 0
                ch.alacak_try = _q(matrah * ch.kur_uygulanan)
        except Exception:
            pass
        _db.session.add(ch)
        logger.info(f"[ENT] Stok girisi -> Cari {cari.unvan}: alacak {matrah} {doviz}")

    # ---- MALİYET (alis maliyeti) -------------------------------------
    if not _maliyet_var_mi("stok", stok.id, "Alis Maliyeti"):
        m = Maliyet(
            id=_yeni_id("M"),
            maliyet_tarihi=getattr(stok, "giris_tarihi", None) or date.today(),
            maliyet_tip="Alis Maliyeti",
            baglanti_tip="stok",
            baglanti_id=stok.id,
            tutar=matrah,
            doviz=doviz,
            aciklama=f"{stok_tip} alis maliyeti - {stok.cins}",
            kullanici=kullanici or "sistem",
            aktif=True,
        )
        _db.session.add(m)


# ──────────────────────────────────────────────────────────────────────
# 2. STOK ÇIKIŞ  →  CARİ HAREKET (müşteriye borç düş / alacak yarat)
# ──────────────────────────────────────────────────────────────────────
def stok_cikis_kayit(stok_cikis) -> None:
    if not stok_cikis or not stok_cikis.musteri:
        return
    if _hareket_var_mi("stok_cikis", stok_cikis.id, "stok-cikis"):
        return
    cari = _find_cari_by_unvan(stok_cikis.musteri)
    if not cari:
        return
    tutar = _q(stok_cikis.satis_fiyati)
    if tutar <= 0:
        return

    CariHareket = _models["CariHareket"]
    ch = CariHareket(
        id=_yeni_id("CH"),
        hareket_tarihi=stok_cikis.cikis_tarihi or date.today(),
        cari_unvan=cari.unvan,
        cari_id=cari.id,
        islem_tip="Satis (Stok Cikis)",
        evrak_no=stok_cikis.id,
        aciklama=f"Stok cikis - {stok_cikis.cins} {stok_cikis.olcu_metraj} ({stok_cikis.stok_id})",
        borc=tutar,
        alacak=0,
        doviz=stok_cikis.doviz or "USD",
        siparis_id=stok_cikis.siparis_id,
        kaynak="stok-cikis",
        baglanti_tip="stok_cikis",
        baglanti_id=stok_cikis.id,
        kullanici=stok_cikis.kullanici or "sistem",
    )
    _db.session.add(ch)
    logger.info(f"[ENT] Stok cikis -> Cari {cari.unvan}: borc {tutar}")


# ──────────────────────────────────────────────────────────────────────
# 3. SİPARİŞ KALEMİ  →  REZERVASYON  (stok_ids_json üzerinden)
# ──────────────────────────────────────────────────────────────────────
def siparis_kalem_rezervasyon(kalem) -> None:
    """If a SiparisKalem references stocks via ``stok_ids_json``, auto-create
    Rezervasyon rows so the linked stocks become 'Rezerve'."""
    if not kalem or not getattr(kalem, "stok_ids_json", None):
        return
    try:
        stok_ids = json.loads(kalem.stok_ids_json or "[]")
    except Exception:
        return
    if not stok_ids:
        return

    Rezervasyon = _models["Rezervasyon"]
    BlokStok = _models["BlokStok"]
    PlakaStok = _models["PlakaStok"]
    EbatliStok = _models["EbatliStok"]

    tip_to_model = {"BLOK": BlokStok, "PLAKA": PlakaStok, "EBATLI": EbatliStok}
    stok_tip = kalem.urun_tip
    Mdl = tip_to_model.get(stok_tip)
    if not Mdl:
        return

    for sid in stok_ids:
        if not sid:
            continue
        # Idempotency
        exists = Rezervasyon.query.filter_by(
            siparis_kalem_id=kalem.id, stok_id=sid
        ).first()
        if exists:
            continue
        stok = Mdl.query.get(sid)
        rez = Rezervasyon(
            id=_yeni_id("REZ"),
            musteri=kalem.siparis.musteri if kalem.siparis else None,
            siparis_id=kalem.siparis_id,
            siparis_kalem_id=kalem.id,
            stok_tip=stok_tip,
            cins=kalem.cins,
            ozellik=kalem.ozellik,
            stok_id=sid,
            miktar=_q(kalem.miktar),
            rez_tip="otomatik-siparis",
            aciklama=f"Siparis {kalem.siparis_id} kalem #{kalem.sira}",
        )
        _db.session.add(rez)
        if stok and stok.durum == "Serbest":
            stok.durum = "Rezerve"
    logger.info(f"[ENT] Siparis kalemi {kalem.id} icin {len(stok_ids)} rezervasyon olusturuldu")


# ──────────────────────────────────────────────────────────────────────
# 4. SEVKİYAT TAMAMLANDI  →  STOK ÇIKIŞ + SİPARİŞ DURUM
# ──────────────────────────────────────────────────────────────────────
def sevkiyat_teslim_edildi(sevkiyat) -> None:
    """When shipment status transitions to *Teslim Edildi* we:
       1) walk reservations of the linked siparis,
       2) create StokCikis for each reserved stock,
       3) set the order status to *Teslim Edildi*."""
    if not sevkiyat or not sevkiyat.siparis_id:
        return
    Siparis = _models["Siparis"]
    Rezervasyon = _models["Rezervasyon"]
    StokCikis = _models["StokCikis"]

    sip = Siparis.query.get(sevkiyat.siparis_id)
    if not sip:
        return

    rezler = Rezervasyon.query.filter_by(
        siparis_id=sip.id, iptal_nedeni=None
    ).all()
    for r in rezler:
        # Idempotent: ayni rez icin StokCikis var mi?
        exists = StokCikis.query.filter_by(
            rezervasyon_id=r.id, siparis_id=sip.id
        ).first()
        if exists:
            continue
        sc = StokCikis(
            id=_yeni_id("SC"),
            cikis_tarihi=sevkiyat.teslim_tarihi or sevkiyat.gercek_teslim or date.today(),
            stok_tip=r.stok_tip,
            stok_id=r.stok_id,
            cins=r.cins,
            ozellik=r.ozellik,
            musteri=sip.musteri,
            siparis_id=sip.id,
            rezervasyon_id=r.id,
            cikis_nedeni="Sevkiyat Teslim",
            doviz=sip.doviz,
            kullanici="sistem",
        )
        _db.session.add(sc)

    if sip.durum not in ("Teslim Edildi", "Iptal Edildi"):
        sip.durum = "Teslim Edildi"
    logger.info(f"[ENT] Sevkiyat {sevkiyat.id} teslim -> {len(rezler)} stok cikis + siparis durum guncel")


# ──────────────────────────────────────────────────────────────────────
# 5. KESİM TAMAMLANDI  →  YENİ STOK + FİRE MALİYETİ
# ──────────────────────────────────────────────────────────────────────
def kesim_yeni_stok_olustur(kesim) -> None:
    """When a Kesim is created its detail rows become new stocks of the
    target type (PLAKA / EBATLI) and the fire ratio becomes a cost entry."""
    if not kesim:
        return
    KesimDetay = _models["KesimDetay"]
    PlakaStok = _models["PlakaStok"]
    EbatliStok = _models["EbatliStok"]
    Maliyet = _models["Maliyet"]

    detaylar = KesimDetay.query.filter_by(kesim_id=kesim.id).all()
    # Üretim blok no: Kesim.uretim_blok_no varsa kullan, yoksa orijinal kaynak_no
    uretim_blok_no = getattr(kesim, "uretim_blok_no", None) or kesim.kaynak_no
    for d in detaylar:
        if d.hedef_stok_id:  # already linked
            continue
        if d.hedef_tip == "PLAKA":
            new_id = _yeni_id("PLK")
            stok = PlakaStok(
                id=new_id,
                uretici="Milestone",
                cins=d.cins,
                blok_no=uretim_blok_no,
                boy=d.boy,
                yukseklik=d.yukseklik,
                kalinlik=d.kalinlik,
                metraj_m2=_q(d.miktar_m2),
                metraj_sqft=_q(_q(d.miktar_m2) * 10.764),
                slab_no=int((d.slab_no or "1").lstrip("S")) if d.slab_no else 1,
                ozellik=d.ozellik,
                alis_fiyati=_q(d.birim_maliyet),
                matrah=_q(d.toplam_maliyet),
                doviz=kesim.kaynak_doviz or "USD",
                durum="Serbest",
                aciklama=f"Kesim {kesim.id} cikisi | Orijinal Blok: {kesim.kaynak_no or '-'}",
                kullanici=kesim.kullanici,
            )
            _db.session.add(stok)
            d.hedef_stok_id = new_id
        elif d.hedef_tip == "EBATLI":
            new_id = _yeni_id("EBT")
            stok = EbatliStok(
                id=new_id,
                uretici="Milestone",
                cins=d.cins,
                kasa_no=d.kasa_no,
                bas_kasa_no=d.kasa_no,
                kasa_adedi=1,
                kasa_ici_adet=d.adet or 1,
                boy=d.boy,
                yukseklik=d.yukseklik,
                kalinlik=d.kalinlik,
                metraj_m2=_q(d.miktar_m2),
                metraj_sqft=_q(_q(d.miktar_m2) * 10.764),
                ozellik=d.ozellik,
                alis_fiyati=_q(d.birim_maliyet),
                matrah=_q(d.toplam_maliyet),
                doviz=kesim.kaynak_doviz or "USD",
                durum="Serbest",
                aciklama=f"Kesim {kesim.id} cikisi",
                kullanici=kesim.kullanici,
            )
            _db.session.add(stok)
            d.hedef_stok_id = new_id

    # Fire maliyeti (toplam maliyetin fire_orani %'si)
    if (kesim.fire_orani or 0) > 0 and not _maliyet_var_mi("kesim", kesim.id, "Fire Maliyeti"):
        fire_tutar = _q(
            (kesim.kaynak_toplam_maliyet or 0) * (kesim.fire_orani or 0) / 100
        )
        if fire_tutar > 0:
            mf = Maliyet(
                id=_yeni_id("M"),
                maliyet_tarihi=kesim.kesim_tarihi or date.today(),
                maliyet_tip="Fire Maliyeti",
                baglanti_tip="kesim",
                baglanti_id=kesim.id,
                tutar=fire_tutar,
                doviz=kesim.kaynak_doviz or "USD",
                aciklama=f"Kesim {kesim.id} fire ({kesim.fire_orani}%)",
                kullanici=kesim.kullanici or "sistem",
                aktif=True,
            )
            _db.session.add(mf)


# ──────────────────────────────────────────────────────────────────────
# 6. FATURA KESİLDİ  →  MALİYET (KDV + iskonto + ana tutar ayrı) + CARİ HAREKET
# ──────────────────────────────────────────────────────────────────────
def fatura_maliyet_olustur(fatura) -> None:
    """Invoice issued -> ensure cost entries + cari hareket exist."""
    if not fatura:
        return
    Maliyet = _models["Maliyet"]
    CariHareket = _models["CariHareket"]
    Cari = _models["Cari"]

    ara = _q(getattr(fatura, "ara_toplam", 0))
    kdv = _q(getattr(fatura, "kdv_tutar", 0))
    toplam = _q(getattr(fatura, "toplam", 0)) or _q(ara + kdv)
    if toplam <= 0 and ara <= 0 and kdv <= 0:
        return
    doviz = fatura.doviz or "USD"

    # Ana fatura tutarı (gelir / gider tipinde)
    tip = "Satis Geliri" if (fatura.yon or "satis") == "satis" else "Alis Maliyeti"
    if ara > 0 and not _maliyet_var_mi("fatura", fatura.id, tip):
        m = Maliyet(
            id=_yeni_id("M"),
            maliyet_tarihi=fatura.fatura_tarihi or date.today(),
            maliyet_tip=tip,
            baglanti_tip="fatura",
            baglanti_id=fatura.id,
            tutar=ara,
            doviz=doviz,
            fatura_no=fatura.fatura_no,
            aciklama=f"Fatura {fatura.fatura_no} ana tutar",
            kullanici=fatura.kullanici or "sistem",
            aktif=True,
        )
        _db.session.add(m)

    if kdv > 0 and not _maliyet_var_mi("fatura", fatura.id, "KDV"):
        m = Maliyet(
            id=_yeni_id("M"),
            maliyet_tarihi=fatura.fatura_tarihi or date.today(),
            maliyet_tip="KDV",
            baglanti_tip="fatura",
            baglanti_id=fatura.id,
            tutar=kdv,
            doviz=doviz,
            fatura_no=fatura.fatura_no,
            aciklama=f"Fatura {fatura.fatura_no} KDV",
            kullanici=fatura.kullanici or "sistem",
            aktif=True,
        )
        _db.session.add(m)

    # ── Fatura → Cari Hareket (borç müşteriye / alacak satıcıya) ─────
    durum_aktif = (fatura.durum or "") in ("Kesildi", "Kismi Tahsil", "Tahsil Edildi")
    if not durum_aktif or toplam <= 0:
        return
    cari = None
    if fatura.musteri:
        cari = _find_cari_by_unvan(fatura.musteri)
    if not cari:
        return
    if _hareket_var_mi("fatura", fatura.id, "fatura-kesim"):
        return

    yon = (fatura.yon or "satis").lower()
    if yon == "satis":
        borc, alacak = toplam, 0
        islem_tip = "Satis Faturasi"
    else:  # alis
        borc, alacak = 0, toplam
        islem_tip = "Alis Faturasi"

    ch = CariHareket(
        id=_yeni_id("CH"),
        hareket_tarihi=fatura.fatura_tarihi or date.today(),
        cari_unvan=cari.unvan,
        cari_id=cari.id,
        islem_tip=islem_tip,
        evrak_no=fatura.fatura_no,
        aciklama=f"{islem_tip} {fatura.fatura_no}",
        borc=borc,
        alacak=alacak,
        doviz=doviz,
        kaynak="fatura-kesim",
        baglanti_tip="fatura",
        baglanti_id=fatura.id,
        kullanici=fatura.kullanici or "sistem",
    )
    _db.session.add(ch)
    logger.info(
        f"[ENT] Fatura {fatura.fatura_no} -> Cari {cari.unvan}: "
        f"borc={borc} alacak={alacak} {doviz}"
    )


# ──────────────────────────────────────────────────────────────────────
# 7. KASA HAREKET  →  CARİ HAREKET (eşzamanlı)
# ──────────────────────────────────────────────────────────────────────
def kasa_cari_senkron(kasa_hareket) -> None:
    """Cash movement linked to a cari → mirror it to cari_hareket so balances
    stay in sync. Triggered only when cari_id is provided AND no mirror
    movement exists yet."""
    if not kasa_hareket or not getattr(kasa_hareket, "cari_id", None):
        return
    Cari = _models["Cari"]
    CariHareket = _models["CariHareket"]

    cari = Cari.query.get(kasa_hareket.cari_id)
    if not cari:
        return
    if _hareket_var_mi("kasa_hareket", str(kasa_hareket.id), "kasa-senkron"):
        return

    # giris  -> kasaya para geldi -> cariden ALACAK (musteri odedi)
    # cikis  -> kasadan para cikti -> cariye BORC (cariye odeme yaptik)
    if kasa_hareket.tip == "giris":
        borc, alacak = 0, _q(kasa_hareket.tutar)
        islem_tip = "Tahsilat (Kasa)"
    else:
        borc, alacak = _q(kasa_hareket.tutar), 0
        islem_tip = "Tediye (Kasa)"

    Kasa = _models["Kasa"]
    kasa = Kasa.query.get(kasa_hareket.kasa_id)
    doviz = (kasa.doviz if kasa else "TRY") or "TRY"

    ch = CariHareket(
        id=_yeni_id("CH"),
        hareket_tarihi=kasa_hareket.tarih or date.today(),
        cari_unvan=cari.unvan,
        cari_id=cari.id,
        islem_tip=islem_tip,
        evrak_no=str(kasa_hareket.id),
        aciklama=kasa_hareket.aciklama or f"Kasa hareket #{kasa_hareket.id}",
        borc=borc,
        alacak=alacak,
        doviz=doviz,
        kaynak="kasa-senkron",
        baglanti_tip="kasa_hareket",
        baglanti_id=str(kasa_hareket.id),
        kullanici=kasa_hareket.kullanici or "sistem",
    )
    _db.session.add(ch)
    # Note: we're inside `after_flush_postexec`, so the new ch will be
    # flushed in the next cycle; we still match against existing rows.
    # Auto-close matching open borc/alacak (FIFO) – fatura kapanışı için de.
    tahsilat_kapanis_uygula(ch)
    logger.info(
        f"[ENT] Kasa hareket #{kasa_hareket.id} -> Cari {cari.unvan} "
        f"({islem_tip}): borc={borc} alacak={alacak} {doviz}"
    )


# ──────────────────────────────────────────────────────────────────────
# 8. TAHSILAT KAPANIŞ  →  FATURA / CARİ HAREKET (FIFO)
# ──────────────────────────────────────────────────────────────────────
def tahsilat_kapanis_uygula(yeni_hareket) -> None:
    """Yeni bir tahsilat (alacak>0) ya da tediye (borc>0) hareketi geldiğinde
    aynı cari + döviz için açık (kapatildi=False) karşı hareketleri FIFO ile
    eşler ve `kapatildi=True` işaretler. Eğer karşı hareket bir faturaya bağlı
    ise faturanın `tahsil_edilen` alanı artırılır ve toplam tahsilat fatura
    tutarına ulaştıysa `durum=Tahsil Edildi` olur.

    Bu fonksiyon **idempotent**'tir: kapatildi=True olan hareketler tekrar
    işlenmez."""
    if not yeni_hareket:
        return
    CariHareket = _models["CariHareket"]
    Fatura = _models["Fatura"]

    is_tahsilat = (yeni_hareket.alacak or 0) > 0
    is_odeme = (yeni_hareket.borc or 0) > 0
    if not (is_tahsilat or is_odeme):
        return
    if yeni_hareket.kapatildi:
        return  # already closed

    # Karşı tarafı FIFO sıraya göre bul
    base_q = CariHareket.query.filter(
        CariHareket.cari_id == yeni_hareket.cari_id,
        CariHareket.doviz == yeni_hareket.doviz,
        CariHareket.kapatildi == False,  # noqa: E712
        CariHareket.id != yeni_hareket.id,
    )
    if is_tahsilat:
        karsi_q = base_q.filter(CariHareket.borc > 0)
    else:
        karsi_q = base_q.filter(CariHareket.alacak > 0)
    karsi_list = karsi_q.order_by(
        CariHareket.hareket_tarihi.asc(), CariHareket.id.asc()
    ).all()
    if not karsi_list:
        return

    kalan = _q(yeni_hareket.alacak) if is_tahsilat else _q(yeni_hareket.borc)
    for karsi in karsi_list:
        if kalan <= 0:
            break
        karsi_tutar = _q(karsi.borc if is_tahsilat else karsi.alacak)
        if karsi_tutar <= 0:
            continue
        eslesen = min(karsi_tutar, kalan)
        # Eğer karşı tutar tamamen eşleşiyorsa kapat
        if karsi_tutar - eslesen < 0.01:
            karsi.kapatildi = True
            karsi.kapanis_hareket_id = yeni_hareket.id
        kalan = _q(kalan - eslesen)

        # FATURA güncelle (eğer karşı hareket faturaya bağlıysa)
        if karsi.baglanti_tip == "fatura" and karsi.baglanti_id:
            fat = Fatura.query.get(karsi.baglanti_id)
            if fat:
                # Fatura'ya bağlı tüm borç hareketleri için kapatılma durumunu
                # taze veriyle hesapla. Bu döngüde dirty olan rows da var,
                # bu yüzden DB'yi sorgulamak yerine session.identity_map'i
                # gez. Pratik: sadece eslesen + karsi.kapatildi mantığı yeterli.
                if karsi.kapatildi:
                    # Tam kapatildi → fatura tahsil edildi
                    fat.durum = "Tahsil Edildi"
                else:
                    fat.durum = "Kismi Tahsil"
                logger.info(
                    f"[ENT] Tahsilat -> Fatura {fat.fatura_no}: "
                    f"eslesen={eslesen}, karsi.kapatildi={karsi.kapatildi}, durum={fat.durum}"
                )

    # Yeni hareket tam karşılandıysa onu da kapat
    if kalan < 0.01:
        yeni_hareket.kapatildi = True


# ──────────────────────────────────────────────────────────────────────
# WIRE - register SQLAlchemy events on the Flask app
# ──────────────────────────────────────────────────────────────────────
def wire_integrations(flask_app) -> None:
    """Attach SQLAlchemy `after_insert` / `after_update` listeners to the
    relevant models so all integrations fire automatically.

    Idempotency guards inside each service prevent double-recording on
    re-runs (so this is safe even if some endpoints already create
    the same records manually).
    """
    # Guard against multiple wirings (uvicorn reload, repeat imports).
    if getattr(flask_app, "_integrations_wired", False):
        return
    flask_app._integrations_wired = True

    global _db, _models
    from flask_app import db as flask_db  # the SQLAlchemy() instance
    from models import (
        BlokStok, PlakaStok, EbatliStok, StokCikis,
        Siparis, SiparisKalem, Rezervasyon,
        Cari, CariHareket,
        Fatura, Maliyet,
        Sevkiyat, Kesim, KesimDetay,
        Kasa, KasaHareket, DovizKur,
    )

    _db = flask_db
    _models = {
        "BlokStok": BlokStok, "PlakaStok": PlakaStok, "EbatliStok": EbatliStok,
        "StokCikis": StokCikis,
        "Siparis": Siparis, "SiparisKalem": SiparisKalem,
        "Rezervasyon": Rezervasyon,
        "Cari": Cari, "CariHareket": CariHareket,
        "Fatura": Fatura, "Maliyet": Maliyet,
        "Sevkiyat": Sevkiyat, "Kesim": Kesim, "KesimDetay": KesimDetay,
        "Kasa": Kasa, "KasaHareket": KasaHareket,
        "DovizKur": DovizKur,
    }

    # ── Stok girişi (3 ayrı model) ────────────────────────────────────
    flask_app._pending_integrations = {
        "stok_giris": [],     # list of (stok_obj, tip)
        "stok_cikis": [],     # list of stok_cikis
        "kalem_rez": [],      # list of kalem
        "sevkiyat": [],       # list of sevkiyat
        "kesim": [],          # list of kesim
        "fatura_maliyet": [], # list of fatura
        "kasa_senkron": [],   # list of kasa_hareket
    }

    @event.listens_for(BlokStok, "after_insert")
    def _blok_inserted(mapper, connection, target):
        flask_app._pending_integrations["stok_giris"].append((target.id, "BLOK"))

    @event.listens_for(PlakaStok, "after_insert")
    def _plaka_inserted(mapper, connection, target):
        flask_app._pending_integrations["stok_giris"].append((target.id, "PLAKA"))

    @event.listens_for(EbatliStok, "after_insert")
    def _ebatli_inserted(mapper, connection, target):
        flask_app._pending_integrations["stok_giris"].append((target.id, "EBATLI"))

    # ── Stok çıkış → cari hareket (müşteri borç) ──────────────────────
    @event.listens_for(StokCikis, "after_insert")
    def _stok_cikis_inserted(mapper, connection, target):
        flask_app._pending_integrations["stok_cikis"].append(target.id)

    # ── Siparis kalemi → rezervasyon ──────────────────────────────────
    @event.listens_for(SiparisKalem, "after_insert")
    def _kalem_inserted(mapper, connection, target):
        flask_app._pending_integrations["kalem_rez"].append(target.id)

    @event.listens_for(SiparisKalem, "after_update")
    def _kalem_updated(mapper, connection, target):
        flask_app._pending_integrations["kalem_rez"].append(target.id)

    # ── Sevkiyat teslim ──────────────────────────────────────────────
    @event.listens_for(Sevkiyat, "after_update")
    def _sevkiyat_updated(mapper, connection, target):
        if (target.durum or "").lower().startswith("teslim"):
            flask_app._pending_integrations["sevkiyat"].append(target.id)

    # ── Kesim → yeni stok + fire maliyet ─────────────────────────────
    @event.listens_for(Kesim, "after_insert")
    def _kesim_inserted(mapper, connection, target):
        flask_app._pending_integrations["kesim"].append(target.id)

    # ── Fatura → maliyet (KDV / iskonto / ana) ────────────────────────
    @event.listens_for(Fatura, "after_insert")
    def _fatura_inserted(mapper, connection, target):
        flask_app._pending_integrations["fatura_maliyet"].append(target.id)

    @event.listens_for(Fatura, "after_update")
    def _fatura_updated(mapper, connection, target):
        if (target.durum or "") in ("Kesildi", "Kismi Tahsil", "Tahsil Edildi"):
            flask_app._pending_integrations["fatura_maliyet"].append(target.id)

    # ── Kasa hareket → cari hareket eş zamanlı ────────────────────────
    @event.listens_for(KasaHareket, "after_insert")
    def _kasa_inserted(mapper, connection, target):
        flask_app._pending_integrations["kasa_senkron"].append(target.id)

    # ── Process queue after the flush so add()'s are safe ─────────────
    @event.listens_for(flask_db.session, "after_flush_postexec")
    def _flush_done(session, flush_context):
        q = flask_app._pending_integrations
        if not any(q.values()):
            return
        # Snapshot & clear (so re-entrancy from new flushes is safe)
        items = {k: list(v) for k, v in q.items()}
        for k in q:
            q[k] = []

        # Stok girişi: cari hareket + maliyet
        for sid, tip in items["stok_giris"]:
            Mdl = {"BLOK": BlokStok, "PLAKA": PlakaStok, "EBATLI": EbatliStok}.get(tip)
            if not Mdl:
                continue
            stok = Mdl.query.get(sid)
            if stok:
                _safe_run(stok_giris_kayit, stok, tip)

        # Stok çıkışı: cari borç
        for scid in items["stok_cikis"]:
            sc = StokCikis.query.get(scid)
            if sc:
                _safe_run(stok_cikis_kayit, sc)

        # Sipariş kalem → rezervasyon
        for kid in items["kalem_rez"]:
            k = SiparisKalem.query.get(kid)
            if k:
                _safe_run(siparis_kalem_rezervasyon, k)

        # Sevkiyat teslim → stok çıkışı + sipariş durumu
        for sid in items["sevkiyat"]:
            s = Sevkiyat.query.get(sid)
            if s:
                _safe_run(sevkiyat_teslim_edildi, s)

        # Kesim → yeni stok + fire maliyet
        for kid in items["kesim"]:
            k = Kesim.query.get(kid)
            if k:
                _safe_run(kesim_yeni_stok_olustur, k)

        # Fatura → maliyet kalemleri
        for fid in items["fatura_maliyet"]:
            f = Fatura.query.get(fid)
            if f:
                _safe_run(fatura_maliyet_olustur, f)

        # Kasa hareket → cari hareket
        for khid in items["kasa_senkron"]:
            kh = KasaHareket.query.get(khid)
            if kh:
                _safe_run(kasa_cari_senkron, kh)

    flask_app.logger.info("[ENT] Cross-module integration triggers wired ✅")


def _safe_run(fn, *args, **kwargs):
    """Run an integration step but never break the parent transaction."""
    try:
        fn(*args, **kwargs)
    except Exception as e:  # pragma: no cover
        logger.exception(f"Integration step failed: {fn.__name__}: {e}")
