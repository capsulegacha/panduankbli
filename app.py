from flask import Flask, flash, render_template, request, redirect, url_for, session
import os
import json
from pathlib import Path
from typing import Dict, List
from docx import Document

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Ganti ini di production
DATA_DIR = Path("data")
ADMIN_PASSWORD = "klinikinvestasisehat"

# ---------- Helper ----------

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

def parse_docx_to_persyaratan(file) -> dict:
    doc = Document(file)
    persyaratan = {}
    current_section = None
    section_counter = 1
    item_counter = 1

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        # Heading: jika diakhiri titik dua → anggap sebagai judul bagian
        if text.endswith(":") and len(text.split()) <= 6:
            current_section = {
                "judul": text.rstrip(":"),
                "items": {}
            }
            persyaratan[str(section_counter)] = current_section
            section_counter += 1
            item_counter = 1
        elif current_section:
            # Tambahkan item ke bagian saat ini
            current_section["items"][str(item_counter)] = {"item": text}
            item_counter += 1

    return persyaratan

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

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not is_admin():
        if request.method == 'POST':
            if request.form.get("password") == ADMIN_PASSWORD:
                session["is_admin"] = True
                return redirect(url_for('admin'))
            else:
                return render_template('admin_login.html', error="Password salah!")

        return render_template('admin_login.html')

    all_data = load_all_kbli_data()
    query = request.args.get("q", "")
    kode = request.args.get("kode")
    new_flag = request.args.get("new") == "1"

    if query:
        filtered = search_kbli(query, all_data)
        all_kode = [item["kode"] for item in filtered]
    else:
        all_kode = []

    # Jika new KBLI
    if request.args.get("draft") == "1":
        kode = session.get("new_kbli_kode")
        data = session.get("new_kbli_data")

    if new_flag:
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
        data_dict=all_data
    )

@app.route('/admin/upload', methods=['GET', 'POST'])
def upload_kbli():
    if not is_admin():
        return redirect(url_for('admin'))

    if request.method == 'POST':
        kode = request.form.get("kode")
        file = request.files.get("file")
        
        # Validasi file harus ada dan berformat .docx
        if not kode or not file or not file.filename.endswith(".docx"):
            flash("Kode KBLI dan file Word wajib diisi.")
            return redirect(request.url)

        # Validasi apakah kode KBLI sudah ada
        all_data = load_all_kbli_data()
        if kode in all_data:
            flash(f"KBLI dengan kode {kode} sudah ada. Silakan cari dan edit melalui pencarian di panel admin.")
            session.pop("new_kbli_data", None)
            session.pop("new_kbli_kode", None)
            return redirect(request.url)

        # Parse dokumen dan simpan ke session
        try:
            data = {
                "nama": "",
                "kategori": "",
                "ruang_lingkup": "",
                "dinas": "",
                "persyaratan": parse_docx_to_persyaratan(file)
            }

            session.pop("new_kbli_data", None)
            session.pop("new_kbli_kode", None)

            session["new_kbli_data"] = data
            session["new_kbli_kode"] = kode
            return redirect(url_for("admin", kode=kode, draft="1"))
        except Exception as e:
            flash(f"Gagal membaca dokumen: {e}")
            return redirect(request.url)

    return render_template("admin_upload.html")

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

    # Simpan ke file
    data = {
        "nama": nama,
        "kategori": kategori,
        "ruang_lingkup": ruang_lingkup,
        "dinas": dinas,
        "persyaratan": {}
    }

    folder_name = data.get("dinas", "LAINNYA").upper().replace(" ", "_")
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
    data['kategori'] = request.form.get("kategori", "")
    data['ruang_lingkup'] = request.form.get("ruang_lingkup", "")
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

    folder_name = data.get("dinas_folder") or "LAINNYA"
    file_path = DATA_DIR / folder_name / f"{kode}.json"
    os.makedirs(file_path.parent, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return redirect(url_for("admin", kode=kode))

@app.route('/admin/delete/<kode>', methods=['POST'])
def delete_kbli(kode):
    if not is_admin():
        return "Unauthorized", 403

    all_data = load_all_kbli_data()
    data = all_data.get(kode)
    if not data:
        flash("KBLI tidak ditemukan.", "warning")
        return redirect(url_for("admin"))

    folder_name = data.get("dinas_folder", "LAINNYA")
    file_path = DATA_DIR / folder_name / f"{kode}.json"
    if file_path.exists():
        os.remove(file_path)
        flash(f"KBLI {kode} berhasil dihapus.", "success")

    return redirect(url_for("admin"))

@app.route('/logout')
def logout():
    session.pop("is_admin", None)
    return redirect(url_for('index'))

# ---------- Main ----------
if __name__ == '__main__':
    app.run(debug=True)