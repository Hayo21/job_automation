import sqlite3
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from contextlib import contextmanager

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
                status TEXT NOT NULL DEFAULT 'Menunggu'
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_lamaran_email ON lamaran(email)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_lamaran_perusahaan ON lamaran(perusahaan)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_lamaran_tanggal ON lamaran(tanggal)")
        conn.commit()


def count_today() -> int:
    today = datetime.now().strftime("%Y-%m-%d")
    with get_db() as conn:
        cur = conn.execute("SELECT COUNT(*) FROM lamaran WHERE tanggal = ?", (today,))
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


def save_lamaran(perusahaan: str, posisi: str, email: str, kategori: str) -> int:
    tanggal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO lamaran (perusahaan, posisi, email, kategori, tanggal, status) VALUES (?, ?, ?, ?, ?, 'Menunggu')",
            (perusahaan, posisi, email, kategori, tanggal)
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
    valid_status = {"Menunggu", "Dipanggil", "Ditolak"}
    if status not in valid_status:
        return False
    with get_db() as conn:
        cur = conn.execute("UPDATE lamaran SET status = ? WHERE id = ?", (status, lamaran_id))
        conn.commit()
        return cur.rowcount > 0


def get_stats() -> dict:
    with get_db() as conn:
        total = conn.execute("SELECT COUNT(*) FROM lamaran").fetchone()[0]
        menunggu = conn.execute("SELECT COUNT(*) FROM lamaran WHERE status = 'Menunggu'").fetchone()[0]
        dipanggil = conn.execute("SELECT COUNT(*) FROM lamaran WHERE status = 'Dipanggil'").fetchone()[0]
        ditolak = conn.execute("SELECT COUNT(*) FROM lamaran WHERE status = 'Ditolak'").fetchone()[0]
        today = count_today()
    return {
        "total": total,
        "menunggu": menunggu,
        "dipanggil": dipanggil,
        "ditolak": ditolak,
        "today": today,
    }