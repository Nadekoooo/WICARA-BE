from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_ROOT = ROOT / "wicara_mvp_10_manim_templates" / "specs" / "samples"


OVERRIDES: dict[str, dict[str, Any]] = {
    "manim.chem_reaction_equation.v1": {
        "phase": "E",
        "audience_level": "sma",
        "title": "Menyeimbangkan Persamaan Reaksi",
        "subtitle": "Jumlah atom kiri dan kanan harus sama.",
        "equation": "Fe + O2 -> Fe2O3",
        "left_expression": "Fe + O2",
        "right_expression": "Fe2O3",
        "solution_steps": [
            {
                "operation": "Set koefisien Fe2O3 = 2",
                "left_result": "Fe + O2",
                "right_result": "2Fe2O3",
                "explanation": "Mulai dari produk agar jumlah atom Fe dan O jelas targetnya.",
            },
            {
                "operation": "Set koefisien Fe = 4",
                "left_result": "4Fe + O2",
                "right_result": "2Fe2O3",
                "explanation": "Samakan atom Fe di ruas kiri dan kanan.",
            },
            {
                "operation": "Set koefisien O2 = 3",
                "left_result": "4Fe + 3O2",
                "right_result": "2Fe2O3",
                "explanation": "Samakan atom O sehingga kedua ruas setara.",
            },
        ],
        "final_solution": "4Fe + 3O2 -> 2Fe2O3",
        "steps": [
            {
                "title": "Hitung atom tiap unsur",
                "body": "Catat jumlah atom Fe dan O sebelum menambah koefisien.",
            },
            {
                "title": "Ubah koefisien bertahap",
                "body": "Mulai dari produk, lalu sesuaikan pereaksi sampai jumlah atom sama.",
            },
            {
                "title": "Verifikasi kesetaraan",
                "body": "Pastikan atom Fe dan O kiri sama dengan kanan.",
            },
        ],
        "summary": "Persamaan reaksi seimbang jika jumlah atom tiap unsur sama pada kedua ruas.",
        "voiceover_script": "Menyeimbangkan reaksi berarti menyamakan jumlah atom tiap unsur di kiri dan kanan persamaan.",
    },
    "manim.stoichiometry_board.v1": {
        "phase": "E",
        "audience_level": "sma",
        "title": "Koefisien Reaksi untuk Stoikiometri",
        "subtitle": "Koefisien seimbang jadi dasar hitung mol.",
        "equation": "N2 + H2 -> NH3",
        "left_expression": "N2 + H2",
        "right_expression": "NH3",
        "solution_steps": [
            {
                "operation": "Set koefisien NH3 = 2",
                "left_result": "N2 + H2",
                "right_result": "2NH3",
                "explanation": "Agar atom N di produk menjadi 2 dan sesuai dengan N2.",
            },
            {
                "operation": "Set koefisien H2 = 3",
                "left_result": "N2 + 3H2",
                "right_result": "2NH3",
                "explanation": "Samakan atom H menjadi 6 di kedua ruas.",
            },
        ],
        "final_solution": "N2 + 3H2 -> 2NH3",
        "steps": [
            {
                "title": "Tetapkan target produk",
                "body": "Mulai dari produk untuk menentukan jumlah atom yang harus dipenuhi pereaksi.",
            },
            {
                "title": "Setarakan pereaksi",
                "body": "Ubah koefisien pereaksi sampai jumlah atom N dan H seimbang.",
            },
        ],
        "summary": "Koefisien seimbang memberi rasio mol N2:H2:NH3 = 1:3:2.",
        "voiceover_script": "Di stoikiometri, koefisien persamaan seimbang dipakai sebagai rasio mol antar zat.",
    },
    "manim.energy_environment_system.v1": {
        "title": "Energi dan Lingkungan",
        "subtitle": "Baca tren emisi saat energi terbarukan meningkat.",
        "formula_latex": "E(t) = -0.6t + 8",
        "function": {"type": "linear", "params": {"m": -0.6, "b": 8}},
        "x_range": [0, 10, 1],
        "y_range": [0, 9, 1],
        "x_label": "tahun",
        "y_label": "indeks emisi",
        "graph_label": "tren emisi",
        "moving_label": "emisi",
        "x_path": [0, 2, 4, 6, 8, 10],
        "highlight_x": 6,
        "show_slope": True,
        "slope_text": "Kemiringan negatif menunjukkan emisi cenderung turun seiring transisi energi.",
        "steps": [
            {
                "title": "Identifikasi sumbu",
                "body": "Sumbu-x menunjukkan waktu, sumbu-y menunjukkan indeks emisi.",
            },
            {
                "title": "Baca arah tren",
                "body": "Garis menurun menandakan emisi berkurang dari waktu ke waktu.",
            },
            {
                "title": "Tafsir kemiringan",
                "body": "Kemiringan memberi laju perubahan emisi per tahun.",
            },
        ],
        "summary": "Grafik tren membantu menilai dampak kebijakan energi terhadap lingkungan.",
        "voiceover_script": "Grafik ini menunjukkan kecenderungan emisi menurun ketika sistem energi bergerak ke sumber yang lebih bersih.",
    },
    "manim.probability_tree.v1": {
        "title": "Peluang Bertahap",
        "subtitle": "Estimasi peluang total dengan membaca pola nilai peluang.",
        "formula_latex": "P(k) = 0.12k + 0.2",
        "function": {"type": "linear", "params": {"m": 0.12, "b": 0.2}},
        "x_range": [0, 6, 1],
        "y_range": [0, 1.0, 0.1],
        "x_label": "tahap",
        "y_label": "peluang",
        "graph_label": "peluang kejadian",
        "moving_label": "P",
        "x_path": [0, 1, 2, 3, 4, 5],
        "highlight_x": 4,
        "show_slope": False,
        "steps": [
            {
                "title": "Pahami rentang peluang",
                "body": "Nilai peluang selalu berada antara 0 dan 1.",
            },
            {
                "title": "Bandingkan antar tahap",
                "body": "Setiap tahap punya peluang yang dapat dibandingkan di grafik.",
            },
            {
                "title": "Tarik kesimpulan",
                "body": "Perubahan nilai peluang membantu memprediksi hasil tahap berikutnya.",
            },
        ],
        "summary": "Visual peluang membantu membaca kecenderungan kejadian dalam proses bertahap.",
        "voiceover_script": "Kita bisa melihat perubahan peluang per tahap lewat grafik agar perbandingan antar kejadian lebih jelas.",
    },
    "manim.data_representation.v1": {
        "title": "Representasi Data Kelas",
        "subtitle": "Bandingkan jumlah siswa per kategori kegiatan.",
        "formula_latex": "y = 3x + 10",
        "function": {"type": "linear", "params": {"m": 3, "b": 10}},
        "x_range": [0, 6, 1],
        "y_range": [0, 30, 5],
        "x_label": "kategori",
        "y_label": "jumlah",
        "graph_label": "data pengamatan",
        "moving_label": "data",
        "x_path": [0, 1, 2, 3, 4, 5],
        "highlight_x": 3,
        "show_slope": False,
        "steps": [
            {"title": "Baca skala", "body": "Pastikan tiap sumbu dibaca dengan skala yang benar."},
            {"title": "Bandingkan nilai", "body": "Nilai yang lebih tinggi berarti jumlah lebih banyak."},
            {"title": "Simpulkan tren", "body": "Gunakan pola naik-turun untuk menyimpulkan data."},
        ],
        "summary": "Representasi visual memudahkan perbandingan data antar kategori.",
        "voiceover_script": "Saat data divisualkan, kita lebih cepat menemukan kategori yang paling tinggi atau paling rendah.",
    },
    "manim.statistics_center_spread.v1": {
        "title": "Pemusatan dan Sebaran",
        "subtitle": "Amati nilai tengah dan penyebaran data.",
        "formula_latex": "y = 0.4x^2 - 2x + 7",
        "function": {"type": "quadratic", "params": {"a": 0.4, "b": -2, "c": 7}},
        "x_range": [0, 8, 1],
        "y_range": [0, 10, 1],
        "x_label": "indeks data",
        "y_label": "nilai",
        "graph_label": "pola data",
        "moving_label": "nilai",
        "x_path": [0, 2, 4, 6, 8],
        "highlight_x": 4,
        "show_slope": False,
        "steps": [
            {"title": "Cari pusat", "body": "Nilai tengah memberi gambaran posisi umum data."},
            {"title": "Lihat sebaran", "body": "Jarak antar nilai menunjukkan apakah data rapat atau menyebar."},
            {"title": "Bandingkan set data", "body": "Data dengan pusat sama bisa punya sebaran berbeda."},
        ],
        "summary": "Ukuran pemusatan dan penyebaran dipakai bersama untuk membaca karakter data.",
        "voiceover_script": "Selain mencari nilai tengah, kita juga perlu melihat seberapa jauh data menyebar dari pusatnya.",
    },
    "manim.function_mapping.v1": {
        "title": "Pemetaan Fungsi",
        "subtitle": "Setiap input dipetakan ke satu output.",
        "formula_latex": "f(x)=2x+1",
        "function": {"type": "linear", "params": {"m": 2, "b": 1}},
        "x_range": [-2, 4, 1],
        "y_range": [-3, 10, 1],
        "x_label": "x",
        "y_label": "f(x)",
        "graph_label": "pemetaan fungsi",
        "moving_label": "pasangan",
        "x_path": [-2, -1, 0, 1, 2, 3],
        "highlight_x": 2,
        "show_slope": True,
        "slope_text": "Kemiringan 2 berarti tiap kenaikan 1 pada x menaikkan f(x) sebesar 2.",
        "steps": [
            {"title": "Pilih input", "body": "Ambil satu nilai x sebagai input fungsi."},
            {"title": "Hitung output", "body": "Gunakan rumus fungsi untuk mencari f(x)."},
            {"title": "Lihat pasangan", "body": "Setiap pasangan (x, f(x)) menjadi titik pada grafik."},
        ],
        "summary": "Fungsi memetakan setiap input ke tepat satu output.",
        "voiceover_script": "Dengan grafik, kita bisa melihat aturan pemetaan input ke output secara konsisten.",
    },
    "manim.scientific_inquiry_data.v1": {
        "title": "Inkuiri Ilmiah Berbasis Data",
        "subtitle": "Gunakan grafik untuk membaca hasil eksperimen.",
        "formula_latex": "y = 1.5x + 2",
        "function": {"type": "linear", "params": {"m": 1.5, "b": 2}},
        "x_range": [0, 8, 1],
        "y_range": [0, 15, 1],
        "x_label": "waktu",
        "y_label": "hasil ukur",
        "graph_label": "hasil eksperimen",
        "moving_label": "ukur",
        "x_path": [0, 1, 2, 3, 4, 5, 6],
        "highlight_x": 5,
        "show_slope": True,
        "slope_text": "Kemiringan menunjukkan seberapa cepat besaran berubah selama eksperimen.",
        "steps": [
            {"title": "Susun data", "body": "Catat hasil ukur secara teratur terhadap waktu."},
            {"title": "Amati pola", "body": "Cari kecenderungan naik, turun, atau tetap."},
            {"title": "Tarik inferensi", "body": "Gunakan pola untuk menjelaskan fenomena yang diamati."},
        ],
        "summary": "Grafik eksperimen membantu membuat kesimpulan ilmiah lebih terukur.",
        "voiceover_script": "Inkuiri ilmiah tidak berhenti di pengamatan, tetapi dilanjutkan dengan membaca pola data secara sistematis.",
    },
    "manim.scatter_association.v1": {
        "title": "Asosiasi Dua Variabel",
        "subtitle": "Lihat hubungan nilai x dan y dari sebaran data.",
        "formula_latex": "y = 0.8x + 2",
        "function": {"type": "linear", "params": {"m": 0.8, "b": 2}},
        "x_range": [0, 10, 1],
        "y_range": [0, 12, 1],
        "x_label": "variabel x",
        "y_label": "variabel y",
        "graph_label": "asosiasi data",
        "moving_label": "titik data",
        "x_path": [0, 2, 4, 6, 8, 10],
        "highlight_x": 6,
        "show_slope": False,
        "steps": [
            {"title": "Plot pasangan data", "body": "Setiap pasangan nilai menjadi satu titik di bidang koordinat."},
            {"title": "Amati arah pola", "body": "Pola naik menunjukkan asosiasi positif, pola turun menunjukkan asosiasi negatif."},
            {"title": "Gunakan untuk prediksi", "body": "Asosiasi dapat dipakai memperkirakan nilai saat salah satu variabel berubah."},
        ],
        "summary": "Asosiasi menunjukkan kecenderungan hubungan antar variabel, bukan sebab-akibat langsung.",
        "voiceover_script": "Sebaran titik membantu kita membaca ada tidaknya kecenderungan hubungan antara dua variabel.",
    },
    "manim.wave_optics.v1": {
        "title": "Getaran, Gelombang, dan Optik",
        "subtitle": "Pola sinus menggambarkan rambatan gelombang periodik.",
        "formula_latex": "y = 2\\sin(x)",
        "function": {"type": "sine", "params": {"a": 2, "b": 1, "c": 0, "d": 0}},
        "x_range": [-6, 6, 1],
        "y_range": [-3, 3, 1],
        "x_label": "posisi",
        "y_label": "simpangan",
        "graph_label": "gelombang sinus",
        "moving_label": "puncak",
        "x_path": [-6, -4, -2, 0, 2, 4, 6],
        "highlight_x": 2,
        "show_slope": True,
        "slope_text": "Kemiringan lokal menunjukkan arah perubahan simpangan di titik itu.",
        "steps": [
            {"title": "Kenali perioda", "body": "Gelombang mengulang pola secara periodik."},
            {"title": "Amati puncak dan lembah", "body": "Puncak bernilai positif maksimum, lembah bernilai negatif minimum."},
            {"title": "Hubungkan ke fenomena", "body": "Model gelombang dipakai pada bunyi, cahaya, dan getaran mekanik."},
        ],
        "summary": "Grafik sinus membantu memahami karakter periodik gelombang.",
        "voiceover_script": "Gelombang periodik dapat dimodelkan dengan fungsi sinus untuk membaca puncak, lembah, dan perubahan fase.",
    },
    "manim.heat_energy_machine.v1": {
        "title": "Kalor dan Perpindahan Energi",
        "subtitle": "Temperatur berubah seiring aliran energi panas.",
        "formula_latex": "T(t)=1.2t+25",
        "function": {"type": "linear", "params": {"m": 1.2, "b": 25}},
        "x_range": [0, 10, 1],
        "y_range": [24, 40, 2],
        "x_label": "menit",
        "y_label": "suhu",
        "graph_label": "tren suhu",
        "moving_label": "temperatur",
        "x_path": [0, 2, 4, 6, 8, 10],
        "highlight_x": 6,
        "show_slope": True,
        "slope_text": "Kemiringan positif menunjukkan suhu meningkat per satuan waktu.",
        "steps": [
            {"title": "Baca kondisi awal", "body": "Nilai awal menunjukkan temperatur saat t = 0."},
            {"title": "Amati laju naik", "body": "Setiap menit, suhu bertambah dengan laju hampir konstan."},
            {"title": "Prediksi nilai berikutnya", "body": "Tren linear memudahkan memperkirakan temperatur pada waktu lain."},
        ],
        "summary": "Grafik suhu-waktu membantu menjelaskan perpindahan energi panas.",
        "voiceover_script": "Saat energi panas masuk ke sistem, temperatur naik dan dapat diamati sebagai tren pada grafik.",
    },
    "manim.modern_atomic_nuclear.v1": {
        "title": "Model Atom Modern dan Peluruhan",
        "subtitle": "Perubahan jumlah inti dapat dimodelkan secara eksponensial.",
        "formula_latex": "N(t)=8(0.5)^t",
        "function": {"type": "exponential", "params": {"a": 8, "base": 0.5, "k": 1, "c": 0}},
        "x_range": [0, 6, 1],
        "y_range": [0, 9, 1],
        "x_label": "waktu",
        "y_label": "jumlah relatif",
        "graph_label": "kurva peluruhan",
        "moving_label": "N",
        "x_path": [0, 1, 2, 3, 4, 5, 6],
        "highlight_x": 3,
        "show_slope": False,
        "steps": [
            {"title": "Nilai awal inti", "body": "Pada awal pengamatan, jumlah inti masih maksimum."},
            {"title": "Laju peluruhan", "body": "Jumlah inti berkurang seiring waktu mengikuti pola eksponensial."},
            {"title": "Interpretasi kurva", "body": "Kurva menurun tajam di awal lalu melandai pada waktu besar."},
        ],
        "summary": "Model eksponensial cocok untuk menggambarkan peluruhan radioaktif.",
        "voiceover_script": "Pada peluruhan inti, penurunan jumlah partikel biasanya mengikuti kurva eksponensial menurun.",
    },
    "manim.quadratic_model.v1": {
        "title": "Model Kuadrat dan Parabola",
        "subtitle": "Fungsi kuadrat menghasilkan grafik berbentuk parabola.",
        "formula_latex": "f(x)=x^2-2x-3",
        "function": {"type": "quadratic", "params": {"a": 1, "b": -2, "c": -3}},
        "x_range": [-3, 5, 1],
        "y_range": [-5, 10, 1],
        "x_label": "x",
        "y_label": "f(x)",
        "graph_label": "parabola kuadrat",
        "moving_label": "titik f(x)",
        "x_path": [-3, -1, 0, 1, 2, 3, 4],
        "highlight_x": 1,
        "show_slope": True,
        "slope_text": "Di sekitar puncak parabola, laju perubahan mendekati nol.",
        "steps": [
            {"title": "Baca bentuk kurva", "body": "Parabola membuka ke atas karena koefisien x^2 bernilai positif."},
            {"title": "Ikuti titik bergerak", "body": "Perubahan x memindahkan titik pada kurva sesuai nilai fungsi."},
            {"title": "Amati puncak", "body": "Titik puncak menjadi nilai minimum fungsi kuadrat pada kasus ini."},
        ],
        "summary": "Model kuadrat memudahkan analisis titik puncak dan arah bukaan parabola.",
        "voiceover_script": "Grafik kuadrat membantu melihat bagaimana fungsi berubah dan di mana nilai ekstremnya berada.",
    },
    "manim.exponential_growth.v1": {
        "audience_level": "smp",
        "title": "Pertumbuhan Eksponensial",
        "subtitle": "Nilai bertambah dengan faktor tetap setiap langkah.",
        "terms": [1, 2, 4, 8],
        "rule": "Dikalikan 2 setiap langkah",
        "table_values": [
            {"n": 1, "value": 1},
            {"n": 2, "value": 2},
            {"n": 3, "value": 4},
            {"n": 4, "value": 8},
        ],
        "target_term": {"n": 5, "value": 16},
        "steps": [
            {"title": "Amati faktor pengali", "body": "Setiap suku diperoleh dengan mengalikan suku sebelumnya dengan 2."},
            {"title": "Lanjutkan pola", "body": "Setelah 8, suku berikutnya adalah 16 karena 8 x 2."},
        ],
        "summary": "Pertumbuhan eksponensial terjadi saat perubahan menggunakan faktor kali tetap.",
        "voiceover_script": "Pada pertumbuhan eksponensial, nilai tidak bertambah selisih tetap, tetapi bertambah dengan faktor kali yang tetap.",
    },
    "manim.financial_growth.v1": {
        "audience_level": "smp",
        "title": "Pertumbuhan Nilai Tabungan",
        "subtitle": "Nilai tabungan naik secara persentase per periode.",
        "terms": [100, 120, 144, 173],
        "rule": "Naik 20% setiap periode",
        "table_values": [
            {"n": 1, "value": 100},
            {"n": 2, "value": 120},
            {"n": 3, "value": 144},
            {"n": 4, "value": 173},
        ],
        "target_term": {"n": 5, "value": 208},
        "steps": [
            {"title": "Hitung kenaikan persentase", "body": "Setiap periode, nilai baru = nilai lama x 1,2."},
            {"title": "Prediksi periode berikutnya", "body": "Setelah 173, nilai perkiraan periode berikutnya sekitar 208."},
        ],
        "summary": "Model pertumbuhan persentase membantu memperkirakan nilai keuangan di masa depan.",
        "voiceover_script": "Dalam konteks keuangan, pertumbuhan periodik sering dimodelkan sebagai kenaikan persentase dari nilai sebelumnya.",
    },
    "manim.geometry_transform.v1": {
        "title": "Transformasi Geometri Dasar",
        "subtitle": "Bentuk bisa digeser, diputar, atau dicerminkan tanpa mengubah sifat utamanya.",
        "shape_type": "triangle",
        "dimensions": {"length": 4, "width": 3, "unit": "satuan"},
        "formula_latex": "A' = A",
        "highlight_features": ["translasi", "rotasi", "refleksi"],
        "steps": [
            {"title": "Kenali bangun awal", "body": "Amati bentuk awal sebelum transformasi dilakukan."},
            {"title": "Lakukan transformasi", "body": "Bangun bisa dipindah atau diputar, tetapi relasi sisinya tetap."},
            {"title": "Bandingkan hasil", "body": "Periksa posisi baru dan pastikan sifat utama bangun tetap."},
        ],
        "summary": "Transformasi mengubah posisi atau orientasi, bukan identitas dasar bangun.",
        "voiceover_script": "Transformasi geometri membantu kita melihat perubahan posisi bangun sambil menjaga sifat pentingnya.",
    },
    "manim.geometry_theorem.v1": {
        "title": "Teorema Sudut Segitiga",
        "subtitle": "Jumlah sudut dalam segitiga selalu 180 derajat.",
        "shape_type": "triangle",
        "dimensions": {"length": 5, "width": 4, "unit": "satuan"},
        "formula_latex": "\\angle A + \\angle B + \\angle C = 180^\\circ",
        "highlight_features": ["sudut A", "sudut B", "sudut C"],
        "steps": [
            {"title": "Tentukan tiga sudut", "body": "Segitiga memiliki tiga sudut yang saling berhubungan."},
            {"title": "Jumlahkan sudut", "body": "Ketiga sudut dalam segitiga jika dijumlahkan selalu 180 derajat."},
            {"title": "Gunakan untuk hitung sudut", "body": "Jika dua sudut diketahui, sudut ketiga bisa dicari dari total 180 derajat."},
        ],
        "summary": "Teorema jumlah sudut segitiga menjadi dasar banyak soal geometri.",
        "voiceover_script": "Dengan teorema jumlah sudut, kita dapat menemukan sudut yang belum diketahui secara sistematis.",
    },
    "manim.geometry_measurement.v1": {
        "title": "Pengukuran Luas dan Keliling",
        "subtitle": "Gunakan panjang dan lebar untuk menghitung besaran geometri.",
        "shape_type": "rectangle",
        "dimensions": {"length": 8, "width": 5, "unit": "cm"},
        "formula_latex": "L = p \\times l,\\ K = 2(p+l)",
        "highlight_features": ["panjang", "lebar", "luas"],
        "steps": [
            {"title": "Ukur dimensi", "body": "Catat panjang dan lebar bangun secara tepat."},
            {"title": "Hitung luas", "body": "Luas diperoleh dari panjang dikali lebar."},
            {"title": "Hitung keliling", "body": "Keliling diperoleh dari jumlah seluruh sisi luar."},
        ],
        "summary": "Pengukuran yang tepat menghasilkan perhitungan luas dan keliling yang akurat.",
        "voiceover_script": "Dengan ukuran sisi yang benar, kita bisa menghitung luas dan keliling bangun secara konsisten.",
    },
    "manim.elementary_number_line_place_value.v1": {
        "phase": "C",
        "audience_level": "sd",
        "title": "Nilai Tempat di Garis Bilangan",
        "subtitle": "Angka lebih besar berada lebih kanan pada garis bilangan.",
        "number_range": {"min": 0, "max": 100, "step": 10},
        "markers": [{"value": 30, "label": "30"}, {"value": 70, "label": "70"}],
        "highlight_values": [30, 70],
        "operation": {"type": "compare", "from": 30, "to": 70, "label": "70 lebih besar dari 30"},
        "steps": [
            {"title": "Tempatkan nilai puluhan", "body": "30 dan 70 ditempatkan sesuai urutan nilainya di garis bilangan."},
            {"title": "Bandingkan posisi", "body": "Bilangan di posisi lebih kanan bernilai lebih besar."},
        ],
        "summary": "Nilai tempat membantu membaca urutan dan besar bilangan.",
        "voiceover_script": "Pada garis bilangan puluhan, posisi angka membuat perbandingan nilai jadi lebih mudah dipahami.",
    },
    "manim.electricity_magnetism.v1": {
        "title": "Gaya Listrik dan Magnet",
        "subtitle": "Resultan gaya menentukan arah gerak partikel bermuatan.",
        "object": {"type": "particle", "label": "Muatan q"},
        "forces": [
            {"label": "F_listrik", "magnitude": 8, "unit": "N", "direction": "right"},
            {"label": "F_magnet", "magnitude": 3, "unit": "N", "direction": "left"},
        ],
        "resultant": {"magnitude": 5, "unit": "N", "direction": "right"},
        "motion_response": "Partikel cenderung bergerak ke kanan.",
        "steps": [
            {"title": "Identifikasi gaya", "body": "Muatan menerima gaya listrik dan gaya magnet dengan arah berlawanan."},
            {"title": "Hitung resultan", "body": "Karena 8 N ke kanan dan 3 N ke kiri, resultannya 5 N ke kanan."},
            {"title": "Prediksi gerak", "body": "Arah resultan menjadi acuan arah percepatan partikel."},
        ],
        "summary": "Gerak partikel ditentukan oleh resultan gaya total yang bekerja padanya.",
        "voiceover_script": "Pada sistem listrik dan magnet, kita menjumlahkan semua gaya vektor untuk mengetahui arah gerak akhir.",
    },
}


def deep_merge(base: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(base)
    for key, value in patch.items():
        out[key] = deepcopy(value)
    return out


def normalize_narration(payload: dict[str, Any]) -> dict[str, Any]:
    steps = payload.get("steps", [])
    if not isinstance(steps, list):
        steps = []
        payload["steps"] = steps

    for step in steps:
        if not isinstance(step, dict):
            continue
        text = str(step.get("narration", "")).strip()
        if text:
            continue
        title = str(step.get("title", "")).strip()
        body = str(step.get("body", "")).strip()
        if title and body:
            step["narration"] = f"{title}. {body}"
        else:
            step["narration"] = title or body

    intro = str(payload.get("voiceover_script", "")).strip()
    summary = str(payload.get("summary", "")).strip()

    payload["intro_narration"] = intro
    payload["summary_narration"] = summary
    if not str(payload.get("voiceover_script", "")).strip() and intro:
        payload["voiceover_script"] = intro

    segments: list[dict[str, Any]] = []
    if intro:
        segments.append({"slot": "intro", "text": intro})
    for idx, step in enumerate(steps, start=1):
        if not isinstance(step, dict):
            continue
        narr = str(step.get("narration", "")).strip()
        if narr:
            segments.append({"slot": "step", "step_index": idx, "text": narr})
    if summary:
        segments.append({"slot": "summary", "text": summary})
    payload["narration_segments"] = segments
    return payload


def template_slug(template_id: str) -> str:
    token = template_id.strip().lower().replace("manim.", "")
    if token.endswith(".v1"):
        token = token[:-3]
    return token


def main() -> None:
    touched = 0
    for template_id, patch in OVERRIDES.items():
        sample_path = SAMPLE_ROOT / template_id / "sample_01.json"
        if not sample_path.exists():
            continue
        data = json.loads(sample_path.read_text(encoding="utf-8"))
        data = deep_merge(data, patch)
        data["template_id"] = template_id
        data["id"] = f"sample_{template_slug(template_id)}"
        data = normalize_narration(data)
        sample_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        touched += 1
    print(f"Retargeted sample specs: {touched}")


if __name__ == "__main__":
    main()
