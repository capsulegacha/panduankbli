from flask import Flask, flash, render_template, request, redirect, url_for, session
from docx import Document
from werkzeug.utils import secure_filename
from reference_data import KATEGORI_LIST, DINAS_LIST, map_dinas_ke_folder, KODE_KBLI_KE_KATEGORI, KATEGORI_KE_DINAS
import os
import re
import json
from pathlib import Path
from typing import Dict, List
from string import ascii_lowercase
from datetime import timedelta

app = Flask(__name__)
app.permanent_session_lifetime = timedelta(minutes=10)
app.secret_key = "supersecretkey"  # Ganti ini di production
DATA_DIR = Path("data")
ADMIN_PASSWORD = "1234567890"

@app.before_request
def before_every_request():
    session.modified = True  # reset timeout
    allowed_routes = ['login', 'logout', 'static']
    if request.endpoint in allowed_routes or request.endpoint.startswith('static'):
        return
    if not session.get('is_admin'):
        return redirect(url_for('login', expired=1))

# ---------- Helper ----------

def sort_persyaratan(data: dict) -> dict:
    def sort_key_huruf(k):
        # ubah huruf jadi angka
        result = 0
        for c in k:
            result = result * 26 + (ord(c) - 96)  # 'a' = 1
        return result

    sorted_data = {}
    for section_key in sorted(data["persyaratan"], key=lambda x: int(x)):
        section = data["persyaratan"][section_key]
        sorted_items = dict(sorted(section["items"].items(), key=lambda x: sort_key_huruf(x[0])))
        sorted_data[section_key] = {
            "judul": section["judul"],
            "items": sorted_items
        }
    return {"persyaratan": sorted_data}

def load_all_kbli_data() -> Dict:
    all_data = {}
    if Path("86104.json").exists():
        with open("86104.json", encoding='utf-8') as f:
            data = json.load(f)
            all_data["86104"] = data
            return all_data

    if DATA_DIR.exists():
        for dinas_folder in DATA_DIR.iterdir():
            if dinas_folder.is_dir():
                for json_file in dinas_folder.glob("*.json"):
                    try:
                        with open(json_file, encoding="utf-8") as f:
                            data = json.load(f)
                            kbli_code = json_file.stem
                            data["dinas_folder"] = dinas_folder.name
                            all_data[kbli_code] = data
                    except:
                        continue
    return all_data

def search_kbli(query: str, kbli_data: Dict, dinas_filter: str = 'semua') -> List[Dict]:
    results = []
    q = query.lower()
    for kode, data in kbli_data.items():
        if dinas_filter != 'semua':
            if data.get("dinas", data.get("dinas_folder", "")).lower() != dinas_filter.lower():
                continue
        if (
            q in kode.lower()
            or q in data.get("nama", "").lower()
            or q in data.get("kategori", "").lower()
            or q in data.get("ruang_lingkup", "").lower()
        ):
            results.append({
                'kode': kode,
                'nama': data.get('nama', 'N/A'),
                'kategori': data.get('kategori', 'N/A'),
                'ruang_lingkup': data.get('ruang_lingkup', 'N/A'),
                'dinas': data.get('dinas', data.get('dinas_folder', 'N/A'))
            })
    return sorted(results, key=lambda x: x['kode'])

def is_admin():
    return session.get("is_admin", False)

def parse_docx_to_persyaratan(file):
    doc = Document(file)
    persyaratan = {}
    meta = {
        "ruang_lingkup": "",
        "nama": ""
    }

    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    i = 0
    current_section = None
    section_counter = 1

    # Ambil metadata
    for idx, text in enumerate(paragraphs):
        if text.lower().startswith("kode kbli"):
            continue
        if text.lower().startswith("nama kbli"):
            nama_line = paragraphs[idx].split(":", 1)
            if len(nama_line) == 2:
                meta["nama"] = nama_line[1].strip()
        if text.lower().startswith("ruang lingkup"):
            ruang_line = paragraphs[idx].split(":", 1)
            if len(ruang_line) == 2:
                meta["ruang_lingkup"] = ruang_line[1].strip()
                i = idx + 1
                break

    # Cari "Persyaratan Perizinan"
    while i < len(paragraphs) and "persyaratan" not in paragraphs[i].lower():
        i += 1
    i += 1  # Lewati judul "Persyaratan Perizinan"

    # Parse struktur isi
    while i < len(paragraphs):
        text = paragraphs[i]

        # Cek jika baris adalah "Nomor X"
        nomor_match = re.match(r"^Nomor (\d+)(.*)?", text, re.IGNORECASE)
        if nomor_match:
            section_no = str(section_counter)
            judul = nomor_match.group(0).strip()
            current_section = {
                "judul": judul,
                "items": {}
            }
            persyaratan[section_no] = current_section
            section_counter += 1
            item_counter = 0
        elif current_section:
            # Tambah item a, b, c
            key = ascii_lowercase[item_counter] if item_counter < 26 else f"extra{item_counter}"
            current_section["items"][key] = text.strip()
            item_counter += 1
        i += 1

    if not persyaratan:
        raise ValueError("Dokumen tidak mengandung struktur persyaratan yang dapat dibaca. Gunakan template yang telah disediakan.")

    return persyaratan, meta

# ---------- Routes ----------

@app.route('/')
def index():
    query = request.args.get("q", "")
    dinas = request.args.get("dinas", "semua")
    all_data = load_all_kbli_data()
    results = search_kbli(query, all_data, dinas) if query else []

    grouped_by_dinas = {}
    for kode, data in all_data.items():
        dinas_key = data.get("dinas") or data.get("dinas_folder", "Lainnya")
        grouped_by_dinas.setdefault(dinas_key, []).append((kode, data.get("nama", "N/A")))

    return render_template('index.html', results=results, query=query, grouped_by_dinas=grouped_by_dinas)

@app.route('/kbli/<kode>')
def kbli_detail(kode):
    all_data = load_all_kbli_data()
    data = all_data.get(kode)
    if not data:
        return f"Data untuk KBLI {kode} tidak ditemukan.", 404
    return render_template('detail.html', kbli_code=kode, data=data, referrer=request.referrer)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    expired = request.args.get("expired")
    error = None

    if request.method == 'POST':
        if request.form.get("password") == ADMIN_PASSWORD:
            session.permanent = True
            session["is_admin"] = True
            return redirect(url_for('index'))
        else:
            flash("Password salah!", "danger")
            return redirect(url_for('login'))

    if expired:
        flash("Sesi Anda telah berakhir. Silakan login kembali.", "warning")

    return render_template('admin_login.html', error=error)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    expired = request.args.get("expired")
    error = None

    if not is_admin():
        return redirect(url_for('login', expired=1))

    all_data = load_all_kbli_data()
    query = request.args.get("q", "")
    kode = request.args.get("kode")
    new_flag = request.args.get("new") == "1"

    if query:
        filtered = search_kbli(query, all_data)
        all_kode = [item["kode"] for item in filtered]
    else:
        all_kode = []

    if request.args.get("draft") == "1":
        kode = session.get("new_kbli_kode")
        data = session.get("new_kbli_data")
    elif new_flag:
        kode = ""
        data = {
            "nama": "",
            "kategori": "",
            "ruang_lingkup": "",
            "dinas": "",
            "persyaratan": {}
        }
    else:
        data = all_data.get(kode) if kode else None

    return render_template(
        'admin_panel.html',
        data=data,
        kode=kode,
        all_kode=all_kode,
        data_dict=all_data,
        kategori_list=KATEGORI_LIST,
        dinas_list=DINAS_LIST
    )

@app.route('/admin/upload', methods=['GET', 'POST'])
def upload_kbli():
    if not is_admin():
        return redirect(url_for('admin'))

    if request.method == 'POST':
        kode = request.form.get("kode")
        file = request.files.get("file")

        if not kode or not file or not file.filename.endswith(".docx"):
            flash("Kode KBLI dan file Word wajib diisi.", "warning")
            return redirect(request.url)

        all_data = load_all_kbli_data()
        if kode in all_data:
            flash(f"KBLI dengan kode {kode} sudah ada. Silakan cari dan edit melalui pencarian di panel admin.", "warning")
            session.pop("new_kbli_data", None)
            session.pop("new_kbli_kode", None)
            return redirect(request.url)

        try:
            persyaratan, meta = parse_docx_to_persyaratan(file)
            if not persyaratan:
                flash("Dokumen tidak mengandung persyaratan yang dapat dibaca.", "warning")
                return redirect(request.url)
            
            persyaratan = sort_persyaratan({"persyaratan": persyaratan})["persyaratan"]

            session.pop("new_kbli_data", None)
            session.pop("new_kbli_kode", None)

            kode_awal = kode[:2]
            kategori_otomatis = KODE_KBLI_KE_KATEGORI.get(kode_awal, "")

            session["new_kbli_data"] = {
                "nama": meta.get("nama", "").upper(),
                "kategori": kategori_otomatis,
                "ruang_lingkup": meta.get("ruang_lingkup", "").title(),
                "dinas": "",
                "persyaratan": persyaratan
            }

            session["new_kbli_data"]["persyaratan"] = sort_persyaratan({
                "persyaratan": session["new_kbli_data"]["persyaratan"]
            })["persyaratan"]

            session["new_kbli_kode"] = kode

            print(f"✅ KBLI {kode} berhasil diparse, redirect ke /admin?kode={kode}&draft=1")
            return redirect(url_for("admin", kode=kode, draft="1"))

        except Exception as e:
            flash(f"Gagal membaca dokumen: {e}", "danger")
            return redirect(request.url)

    return render_template(
        "admin_upload.html",
        kategori_list=KATEGORI_LIST,
        dinas_list=DINAS_LIST,
        data=None
    )

@app.route('/admin/add_manual', methods=['POST'])
def add_kbli_manual():
    if not is_admin():
        return redirect(url_for('admin'))

    kode = request.form.get("kode")
    nama = request.form.get("nama")
    kategori = request.form.get("kategori")
    ruang_lingkup = request.form.get("ruang_lingkup")
    dinas = request.form.get("dinas")

    if not kode or not nama:
        flash("Kode dan Nama KBLI wajib diisi.", "danger")
        return redirect(url_for("upload_kbli"))

    all_data = load_all_kbli_data()

    if kode in all_data:
        flash(f"Kode {kode} sudah terdaftar!", "warning")
        return redirect(url_for("admin", kode=kode))
    
    kode_awal = kode[:2]
    kategori_otomatis = KODE_KBLI_KE_KATEGORI.get(kode_awal, kategori)

    # Simpan ke file
    data = {
        "nama": nama,
        "kategori": kategori_otomatis,
        "ruang_lingkup": ruang_lingkup,
        "dinas": dinas,
        "persyaratan": {}
    }

    folder_name = map_dinas_ke_folder.get(data.get("dinas"), "LAINNYA")
    file_path = DATA_DIR / folder_name / f"{kode}.json"
    os.makedirs(file_path.parent, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    flash(f"KBLI {kode} berhasil ditambahkan.", "success")
    return redirect(url_for("admin", kode=kode))

@app.route('/admin/save', methods=['POST'])
def save():
    if not is_admin():
        return "Unauthorized", 403

    kode = request.form.get("kode")
    if not kode:
        return "Kode KBLI harus diisi.", 400

    all_data = load_all_kbli_data()
    data = all_data.get(kode, {
        "nama": "",
        "kategori": "",
        "ruang_lingkup": "",
        "dinas": "",
        "persyaratan": {}
    })

    data['nama'] = request.form.get("nama", "")
    data['ruang_lingkup'] = request.form.get("ruang_lingkup", "")

    kategori = request.form.get("kategori", "")
    data['kategori'] = kategori

    # Cek jika kategori kosong, tetapkan otomatis berdasarkan 2 digit awal kode
    if not data['kategori']:
        kode_awal = kode[:2]
        kategori_otomatis = KODE_KBLI_KE_KATEGORI.get(kode_awal)
        if kategori_otomatis:
            data['kategori'] = kategori_otomatis

    # Otomatis isi dinas jika kosong
    if not request.form.get("dinas"):
        data['dinas'] = KATEGORI_KE_DINAS.get(kategori, "")
    else:
        data['dinas'] = request.form.get("dinas", "")

    # Siapkan dict kosong untuk persyaratan
    persyaratan = {}

    # Ambil semua judul bagian
    for key in request.form.keys():
        if key.startswith("persyaratan_") and "_item_" not in key:
            parts = key.split("_")
            if len(parts) >= 3:
                nomor = parts[1]
                jenis = parts[2]
                if nomor not in persyaratan:
                    persyaratan[nomor] = {}
                value = request.form[key].strip()
                if value:  # hanya simpan jika tidak kosong
                    persyaratan[nomor][jenis] = value

    # Ambil semua item a, b, c
    for key in request.form.keys():
        if "_item_" in key:
            parts = key.split("_")
            if len(parts) == 4:
                nomor, _, item_kode = parts[1], parts[2], parts[3]
                value = request.form[key].strip()
                if value:  # hanya simpan jika tidak kosong
                    if nomor not in persyaratan:
                        persyaratan[nomor] = {}
                    if "items" not in persyaratan[nomor]:
                        persyaratan[nomor]["items"] = {}
                    persyaratan[nomor]["items"][item_kode] = value

    # Hapus bagian-bagian yang benar-benar kosong
    persyaratan = {
        nomor: bagian for nomor, bagian in persyaratan.items()
        if bagian.get("judul") or bagian.get("items")
    }

    data["persyaratan"] = persyaratan

    folder_name = map_dinas_ke_folder.get(data.get("dinas"), "LAINNYA")
    file_path = DATA_DIR / folder_name / f"{kode}.json"
    os.makedirs(file_path.parent, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return redirect(url_for("admin", kode=kode))

@app.route('/admin/delete', methods=['POST'])
def delete_kbli():
    if not is_admin():
        return "Unauthorized", 403

    kode = request.form.get("kode")
    password = request.form.get("password")

    if password != ADMIN_PASSWORD:
        flash("Password salah. Penghapusan dibatalkan.", "danger")
        return redirect(url_for("admin", kode=kode))

    all_data = load_all_kbli_data()
    data = all_data.get(kode)

    if not data:
        flash("Data KBLI tidak ditemukan.", "warning")
        return redirect(url_for("admin"))

    folder = data.get("dinas_folder") or "LAINNYA"
    file_path = DATA_DIR / folder / f"{kode}.json"

    if file_path.exists():
        os.remove(file_path)
        flash(f"KBLI {kode} berhasil dihapus.", "success")
    else:
        flash("File tidak ditemukan saat menghapus.", "warning")

    return redirect(url_for("admin"))

@app.route('/logout')
def logout():
    session.pop("is_admin", None)
    return redirect(url_for('login'))

@app.template_filter('to_letter')
def to_letter_filter(n):
    """Ubah angka menjadi huruf a, b, c, ..., aa, ab, ..."""
    n = int(n)
    result = ""
    while n > 0:
        n -= 1
        result = chr(97 + (n % 26)) + result
        n //= 26
    return result

# ---------- Main ----------
if __name__ == '__main__':
    app.run(debug=True)