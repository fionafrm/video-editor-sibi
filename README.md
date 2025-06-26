# Django Video Annotation System

Sistem ini adalah platform berbasis Django untuk manajemen, pengunggahan, penggabungan, pemotongan, dan anotasi video. Sangat cocok untuk proyek yang melibatkan transkripsi otomatis dan penerjemahan Bahasa Isyarat Indonesia (SIBI dan BISINDO).

## 🚀 Fitur Utama

- 📤 **Upload Video**: Unggah video mentah dan versi final secara otomatis.
- ✂️ **Trim Video**: Potong bagian video berdasarkan waktu mulai dan akhir.
- 🔗 **Merge Video**: Gabungkan dua video berurutan berdasarkan penamaan.
- 🧠 **Anotasi**: Tambahkan transkrip, alignment teks dan isyarat, serta komentar.
- 📦 **Import CSV/Excel**: Unggah data massal dari file dengan metadata dan link Google Drive.
- 👥 **Autentikasi**: Role-based access untuk Admin dan Annotator.
- 🔍 **Navigasi Pintar**: Mendeteksi video berikutnya atau sebelumnya yang belum/telah dianotasi.
- 📂 **Tampilan Folder**: Lihat progres anotasi per folder.

---

## 🗃️ Struktur Model

Model `Video` memiliki atribut:

- `title`, `folder_name`, `file`
- `automated_transcript`, `transcript_alignment`, `sibi_sentence`, `potential_problem`, `comment`
- `transcript`, `is_annotated`, `annotated_by`, `merged_video_path`, `created_at`

---

## 🔗 API & Routing Penting

| Endpoint | Method | Keterangan |
|----------|--------|------------|
| `/upload_video/` | POST | Upload video baru |
| `/merge_videos/<video_title>/` | GET | Gabungkan video dengan urutan selanjutnya |
| `/trim_video/<video_title>/` | POST | Potong video berdasarkan waktu |
| `/save_transcript/<video_title>/` | POST | Simpan transkrip & anotasi |
| `/get_video_details/<video_title>/` | GET | Ambil info video |
| `/get_merged_video/<video_title>/` | GET | Ambil video hasil merge |
| `/upload_transcript_csv/` | POST | Upload transkrip dari CSV |
| `/upload_file/` | POST | Upload metadata dari file Excel |
| `/delete_video/<video_title>/` | DELETE | Hapus video |
| `/get_next_video_status/<folder>/<current_title>/` | GET | Cek video belum dianotasi berikutnya |
| `/get_previous_video/<folder>/` | GET | Ambil video sebelumnya (oleh user) |
| `/search_videos/<folder>/` | GET | Redirect ke video belum dianotasi |
| `/landing_page/` | GET | Halaman utama folder |
| `/folder_page/<folder>/` | GET | Daftar video dalam folder |
| `/video_editor/<video_title>/` | GET | Halaman anotasi video |

---

## ⚙️ Instalasi

### 1. Buat sebuah folder baru
### 2. Clone repository
1. Salin URL berikut
	`https://github.com/fionafrm/video-editor-sibi.git`
3. _Clone_ Repositori ke Komputer Lokal
	- Buka terminal atau _command prompt_ di folder yang telah kamu buat sebelumnya.
	- Jalankan perintah `git clone https://github.com/fionafrm/video-editor-sibi.git`
### 3. Membuat Virtual Environment Python
- Windows:
`python -m venv env`
- Unix (macOS, Linux):
`python3 -m venv env`
### 4. Aktifkan virtual environment
- Windows :

		env\Scripts\activate

- Unix (Mac/Linux):

		source env/bin/activate

### 5. Install dependencies yang diperlukan

`pip install -r requirements.txt`