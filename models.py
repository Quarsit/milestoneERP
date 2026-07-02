from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
db = SQLAlchemy()

# ── KULLANICILAR ──────────────────────────────────────────────────────
class Kullanici(db.Model):
    __tablename__ = 'kullanicilar'
    id       = db.Column(db.Integer, primary_key=True)
    ad       = db.Column(db.String(50), unique=True, nullable=False)
    sifre    = db.Column(db.String(255), nullable=False)
    rol      = db.Column(db.String(20), default='SATIS')
    aktif    = db.Column(db.Boolean, default=True)
    yetkiler = db.Column(db.Text, default='{}')
    olusturma = db.Column(db.DateTime, default=datetime.now)

# ── STOK ─────────────────────────────────────────────────────────────
class BlokStok(db.Model):
    __tablename__ = 'blok_stok'
    id              = db.Column(db.String(20), primary_key=True)
    giris_tarihi    = db.Column(db.Date, default=date.today)
    uretici         = db.Column(db.String(100))
    cins            = db.Column(db.String(100))
    blok_no         = db.Column(db.String(50))
    boy             = db.Column(db.Float)
    yukseklik       = db.Column(db.Float)
    en              = db.Column(db.Float)
    hacim_m3        = db.Column(db.Float)
    tonaj           = db.Column(db.Float)
    alis_fiyati     = db.Column(db.Float)
    alis_fiyat_birim = db.Column(db.String(5), default='ton')
    kdv_dahil_mi    = db.Column(db.Boolean, default=False)
    kdv_oran        = db.Column(db.Float, default=0)
    alis_tipi       = db.Column(db.String(20), default='yurtici_kdvli')
    kdv_tutar       = db.Column(db.Float, default=0)
    matrah          = db.Column(db.Float, default=0)
    doviz           = db.Column(db.String(5), default='USD')
    konum           = db.Column(db.String(100))
    durum           = db.Column(db.String(20), default='Serbest')
    aciklama        = db.Column(db.Text)
    kullanici       = db.Column(db.String(50))
    guncelleme      = db.Column(db.DateTime, default=datetime.now)
    nakliye_dahil   = db.Column(db.Boolean, default=False)
    fatura_no       = db.Column(db.String(50))
    alis_tarihi     = db.Column(db.Date)               # Fatura/borç tarihi (giris_tarihi'nden farklı olabilir)
    fatura_durumu   = db.Column(db.String(20), default='faturali')  # faturali / faturasiz / mal_bekliyor

class PlakaStok(db.Model):
    __tablename__ = 'plaka_stok'
    id              = db.Column(db.String(20), primary_key=True)
    giris_tarihi    = db.Column(db.Date, default=date.today)
    uretici         = db.Column(db.String(100))
    cins            = db.Column(db.String(100))
    blok_no         = db.Column(db.String(50))
    boy             = db.Column(db.Float)
    yukseklik       = db.Column(db.Float)
    kalinlik        = db.Column(db.Float)
    m2_kg           = db.Column(db.Float)
    ozellik         = db.Column(db.String(50))
    metraj_m2       = db.Column(db.Float)
    metraj_sqft     = db.Column(db.Float)
    slab_no         = db.Column(db.Integer)
    alis_fiyati     = db.Column(db.Float)
    alis_fiyat_birim = db.Column(db.String(5), default='m2')
    kdv_dahil_mi    = db.Column(db.Boolean, default=False)
    kdv_oran        = db.Column(db.Float, default=0)
    alis_tipi       = db.Column(db.String(20), default='yurtici_kdvli')
    kdv_tutar       = db.Column(db.Float, default=0)
    matrah          = db.Column(db.Float, default=0)
    doviz           = db.Column(db.String(5), default='USD')
    konum           = db.Column(db.String(100))
    durum           = db.Column(db.String(20), default='Serbest')
    aciklama        = db.Column(db.Text)
    kullanici       = db.Column(db.String(50))
    guncelleme      = db.Column(db.DateTime, default=datetime.now)
    nakliye_dahil   = db.Column(db.Boolean, default=False)
    fatura_no       = db.Column(db.String(50))
    alis_tarihi     = db.Column(db.Date)
    fatura_durumu   = db.Column(db.String(20), default='faturali')

class EbatliStok(db.Model):
    __tablename__ = 'ebatli_stok'
    id              = db.Column(db.String(20), primary_key=True)
    giris_tarihi    = db.Column(db.Date, default=date.today)
    uretici         = db.Column(db.String(100))
    cins            = db.Column(db.String(100))
    kasa_no         = db.Column(db.String(50))
    boy             = db.Column(db.Float)
    yukseklik       = db.Column(db.Float)
    kalinlik        = db.Column(db.Float)
    m2_kg           = db.Column(db.Float)
    ozellik         = db.Column(db.String(50))
    kasa_ici_adet   = db.Column(db.Integer)
    metraj_m2       = db.Column(db.Float)
    metraj_sqft     = db.Column(db.Float)
    alis_fiyati     = db.Column(db.Float)
    alis_fiyat_birim = db.Column(db.String(5), default='m2')
    kdv_dahil_mi    = db.Column(db.Boolean, default=False)
    kdv_oran        = db.Column(db.Float, default=0)
    alis_tipi       = db.Column(db.String(20), default='yurtici_kdvli')
    kdv_tutar       = db.Column(db.Float, default=0)
    matrah          = db.Column(db.Float, default=0)
    doviz           = db.Column(db.String(5), default='USD')
    konum           = db.Column(db.String(100))
    durum           = db.Column(db.String(20), default='Serbest')
    aciklama        = db.Column(db.Text)
    kullanici       = db.Column(db.String(50))
    guncelleme      = db.Column(db.DateTime, default=datetime.now)
    nakliye_dahil   = db.Column(db.Boolean, default=False)
    bas_kasa_no     = db.Column(db.String(50))
    kasa_adedi      = db.Column(db.Integer, default=1)
    fatura_no       = db.Column(db.String(50))
    alis_tarihi     = db.Column(db.Date)
    fatura_durumu   = db.Column(db.String(20), default='faturali')

class StokCikis(db.Model):
    __tablename__ = 'stok_cikis'
    id              = db.Column(db.String(20), primary_key=True)
    cikis_tarihi    = db.Column(db.Date, default=date.today)
    stok_tip        = db.Column(db.String(10))
    stok_id         = db.Column(db.String(20))
    uretici         = db.Column(db.String(100))
    cins            = db.Column(db.String(100))
    ozellik         = db.Column(db.String(50))
    olcu_metraj     = db.Column(db.String(50))
    musteri         = db.Column(db.String(100))
    siparis_id      = db.Column(db.String(20))
    rezervasyon_id  = db.Column(db.String(20))
    alis_fiyati     = db.Column(db.Float)
    satis_fiyati    = db.Column(db.Float)
    doviz           = db.Column(db.String(5))
    cikis_nedeni    = db.Column(db.String(50))
    kullanici       = db.Column(db.String(50))
    guncelleme      = db.Column(db.DateTime, default=datetime.now)

# ═══════════════════════════════════════════════════════════════════════
# ── SİPARİŞ (PARENT) ─────────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════
# FAZ 16 DEGISIKLIK NOTLARI:
# KALDIRILANLAR (artik SiparisKalem'de):
#   - urun_tip, cins, ozellik, olcu, satis_fiyati, miktar, birim
# EKLENENLER:
#   - toplam_tutar (kalemlerin toplami, kalem kayit/silme'de senkronize)
#   - kalemler relationship (1-N)
# ═══════════════════════════════════════════════════════════════════════
class Siparis(db.Model):
    __tablename__ = 'siparis_kayit'
    id              = db.Column(db.String(20), primary_key=True)
    siparis_tarihi  = db.Column(db.Date, default=date.today)
    musteri         = db.Column(db.String(100))

    # Sipariş geneli para birimi (kalemler bunu inherit eder, override edebilir)
    doviz           = db.Column(db.String(5), default='USD')

    # Ödeme & Teslim & Termin
    odeme_sekli     = db.Column(db.String(50))
    teslim_sekli    = db.Column(db.String(50))
    termin          = db.Column(db.Date)
    durum           = db.Column(db.String(30), default='Teklif Asam.')
    aciklama        = db.Column(db.Text)

    # YENİ: Toplam (kalemlerin sum'i, otomatik güncellenir)
    toplam_tutar    = db.Column(db.Float, default=0)

    # Vergi (sipariş geneli)
    satis_tipi      = db.Column(db.String(30), default='ihracat')
    kdv_oran        = db.Column(db.Float, default=0)
    kdv_tutar       = db.Column(db.Float, default=0)
    tevkifat_oran   = db.Column(db.String(10), default='')
    tevkifat_tutar  = db.Column(db.Float, default=0)

    # Acente / Komisyon
    acente_cari_id  = db.Column(db.String(20))
    komisyon_yontem = db.Column(db.String(20))
    komisyon_deger  = db.Column(db.Float, default=0)
    komisyon_tutar  = db.Column(db.Float, default=0)
    komisyon_doviz  = db.Column(db.String(5))
    komisyon_aciklama = db.Column(db.String(200))

    # İz
    kullanici       = db.Column(db.String(50))
    guncelleme      = db.Column(db.DateTime, default=datetime.now)

    # İlişkiler
    kalemler        = db.relationship('SiparisKalem', backref='siparis',
                                      lazy=True, cascade='all, delete-orphan',
                                      order_by='SiparisKalem.sira')
    rezervasyonlar  = db.relationship('Rezervasyon', backref='siparis', lazy=True)
    maliyetler      = db.relationship('Maliyet', backref='siparis', lazy=True,
                                       foreign_keys='Maliyet.baglanti_id',
                                       primaryjoin='Maliyet.baglanti_id==Siparis.id')


# ═══════════════════════════════════════════════════════════════════════
# ── SİPARİŞ KALEMLERİ (YENİ) ─────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════
# Bir siparişte birden fazla ürün kalemi olur. ProformaKalem yapısı
# referans alınmıştır, ama siparişe özgü sadeleştirilmiştir.
#
# TÜR-SPESİFİK ALAN KULLANIMI:
#   BLOK   : boy + yukseklik + en + hacim_m3 + tonaj   (birim: m3 veya ton)
#   PLAKA  : boy + yukseklik + kalinlik + m2_toplam    (birim: m2 veya sqft)
#   EBATLI : boy + yukseklik + kalinlik + adet + kasa_ici_adet + m2_toplam
#                                                       (birim: m2, sqft veya adet)
# ═══════════════════════════════════════════════════════════════════════
class SiparisKalem(db.Model):
    __tablename__ = 'siparis_kalem'
    id              = db.Column(db.Integer, primary_key=True, autoincrement=True)
    siparis_id      = db.Column(db.String(20), db.ForeignKey('siparis_kayit.id'),
                                nullable=False, index=True)
    sira            = db.Column(db.Integer, default=1)   # 1, 2, 3, ...

    # ÜRÜN BİLGİLERİ
    urun_tip        = db.Column(db.String(20), nullable=False)  # BLOK / PLAKA / EBATLI
    cins            = db.Column(db.String(100))
    ozellik         = db.Column(db.String(50))                  # Yüzey: polished, honed, leather...
    aciklama        = db.Column(db.String(300))                 # serbest ek not (kalem için)

    # ÖLÇÜLER (cm)
    boy             = db.Column(db.Float)        # genelde "en" boyutu
    yukseklik       = db.Column(db.Float)        # genelde "boy" boyutu
    en              = db.Column(db.Float)        # BLOK için 3. boyut
    kalinlik        = db.Column(db.Float)        # PLAKA / EBATLI
    olcu            = db.Column(db.String(100))  # otomatik string: "60x60x2cm"

    # ADET / MİKTAR
    adet            = db.Column(db.Integer, default=1)   # Plaka sayısı (PLAKA) veya Kasa sayısı (EBATLI)
    kasa_ici_adet   = db.Column(db.Integer, default=1)   # EBATLI: 1 kasada kaç parça
    miktar          = db.Column(db.Float)                # Kullanıcının girdiği toplam (m2, m3, ton, sqft, adet)
    birim           = db.Column(db.String(10))           # m2 / m3 / sqft / ton / adet

    # OTOMATİK HESAPLAMALAR
    m2_toplam       = db.Column(db.Float, default=0)     # (boy*yukseklik/10000) * adet * kasa_ici_adet
    m3_toplam       = db.Column(db.Float, default=0)     # BLOK için (boy*yukseklik*en/1000000) * adet
    sqft_toplam     = db.Column(db.Float, default=0)     # m2 * 10.7639
    kg_toplam       = db.Column(db.Float, default=0)     # opsiyonel (m²*m2_kg gibi)

    # FİYAT
    birim_fiyat     = db.Column(db.Float)         # miktar başına fiyat (m2'de USD/m²)
    toplam_fiyat    = db.Column(db.Float)         # birim_fiyat * miktar
    doviz           = db.Column(db.String(5), default='USD')  # sipariş dövizinden inherit

    # STOK BAĞLANTISI (Çoklu destek)
    stoktan_geldi   = db.Column(db.Boolean, default=False)
    stok_ids_json   = db.Column(db.Text)  # JSON array: ["PLK-001","PLK-002"]
    # (Tek alanda saklanır, rezervasyon kayıtları her stok için ayrı oluşur)

    # İz
    notlar          = db.Column(db.Text)
    olusturma       = db.Column(db.DateTime, default=datetime.now)
    guncelleme      = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


# ── REZERVASYON ───────────────────────────────────────────────────────
# FAZ 16: siparis_kalem_id eklendi (hangi kaleme bağlı olduğu)
class Rezervasyon(db.Model):
    __tablename__ = 'rezervasyon'
    id              = db.Column(db.String(20), primary_key=True)
    musteri         = db.Column(db.String(100))
    siparis_id      = db.Column(db.String(20), db.ForeignKey('siparis_kayit.id'), nullable=True)
    siparis_kalem_id = db.Column(db.Integer, db.ForeignKey('siparis_kalem.id'), nullable=True)  # YENİ
    proforma_id     = db.Column(db.String(20), db.ForeignKey('proforma.id'), nullable=True)
    stok_tip        = db.Column(db.String(10))
    cins            = db.Column(db.String(100))
    ozellik         = db.Column(db.String(50))
    stok_id         = db.Column(db.String(20))
    miktar          = db.Column(db.Float)
    aciklama        = db.Column(db.Text)
    rez_tip         = db.Column(db.String(50))
    kullanici       = db.Column(db.String(50))
    olusturma       = db.Column(db.DateTime, default=datetime.now)
    bitis_tarihi    = db.Column(db.Date)
    iptal_nedeni    = db.Column(db.String(200))
    iptal_tarihi    = db.Column(db.DateTime)
    iptal_eden      = db.Column(db.String(80))

# ── CARİ ──────────────────────────────────────────────────────────────
class Cari(db.Model):
    __tablename__ = 'cariler'
    id              = db.Column(db.String(20), primary_key=True)
    unvan           = db.Column(db.String(200), nullable=False)
    cari_tip        = db.Column(db.String(30))
    vergi_dairesi   = db.Column(db.String(100))
    vergi_no        = db.Column(db.String(20))
    para_birimi     = db.Column(db.String(5), default='USD')
    yetkili         = db.Column(db.String(100))
    telefon         = db.Column(db.String(30))
    email           = db.Column(db.String(100))
    adres           = db.Column(db.Text)
    iban            = db.Column(db.String(50))
    ulke            = db.Column(db.String(80))
    risk_limiti     = db.Column(db.Float)
    uretici_kisaltma = db.Column(db.String(5))
    urun_tedarikcisi = db.Column(db.Boolean, default=False)
    aciklama        = db.Column(db.Text)
    olusturma       = db.Column(db.DateTime, default=datetime.now)
    hareketler      = db.relationship('CariHareket', backref='cari_hesap',
                                      lazy=True, cascade='all, delete-orphan')

class CariHareket(db.Model):
    __tablename__ = 'cari_hareket'
    id              = db.Column(db.String(20), primary_key=True)
    hareket_tarihi  = db.Column(db.Date, default=date.today)
    cari_unvan      = db.Column(db.String(200))
    cari_id         = db.Column(db.String(20), db.ForeignKey('cariler.id'), nullable=True)
    islem_tip       = db.Column(db.String(50))
    evrak_no        = db.Column(db.String(50))
    aciklama        = db.Column(db.Text)
    borc            = db.Column(db.Float, default=0)
    alacak          = db.Column(db.Float, default=0)
    doviz           = db.Column(db.String(5))
    vade_tarihi     = db.Column(db.Date)
    kur_uygulanan   = db.Column(db.Float, default=0)
    kur_kaynak      = db.Column(db.String(10), default='TCMB')
    borc_try        = db.Column(db.Float, default=0)
    alacak_try      = db.Column(db.Float, default=0)
    kapatildi       = db.Column(db.Boolean, default=False)
    kapanis_hareket_id = db.Column(db.String(20))
    usd_kur         = db.Column(db.Float)
    eur_kur         = db.Column(db.Float)
    bakiye_try      = db.Column(db.Float)
    bakiye_usd      = db.Column(db.Float)
    bakiye_eur      = db.Column(db.Float)
    siparis_id      = db.Column(db.String(20))
    kaynak          = db.Column(db.String(30), default='manuel')
    baglanti_tip    = db.Column(db.String(20))
    baglanti_id     = db.Column(db.String(20))
    kullanici       = db.Column(db.String(50))
    guncelleme      = db.Column(db.DateTime, default=datetime.now)

# ── FATURA ────────────────────────────────────────────────────────────
class Fatura(db.Model):
    __tablename__ = 'faturalar'
    id              = db.Column(db.String(20), primary_key=True)
    fatura_no       = db.Column(db.String(50))
    fatura_tarihi   = db.Column(db.Date, default=date.today)
    vade_tarihi     = db.Column(db.Date)
    proforma_id     = db.Column(db.String(20))
    siparis_id      = db.Column(db.String(20))
    musteri         = db.Column(db.String(200))
    musteri_adres   = db.Column(db.Text)
    musteri_ulke    = db.Column(db.String(80))
    toplam          = db.Column(db.Float, default=0)
    ara_toplam      = db.Column(db.Float, default=0)
    kdv_oran        = db.Column(db.Float, default=0)
    kdv_tutar       = db.Column(db.Float, default=0)
    doviz           = db.Column(db.String(5), default='USD')
    odeme_sekli     = db.Column(db.String(50))
    teslim_sekli    = db.Column(db.String(50))
    durum           = db.Column(db.String(30), default='Taslak')
    aciklama        = db.Column(db.Text)
    kalemler_json   = db.Column(db.Text)
    fatura_tipi     = db.Column(db.String(20), default='stoklu')
    yon             = db.Column(db.String(10), default='satis')
    kur_farki_modu  = db.Column(db.String(10), default='gider')
    cari_hareket_id = db.Column(db.String(20))
    satis_tipi      = db.Column(db.String(30), default='ihracat')
    tevkifat_oran   = db.Column(db.String(10), default='')
    tevkifat_tutar  = db.Column(db.Float, default=0)
    alis_maliyeti   = db.Column(db.Float, default=0)
    maliyet_doviz   = db.Column(db.String(5), default='USD')
    maliyet_kalemleri_json = db.Column(db.Text)
    olusturma       = db.Column(db.DateTime, default=datetime.now)
    kullanici       = db.Column(db.String(50))

# ── MALİYET ───────────────────────────────────────────────────────────
class Maliyet(db.Model):
    __tablename__ = 'maliyetler'
    id              = db.Column(db.String(20), primary_key=True)
    maliyet_tarihi  = db.Column(db.Date, default=date.today)
    maliyet_tip     = db.Column(db.String(50))
    baglanti_tip    = db.Column(db.String(20))
    baglanti_id     = db.Column(db.String(20))
    tutar           = db.Column(db.Float)
    doviz           = db.Column(db.String(5))
    kur             = db.Column(db.Float)
    try_karsilik    = db.Column(db.Float)
    usd_karsilik    = db.Column(db.Float)
    eur_karsilik    = db.Column(db.Float)
    fatura_no       = db.Column(db.String(50))
    aciklama        = db.Column(db.Text)
    kullanici       = db.Column(db.String(50))
    guncelleme      = db.Column(db.DateTime, default=datetime.now)
    grup_id         = db.Column(db.String(20), nullable=True)
    toplam_miktar   = db.Column(db.Float, nullable=True)
    birim_maliyet   = db.Column(db.Float, nullable=True)
    aktif           = db.Column(db.Boolean, default=True, nullable=False)
    donusum_id      = db.Column(db.String(20), nullable=True)
    donusum_tarihi  = db.Column(db.Date, nullable=True)

# ── SEVKİYAT ──────────────────────────────────────────────────────────
class Sevkiyat(db.Model):
    __tablename__ = 'sevkiyat_kayit'
    id              = db.Column(db.String(20), primary_key=True)
    sevk_tarihi     = db.Column(db.Date, default=date.today)
    sevk_tip        = db.Column(db.String(30))
    siparis_id      = db.Column(db.String(20), db.ForeignKey('siparis_kayit.id'), nullable=True)
    siparis_li      = db.Column(db.String(15))
    musteri         = db.Column(db.String(100))
    cikis_noktasi   = db.Column(db.String(100))
    varis_noktasi   = db.Column(db.String(100))
    tah_yukleme     = db.Column(db.Date)
    tah_teslim      = db.Column(db.Date)
    gercek_teslim   = db.Column(db.Date)
    hazirlama_tarihi = db.Column(db.Date)
    cikis_tarihi    = db.Column(db.Date)
    gumruk_tarihi   = db.Column(db.Date)
    teslim_tarihi   = db.Column(db.Date)
    iptal_tarihi    = db.Column(db.Date)
    durum           = db.Column(db.String(30), default='Hazirlaniyor')
    nakliye_firma   = db.Column(db.String(100))
    arac_plaka      = db.Column(db.String(20))
    sofor           = db.Column(db.String(100))
    konteyner_no    = db.Column(db.String(50))
    doseme          = db.Column(db.String(50))
    belge_no        = db.Column(db.String(50))
    belge_tip       = db.Column(db.String(30))
    aciklama        = db.Column(db.Text)
    sofor_adi       = db.Column(db.String(100))
    sofor_tc        = db.Column(db.String(20))
    kullanici       = db.Column(db.String(50))
    guncelleme      = db.Column(db.DateTime, default=datetime.now)

# ── KUR ───────────────────────────────────────────────────────────────
class DovizKur(db.Model):
    __tablename__ = 'doviz_kur'
    id          = db.Column(db.Integer, primary_key=True)
    tarih       = db.Column(db.Date, default=date.today)
    doviz       = db.Column(db.String(5))
    alis        = db.Column(db.Float)
    satis       = db.Column(db.Float)
    efektif     = db.Column(db.Float)
    kaynak      = db.Column(db.String(20), default='TCMB')

# ── VERILER (lookup) ───────────────────────────────────────────────────
class Veriler(db.Model):
    __tablename__ = 'veriler'
    id          = db.Column(db.Integer, primary_key=True)
    kategori    = db.Column(db.String(30))
    deger       = db.Column(db.String(200))
    kisaltma    = db.Column(db.String(10))
    ek_bilgi    = db.Column(db.String(200))

# ── BANKA ──────────────────────────────────────────────────────────────
class Banka(db.Model):
    __tablename__ = 'banka'
    id          = db.Column(db.Integer, primary_key=True)
    banka_adi   = db.Column(db.String(100), nullable=False)
    sube        = db.Column(db.String(100))
    hesap_no    = db.Column(db.String(50))
    iban        = db.Column(db.String(50))
    swift       = db.Column(db.String(20))
    doviz       = db.Column(db.String(5), default='USD')
    aciklama    = db.Column(db.String(200))
    varsayilan  = db.Column(db.Boolean, default=False)
    aktif       = db.Column(db.Boolean, default=True)
    olusturma   = db.Column(db.DateTime, default=datetime.now)

# ── KASA ──────────────────────────────────────────────────────────────
class Kasa(db.Model):
    __tablename__ = 'kasa'
    id          = db.Column(db.Integer, primary_key=True)
    ad          = db.Column(db.String(100), nullable=False)
    doviz       = db.Column(db.String(5), default='TRY')
    bakiye      = db.Column(db.Float, default=0)
    ana_kasa    = db.Column(db.Boolean, default=False, nullable=False)
    aciklama    = db.Column(db.String(200))
    varsayilan  = db.Column(db.Boolean, default=False)
    aktif       = db.Column(db.Boolean, default=True)
    olusturma   = db.Column(db.DateTime, default=datetime.now)

class KasaHareket(db.Model):
    __tablename__ = 'kasa_hareket'
    id              = db.Column(db.Integer, primary_key=True)
    kasa_id         = db.Column(db.Integer, db.ForeignKey('kasa.id'), nullable=False)
    tarih           = db.Column(db.Date, default=date.today)
    tip             = db.Column(db.String(10), nullable=False)
    tutar           = db.Column(db.Float, nullable=False)
    aciklama        = db.Column(db.String(300))
    baglanti_tip    = db.Column(db.String(20))
    baglanti_id     = db.Column(db.String(50))
    cari_id         = db.Column(db.String(20))
    kullanici       = db.Column(db.String(50))
    olusturma       = db.Column(db.DateTime, default=datetime.now)
    kasa            = db.relationship('Kasa', backref='hareketler', lazy=True)

# ── KESİM ─────────────────────────────────────────────────────────────
class Kesim(db.Model):
    __tablename__ = 'kesim'
    id              = db.Column(db.String(20), primary_key=True)
    kesim_tarihi    = db.Column(db.Date, default=date.today)
    kaynak_tip      = db.Column(db.String(10), nullable=False)
    kaynak_id       = db.Column(db.String(20), nullable=False)
    kaynak_ids_json = db.Column(db.Text)
    kaynak_no       = db.Column(db.String(50))
    kaynak_cins     = db.Column(db.String(50))
    kaynak_miktar_once  = db.Column(db.Float)
    kaynak_miktar_sonra = db.Column(db.Float, default=0)
    kaynak_durum    = db.Column(db.String(20), default='Kismi')
    kaynak_birim_maliyet  = db.Column(db.Float)
    kaynak_toplam_maliyet = db.Column(db.Float)
    kaynak_doviz    = db.Column(db.String(5), default='USD')
    # Üretim Blok No: kesilen bloktan üretilen plakaların yeni blok numarası.
    # Hem orijinal blok no (kaynak_no) hem de bu yeni üretim blok no
    # üzerinden tüm takip (maliyet, karlılık, izleme) yapılabilir.
    uretim_blok_no  = db.Column(db.String(50))
    fire_orani      = db.Column(db.Float, default=0)
    fire_miktar     = db.Column(db.Float, default=0)
    aciklama        = db.Column(db.String(300))
    kullanici       = db.Column(db.String(50))
    olusturma       = db.Column(db.DateTime, default=datetime.now)
    detaylar        = db.relationship('KesimDetay', backref='kesim', lazy=True, cascade='all, delete-orphan')

class KesimDetay(db.Model):
    __tablename__ = 'kesim_detay'
    id              = db.Column(db.Integer, primary_key=True)
    kesim_id        = db.Column(db.String(20), db.ForeignKey('kesim.id'), nullable=False)
    hedef_tip       = db.Column(db.String(10), nullable=False)
    hedef_stok_id   = db.Column(db.String(20))
    cins            = db.Column(db.String(50))
    boy             = db.Column(db.Float)
    yukseklik       = db.Column(db.Float)
    kalinlik        = db.Column(db.Float)
    en              = db.Column(db.Float)
    miktar_m2       = db.Column(db.Float)
    adet            = db.Column(db.Integer, default=1)
    kasa_no         = db.Column(db.String(50))
    slab_no         = db.Column(db.String(50))
    ozellik         = db.Column(db.String(100))
    birim_maliyet   = db.Column(db.Float)
    toplam_maliyet  = db.Column(db.Float)
    aciklama        = db.Column(db.String(200))

# ── PROFORMA ──────────────────────────────────────────────────────────
class Proforma(db.Model):
    __tablename__ = 'proforma'
    id              = db.Column(db.String(20), primary_key=True)
    olusturma       = db.Column(db.DateTime, default=datetime.now)
    siparis_id      = db.Column(db.String(20), db.ForeignKey('siparis_kayit.id'), nullable=True)
    musteri         = db.Column(db.String(200))
    musteri_adres   = db.Column(db.Text)
    musteri_ulke    = db.Column(db.String(100))
    urun_tip        = db.Column(db.String(20))
    cins            = db.Column(db.String(100))
    ozellik         = db.Column(db.String(50))
    olcu            = db.Column(db.String(200))
    adet            = db.Column(db.Integer, default=1)
    birim_fiyat     = db.Column(db.Float)
    miktar          = db.Column(db.Float)
    birim           = db.Column(db.String(20))
    doviz           = db.Column(db.String(5), default='USD')
    toplam          = db.Column(db.Float)
    odeme_sekli     = db.Column(db.String(50))
    teslim_sekli    = db.Column(db.String(20))
    termin          = db.Column(db.Date)
    yuklenme_limani = db.Column(db.String(100))
    varis_limani    = db.Column(db.String(100))
    banka_adi       = db.Column(db.String(100))
    iban            = db.Column(db.String(50))
    ulke            = db.Column(db.String(80))
    swift           = db.Column(db.String(20))
    satici_firma    = db.Column(db.String(200))
    satici_adres    = db.Column(db.Text)
    satici_tel      = db.Column(db.String(50))
    satici_email    = db.Column(db.String(100))
    notlar          = db.Column(db.Text)
    ozel_sartlar    = db.Column(db.Text)
    konteyner_no    = db.Column(db.String(100))
    hs_kodu         = db.Column(db.String(30), default='680221000019')
    iskonto         = db.Column(db.Float, default=0)
    iskonto_tip     = db.Column(db.String(5), default='%')
    iskonto_sabit   = db.Column(db.Float, default=0)
    avans_yuzdesi   = db.Column(db.Float, default=0)
    avans_tutari    = db.Column(db.Float, default=0)
    avans_tip       = db.Column(db.String(5), default='%')
    avans_sabit     = db.Column(db.Float, default=0)
    tur             = db.Column(db.String(20), default='ihracat')
    kdv_oran        = db.Column(db.Float, default=0)
    packing_list    = db.Column(db.Boolean, default=False)
    genel_bundle_sayisi = db.Column(db.Integer, default=10)
    karma_bundle    = db.Column(db.Boolean, default=False)
    kullanici       = db.Column(db.String(50))
    durum           = db.Column(db.String(20), default='Taslak')
    proforma_tipi   = db.Column(db.String(20), default='satis')
    kalemler        = db.relationship('ProformaKalem', backref='proforma', lazy=True, cascade='all, delete-orphan')

class ProformaKalem(db.Model):
    __tablename__ = 'proforma_kalem'
    id              = db.Column(db.Integer, primary_key=True, autoincrement=True)
    proforma_id     = db.Column(db.String(20), db.ForeignKey('proforma.id'), nullable=False)
    konteyner_no    = db.Column(db.String(20))
    kap_no          = db.Column(db.String(20))
    kap_tip         = db.Column(db.String(20))
    urun_tip        = db.Column(db.String(20))
    cins            = db.Column(db.String(100))
    aciklama        = db.Column(db.String(200))
    yuzey_spec      = db.Column(db.String(50))
    ozellik         = db.Column(db.String(50))
    kalinlik        = db.Column(db.Float)
    en              = db.Column(db.Float)
    boy             = db.Column(db.Float)
    yukseklik       = db.Column(db.Float)
    adet            = db.Column(db.Integer, default=1)
    kasa_ici_adet   = db.Column(db.Integer, default=1)
    miktar          = db.Column(db.Float)
    birim           = db.Column(db.String(10))
    agirlik         = db.Column(db.Float)
    agirlik_birim   = db.Column(db.String(5), default='KG')
    birim_fiyat     = db.Column(db.Float)
    toplam_fiyat    = db.Column(db.Float)
    net_fiyat       = db.Column(db.Float)
    iskonto         = db.Column(db.Float, default=0)
    iskonto_tip     = db.Column(db.String(5), default='%')
    iskonto_sabit   = db.Column(db.Float, default=0)
    doviz           = db.Column(db.String(5), default='USD')
    avans_yuzdesi   = db.Column(db.Float, default=0)
    avans_oran      = db.Column(db.Float, default=0)
    sira            = db.Column(db.Integer, default=0)
    olcu            = db.Column(db.String(100))
    notlar          = db.Column(db.Text)
    blok_no         = db.Column(db.String(50))
    bundle_no       = db.Column(db.String(50))
    slab_no         = db.Column(db.Text)
    stok_id         = db.Column(db.String(20))
    m2_toplam       = db.Column(db.Float)
    sqft_toplam     = db.Column(db.Float)

# ── SATIŞ KAYDI ────────────────────────────────────────────────────────
# FAZ 16: siparis_kalem_id eklendi
class SatisKaydi(db.Model):
    __tablename__ = 'satis_kaydi'
    id              = db.Column(db.String(30), primary_key=True)
    stok_id         = db.Column(db.String(50), index=True)
    stok_tip        = db.Column(db.String(10))
    cins            = db.Column(db.String(100))
    ozellik         = db.Column(db.String(100))
    blok_no         = db.Column(db.String(50))
    boy             = db.Column(db.Float)
    yukseklik       = db.Column(db.Float)
    kalinlik        = db.Column(db.Float)
    en              = db.Column(db.Float)
    metraj_m2       = db.Column(db.Float)
    metraj_sqft     = db.Column(db.Float)
    hacim_m3        = db.Column(db.Float)
    tonaj           = db.Column(db.Float)
    agirlik_kg      = db.Column(db.Float)
    siparis_id      = db.Column(db.String(20), db.ForeignKey('siparis_kayit.id'), nullable=True, index=True)
    siparis_kalem_id = db.Column(db.Integer, db.ForeignKey('siparis_kalem.id'), nullable=True, index=True)  # YENİ
    proforma_id     = db.Column(db.String(20), db.ForeignKey('proforma.id'), nullable=True, index=True)
    sevkiyat_id     = db.Column(db.String(20), nullable=True)
    musteri         = db.Column(db.String(200), index=True)
    musteri_ulke    = db.Column(db.String(50))
    satis_tarihi    = db.Column(db.Date, default=date.today)
    teslim_tarihi   = db.Column(db.Date)
    olusturma       = db.Column(db.DateTime, default=datetime.now)
    birim_fiyat     = db.Column(db.Float)
    miktar          = db.Column(db.Float)
    birim           = db.Column(db.String(10))
    doviz           = db.Column(db.String(5))
    tutar           = db.Column(db.Float)
    kur_usd         = db.Column(db.Float)
    kur_eur         = db.Column(db.Float)
    tutar_usd       = db.Column(db.Float)
    tutar_try       = db.Column(db.Float)
    maliyet_usd     = db.Column(db.Float, default=0)
    maliyet_try     = db.Column(db.Float, default=0)
    kar_usd         = db.Column(db.Float, default=0)
    marj_yuzde      = db.Column(db.Float, default=0)
    fatura_id       = db.Column(db.String(20))
    kaynak          = db.Column(db.String(20), default='teslim')
    fatura_no       = db.Column(db.String(50))
    fatura_tarihi   = db.Column(db.Date)
    notlar          = db.Column(db.Text)
    kullanici       = db.Column(db.String(50))
    guncelleme      = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

# ── ÇEK / SENET ───────────────────────────────────────────────────────
class Cek(db.Model):
    """Alınan (müşteriden) ve verilen (tedarikçiye) çekler/senetler.
    Bir çek yaşam döngüsünden geçer: portföy → tahsilde/ciro/teminat → tahsil/öded."""
    __tablename__ = 'cek'
    id              = db.Column(db.String(20), primary_key=True)  # CEK-0001 gibi
    # Yön: 'alinan' (müşteriden aldık, bizim alacağımız) | 'verilen' (tedarikçiye verdik, borcumuz)
    yon             = db.Column(db.String(10), nullable=False)
    tip             = db.Column(db.String(10), default='cek')  # 'cek' | 'senet'
    # Çek üzerindeki bilgiler
    cek_no          = db.Column(db.String(50))      # çek numarası
    banka_adi       = db.Column(db.String(100))     # çeki yazan banka (alınan çekte müşterinin bankası)
    sube            = db.Column(db.String(100))
    hesap_sahibi    = db.Column(db.String(200))     # çeki düzenleyen (keşideci)
    tutar           = db.Column(db.Float, nullable=False)
    doviz           = db.Column(db.String(5), default='TRY')
    keside_tarihi   = db.Column(db.Date)            # düzenlenme tarihi
    vade_tarihi     = db.Column(db.Date, nullable=False)  # tahsil/ödeme tarihi (en kritik alan)
    # Cari bağlantısı (kimden aldık / kime verdik)
    cari_id         = db.Column(db.String(20), db.ForeignKey('cariler.id'))
    cari_unvan      = db.Column(db.String(200))
    # Durum: çekin güncel hali
    #  alinan için:  Portfoyde, TahsildeBanka, Tahsil Edildi, Ciro Edildi, Teminatta, Karsiliksiz, Iade Edildi
    #  verilen için: Verildi, Odendi, Karsiliksiz, Iade Alindi
    durum           = db.Column(db.String(20), default='Portfoyde')
    # İlişkili kayıtlar
    tahsil_banka_id = db.Column(db.Integer, db.ForeignKey('banka.id'))  # tahsile/teminata verilen banka
    ciro_cari_id    = db.Column(db.String(20))      # ciro edildiyse kime
    ciro_cari_unvan = db.Column(db.String(200))
    fatura_id       = db.Column(db.String(20))      # hangi faturaya karşılık (opsiyonel)
    cari_hareket_id = db.Column(db.String(30))      # çek tahsil/ödeme olunca oluşan cari hareket
    kasa_hareket_id = db.Column(db.Integer)         # kasaya/bankaya işlenince
    # Meta
    aciklama        = db.Column(db.String(300))
    aktif           = db.Column(db.Boolean, default=True)  # iptal edilirse False
    kullanici       = db.Column(db.String(50))
    olusturma       = db.Column(db.DateTime, default=datetime.now)
    guncelleme      = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


class CekHareket(db.Model):
    """Bir çekin yaşam döngüsündeki her durum değişikliğinin kaydı (geçmiş/log)."""
    __tablename__ = 'cek_hareket'
    id              = db.Column(db.Integer, primary_key=True)
    cek_id          = db.Column(db.String(20), db.ForeignKey('cek.id'), nullable=False)
    tarih           = db.Column(db.Date, default=date.today)
    islem           = db.Column(db.String(40))   # 'Alındı', 'Tahsile Verildi', 'Tahsil Edildi', 'Ciro Edildi', 'Teminata Verildi', 'Karşılıksız', 'İade' ...
    onceki_durum    = db.Column(db.String(20))
    yeni_durum      = db.Column(db.String(20))
    aciklama        = db.Column(db.String(300))
    kullanici       = db.Column(db.String(50))
    olusturma       = db.Column(db.DateTime, default=datetime.now)
    cek             = db.relationship('Cek', backref='hareketler', lazy=True)


# ── AUDIT LOG ─────────────────────────────────────────────────────────
class AuditLog(db.Model):
    __tablename__ = 'audit_log'
    id              = db.Column(db.Integer, primary_key=True)
    tarih           = db.Column(db.DateTime, default=datetime.utcnow)
    kullanici       = db.Column(db.String(100))
    islem_tipi      = db.Column(db.String(50))
    tablo_adi       = db.Column(db.String(50))
    kayit_id        = db.Column(db.String(50))
    eski_veri       = db.Column(db.Text)
    yeni_veri       = db.Column(db.Text)
    ip_adresi       = db.Column(db.String(50))
    
    
