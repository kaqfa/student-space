# Product Requirements Document (PRD)

## Ruang Belajar — Platform Homeschooling & Persiapan Ujian

**Versi:** 2.0  
**Tanggal:** 26 Juni 2026  
**Product Owner:** Fahri (Kaqfa)  
**Status:** Draft

---

## Daftar Isi

1. [Ringkasan Eksekutif](#1-ringkasan-eksekutif)
2. [Latar Belakang & Masalah](#2-latar-belakang--masalah)
3. [Target Pengguna & Persona](#3-target-pengguna--persona)
4. [Arsitektur Sistem](#4-arsitektur-sistem)
5. [Data Model (Konseptual)](#5-data-model-konseptual)
6. [Fitur & Spesifikasi](#6-fitur--spesifikasi)
7. [Monetisasi & Subscription](#7-monetisasi--subscription)
8. [User Interface & Experience](#8-user-interface--experience)
9. [Non-Functional Requirements](#9-non-functional-requirements)
10. [Roadmap & Prioritas](#10-roadmap--prioritas)
11. [Metrik Keberhasilan](#11-metrik-keberhasilan)
12. [Risiko & Mitigasi](#12-risiko--mitigasi)
13. [Lampiran](#13-lampiran)

---

## 1. Ringkasan Eksekutif

### 1.1 Visi Produk

Ruang Belajar adalah platform pembelajaran berbasis web yang dirancang untuk membantu orang tua homeschooling mengelola pendidikan anak dari jenjang SD hingga SMP. Platform ini menyediakan bank soal terstruktur, ujian simulasi (try-out), pelacakan perkembangan lintas tahun ajaran, dan analitik mendalam — sehingga orang tua memiliki visibilitas penuh terhadap kekuatan dan kelemahan belajar anak.

Platform ini juga menjawab kebutuhan spesifik pasar: **persiapan Tes Kemampuan Akademik (TKA)** untuk masuk SD, SMP, maupun program unggulan, dengan fitur try-out simulasi, skor kesiapan, dan rencana belajar otomatis.

### 1.2 Proposisi Nilai

- **Untuk orang tua:** Satu tempat untuk mengelola, memantau, dan mengevaluasi pendidikan anak — termasuk yang sudah naik kelas.
- **Untuk anak:** Pengalaman belajar mandiri yang terstruktur dengan umpan balik langsung.
- **Untuk pasar TKA:** Alternatif bimbel yang terjangkau dengan analitik setara lembaga profesional.

### 1.3 Tech Stack

| Komponen | Teknologi |
|---|---|
| Backend | Django 5.x, Python 3.12+ |
| Frontend | Django Templates, HTMX 2.x, Tailwind CSS 3.x |
| Admin Interface | Django Admin (built-in) |
| Database | PostgreSQL 16 |
| Deployment | Docker, Phusion Passenger + Apache (kompatibel DomaiNesia) |
| Hosting | VPS (Linux) |
| Payment | Midtrans / Xendit |
| Task Queue | Celery + Redis (untuk report generation, notifikasi) |

---

## 2. Latar Belakang & Masalah

### 2.1 Konteks

Jumlah keluarga yang memilih jalur homeschooling di Indonesia terus meningkat, didorong oleh fleksibilitas kurikulum dan ketidakpuasan terhadap sistem sekolah formal. Namun, orang tua homeschooling menghadapi beberapa tantangan fundamental:

1. **Tidak ada LKS atau bank soal terstruktur** yang bisa menjadi pedoman pengajaran harian.
2. **Tidak ada visibilitas terhadap perkembangan anak** — semuanya bersifat subjektif dan manual.
3. **Keterbatasan waktu** — orang tua yang juga bekerja kesulitan menyiapkan materi berkualitas.
4. **Persiapan ujian masuk (TKA) bergantung pada bimbel mahal** tanpa transparansi data.
5. **Data pembelajaran tidak terakumulasi** — ketika anak naik kelas, catatan tahun sebelumnya hilang atau tercerai-berai.

### 2.2 Peluang Pasar

Segmen persiapan TKA memiliki demand yang tinggi dan willingness-to-pay yang jelas. Orang tua yang menyiapkan anaknya untuk masuk SD/SMP favorit biasanya menghabiskan Rp 1-5 juta per bulan untuk bimbel. Platform digital yang menawarkan try-out simulasi dengan analitik terukur dan harga terjangkau memiliki ruang yang besar.

### 2.3 Kriteria Keberhasilan

- Mengurangi waktu persiapan materi belajar dari hitungan jam menjadi menit.
- Memberikan visibilitas data-driven terhadap perkembangan anak per kompetensi.
- Menyediakan prediksi kesiapan TKA yang akurat berdasarkan data try-out berkala.
- Menghasilkan recurring revenue melalui model subscription.

---

## 3. Target Pengguna & Persona

### 3.1 Peran Pengguna (User Roles)

| Peran | Deskripsi | Interface | Hak Akses |
|---|---|---|---|
| **Admin** | Pengelola platform, mengelola konten dan pengguna | Django Admin | Full access, manajemen konten, manajemen user, konfigurasi sistem |
| **Orang Tua** | Mendaftarkan anak, memantau perkembangan, memilih paket | Custom UI | Dashboard orang tua, kelola profil anak, lihat analytics, kelola subscription |
| **Pengajar** | Opsional — tutor yang membantu orang tua | Django Admin (limited) | Assign soal, lihat progress anak yang di-assign, buat quiz custom |
| **Siswa** | Anak yang mengerjakan soal dan quiz | Custom UI | Mengerjakan quiz, lihat hasil sendiri, lihat progress pribadi |

### 3.2 Persona Utama

**Persona 1: Ibu Ratna — Orang Tua Homeschooling**

- Ibu rumah tangga dengan 2 anak (kelas 2 dan kelas 5 SD)
- Homeschooling karena lingkungan sekolah yang kurang kondusif
- Kesulitan tracking materi apa yang sudah diajarkan dan belum
- Butuh bank soal yang terstruktur per kurikulum
- Ingin lihat perkembangan anak dari waktu ke waktu, termasuk lintas tahun ajaran

**Persona 2: Pak Budi — Orang Tua Persiapan TKA**

- Ayah yang bekerja, anak kelas 6 akan masuk SMP favorit
- Sudah coba bimbel tapi merasa "buta" — tidak tahu anak kuat di mana, lemah di mana
- Mau try-out berkala dengan analitik seperti di lembaga bimbel besar
- Bersedia bayar untuk fitur premium asal ada value yang jelas

**Persona 3: Kak Dina — Tutor Freelance**

- Tutor privat yang menangani 5-8 anak homeschooling
- Butuh satu platform untuk assign soal ke masing-masing anak dan lihat progress mereka
- Saat ini pakai WhatsApp + foto soal — tidak efisien

---

## 4. Arsitektur Sistem

### 4.1 Struktur Aplikasi Django

Platform dibagi menjadi beberapa Django app berdasarkan domain:

| App | Tanggung Jawab |
|---|---|
| `accounts` | Registrasi, autentikasi, profil user, manajemen keluarga, role management |
| `academic` | Data referensi akademik: jenjang, kelas, mata pelajaran, topik, kompetensi dasar (KD), tahun ajaran, enrollment siswa |
| `questions` | Bank soal, tag, set soal, import/export konten |
| `quizzes` | Sesi quiz, konfigurasi mode quiz, jawaban, penilaian otomatis |
| `tryouts` | Cetak biru ujian (exam blueprint), sesi try-out, skor per seksi, rencana belajar, laporan kesiapan |
| `analytics` | Perhitungan metrik, dashboard progress, laporan, visualisasi data |
| `subscriptions` | Paket langganan, manajemen subscription, integrasi payment gateway, feature gating |
| `core` | Utilitas bersama, HTMX helper, middleware, template tags, konfigurasi sistem |

### 4.2 Pola Arsitektur

- **Server-rendered dengan progressive enhancement:** Django Templates sebagai basis, HTMX untuk interaksi dinamis tanpa full page reload.
- **Feature gating via middleware:** Setiap request dicek terhadap subscription plan aktif untuk menentukan fitur yang tersedia.
- **Background processing:** Celery + Redis untuk tugas berat (generate PDF report, kalkulasi analitik batch, kirim notifikasi email).
- **Multi-tenancy via foreign key:** Bukan schema-level isolation, tetapi semua data terikat ke `Family` → filtering di query level.

---

## 5. Data Model (Konseptual)

Bagian ini menjelaskan entitas data dan relasinya secara konseptual. Tidak ada implementasi kode — fokus pada *apa* yang disimpan dan *mengapa*.

### 5.1 Domain: Accounts & Family

| Entitas | Deskripsi | Relasi Utama |
|---|---|---|
| **User** | Akun pengguna platform (extends Django User) | — |
| **Family** | Unit keluarga — wadah yang mengikat orang tua dan anak-anak | Has many User (parents), has many StudentProfile |
| **StudentProfile** | Profil siswa (anak) — berisi data personal dan akademik | Belongs to Family, has many Enrollment |
| **ParentProfile** | Profil orang tua — preferensi notifikasi, settings | Belongs to User, belongs to Family |
| **TutorProfile** | Profil pengajar — data profesional | Belongs to User, has many StudentProfile (assigned) |

**Catatan desain:**
- Satu `Family` bisa punya banyak orang tua (ayah + ibu) dan banyak anak.
- `StudentProfile` terpisah dari `User` karena anak kecil mungkin tidak punya akun sendiri — orang tua yang mengoperasikan.
- Jika anak sudah cukup umur, `StudentProfile` bisa dihubungkan ke `User` agar anak login sendiri.

### 5.2 Domain: Academic Reference

| Entitas | Deskripsi | Relasi Utama |
|---|---|---|
| **EducationLevel** | Jenjang pendidikan (SD, SMP) | Has many Grade |
| **Grade** | Kelas/tingkat (Kelas 1, Kelas 2, ..., Kelas 9) | Belongs to EducationLevel, has many Subject |
| **Subject** | Mata pelajaran (Matematika, IPA, Bahasa Indonesia, dll.) | Many-to-many with Grade (melalui GradeSubject) |
| **GradeSubject** | Tabel penghubung — mendefinisikan mapel apa saja yang berlaku di kelas tertentu | Belongs to Grade, belongs to Subject |
| **Topic** | Topik/bab dalam suatu mata pelajaran di kelas tertentu | Belongs to GradeSubject, has many Competency |
| **Competency** | Kompetensi Dasar (KD) — standar capaian kurikulum | Belongs to Topic |
| **AcademicYear** | Tahun ajaran (2025/2026, 2026/2027) | Has many Enrollment |
| **Enrollment** | Pendaftaran siswa di kelas tertentu pada tahun ajaran tertentu | Belongs to StudentProfile, belongs to Grade, belongs to AcademicYear |

**Catatan desain:**
- `Grade` adalah tabel tersendiri, bukan enum atau array — ini mempermudah relasi, query, dan penambahan jenjang baru di masa depan.
- `GradeSubject` diperlukan karena tidak semua mapel ada di semua kelas (contoh: IPA baru ada di kelas 4 SD ke atas di Kurikulum Merdeka).
- `Enrollment` merekam jejak kelas anak per tahun ajaran — ini yang memungkinkan orang tua melihat riwayat lintas tahun.
- `Competency` (KD) di-attach ke `Topic`, bukan langsung ke `Grade`, karena satu KD bisa mencakup beberapa topik.

### 5.3 Domain: Questions & Content

| Entitas | Deskripsi | Relasi Utama |
|---|---|---|
| **Question** | Satu butir soal | Belongs to Topic, has many Tag (M2M), has many QuestionOption |
| **QuestionOption** | Pilihan jawaban (untuk soal pilihan ganda) | Belongs to Question |
| **Tag** | Label fleksibel untuk kategorisasi soal (problem-solving, literasi, HOTS, dll.) | Many-to-many with Question |
| **QuestionSet** | Kumpulan soal yang dikurasi (untuk paket latihan atau try-out) | Many-to-many with Question |
| **ImportBatch** | Metadata batch import soal (JSON) — untuk audit trail | Has many Question (yang di-import dalam batch tersebut) |

**Atribut penting pada Question:**
- Tipe soal: pilihan ganda, isian singkat, essay, benar/salah
- Tingkat kesulitan: mudah, sedang, sulit
- Penjelasan/pembahasan jawaban
- Media pendukung: gambar, audio (opsional)
- Status: draft, published, archived
- Sumber/referensi (opsional)

**Catatan desain:**
- Tag bersifat bebas dan cross-cutting — satu soal bisa punya tag "problem-solving" + "HOTS" + "kontekstual".
- `QuestionSet` memungkinkan kurasi soal tanpa mengubah data soal aslinya — satu soal bisa masuk ke banyak set.
- `ImportBatch` penting untuk traceability — jika ada soal bermasalah dari batch tertentu, bisa di-rollback.

### 5.4 Domain: Quizzes

| Entitas | Deskripsi | Relasi Utama |
|---|---|---|
| **QuizConfig** | Konfigurasi quiz: jumlah soal, filter topik/tag, mode, durasi | Created by User (orang tua/pengajar) |
| **QuizSession** | Sesi pengerjaan quiz oleh siswa | Belongs to StudentProfile, belongs to QuizConfig |
| **QuizAnswer** | Jawaban siswa per soal dalam satu sesi | Belongs to QuizSession, belongs to Question |

**Mode quiz:**
- **Practice:** Tanpa timer, ada feedback langsung setelah setiap soal.
- **Timed:** Dengan timer, feedback setelah selesai atau waktu habis.
- **Custom:** Pengajar/orang tua bisa atur jumlah soal, topik, tingkat kesulitan, dan durasi.

**Atribut penting pada QuizSession:**
- Status: in_progress, completed, timed_out, abandoned
- Waktu mulai, waktu selesai
- Skor total, skor per topik/tag
- Durasi aktual pengerjaan

**Atribut penting pada QuizAnswer:**
- Jawaban yang dipilih/ditulis
- Benar/salah (auto-graded untuk pilihan ganda dan isian)
- Waktu pengerjaan per soal (time spent)
- Urutan pengerjaan

### 5.5 Domain: Try-out & TKA Prep

| Entitas | Deskripsi | Relasi Utama |
|---|---|---|
| **ExamBlueprint** | Template/cetak biru format ujian | Has many ExamSection |
| **ExamSection** | Seksi dalam cetak biru (Numerasi: 15 soal, Literasi: 10 soal, dst.) | Belongs to ExamBlueprint, linked to Tag/Topic filter |
| **TryoutSession** | Sesi try-out yang dikerjakan siswa | Belongs to StudentProfile, belongs to ExamBlueprint |
| **TryoutSectionScore** | Skor per seksi dalam satu sesi try-out | Belongs to TryoutSession, belongs to ExamSection |
| **StudyPlan** | Rencana belajar yang di-generate dari hasil try-out | Belongs to StudentProfile |
| **StudyPlanItem** | Item dalam rencana belajar — area lemah + rekomendasi drill | Belongs to StudyPlan, linked to Tag/Topic |
| **ExamTarget** | Target ujian siswa — tanggal ujian, skor target | Belongs to StudentProfile, belongs to ExamBlueprint |

**Atribut penting pada ExamBlueprint:**
- Nama ujian (TKA SD Negeri, TKA SMP Favorit, SNBT SMA, dll.)
- Total durasi (menit)
- Passing score (jika ada)
- Deskripsi format dan aturan
- Status: active, archived

**Atribut penting pada ExamSection:**
- Nama seksi (Numerasi, Literasi, Penalaran, dll.)
- Jumlah soal
- Bobot skor
- Filter soal: topik, tag, tingkat kesulitan yang masuk ke seksi ini

**Atribut penting pada TryoutSession:**
- Skor total dan skor per seksi
- Persentil (jika ada data populasi cukup)
- Perbandingan dengan try-out sebelumnya (delta)

**Catatan desain:**
- `ExamBlueprint` adalah kunci fleksibilitas — mau TKA SD, TKA SMP, atau nanti SNBT SMA, tinggal buat blueprint baru tanpa ubah kode.
- Setiap seksi dalam blueprint mendefinisikan filter soal, sehingga saat generate try-out, sistem otomatis memilih soal yang sesuai (random dari pool yang memenuhi filter).
- `StudyPlan` di-generate secara otomatis dari analisis try-out: area dengan skor terendah → jadi prioritas latihan.
- `ExamTarget` memungkinkan fitur "countdown + readiness meter" — anak punya target tanggal ujian dan skor target, lalu sistem menghitung apakah tren skor try-out mengarah ke pencapaian target.

### 5.6 Domain: Analytics

| Entitas | Deskripsi | Relasi Utama |
|---|---|---|
| **ProgressSnapshot** | Rekaman periodik metrik progress siswa | Belongs to StudentProfile, belongs to AcademicYear |
| **MasteryRecord** | Tingkat penguasaan per topik/KD | Belongs to StudentProfile, belongs to Topic/Competency |

**Tingkat penguasaan (Mastery Level):**
- Not Attempted
- Beginner (akurasi < 40%)
- Developing (akurasi 40-60%)
- Proficient (akurasi 60-80%)
- Mastered (akurasi > 80%, minimal N attempt)

**Metrik yang dihitung:**
- Akurasi keseluruhan dan per topik/tag
- Tren akurasi over time
- Distribusi soal per mata pelajaran yang sudah dikerjakan
- Cakupan KD (berapa persen KD di kelas tersebut yang sudah dilatih)
- Kekuatan dan kelemahan (tag/topik dengan akurasi tertinggi dan terendah)
- Waktu rata-rata pengerjaan per soal
- Konsistensi (standar deviasi skor antar sesi)

**Catatan desain:**
- `ProgressSnapshot` dibuat secara periodik (misal mingguan) oleh background job, bukan dihitung real-time — ini untuk performa.
- `MasteryRecord` diupdate setiap kali ada quiz/try-out selesai.
- Analytics dashboard membaca dari snapshot dan record ini, bukan query langsung ke tabel jawaban.

### 5.7 Domain: Subscriptions

| Entitas | Deskripsi | Relasi Utama |
|---|---|---|
| **Plan** | Definisi paket langganan (Free, Basic, Pro) | Has many PlanFeature |
| **PlanFeature** | Fitur dan limitnya per plan | Belongs to Plan |
| **Subscription** | Langganan aktif suatu Family | Belongs to Family, belongs to Plan |
| **Invoice** | Catatan tagihan dan pembayaran | Belongs to Subscription |
| **PaymentTransaction** | Log transaksi dari payment gateway | Belongs to Invoice |

**Catatan desain:**
- Feature gating berbasis `PlanFeature` — setiap fitur punya key (contoh: `max_students`, `tryout_per_month`, `analytics_level`) dan value per plan.
- Middleware mengecek subscription aktif dan PlanFeature di setiap request yang membutuhkan gating.
- Subscription berbasis Family, bukan per User — satu subscription berlaku untuk seluruh keluarga.
- Grace period saat subscription expire — data tetap bisa diakses (read-only) selama N hari.

### 5.8 Diagram Relasi Antar Domain

Relasi tingkat tinggi antar domain:

```
Family ──┬── ParentProfile(s) ── User
         ├── StudentProfile(s) ──┬── Enrollment(s) ── Grade + AcademicYear
         │                       ├── QuizSession(s) ── QuizConfig
         │                       ├── TryoutSession(s) ── ExamBlueprint
         │                       ├── MasteryRecord(s) ── Topic/Competency
         │                       ├── ProgressSnapshot(s)
         │                       ├── StudyPlan(s)
         │                       └── ExamTarget(s)
         └── Subscription ── Plan

EducationLevel ── Grade ──┬── GradeSubject ── Subject
                          └── Topic ── Competency

Question ──┬── QuestionOption(s)
           ├── Tag(s)
           ├── Topic
           └── QuestionSet(s)

ExamBlueprint ── ExamSection(s) ── Tag/Topic filter
```

---

## 6. Fitur & Spesifikasi

### 6.1 Manajemen Akun & Keluarga

**F-01: Registrasi & Autentikasi**
- Registrasi orang tua dengan email/password
- Login/logout
- Reset password via email
- Opsional: login via Google OAuth

**F-02: Manajemen Keluarga**
- Orang tua membuat Family dan mengundang pasangan (orang tua kedua)
- Menambah profil anak ke Family
- Setiap anak: nama, tanggal lahir, foto (opsional)
- Anak bisa punya akun sendiri (opsional, untuk anak yang lebih besar) atau dioperasikan orang tua

**F-03: Enrollment & Kenaikan Kelas**
- Setiap awal tahun ajaran, orang tua mendaftarkan anak ke kelas tertentu (enrollment)
- Kenaikan kelas: membuat enrollment baru di kelas berikutnya pada tahun ajaran baru
- Riwayat enrollment tersimpan — orang tua bisa melihat jejak anak dari kelas 1 hingga saat ini
- Sistem bisa menampilkan data progress per tahun ajaran

### 6.2 Data Referensi Akademik

**F-04: Manajemen Jenjang, Kelas, dan Mata Pelajaran**
- Admin mengelola data referensi: jenjang (SD, SMP), kelas, mata pelajaran
- Mapping mata pelajaran ke kelas (tidak semua mapel ada di semua kelas)
- Manajemen topik per mata pelajaran per kelas
- Manajemen Kompetensi Dasar (KD) per topik
- Data ini bersifat referensi dan jarang berubah — dikelola oleh admin

**F-05: Tahun Ajaran**
- Admin membuat tahun ajaran baru
- Tahun ajaran aktif menentukan konteks default untuk enrollment dan progress tracking
- Saat berganti tahun ajaran, data tahun sebelumnya tetap tersimpan dan bisa diakses

### 6.3 Bank Soal

**F-06: Manajemen Soal**
- Admin membuat, mengedit, dan menghapus soal
- Tipe soal: pilihan ganda, isian singkat, essay, benar/salah
- Setiap soal terikat ke satu topik (yang implisit menentukan kelas dan mapelnya)
- Setiap soal memiliki: tingkat kesulitan, pembahasan, tag (multiple), media pendukung (opsional)
- Status soal: draft, published, archived
- Filter dan pencarian soal berdasarkan kelas, mapel, topik, tag, kesulitan, tipe

**F-07: Tagging System**
- Tag bersifat bebas dan cross-cutting
- Contoh tag: `problem-solving`, `HOTS`, `literasi`, `numerasi`, `kontekstual`, `penalaran-spasial`
- Tag digunakan untuk filtering soal, analitik per skill, dan konfigurasi seksi try-out
- Admin bisa mengelola (CRUD) daftar tag

**F-08: Import Soal via JSON**
- Admin mengupload file JSON berisi batch soal
- Format JSON terdefinisi dan terdokumentasi
- Validasi sebelum import: format, kelengkapan field, referensi topik/tag yang valid
- Preview sebelum commit
- Audit trail: setiap batch import tercatat dengan metadata (tanggal, jumlah soal, uploader)
- Rollback: bisa menghapus seluruh soal dari batch tertentu

**F-09: Question Set (Kurasi Soal)**
- Admin/pengajar membuat set soal dari soal-soal yang sudah ada
- Satu soal bisa masuk ke banyak set
- Set soal bisa digunakan sebagai sumber quiz atau try-out

### 6.4 Quiz Engine

**F-10: Konfigurasi Quiz**
- Orang tua/pengajar membuat konfigurasi quiz:
  - Pilih kelas dan mata pelajaran
  - Filter topik dan/atau tag
  - Jumlah soal
  - Mode: practice, timed, custom
  - Durasi (untuk mode timed)
  - Tingkat kesulitan (opsional: campuran, atau spesifik)
  - Randomisasi urutan soal dan pilihan jawaban

**F-11: Pengerjaan Quiz**
- Siswa mengerjakan quiz sesuai konfigurasi
- Mode practice: feedback langsung per soal (benar/salah + pembahasan)
- Mode timed: timer berjalan, auto-submit saat waktu habis
- Navigasi soal: maju, mundur, tandai ragu
- HTMX-powered: perpindahan soal tanpa full page reload
- Sesi tersimpan — jika browser tertutup, bisa dilanjutkan (untuk mode practice)

**F-12: Hasil Quiz**
- Skor total dan per topik/tag
- Detail per soal: jawaban siswa, jawaban benar, pembahasan
- Waktu pengerjaan per soal
- Ringkasan: jumlah benar, salah, tidak dijawab

### 6.5 Try-out & Persiapan TKA

**F-13: Exam Blueprint**
- Admin membuat cetak biru format ujian
- Definisi per seksi: nama, jumlah soal, bobot, filter topik/tag
- Contoh: "TKA SMP Negeri" → Numerasi (15 soal), Literasi (10 soal), Penalaran (10 soal), Pengetahuan Umum (5 soal)
- Blueprint bersifat reusable — bisa dipakai berkali-kali untuk generate try-out yang berbeda
- Admin bisa membuat blueprint baru untuk format ujian yang berbeda tanpa mengubah kode

**F-14: Sesi Try-out**
- Orang tua memulai sesi try-out untuk anak berdasarkan blueprint
- Sistem otomatis memilih soal secara random dari pool yang memenuhi filter tiap seksi
- Timer keseluruhan (sesuai durasi blueprint) dan opsional timer per seksi
- Pengerjaan berurutan per seksi atau bebas navigasi (sesuai konfigurasi blueprint)
- Auto-submit saat waktu habis

**F-15: Hasil Try-out & Scoring**
- Skor total dan skor per seksi
- Perbandingan dengan passing score (jika didefinisikan di blueprint)
- Perbandingan dengan try-out sebelumnya (delta skor)
- Breakdown per soal: jawaban, pembahasan
- Persentil (jika ada data populasi yang cukup — fitur future)

**F-16: Readiness Score & Countdown**
- Siswa/orang tua menetapkan target ujian: tanggal hari-H dan skor target
- Sistem menghitung readiness score berdasarkan tren skor try-out
- Visualisasi: "Skor saat ini vs target" + tren (naik/turun/stagnan)
- Countdown ke hari-H ujian
- Indikator: "On track", "Perlu effort lebih", "Belum siap" berdasarkan proyeksi tren

**F-17: Study Plan (Rencana Belajar Otomatis)**
- Setelah try-out, sistem menganalisis seksi/tag dengan skor terendah
- Generate rencana belajar berisi rekomendasi area yang perlu dilatih
- Setiap item rencana belajar terhubung ke topik/tag spesifik + link ke latihan soal terkait
- Orang tua bisa melihat dan menandai item yang sudah dilatih
- Rencana belajar diperbarui setiap ada try-out baru

### 6.6 Analytics & Monitoring Orang Tua

**F-18: Dashboard Orang Tua**
- Overview semua anak dalam keluarga
- Per anak: enrollment saat ini, aktivitas terakhir, skor rata-rata
- Quick stats: jumlah soal dikerjakan minggu ini, akurasi minggu ini
- Notifikasi: anak belum belajar N hari, try-out tersedia

**F-19: Progress Per Anak (Detail)**
- Akurasi keseluruhan dan per mata pelajaran
- Tren akurasi over time (grafik garis)
- Distribusi soal per mapel (pie chart)
- Kekuatan (tag/topik akurasi tinggi) dan kelemahan (tag/topik akurasi rendah)
- Cakupan KD: berapa persen KD di kelas tersebut yang sudah dilatih
- Filter berdasarkan tahun ajaran — bisa lihat progress tahun lalu vs tahun ini

**F-20: Riwayat Lintas Tahun Ajaran**
- Timeline perkembangan anak dari enrollment pertama hingga saat ini
- Per tahun ajaran: kelas, rata-rata akurasi, jumlah soal dikerjakan, mastery level per mapel
- Perbandingan antar tahun ajaran

**F-21: Laporan (Report)**
- Generate laporan progress per anak dalam format PDF
- Laporan try-out: skor, breakdown per seksi, rekomendasi
- Shareable: orang tua bisa share link atau PDF ke tutor/keluarga
- Laporan periodik (bulanan) via email — fitur premium

**F-22: Tag Heatmap & Mastery Matrix**
- Heatmap visual: skill/tag vs tingkat penguasaan
- Mastery matrix: topik × mastery level
- Identifikasi pola: "Anak kuat di soal hafalan tapi lemah di penalaran"

### 6.7 Manajemen Konten & Administrasi (Django Admin)

Semua fungsi administratif menggunakan Django Admin bawaan — tidak ada custom admin interface. Ini mencakup:

**F-23: Admin via Django Admin**
- Manajemen user, family, dan student profile
- CRUD data referensi akademik: jenjang, kelas, mata pelajaran, topik, KD, tahun ajaran
- CRUD soal: buat, edit, filter, search, bulk actions (publish/archive)
- Manajemen tag dan question set
- Import soal via JSON (custom admin action)
- Manajemen exam blueprint dan exam section
- Monitoring subscription, invoice, dan payment transaction
- Dashboard statistik via django-admin-charts atau sejenisnya (opsional)

**Kustomisasi Django Admin yang diperlukan:**
- Custom `ModelAdmin` dengan filter, search, dan list display yang informatif
- Inline admin untuk relasi parent-child (ExamSection inline di ExamBlueprint, QuestionOption inline di Question, dll.)
- Custom admin action untuk bulk import JSON, bulk publish/archive soal
- Read-only fields untuk data yang tidak boleh diedit langsung (skor, payment transaction)
- Admin permission groups: content manager (soal & blueprint), user manager (user & family), finance (subscription & payment)

**F-24: Content Pipeline**
- Workflow soal: draft → review → published (via status field + Django Admin filter)
- Bulk operations: publish/archive banyak soal sekaligus (Django Admin actions)
- Integrasi AI-assisted question generation (future — via import JSON dari pipeline LLM eksternal)

### 6.8 Fitur Pengajar (Opsional)

**F-25: Assignment**
- Pengajar di-assign ke siswa tertentu oleh orang tua
- Pengajar bisa membuat quiz custom untuk siswa yang di-assign
- Pengajar bisa melihat progress siswa yang di-assign

**F-26: Catatan Pengajar**
- Pengajar bisa menambahkan catatan per siswa per sesi
- Catatan visible oleh orang tua

---

## 7. Monetisasi & Subscription

### 7.1 Model Bisnis

Freemium dengan subscription bulanan/tahunan. Free tier cukup fungsional untuk menarik pengguna, paid tier menawarkan value yang jelas untuk persiapan ujian dan monitoring mendalam.

### 7.2 Tier & Fitur

| Fitur | Free | Basic | Pro |
|---|---|---|---|
| **Harga** | Rp 0 | ~Rp 49.000/bln | ~Rp 99.000/bln |
| **Jumlah anak** | 1 | 3 | Unlimited |
| **Soal latihan/bulan** | 50 soal | Unlimited | Unlimited |
| **Mode quiz** | Practice only | + Timed | + Custom + filter lanjutan |
| **Try-out/bulan** | — | 2 sesi | Unlimited |
| **Analytics** | Akurasi dasar | + Per topik + tren | + Heatmap + mastery matrix + export |
| **Riwayat tahun ajaran** | Tahun ini saja | 2 tahun | Seluruh riwayat |
| **Readiness score** | — | — | Tersedia |
| **Study plan otomatis** | — | — | Tersedia |
| **Laporan PDF** | — | Dasar | Lengkap + share |
| **Import JSON** | — | Tersedia | Tersedia + API |
| **Pengajar** | — | 1 pengajar | Unlimited |
| **Laporan email bulanan** | — | — | Tersedia |
| **Diskon tahunan** | — | ~20% | ~20% |

### 7.3 Payment Integration

- Payment gateway: Midtrans atau Xendit (evaluasi saat implementasi)
- Metode bayar: transfer bank, e-wallet (GoPay, OVO, Dana), kartu kredit
- Webhook untuk konfirmasi pembayaran otomatis
- Auto-renewal dengan notifikasi sebelum renewal
- Grace period 7 hari saat expire — akses read-only

### 7.4 Feature Gating Implementation

- Setiap fitur yang di-gate punya key unik (contoh: `max_students`, `quiz_modes`, `tryout_monthly_limit`)
- Tabel `PlanFeature` mendefinisikan value per plan per key
- Middleware mengecek subscription + plan + feature di setiap request terkait
- UI menampilkan indikator upgrade saat user menyentuh batas fitur (soft upsell, bukan hard block)

---

## 8. User Interface & Experience

### 8.1 Pembagian Interface

| Pengguna | Interface | Keterangan |
|---|---|---|
| Admin | Django Admin | Built-in, tidak ada custom UI. Kustomisasi via ModelAdmin, inline, actions. |
| Pengajar | Django Admin (limited) | Akses terbatas via Django Admin permission groups — hanya melihat siswa yang di-assign dan membuat quiz. |
| Orang Tua | Custom UI (Django Templates + HTMX + Tailwind) | Dashboard, manajemen anak, analytics, subscription. |
| Siswa | Custom UI (Django Templates + HTMX + Tailwind) | Simplified view untuk mengerjakan quiz/try-out dan melihat progress. |

Custom UI hanya dibangun untuk dua peran: **Orang Tua** dan **Siswa**. Semua fungsi admin dan pengajar cukup dilayani oleh Django Admin dengan kustomisasi yang tepat.

### 8.2 Prinsip Desain (Custom UI)

- **Mobile-first:** Mayoritas orang tua Indonesia mengakses via smartphone.
- **Minimal cognitive load:** Navigasi jelas, tidak overwhelm dengan terlalu banyak opsi.
- **Progressive disclosure:** Fitur lanjutan terungkap bertahap, tidak sekaligus.
- **Anak-friendly untuk siswa view:** Font besar, warna cerah, interaksi sederhana.
- **Data-rich untuk parent view:** Dashboard informatif tapi tidak cluttered.

### 8.3 Layout Utama

**Landing Page (Public)**
- Hero section: value proposition
- Fitur utama dengan ilustrasi
- Pricing table
- Testimoni (future)
- CTA: daftar gratis

**Parent Dashboard**
- Sidebar: navigasi utama
- Main area: overview anak-anak, quick actions
- Top bar: notifikasi, profil, subscription status

**Student View**
- Simplified layout: daftar mata pelajaran → topik → mulai quiz
- Progress bar visual
- Badge/streak (gamification ringan)

**Quiz/Try-out View**
- Full-screen focus mode
- Navigasi soal di sidebar atau bottom bar
- Timer prominent (untuk timed mode)
- Clear CTA per soal: pilih jawaban → next

### 8.4 Interaksi HTMX

Area yang menggunakan HTMX untuk partial update (hanya di custom UI):
- Navigasi soal dalam quiz (tanpa full reload)
- Dashboard charts (lazy load)
- Inline edit profil anak
- Toggle enrollment status
- Notifikasi real-time indicator

---

## 9. Non-Functional Requirements

### 9.1 Performa

- Halaman dashboard load < 2 detik
- Perpindahan soal dalam quiz < 500ms (HTMX partial)
- Kalkulasi analitik menggunakan pre-computed snapshot, bukan query on-the-fly
- Database indexing pada kolom yang sering di-filter: student_id, topic_id, tag, created_at

### 9.2 Keamanan

- Autentikasi berbasis session (Django default)
- CSRF protection pada semua form
- Row-level security: user hanya bisa akses data milik Family-nya sendiri
- Input sanitization pada semua field
- Rate limiting pada endpoint sensitif (login, registrasi, payment)
- HTTPS wajib

### 9.3 Skalabilitas

- Target awal: 100-500 keluarga
- Database: PostgreSQL single instance cukup untuk skala awal
- Static files: CDN atau object storage (S3-compatible)
- Background jobs: Celery worker terpisah
- Jika skala > 5.000 keluarga: evaluasi read replica, caching layer (Redis), CDN

### 9.4 Backup & Recovery

- Database backup otomatis harian
- Backup retention: 30 hari
- Documented restore procedure
- Uptime target: 99.5%

### 9.5 Aksesibilitas

- Semantic HTML
- Keyboard navigable
- Kontras warna memadai (WCAG 2.1 AA)
- Font size adjustable (terutama untuk siswa view)

### 9.6 Deployment

Deployment menggunakan Docker dengan stack Phusion Passenger + Apache, agar kompatibel dengan environment shared hosting DomaiNesia dan mudah dimigrasi antar provider.

**Arsitektur Container:**

| Container | Isi | Port |
|---|---|---|
| `app` | Django + Phusion Passenger + Apache | 80/443 |
| `db` | PostgreSQL 16 | 5432 |
| `redis` | Redis (cache + Celery broker) | 6379 |
| `worker` | Celery worker (background jobs) | — |

**Kenapa Passenger + Apache (bukan Gunicorn + Nginx)?**
- DomaiNesia dan banyak shared hosting Indonesia menggunakan Apache + Passenger sebagai stack default.
- Dengan Docker yang meniru environment ini, development ↔ production gap diminimalisir.
- Passenger menangani process management (auto-restart, scaling worker) tanpa perlu supervisor tambahan.

**Konfigurasi kunci:**
- `passenger_wsgi.py` sebagai entry point WSGI
- Apache VirtualHost dengan `PassengerAppRoot` pointing ke Django project
- Static files di-serve langsung oleh Apache (bukan lewat Django)
- Media files (upload gambar soal, dll.) di volume terpisah
- Environment variables via `.env` file (tidak di-commit ke repo)
- SSL termination di level Apache (Let's Encrypt / Certbot)

**Docker Compose services:**
- `docker-compose.yml` untuk production
- `docker-compose.dev.yml` override untuk development (mount source code, debug mode)
- Shared volume untuk static/media files antara `app` container dan Apache

**CI/CD consideration:**
- Build image → push ke registry → pull di VPS → `docker compose up -d`
- Database migration otomatis saat container start (entrypoint script)
- Zero-downtime deployment via Passenger rolling restart

---

## 10. Roadmap & Prioritas

### Phase 1: Foundation (Minggu 1-3)

**Tujuan:** Setup proyek, Docker environment, data model, autentikasi, data referensi akademik.

- Setup Django project, Docker (Passenger + Apache), PostgreSQL, Redis
- Konfigurasi Tailwind CSS build pipeline dan HTMX
- App `accounts`: registrasi, login, profil, family, student profile
- App `academic`: education level, grade, subject, grade-subject mapping, topic, competency, academic year, enrollment
- Django Admin kustomisasi untuk semua model di atas (ModelAdmin, inline, filter, search)
- Seed data: jenjang SD, kelas 1-6, mata pelajaran, topik awal

### Phase 2: Bank Soal & Quiz (Minggu 3-6)

**Tujuan:** Bank soal fungsional dan quiz engine dasar.

- App `questions`: CRUD soal via Django Admin, tagging, question set, import JSON (admin action)
- App `quizzes`: konfigurasi quiz, sesi quiz, pengerjaan (practice mode), hasil
- Custom UI orang tua: pilih quiz untuk anak, lihat hasil
- Custom UI siswa: pengerjaan quiz dengan HTMX
- Timed mode + auto-submit

### Phase 3: Try-out & TKA (Minggu 6-8)

**Tujuan:** Fitur persiapan ujian.

- App `tryouts`: exam blueprint, exam section, sesi try-out, scoring
- Readiness score + countdown ke hari-H
- Study plan otomatis dari hasil try-out
- Blueprint awal: TKA SD, TKA SMP

### Phase 4: Analytics & Parent Dashboard (Minggu 8-10)

**Tujuan:** Monitoring mendalam untuk orang tua.

- App `analytics`: progress snapshot, mastery record, background job kalkulasi
- Dashboard orang tua: overview, per-anak detail
- Grafik tren, heatmap tag, mastery matrix
- Riwayat lintas tahun ajaran
- Generate laporan PDF

### Phase 5: Subscription & Payment (Minggu 10-12)

**Tujuan:** Monetisasi.

- App `subscriptions`: plan, subscription, invoice, payment transaction
- Integrasi payment gateway
- Feature gating middleware
- Pricing page di landing page
- Webhook handler untuk konfirmasi bayar
- Grace period logic

### Phase 6: Polish & Launch (Minggu 12-14)

**Tujuan:** Persiapan launch.

- Landing page public
- Onboarding flow untuk user baru
- Email notifikasi (registrasi, payment, reminder belajar)
- Bug fixing & performance tuning
- Seed data konten: minimal 500 soal untuk kelas 1-6 SD
- Dokumentasi user

### Future Phases

- App `tutors`: fitur pengajar (assignment, catatan, multi-student view)
- Gamification: badge, streak, leaderboard (opsional, per family)
- AI-assisted question generation via pipeline LLM
- SMP support: mapel dan konten kelas 7-9
- Mobile app (Flutter) — jika demand cukup
- Persentil try-out (butuh data populasi)
- Integrasi Kurikulum Merdeka secara formal (Capaian Pembelajaran)

---

## 11. Metrik Keberhasilan

### 11.1 Product Metrics

| Metrik | Target (6 bulan post-launch) |
|---|---|
| Registered families | 500 |
| Monthly active families | 200 |
| Conversion free → paid | 10-15% |
| Retention rate (bulan ke-3) | 60% |
| Average quiz sessions / student / week | 3 |
| NPS (Net Promoter Score) | > 40 |

### 11.2 Technical Metrics

| Metrik | Target |
|---|---|
| Uptime | 99.5% |
| Page load time (dashboard) | < 2s |
| Quiz interaction latency | < 500ms |
| Payment success rate | > 95% |
| Error rate | < 1% |

### 11.3 Business Metrics

| Metrik | Target (tahun pertama) |
|---|---|
| Monthly Recurring Revenue (MRR) | Rp 10-20 juta |
| Customer Acquisition Cost (CAC) | < Rp 50.000 |
| Lifetime Value (LTV) | > Rp 500.000 |
| LTV/CAC ratio | > 10 |
| Churn rate (bulanan) | < 10% |

---

## 12. Risiko & Mitigasi

| Risiko | Dampak | Probabilitas | Mitigasi |
|---|---|---|---|
| Konten soal tidak cukup banyak saat launch | Tinggi | Tinggi | Prioritaskan pipeline content creation, AI-assisted generation, mulai dari 2-3 kelas dulu |
| Orang tua tidak mau bayar | Tinggi | Sedang | Free tier yang fungsional, trial period untuk fitur premium, pricing kompetitif vs bimbel |
| Persaingan dengan platform besar (Ruangguru, Zenius) | Sedang | Sedang | Fokus niche homeschooling + TKA prep, bukan general edtech |
| Teknis: performa analytics lambat | Sedang | Sedang | Pre-computed snapshot, proper indexing, profiling sejak awal |
| Regulasi konten pendidikan | Rendah | Rendah | Soal bersifat latihan, bukan ujian resmi — tidak ada regulasi ketat |
| Scope creep | Tinggi | Tinggi | PRD ini sebagai anchor, strict phase-based delivery, MVP first |

---

## 13. Lampiran

### 13.1 Contoh Format JSON Import Soal

```json
{
  "batch_name": "Matematika Kelas 3 - Perkalian",
  "questions": [
    {
      "type": "multiple_choice",
      "difficulty": "easy",
      "topic_code": "MTK-3-01",
      "tags": ["numerasi", "perkalian"],
      "text": "Berapakah hasil dari 7 × 8?",
      "options": [
        {"label": "A", "text": "54", "is_correct": false},
        {"label": "B", "text": "56", "is_correct": true},
        {"label": "C", "text": "58", "is_correct": false},
        {"label": "D", "text": "64", "is_correct": false}
      ],
      "explanation": "7 × 8 = 56. Cara mudah mengingatnya: 56 = 7 × 8 (angka 5, 6, 7, 8 berurutan)."
    }
  ]
}
```

### 13.2 Contoh ExamBlueprint: TKA SMP Negeri

| Seksi | Jumlah Soal | Bobot | Filter Tag | Durasi |
|---|---|---|---|---|
| Numerasi | 15 | 30% | `numerasi`, `logika-matematika` | 30 menit |
| Literasi | 10 | 25% | `literasi`, `reading-comprehension` | 20 menit |
| Penalaran | 10 | 25% | `penalaran`, `problem-solving`, `HOTS` | 25 menit |
| Pengetahuan Umum | 5 | 20% | `pengetahuan-umum` | 10 menit |
| **Total** | **40** | **100%** | — | **85 menit** |

### 13.3 Glossary

| Istilah | Definisi |
|---|---|
| TKA | Tes Kemampuan Akademik — ujian masuk sekolah |
| KD | Kompetensi Dasar — standar capaian pembelajaran dalam kurikulum nasional |
| HOTS | Higher Order Thinking Skills — soal yang menguji kemampuan analisis, evaluasi, dan kreasi |
| Mastery Level | Tingkat penguasaan siswa terhadap suatu topik, dihitung dari akurasi dan jumlah attempt |
| ExamBlueprint | Template/cetak biru format ujian yang mendefinisikan struktur seksi dan distribusi soal |
| Readiness Score | Skor prediksi kesiapan siswa menghadapi ujian, dihitung dari tren skor try-out |
| Feature Gating | Mekanisme pembatasan akses fitur berdasarkan tier subscription |
| Enrollment | Pendaftaran siswa di kelas tertentu pada tahun ajaran tertentu |

---

*Dokumen ini adalah living document yang akan diperbarui seiring perkembangan proyek.*
