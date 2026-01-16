# Demo Question Bank - Matematika Kelas 3 & 6

## 📊 Summary

**Total Soal:** 211 soal  
**Kelas 3:** 95 soal  
**Kelas 6:** 116 soal

---

## 📁 File Structure

### Kelas 3 (95 soal)
1. `matematika-kelas3-part1.json` - 33 soal
2. `matematika-kelas3-part2.json` - 33 soal
3. `matematika-kelas3-part3.json` - 24 soal
4. `matematika-campuran.json` - 5 soal kelas 3

### Kelas 6 (116 soal)
1. `matematika-kelas6-part1.json` - 31 soal
2. `matematika-kelas6-part2.json` - 31 soal
3. `matematika-kelas6-part3.json` - 24 soal
4. `matematika-campuran.json` - 16 soal kelas 6 + 14 soal campuran

---

## 📚 Topik yang Dicakup

### Kelas 3
- **Penjumlahan dan Pengurangan** (30+ soal)
  - Penjumlahan 2 bilangan
  - Pengurangan 2 bilangan
  - Operasi campuran
  - Soal cerita

- **Perkalian dan Pembagian** (30+ soal)
  - Perkalian dasar (1-12)
  - Pembagian dasar
  - Soal cerita

- **Pecahan Sederhana** (15+ soal)
  - Mengenal pecahan
  - Penjumlahan pecahan
  - Pengurangan pecahan
  - Perbandingan pecahan

- **Bangun Datar** (10+ soal)
  - Mengenal bangun datar
  - Keliling persegi & persegi panjang
  - Luas persegi & persegi panjang

- **Pengukuran** (10+ soal)
  - Konversi satuan panjang
  - Konversi satuan berat
  - Konversi satuan waktu

### Kelas 6
- **Bilangan Bulat** (20+ soal)
  - Penjumlahan bilangan bulat
  - Pengurangan bilangan bulat
  - Perkalian bilangan bulat
  - Pembagian bilangan bulat
  - Operasi campuran

- **Pecahan dan Desimal** (40+ soal)
  - Operasi pecahan (tambah, kurang, kali, bagi)
  - Operasi desimal
  - Konversi pecahan-desimal
  - Pecahan campuran

- **Geometri** (25+ soal)
  - Luas bangun datar (segitiga, trapesium, lingkaran, dll)
  - Keliling lingkaran
  - Volume bangun ruang (kubus, balok, tabung)
  - Luas permukaan

- **Statistika Sederhana** (15+ soal)
  - Rata-rata
  - Median
  - Modus

- **Soal Cerita** (16+ soal)
  - Persentase (diskon, untung/rugi)
  - Kecepatan, jarak, waktu
  - Perbandingan
  - Aplikasi geometri

---

## 🎯 Tingkat Kesulitan

| Tingkat | Kelas 3 | Kelas 6 | Total |
|---------|---------|---------|-------|
| Mudah | ~50 soal | ~35 soal | ~85 soal |
| Sedang | ~40 soal | ~70 soal | ~110 soal |
| Sulit | ~5 soal | ~11 soal | ~16 soal |

---

## 🏷️ Tags yang Digunakan

### Kelas 3
- `operasi-hitung`, `penjumlahan`, `pengurangan`
- `perkalian`, `pembagian`
- `pecahan`, `konsep-dasar`, `penyederhanaan`
- `geometri`, `bangun-datar`, `keliling`, `luas`
- `pengukuran`, `konversi`, `waktu`, `berat`, `panjang`
- `soal-cerita`

### Kelas 6
- `bilangan-bulat`, `operasi-campuran`
- `pecahan`, `desimal`, `konversi`
- `geometri`, `lingkaran`, `segitiga`, `trapesium`, `jajar-genjang`, `belah-ketupat`
- `bangun-ruang`, `volume`, `luas-permukaan`, `kubus`, `balok`, `tabung`
- `statistika`, `rata-rata`, `median`, `modus`
- `soal-cerita`, `persentase`, `kecepatan`, `perbandingan`

---

## 📝 Format Soal

Setiap soal memiliki struktur:
```json
{
  "grade": 3,
  "subject": "Matematika",
  "topic": "Penjumlahan dan Pengurangan",
  "type": "pilgan",
  "difficulty": "mudah",
  "text": "Berapa hasil dari 45 + 23?",
  "options": ["68", "78", "58", "88"],
  "answer": "68",
  "explanation": "45 + 23 = 68"
}
```

**Field Descriptions:**
- `grade`: Kelas (1-6)
- `subject`: Mata pelajaran
- `topic`: Topik/sub-bab
- `type`: Tipe soal (`pilgan` untuk pilihan ganda)
- `difficulty`: Tingkat kesulitan (`mudah`, `sedang`, `sulit`)
- `text`: Teks soal
- `options`: Array 4 pilihan jawaban
- `answer`: Jawaban yang benar (nilai dari options, bukan index)
- `explanation`: Penjelasan jawaban

---

## 🚀 Cara Import

### Import Satu File
```bash
python manage.py import_questions data/questions/matematika-kelas3-part1.json
```

### Import Semua File Sekaligus
```bash
# Kelas 3
python manage.py import_questions data/questions/matematika-kelas3-part1.json
python manage.py import_questions data/questions/matematika-kelas3-part2.json
python manage.py import_questions data/questions/matematika-kelas3-part3.json

# Kelas 6
python manage.py import_questions data/questions/matematika-kelas6-part1.json
python manage.py import_questions data/questions/matematika-kelas6-part2.json
python manage.py import_questions data/questions/matematika-kelas6-part3.json

# Campuran
python manage.py import_questions data/questions/matematika-campuran.json
```

### Import dengan Script
Buat file `import_all_questions.sh`:
```bash
#!/bin/bash
cd /Users/kaqfa/Documents/Project/Pribadi/Bank-Soal-Django
source venv/bin/activate

for file in data/questions/*.json; do
    echo "Importing $file..."
    python manage.py import_questions "$file"
done

echo "✅ All questions imported successfully!"
```

Jalankan:
```bash
chmod +x import_all_questions.sh
./import_all_questions.sh
```

---

## ✅ Quality Checklist

- [x] Semua soal memiliki 4 opsi jawaban
- [x] Setiap soal memiliki answer_key yang jelas
- [x] Setiap soal memiliki explanation
- [x] Soal diberi tag yang sesuai
- [x] Tingkat kesulitan bervariasi
- [x] Mencakup berbagai topik sesuai kurikulum
- [x] Format JSON valid
- [x] Total soal >200 (achieved: 211)

---

## 📈 Distribusi Soal

### Kelas 3 (95 soal)
```
Penjumlahan & Pengurangan: 32%
Perkalian & Pembagian:     32%
Pecahan Sederhana:         16%
Bangun Datar:              11%
Pengukuran:                9%
```

### Kelas 6 (116 soal)
```
Pecahan & Desimal:         35%
Bilangan Bulat:            17%
Geometri:                  22%
Statistika:                13%
Soal Cerita:               13%
```

---

## 💡 Tips Penggunaan

1. **Untuk Demo:** Import semua file untuk mendapatkan bank soal yang lengkap
2. **Untuk Testing:** Pilih 1-2 file saja untuk testing cepat
3. **Untuk Quiz:** Gunakan filter berdasarkan topic dan difficulty di admin panel
4. **Untuk Analytics:** Soal sudah diberi tag yang memudahkan analisis per skill

---

## 🎓 Next Steps

Setelah import:
1. Verifikasi di Django Admin (`/admin/questions/question/`)
2. Buat quiz menggunakan soal-soal ini
3. Test quiz flow dengan berbagai kombinasi soal
4. Lihat analytics untuk memastikan scoring bekerja dengan baik

---

**Status:** ✅ Ready for Import  
**Created:** 16 Januari 2026  
**Total Files:** 7 JSON files  
**Total Questions:** 211 soal
