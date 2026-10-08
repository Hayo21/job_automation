from dataclasses import dataclass
from string import Template


@dataclass
class TemplateData:
    perusahaan: str
    posisi: str
    nama_pelamar: str = "Muniff Agustiansah"
    telepon: str = "08xx-xxxx-xxxx"
    email: str = "muniff@example.com"
    linkedin: str = "linkedin.com/in/muniff"


TEMPLATES = {
    "teknisi_jaringan": Template("""
Yth. Tim HRD ${perusahaan},

Dengan hormat,

Saya ${nama_pelamar}, bermaksud melamar posisi **${posisi}** di ${perusahaan} sebagaimana diiklankan.

Saya memiliki pengalaman di bidang jaringan komputer meliputi:
- Konfigurasi & troubleshooting router/switch (Cisco, MikroTik)
- Monitoring jaringan & manajemen bandwidth
- Implementasi VPN, VLAN, dan keamanan jaringan dasar
- Dokumentasi topologi & SOP operasional

Saya tertarik bergabung dengan ${perusahaan} karena reputasi perusahaan di bidang infrastruktur IT. CV lengkap saya terlampir untuk pertimbangan Bapak/Ibu.

Terima kasih atas waktu dan kesempatannya. Saya berharap dapat diwawancarai.

Hormat saya,
${nama_pelamar}
${telepon} | ${email}
${linkedin}
"""),
    "it_support": Template("""
Yth. Tim HRD ${perusahaan},

Dengan hormat,

Saya ${nama_pelamar}, bermaksud melamar posisi **${posisi}** di ${perusahaan}.

Sebagai IT Support dengan pengalaman:
- Troubleshooting hardware/software end-user (Windows, Office, printer)
- Manajemen tiket via Helpdesk (SLA response < 30 menit)
- Asset management & inventory IT
- Onboarding/offboarding karyawan (akses, email, device)
- Dokumentasi KB article & SOP support

Saya siap berkontribusi menjaga kelancaran operasional IT di ${perusahaan}. CV terlampir.

Terima kasih atas perhatiannya.

Hormat saya,
${nama_pelamar}
${telepon} | ${email}
${linkedin}
"""),
    "teknisi_it_pabrik": Template("""
Yth. Tim HRD ${perusahaan},

Dengan hormat,

Saya ${nama_pelamar}, melamar posisi **${posisi}** di ${perusahaan}.

Pengalaman saya di lingkungan manufaktur/industri:
- Maintenance PC, scanner, printer, barcode reader di lantai produksi
- Troubleshooting sistem MES/SCADA level dasar
- Koordinasi dengan vendor untuk perbaikan hardware kritis
- Preventive maintenance jaringan & device IT area produksi
- Shift support (siap fleksibel jam kerja)

Minat saya pada ${perusahaan} karena skala operasional IT yang menantang. CV terlampir.

Terima kasih.

Hormat saya,
${nama_pelamar}
${telepon} | ${email}
${linkedin}
"""),
}


SUBJECT_TEMPLATE = "Lamaran ${posisi} - ${nama_pelamar}"


def render_template(category: str, data: TemplateData) -> tuple[str, str]:
    template = TEMPLATES.get(category)
    if not template:
        raise ValueError(f"Template tidak dikenal: {category}")

    subject = Template(SUBJECT_TEMPLATE).substitute(
        posisi=data.posisi, nama_pelamar=data.nama_pelamar
    )
    body = template.substitute(
        perusahaan=data.perusahaan,
        posisi=data.posisi,
        nama_pelamar=data.nama_pelamar,
        telepon=data.telepon,
        email=data.email,
        linkedin=data.linkedin,
    )
    return subject, body


def get_categories() -> list[str]:
    return list(TEMPLATES.keys())