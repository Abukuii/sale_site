import sqlite3
from datetime import date, datetime
from config import DB_PATH


def get_connection():
    return sqlite3.connect(DB_PATH)


def get_daily_report() -> dict:
    """Bugungi savdo hisobotini qaytaradi."""
    conn = get_connection()
    cur = conn.cursor()
    bugun = date.today().isoformat()

    # Jami savdolar soni va summalar
    cur.execute("""
        SELECT
            COUNT(*) as soni,
            COALESCE(SUM(CASE WHEN tolov_turi='naqd' THEN jami_summa ELSE 0 END), 0) as naqd,
            COALESCE(SUM(CASE WHEN tolov_turi='plastik' THEN jami_summa ELSE 0 END), 0) as plastik,
            COALESCE(SUM(CASE WHEN tolov_turi='nasiya' THEN jami_summa ELSE 0 END), 0) as nasiya,
            COALESCE(SUM(jami_summa), 0) as jami
        FROM crm_savdo
        WHERE sana = ?
    """, (bugun,))
    row = cur.fetchone()

    if not row or row[0] == 0:
        conn.close()
        return {}

    # Top 3 eng ko'p sotilgan mahsulot
    cur.execute("""
        SELECT m.nomi, SUM(si.soni) as jami_son
        FROM crm_savdoitem si
        JOIN crm_mahsulot m ON si.mahsulot_id = m.id
        JOIN crm_savdo s ON si.savdo_id = s.id
        WHERE s.sana = ?
        GROUP BY m.id, m.nomi
        ORDER BY jami_son DESC
        LIMIT 3
    """, (bugun,))
    top = [{"nomi": r[0], "soni": r[1]} for r in cur.fetchall()]

    # Bugun qo'shilgan nasiyalar soni
    cur.execute("""
        SELECT COUNT(*) FROM crm_savdo
        WHERE sana = ? AND tolov_turi = 'nasiya'
    """, (bugun,))
    yangi_nasiya = cur.fetchone()[0]

    conn.close()
    return {
        "sana": date.today().strftime("%d.%m.%Y"),
        "savdolar_soni": row[0],
        "naqd": int(row[1]),
        "plastik": int(row[2]),
        "nasiya": int(row[3]),
        "jami": int(row[4]),
        "top_mahsulotlar": top,
        "yangi_qarzdorlar": yangi_nasiya,
    }


def get_monthly_stats() -> dict:
    """Joriy oylik statistikani qaytaradi."""
    conn = get_connection()
    cur = conn.cursor()
    bugun = date.today()
    oy_boshi = bugun.replace(day=1).isoformat()

    cur.execute("""
        SELECT
            COUNT(*) as soni,
            COALESCE(SUM(jami_summa), 0) as jami,
            COALESCE(SUM(CASE WHEN tolov_turi='nasiya' THEN jami_summa ELSE 0 END), 0) as nasiya
        FROM crm_savdo
        WHERE sana >= ?
    """, (oy_boshi,))
    row = cur.fetchone()

    # Yangi mijozlar
    cur.execute("""
        SELECT COUNT(*) FROM crm_mijoz
        WHERE DATE(yaratilgan) >= ?
    """, (oy_boshi,))
    yangi_mijozlar = cur.fetchone()[0]

    # Eng ko'p sotilgan mahsulot
    cur.execute("""
        SELECT m.nomi, SUM(si.soni) as jami_son
        FROM crm_savdoitem si
        JOIN crm_mahsulot m ON si.mahsulot_id = m.id
        JOIN crm_savdo s ON si.savdo_id = s.id
        WHERE s.sana >= ?
        GROUP BY m.id, m.nomi
        ORDER BY jami_son DESC
        LIMIT 1
    """, (oy_boshi,))
    top = cur.fetchone()

    conn.close()

    oy_nomi = bugun.strftime("%B %Y")
    return {
        "oy": oy_nomi,
        "savdolar_soni": row[0],
        "jami_daromad": int(row[1]),
        "nasiya_jami": int(row[2]),
        "yangi_mijozlar": yangi_mijozlar,
        "top_mahsulot": f"{top[0]} ({top[1]} ta)" if top else "—",
    }


def get_qarzdorlar() -> list:
    """Barcha to'lanmagan nasiya mijozlarni qaytaradi."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            mj.ism_familiya,
            mj.telefon,
            COALESCE(SUM(s.jami_summa), 0) as jami_qarz
        FROM crm_mijoz mj
        JOIN crm_savdo s ON s.mijoz_id = mj.id
        WHERE s.to_langan = 0
        GROUP BY mj.id, mj.ism_familiya, mj.telefon
        ORDER BY jami_qarz DESC
    """)
    rows = cur.fetchall()
    conn.close()

    return [
        {"ism": r[0], "telefon": r[1], "qarz": int(r[2])}
        for r in rows
    ]
