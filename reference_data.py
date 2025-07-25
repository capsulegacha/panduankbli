KATEGORI_LIST = [
    "A - Pertanian, Kehutanan dan Perikanan",
    "B - Pertambangan dan Penggalian",
    "C - Industri Pengolahan",
    "D - Pengadaan Listrik, Gas, Uap/Air Panas Dan Udara Dingin",
    "E - Treatment Air, Treatment Air Limbah, Treatment dan Pemulihan Material Sampah, dan Aktivitas Remediasi",
    "F - Konstruksi",
    "G - Perdagangan Besar Dan Eceran; Reparasi Dan Perawatan Mobil Dan Sepeda Motor",
    "H - Pengangkutan dan Pergudangan",
    "I - Penyediaan Akomodasi Dan Penyediaan Makan Minum",
    "J - Informasi Dan Komunikasi",
    "K - Aktivitas Keuangan dan Asuransi",
    "L - Real Estat",
    "M - Aktivitas Profesional, Ilmiah Dan Teknis",
    "N - Aktivitas Penyewaan dan Sewa Guna Usaha Tanpa Hak Opsi, Ketenagakerjaan, Agen Perjalanan dan Penunjang Usaha Lainnya",
    "O - Administrasi Pemerintahan, Pertahanan Dan Jaminan Sosial Wajib",
    "P - Pendidikan",
    "Q - Aktivitas Kesehatan Manusia Dan Aktivitas Sosial",
    "R - Kesenian, Hiburan Dan Rekreasi",
    "S - Aktivitas Jasa Lainnya",
    "T - Aktivitas Rumah Tangga Sebagai Pemberi Kerja; Aktivitas Yang Menghasilkan Barang Dan Jasa Oleh Rumah Tangga yang Digunakan untuk Memenuhi Kebutuhan Sendiri",
    "U - Aktivitas Badan Internasional Dan Badan Ekstra Internasional Lainnya"
]

DINAS_LIST = [
    "Dinas Pendidikan",
    "Dinas Kesehatan",
    "Dinas Sumber Daya Air dan Bina Marga",
    "Dinas Perumahan Rakyat dan Kawasan Permukiman Serta Pertanahan",
    "Dinas Pemadam Kebakaran dan Penyelamatan",
    "Dinas Sosial",
    "Dinas Perindustrian dan Tenaga Kerja",
    "Dinas Pemberdayaan Perempuan dan Perlindungan Anak serta Pengendalian Penduduk dan Keluarga Berencana",
    "Dinas Ketahanan Pangan dan Pertanian",
    "Dinas Lingkungan Hidup",
    "Dinas Kependudukan dan Pencatatan Sipil",
    "Dinas Perhubungan",
    "Dinas Komunikasi dan Informatika",
    "Dinas Koperasi Usaha Kecil dan Menengah dan Perdagangan",
    "Dinas Penanaman Modal dan Pelayanan Terpadu Satu Pintu",
    "Dinas Kebudayaan, Kepemudaan dan Olahraga serta Pariwisata",
    "Dinas Perpustakaan dan Kearsipan",
    "Satuan Polisi Pamong Praja"
]

map_dinas_ke_folder = {
    "Dinas Pendidikan": "disdik",
    "Dinas Kesehatan": "dinkes",
    "Dinas Sumber Daya Air dan Bina Marga": "dsdabm",
    "Dinas Perumahan Rakyat dan Kawasan Permukiman Serta Pertanahan": "dprkpp",
    "Dinas Pemadam Kebakaran dan Penyelamatan": "dpkp",
    "Dinas Sosial": "dinsos",
    "Dinas Perindustrian dan Tenaga Kerja": "disperinaker",
    "Dinas Pemberdayaan Perempuan dan Perlindungan Anak serta Pengendalian Penduduk dan Keluarga Berencana": "dp3ap2kb",
    "Dinas Ketahanan Pangan dan Pertanian": "dkppp",
    "Dinas Lingkungan Hidup": "dlh",
    "Dinas Kependudukan dan Pencatatan Sipil": "disdukcapil",
    "Dinas Perhubungan": "dishub",
    "Dinas Komunikasi dan Informatika": "diskominfo",
    "Dinas Koperasi Usaha Kecil dan Menengah dan Perdagangan": "dinkopdag",
    "Dinas Penanaman Modal dan Pelayanan Terpadu Satu Pintu": "dpmptsp",
    "Dinas Kebudayaan, Kepemudaan dan Olahraga serta Pariwisata": "disbudporapar",
    "Dinas Perpustakaan dan Kearsipan": "dispusip",
    "Satuan Polisi Pamong Praja": "satpolpp",
    "LAINNYA": "LAINNYA"
}

KODE_KBLI_KE_KATEGORI = {
    "01": "A - Pertanian, Kehutanan dan Perikanan",
    "02": "A - Pertanian, Kehutanan dan Perikanan",
    "03": "A - Pertanian, Kehutanan dan Perikanan",

    "05": "B - Pertambangan dan Penggalian",
    "06": "B - Pertambangan dan Penggalian",
    "07": "B - Pertambangan dan Penggalian",
    "08": "B - Pertambangan dan Penggalian",
    "09": "B - Pertambangan dan Penggalian",

    **{str(i).zfill(2): "C - Industri Pengolahan" for i in range(10, 34)},
    "35": "D - Pengadaan Listrik, Gas, Uap/Air Panas Dan Udara Dingin",
    **{str(i).zfill(2): "E - Treatment Air, Treatment Air Limbah, Treatment dan Pemulihan Material Sampah, dan Aktivitas Remediasi" for i in range(36, 40)},
    **{str(i).zfill(2): "F - Konstruksi" for i in range(41, 44)},
    **{str(i).zfill(2): "G - Perdagangan Besar Dan Eceran; Reparasi Dan Perawatan Mobil Dan Sepeda Motor" for i in range(45, 48)},
    **{str(i).zfill(2): "H - Pengangkutan dan Pergudangan" for i in range(49, 54)},
    **{str(i).zfill(2): "I - Penyediaan Akomodasi Dan Penyediaan Makan Minum" for i in range(55, 57)},
    **{str(i).zfill(2): "J - Informasi Dan Komunikasi" for i in range(58, 64)},
    **{str(i).zfill(2): "K - Aktivitas Keuangan dan Asuransi" for i in range(64, 67)},
    "68": "L - Real Estat",
    **{str(i).zfill(2): "M - Aktivitas Profesional, Ilmiah Dan Teknis" for i in range(69, 76)},
    **{str(i).zfill(2): "N - Aktivitas Penyewaan dan Sewa Guna Usaha Tanpa Hak Opsi, Ketenagakerjaan, Agen Perjalanan dan Penunjang Usaha Lainnya" for i in range(77, 83)},
    "84": "O - Administrasi Pemerintahan, Pertahanan Dan Jaminan Sosial Wajib",
    "85": "P - Pendidikan",
    **{str(i).zfill(2): "Q - Aktivitas Kesehatan Manusia Dan Aktivitas Sosial" for i in range(86, 89)},
    **{str(i).zfill(2): "R - Kesenian, Hiburan Dan Rekreasi" for i in range(90, 94)},
    **{str(i).zfill(2): "S - Aktivitas Jasa Lainnya" for i in range(94, 97)},
    **{str(i).zfill(2): "T - Aktivitas Rumah Tangga Sebagai Pemberi Kerja; Aktivitas Yang Menghasilkan Barang Dan Jasa Oleh Rumah Tangga yang Digunakan untuk Memenuhi Kebutuhan Sendiri" for i in range(97, 99)},
    "99": "U - Aktivitas Badan Internasional Dan Badan Ekstra Internasional Lainnya"
}

KATEGORI_KE_DINAS = {
    "A - Pertanian, Kehutanan dan Perikanan": "Dinas Ketahanan Pangan dan Pertanian",
    "B - Pertambangan dan Penggalian": "Dinas Lingkungan Hidup",
    "C - Industri Pengolahan": "Dinas Perindustrian dan Tenaga Kerja",
    "D - Pengadaan Listrik, Gas, Uap/Air Panas Dan Udara Dingin": "Dinas Lingkungan Hidup",
    "E - Treatment Air, Treatment Air Limbah, Treatment dan Pemulihan Material Sampah, dan Aktivitas Remediasi": "Dinas Lingkungan Hidup",
    "F - Konstruksi": "Dinas Sumber Daya Air dan Bina Marga",
    "G - Perdagangan Besar Dan Eceran; Reparasi Dan Perawatan Mobil Dan Sepeda Motor": "Dinas Koperasi Usaha Kecil dan Menengah dan Perdagangan",
    "H - Pengangkutan dan Pergudangan": "Dinas Perhubungan",
    "I - Penyediaan Akomodasi Dan Penyediaan Makan Minum": "Dinas Kebudayaan, Kepemudaan dan Olahraga serta Pariwisata",
    "J - Informasi Dan Komunikasi": "Dinas Komunikasi dan Informatika",
    "K - Aktivitas Keuangan dan Asuransi": "Dinas Penanaman Modal dan Pelayanan Terpadu Satu Pintu",
    "L - Real Estat": "Dinas Penanaman Modal dan Pelayanan Terpadu Satu Pintu",
    "M - Aktivitas Profesional, Ilmiah Dan Teknis": "Dinas Penanaman Modal dan Pelayanan Terpadu Satu Pintu",
    "N - Aktivitas Penyewaan dan Sewa Guna Usaha Tanpa Hak Opsi, Ketenagakerjaan, Agen Perjalanan dan Penunjang Usaha Lainnya": "Dinas Penanaman Modal dan Pelayanan Terpadu Satu Pintu",
    "O - Administrasi Pemerintahan, Pertahanan Dan Jaminan Sosial Wajib": "Satuan Polisi Pamong Praja",
    "P - Pendidikan": "Dinas Pendidikan",
    "Q - Aktivitas Kesehatan Manusia Dan Aktivitas Sosial": "Dinas Kesehatan",
    "R - Kesenian, Hiburan Dan Rekreasi": "Dinas Kebudayaan, Kepemudaan dan Olahraga serta Pariwisata",
    "S - Aktivitas Jasa Lainnya": "Dinas Sosial",
    "T - Aktivitas Rumah Tangga Sebagai Pemberi Kerja; Aktivitas Yang Menghasilkan Barang Dan Jasa Oleh Rumah Tangga yang Digunakan untuk Memenuhi Kebutuhan Sendiri": "LAINNYA",
    "U - Aktivitas Badan Internasional Dan Badan Ekstra Internasional Lainnya": "LAINNYA"
}