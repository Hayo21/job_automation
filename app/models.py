import sqlite3
import csv
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
from io import StringIO

from app.config import Config


DB_PATH = Path(Config.CV_PATH).parent / "instance" / "lamaran.db"
DB_PATH.parent.mkdir(exist_ok=True)


@dataclass
class Lamaran:
    id: Optional[int]
    perusahaan: str
    posisi: str
    email: str
    kategori: str
    tanggal: str
    status: str
    error: Optional[str] = None
    retry_count: int = 0
    last_retry: Optional[str] = None


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS lamaran (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                perusahaan TEXT NOT NULL,
                posisi TEXT NOT NULL,
                email TEXT NOT NULL,
                kategori TEXT NOT NULL,
                tanggal TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Menunggu',
                error TEXT,
                retry_count INTEGER DEFAULT 0,
                last_retry TEXT
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_lamaran_email ON lamaran(email)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_lamaran_perusahaan ON lamaran(perusahaan)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_lamaran_tanggal ON lamaran(tanggal)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_lamaran_status ON lamaran(status)")
        conn.commit()


def count_today() -> int:
    today = datetime.now().strftime("%Y-%m-%d")
    with get_db() as conn:
        cur = conn.execute("SELECT COUNT(*) FROM lamaran WHERE tanggal LIKE ?", (f"{today}%",))
        return cur.fetchone()[0]


def check_duplicate(perusahaan: str, email: str) -> Optional[Lamaran]:
    with get_db() as conn:
        cur = conn.execute(
            "SELECT * FROM lamaran WHERE email = ? OR perusahaan = ? ORDER BY tanggal DESC LIMIT 1",
            (email, perusahaan)
        )
        row = cur.fetchone()
        if row:
            return Lamaran(**dict(row))
    return None


def save_lamaran(perusahaan: str, posisi: str, email: str, kategori: str, error: Optional[str] = None) -> int:
    tanggal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "Gagal" if error else "Menunggu"
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO lamaran (perusahaan, posisi, email, kategori, tanggal, status, error, retry_count) VALUES (?, ?, ?, ?, ?, ?, ?, 0)",
            (perusahaan, posisi, email, kategori, tanggal, status, error)
        )
        conn.commit()
        return cur.lastrowid


def get_all_lamaran(
    kategori_filter: Optional[str] = None,
    status_filter: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> list[Lamaran]:
    query = "SELECT * FROM lamaran WHERE 1=1"
    params = []
    if kategori_filter:
        query += " AND kategori = ?"
        params.append(kategori_filter)
    if status_filter:
        query += " AND status = ?"
        params.append(status_filter)
    query += " ORDER BY tanggal DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    with get_db() as conn:
        cur = conn.execute(query, params)
        return [Lamaran(**dict(row)) for row in cur.fetchall()]


def update_status(lamaran_id: int, status: str) -> bool:
    valid_status = {"Menunggu", "Dipanggil", "Ditolak", "Gagal"}
    if status not in valid_status:
        return False
    with get_db() as conn:
        cur = conn.execute("UPDATE lamaran SET status = ? WHERE id = ?", (status, lamaran_id))
        conn.commit()
        return cur.rowcount > 0


def get_lamaran_by_id(lamaran_id: int) -> Optional[Lamaran]:
    with get_db() as conn:
        cur = conn.execute("SELECT * FROM lamaran WHERE id = ?", (lamaran_id,))
        row = cur.fetchone()
        if row:
            return Lamaran(**dict(row))
    return None


def retry_lamaran(lamaran_id: int) -> bool:
    with get_db() as conn:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur = conn.execute(
            "UPDATE lamaran SET status = 'Menunggu', error = NULL, retry_count = retry_count + 1, last_retry = ? WHERE id = ?",
            (now, lamaran_id)
        )
        conn.commit()
        return cur.rowcount > 0


def get_stats() -> dict:
    with get_db() as conn:
        total = conn.execute("SELECT COUNT(*) FROM lamaran").fetchone()[0]
        menunggu = conn.execute("SELECT COUNT(*) FROM lamaran WHERE status = 'Menunggu'").fetchone()[0]
        dipanggil = conn.execute("SELECT COUNT(*) FROM lamaran WHERE status = 'Dipanggil'").fetchone()[0]
        ditolak = conn.execute("SELECT COUNT(*) FROM lamaran WHERE status = 'Ditolak'").fetchone()[0]
        gagal = conn.execute("SELECT COUNT(*) FROM lamaran WHERE status = 'Gagal'").fetchone()[0]
        today = count_today()
        # 7 hari reminder
        seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
        reminder = conn.execute(
            "SELECT COUNT(*) FROM lamaran WHERE status = 'Menunggu' AND tanggal < ?",
            (seven_days_ago,)
        ).fetchone()[0]
    return {
        "total": total,
        "menunggu": menunggu,
        "dipanggil": dipanggil,
        "ditolak": ditolak,
        "gagal": gagal,
        "today": today,
        "reminder_7_hari": reminder,
    }


def export_csv() -> str:
    """Return CSV content as string"""
    with get_db() as conn:
        cur = conn.execute("SELECT * FROM lamaran ORDER BY tanggal DESC")
        rows = cur.fetchall()
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Perusahaan", "Posisi", "Email", "Kategori", "Tanggal", "Status", "Error", "Retry Count", "Last Retry"])
    for row in rows:
        writer.writerow([
            row["id"], row["perusahaan"], row["posisi"], row["email"],
            row["kategori"], row["tanggal"], row["status"],
            row["error"] or "", row["retry_count"], row["last_retry"] or ""
        ])
    return output.getvalue()