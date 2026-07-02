# -*- coding: utf-8 -*-
"""
Milestone ERP - Yedekleme Modülü (PostgreSQL)
PostgreSQL veritabanını pg_dump ile yedekler, eski yedekleri temizler,
pg_restore ile geri yükler.

Aynı fonksiyon arayüzünü korur (flask_app.py değişmeden çalışır):
  yedek_al(tip), yedek_listesi(), yedek_geri_yukle(dosya), yedek_sil(dosya), BACKUP_DIR

ÖNEMLİ: pg_dump/pg_restore/psql araçları PATH'te yoksa, Windows'taki tipik
PostgreSQL kurulum klasörlerinde otomatik aranır.
"""
import os
import re
import glob
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, unquote

BASE_DIR = Path(__file__).parent
BACKUP_DIR = BASE_DIR / 'backups'
MAX_BACKUPS = 30
YEDEK_UZANTI = '.dump'
_ARAC_CACHE = {}


def _arac_bul(arac_adi):
    """pg_dump / pg_restore / psql aracının tam yolunu bul.
    Önce PATH'e bakar, bulamazsa tipik kurulum yerlerinde arar."""
    if arac_adi in _ARAC_CACHE:
        return _ARAC_CACHE[arac_adi]

    exe = arac_adi + ('.exe' if os.name == 'nt' else '')
    # 1) PATH'te dene
    try:
        r = subprocess.run([arac_adi, '--version'],
                           capture_output=True, text=True, timeout=10)
        if r.returncode == 0:
            _ARAC_CACHE[arac_adi] = arac_adi
            return arac_adi
    except Exception:
        pass

    # 2) Tipik kurulum yerleri
    if os.name == 'nt':
        desenler = [
            r'C:\Program Files\PostgreSQL\*\bin',
            r'C:\Program Files (x86)\PostgreSQL\*\bin',
            r'C:\PostgreSQL\*\bin',
        ]
    else:
        desenler = [
            '/usr/lib/postgresql/*/bin',
            '/usr/pgsql-*/bin',
            '/usr/local/pgsql/bin',
            '/opt/homebrew/opt/postgresql*/bin',
        ]

    bulunanlar = []
    for desen in desenler:
        for bin_dir in glob.glob(desen):
            aday = os.path.join(bin_dir, exe)
            if os.path.isfile(aday):
                bulunanlar.append(aday)

    if bulunanlar:
        bulunanlar.sort(reverse=True)
        _ARAC_CACHE[arac_adi] = bulunanlar[0]
        logging.info(f"{arac_adi} bulundu: {bulunanlar[0]}")
        return bulunanlar[0]

    _ARAC_CACHE[arac_adi] = None
    return None


def _db_baglanti_bilgisi():
    """DATABASE_URL'den PostgreSQL bağlantı parçalarını çıkarır."""
    db_url = os.environ.get(
        'DATABASE_URL',
        'postgresql://postgres:postgres@localhost:5432/milestone'
    )
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    if not db_url.startswith('postgresql'):
        return None
    try:
        p = urlparse(db_url)
        return {
            'host': p.hostname or 'localhost',
            'port': str(p.port or 5432),
            'user': unquote(p.username) if p.username else 'postgres',
            'password': unquote(p.password) if p.password else '',
            'dbname': (p.path or '/milestone').lstrip('/') or 'milestone',
        }
    except Exception as e:
        logging.error(f"DATABASE_URL ayrıştırma hatası: {e}")
        return None


def _pg_ortam(conn):
    env = os.environ.copy()
    if conn.get('password'):
        env['PGPASSWORD'] = conn['password']
    return env


def ensure_backup_dir():
    BACKUP_DIR.mkdir(exist_ok=True)


def tani():
    """Yedekleme sisteminin durumunu kontrol eder (sorun giderme)."""
    sonuc = {
        'pg_dump_bulundu': False, 'pg_dump_yol': None,
        'pg_restore_bulundu': False, 'pg_restore_yol': None,
        'baglanti_ok': False, 'db_bilgisi': None,
        'backup_dir': str(BACKUP_DIR), 'backup_dir_var': BACKUP_DIR.exists(),
        'yedek_sayisi': 0, 'mesaj': '',
    }
    pgd = _arac_bul('pg_dump')
    sonuc['pg_dump_bulundu'] = pgd is not None
    sonuc['pg_dump_yol'] = pgd
    pgr = _arac_bul('pg_restore')
    sonuc['pg_restore_bulundu'] = pgr is not None
    sonuc['pg_restore_yol'] = pgr
    conn = _db_baglanti_bilgisi()
    if conn:
        sonuc['baglanti_ok'] = True
        sonuc['db_bilgisi'] = f"{conn['host']}:{conn['port']}/{conn['dbname']} (kullanıcı: {conn['user']})"
    if BACKUP_DIR.exists():
        sonuc['yedek_sayisi'] = len(list(BACKUP_DIR.glob(f'milestone_*{YEDEK_UZANTI}')))
    if not pgd:
        sonuc['mesaj'] = "pg_dump bulunamadı. PostgreSQL kurulu mu? bin klasörü PATH'te mi?"
    elif not conn:
        sonuc['mesaj'] = 'DATABASE_URL çözülemedi (.env dosyasını kontrol edin).'
    else:
        sonuc['mesaj'] = 'Yedekleme sistemi hazır.'
    return sonuc


def yedek_al(tip='auto'):
    """PostgreSQL veritabanının yedeğini pg_dump ile al (custom format)."""
    conn = _db_baglanti_bilgisi()
    if not conn:
        logging.warning("Yedekleme atlandı: PostgreSQL bağlantı bilgisi çözülemedi")
        return None

    pg_dump = _arac_bul('pg_dump')
    if not pg_dump:
        logging.error("pg_dump bulunamadı. PostgreSQL bin klasörü PATH'e ekli olmalı.")
        return None

    ensure_backup_dir()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    yedek_adi = f"milestone_{tip}_{timestamp}{YEDEK_UZANTI}"
    yedek_yolu = BACKUP_DIR / yedek_adi

    cmd = [
        pg_dump, '-h', conn['host'], '-p', conn['port'],
        '-U', conn['user'], '-d', conn['dbname'],
        '-Fc', '-f', str(yedek_yolu),
    ]
    try:
        sonuc = subprocess.run(cmd, env=_pg_ortam(conn),
                               capture_output=True, text=True, timeout=300)
        if sonuc.returncode != 0:
            logging.error(f"pg_dump hatası: {sonuc.stderr.strip()}")
            if yedek_yolu.exists():
                try: yedek_yolu.unlink()
                except Exception: pass
            return None
        logging.info(f"Yedek alındı: {yedek_adi}")
        eski_yedekleri_temizle()
        return str(yedek_yolu)
    except FileNotFoundError:
        logging.error("pg_dump bulunamadı (FileNotFoundError).")
        return None
    except subprocess.TimeoutExpired:
        logging.error("Yedekleme zaman aşımına uğradı (300s)")
        return None
    except Exception as e:
        logging.error(f"Yedekleme hatası: {e}")
        return None


def eski_yedekleri_temizle():
    """Son MAX_BACKUPS auto+manual yedeği tut; pre_restore'a dokunma."""
    ensure_backup_dir()
    yedekler = sorted(
        [p for p in BACKUP_DIR.glob(f'milestone_*{YEDEK_UZANTI}')
         if '_pre_restore_' not in p.name],
        key=lambda p: p.stat().st_mtime, reverse=True
    )
    if len(yedekler) > MAX_BACKUPS:
        for eski in yedekler[MAX_BACKUPS:]:
            try:
                eski.unlink()
                logging.info(f"Eski yedek silindi: {eski.name}")
            except Exception as e:
                logging.error(f"Silme hatası ({eski.name}): {e}")


def yedek_listesi():
    """Mevcut yedekleri en yeniden eskiye doğru listele."""
    ensure_backup_dir()
    yedekler = []
    for p in sorted(BACKUP_DIR.glob(f'milestone_*{YEDEK_UZANTI}'),
                    key=lambda p: p.stat().st_mtime, reverse=True):
        st = p.stat()
        if '_auto_' in p.name:
            tip = 'auto'
        elif '_pre_restore_' in p.name:
            tip = 'pre_restore'
        else:
            tip = 'manual'
        yedekler.append({
            'dosya': p.name,
            'tarih': datetime.fromtimestamp(st.st_mtime).strftime('%d.%m.%Y %H:%M:%S'),
            'boyut_kb': round(st.st_size / 1024, 1),
            'tip': tip
        })
    return yedekler


def yedek_geri_yukle(dosya_adi):
    """Yedekten DB'yi geri yükler (pg_restore --clean). Önce pre_restore yedeği alır."""
    if not re.match(r'^milestone_[\w]+_\d{8}_\d{6}' + re.escape(YEDEK_UZANTI) + r'$', dosya_adi):
        return False, "Geçersiz yedek dosyası adı"

    yedek_yolu = BACKUP_DIR / dosya_adi
    if not yedek_yolu.exists():
        return False, f"Yedek bulunamadı: {dosya_adi}"

    conn = _db_baglanti_bilgisi()
    if not conn:
        return False, "PostgreSQL bağlantı bilgisi çözülemedi"

    pg_restore = _arac_bul('pg_restore')
    if not pg_restore:
        return False, "pg_restore bulunamadı. PostgreSQL bin klasörü PATH'e ekli olmalı."

    try:
        yedek_al('pre_restore')
        cmd = [
            pg_restore, '-h', conn['host'], '-p', conn['port'],
            '-U', conn['user'], '-d', conn['dbname'],
            '--clean', '--if-exists', '--no-owner', '--no-acl',
            str(yedek_yolu),
        ]
        sonuc = subprocess.run(cmd, env=_pg_ortam(conn),
                               capture_output=True, text=True, timeout=300)
        if sonuc.returncode != 0:
            stderr = sonuc.stderr.strip()
            kritik = [s for s in stderr.split('\n')
                      if s and 'does not exist' not in s and 'skipping' not in s
                      and 'warning' not in s.lower()]
            if kritik:
                logging.error(f"pg_restore hatası: {stderr}")
                return False, f"Geri yükleme hatası: {kritik[0][:200]}"
        logging.info(f"Yedek geri yüklendi: {dosya_adi}")
        return True, f"Yedek geri yüklendi: {dosya_adi}. Uygulamayı yeniden başlatın."
    except FileNotFoundError:
        return False, "pg_restore bulunamadı. PostgreSQL bin klasörü PATH'e ekli olmalı."
    except subprocess.TimeoutExpired:
        return False, "Geri yükleme zaman aşımına uğradı (300s)"
    except Exception as e:
        logging.error(f"Geri yükleme hatası: {e}")
        return False, str(e)


def yedek_sil(dosya_adi):
    """Tek bir yedek dosyasını sil."""
    if not re.match(r'^milestone_[\w]+_\d{8}_\d{6}' + re.escape(YEDEK_UZANTI) + r'$', dosya_adi):
        return False, "Geçersiz dosya adı"
    yedek_yolu = BACKUP_DIR / dosya_adi
    if not yedek_yolu.exists():
        return False, "Dosya bulunamadı"
    try:
        yedek_yolu.unlink()
        return True, "Yedek silindi"
    except Exception as e:
        return False, str(e)
