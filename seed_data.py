"""
Milestone ERP - Demo data seeder.

Creates a small but realistic dataset that exercises ALL cross-module
integrations defined in the project (Cari, Stok, Sipariş, Fatura, Kasa,
Sevkiyat, Kesim, Maliyet).

Usage:
    cd <proje_dizini> && python seed_data.py
"""
import os
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(__file__))

os.environ.setdefault(
    "DATABASE_URL",
    "sqlite:///instance/milestone.db",
)

from flask_app import app  # noqa
from models import (  # noqa
    db,
    Cari,
    BlokStok,
    PlakaStok,
    EbatliStok,
    Siparis,
    SiparisKalem,
    Fatura,
    Kasa,
    KasaHareket,
    Banka,
    Veriler,
)
from integration_bootstrap import wire_integrations, _yeni_id  # noqa


def main() -> None:
    wire_integrations(app)
    with app.app_context():
        if Cari.query.count() > 0:
            print("[seed] Skipped - cari already exists")
            return

        today = date.today()

        # ── CARİLER ──────────────────────────────────────────────
        cariler = [
            Cari(
                id="CR-0001",
                unvan="Anka Mermer Tic. Ltd.",
                cari_tip="Üretici",
                urun_tedarikcisi=True,
                uretici_kisaltma="ANK",
                vergi_dairesi="Denizli",
                vergi_no="1234567890",
                para_birimi="USD",
                yetkili="Cem Yılmaz",
                telefon="+90 258 555 1234",
                email="info@ankamermer.com",
                ulke="Türkiye",
                risk_limiti=100000,
            ),
            Cari(
                id="CR-0002",
                unvan="Stone Bros LLC",
                cari_tip="Müşteri",
                vergi_dairesi="-",
                vergi_no="-",
                para_birimi="USD",
                yetkili="John Smith",
                telefon="+1 305 555 9876",
                email="orders@stonebros.com",
                ulke="USA",
                risk_limiti=250000,
            ),
            Cari(
                id="CR-0003",
                unvan="Milano Marmi SpA",
                cari_tip="Müşteri",
                vergi_dairesi="-",
                vergi_no="IT-9988776",
                para_birimi="EUR",
                yetkili="Luca Bianchi",
                telefon="+39 02 555 4321",
                email="acquisti@milanomarmi.it",
                ulke="Italia",
                risk_limiti=180000,
            ),
            Cari(
                id="CR-0004",
                unvan="Aydın Nakliyat",
                cari_tip="Tedarikçi",
                urun_tedarikcisi=True,
                uretici_kisaltma="AYD",
                vergi_dairesi="Aydın",
                vergi_no="5566778899",
                para_birimi="TRY",
                yetkili="Hasan Aydın",
                telefon="+90 256 555 6677",
                ulke="Türkiye",
                risk_limiti=50000,
            ),
        ]
        for c in cariler:
            db.session.add(c)

        # ── LOOKUPS ─────────────────────────────────────────────
        lookups = [
            # Mermer cinsleri
            ("cins", "Beige Marble",                    None),
            ("cins", "Black Marquina",                  None),
            ("cins", "Bursa Beige",                     None),
            ("cins", "Emperador",                       None),
            ("cins", "Fildişi",                         None),
            ("cins", "Nero",                            None),
            ("cins", "Traverten",                       None),
            # Yüzey özellikleri
            ("ozellik", "Polished",                     None),
            ("ozellik", "Honed",                        None),
            ("ozellik", "Leather",                      None),
            ("ozellik", "Honlu",                        None),
            ("ozellik", "Patine",                       None),
            ("ozellik", "Cilali",                       None),
            # Stok durum tipleri
            ("durum", "Serbest",                        None),
            ("durum", "Rezerve",                        None),
            ("durum", "Satildi",                        None),
            ("durum", "Hasarlı",                        None),
            # Ödeme koşulları
            ("odeme", "%30 Avans %70 Yukleme Oncesi",   None),
            ("odeme", "%50 Avans %50 Yukleme Oncesi",   None),
            ("odeme", "Pesin",                          None),
            ("odeme", "Banka Havalesi (T/T)",           None),
            ("odeme", "Akreditif (L/C)",                None),
            ("odeme", "Vesaik Mukabili",                None),
            ("odeme", "Mal Mukabili",                   None),
            # Teslim koşulları (Incoterms)
            ("teslim", "FOB",                           None),
            ("teslim", "CFR",                           None),
            ("teslim", "CIF",                           None),
            ("teslim", "EXW",                           None),
            ("teslim", "FCA",                           None),
            ("teslim", "DAP",                           None),
            ("teslim", "DDP",                           None),
            ("teslim", "CPT",                           None),
            # Sipariş durum tipleri
            ("siparis_durum", "Teklif Asam.",           None),
            ("siparis_durum", "Onaylandi",              None),
            ("siparis_durum", "Uretimde",               None),
            ("siparis_durum", "Hazir",                  None),
            ("siparis_durum", "Teslim Edildi",          None),
            ("siparis_durum", "Iptal Edildi",           None),
            # KDV ayarı (kisaltma alanında oran saklanır)
            ("kdv_ayar", "varsayilan_oran",             "20"),
        ]
        for kat, deger, kisaltma in lookups:
            if not Veriler.query.filter_by(kategori=kat, deger=deger).first():
                db.session.add(Veriler(kategori=kat, deger=deger, kisaltma=kisaltma))

        # ── KASA & BANKA ─────────────────────────────────────────
        if Kasa.query.count() == 0:
            db.session.add(Kasa(ad="Merkez Kasa TL", doviz="TRY", bakiye=0, varsayilan=True))
            db.session.add(Kasa(ad="USD Kasa",       doviz="USD", bakiye=0))
            db.session.add(Kasa(ad="EUR Kasa",       doviz="EUR", bakiye=0))
        if Banka.query.count() == 0:
            db.session.add(
                Banka(
                    banka_adi="İş Bankası",
                    sube="Denizli Merkez",
                    hesap_no="1234567",
                    iban="TR12 0006 4000 0011 1111 2222 33",
                    swift="ISBKTRIS",
                    doviz="USD",
                    varsayilan=True,
                )
            )

        # ── STOK ─────────────────────────────────────────────────
        blok = BlokStok(
            id="BLK-DEMO01",
            uretici="Anka Mermer Tic. Ltd.",
            cins="Beige Marble",
            blok_no="A-2026-001",
            boy=300,
            yukseklik=180,
            en=160,
            hacim_m3=8.64,
            tonaj=23.3,
            alis_fiyati=420,
            alis_fiyat_birim="ton",
            doviz="USD",
            matrah=420 * 23.3,
            durum="Serbest",
            giris_tarihi=today - timedelta(days=20),
            aciklama="Birinci kalite, açık beje renk",
            fatura_no="ANK-2026-0001",
            kullanici="seed",
        )
        plaka = PlakaStok(
            id="PLK-DEMO01",
            uretici="Anka Mermer Tic. Ltd.",
            cins="Bursa Beige",
            blok_no="B-2026-002",
            boy=300,
            yukseklik=180,
            kalinlik=2,
            metraj_m2=5.4,
            metraj_sqft=58.12,
            slab_no=1,
            ozellik="Polished",
            alis_fiyati=42,
            alis_fiyat_birim="m2",
            matrah=42 * 5.4,
            doviz="USD",
            durum="Serbest",
            giris_tarihi=today - timedelta(days=10),
            fatura_no="ANK-2026-0002",
            kullanici="seed",
        )
        ebatli = EbatliStok(
            id="EBT-DEMO01",
            uretici="Anka Mermer Tic. Ltd.",
            cins="Black Marquina",
            kasa_no="K-001",
            bas_kasa_no="K-001",
            kasa_adedi=1,
            boy=60,
            yukseklik=60,
            kalinlik=2,
            kasa_ici_adet=20,
            metraj_m2=7.2,
            metraj_sqft=77.5,
            ozellik="Polished",
            alis_fiyati=68,
            alis_fiyat_birim="m2",
            matrah=68 * 7.2,
            doviz="USD",
            durum="Serbest",
            giris_tarihi=today - timedelta(days=6),
            fatura_no="ANK-2026-0003",
            kullanici="seed",
        )
        db.session.add_all([blok, plaka, ebatli])
        db.session.flush()

        # ── SİPARİŞ ─────────────────────────────────────────────
        sip = Siparis(
            id="SIP-DEMO01",
            siparis_tarihi=today - timedelta(days=4),
            musteri="Stone Bros LLC",
            doviz="USD",
            odeme_sekli="%30 Avans %70 Yukleme Oncesi",
            teslim_sekli="FOB",
            termin=today + timedelta(days=30),
            durum="Onaylandi",
            satis_tipi="ihracat",
            toplam_tutar=58 * 5.4,
            kullanici="seed",
        )
        db.session.add(sip)
        db.session.flush()

        kalem = SiparisKalem(
            siparis_id="SIP-DEMO01",
            sira=1,
            urun_tip="PLAKA",
            cins="Bursa Beige",
            ozellik="Polished",
            boy=300,
            yukseklik=180,
            kalinlik=2,
            adet=1,
            miktar=5.4,
            birim="m2",
            m2_toplam=5.4,
            sqft_toplam=58.12,
            birim_fiyat=58,
            toplam_fiyat=58 * 5.4,
            doviz="USD",
            stoktan_geldi=True,
            stok_ids_json='["PLK-DEMO01"]',
        )
        db.session.add(kalem)

        db.session.commit()
        print("[seed] Demo data installed:")
        print("       4 cari, 3 stok, 1 siparis")
        print("       42 lookup kaydı (cins/ozellik/durum/odeme/teslim/siparis_durum/kdv_ayar)")
        print("       3 kasa, 1 banka")
        print("       stok-giris cari/maliyet kayıtları otomatik")


if __name__ == "__main__":
    main()
