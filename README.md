# Video Editor SIBI

### To Do:
- [x] Prep env dan Model Video BE
- [x] Transkripsi otomatis BE
- [x] Kalimat yang diperagakan BE
- [] Penyelarasan (kolom E) BE
- [] Button Cut FE
- [] Button OK FE
- [] Button Prev/Next FE
- [] Show videos FE
- [x] upload batch BE
- [] Preview video after tekan cut (jadi nanti kalo pilih opsi cancel, video nya kembali ke yang awal) BE dan FE
- [] Necessary FE
- [x] upload text bareng video BE
- [] auth BE
- [] Pilihan tanggal FE
- [] Home FE

### Model Video
- title : Judul yang nantinya diberikan kalau sudah approve. Bersifat nullable.
- file : File dari video
- transcript : Ketika diunggah pertama kali oleh mesin, akan berisi transkrip otomatis. Namun, jika sudah dianotasikan oleh anotator, maka akan berisi transkrip final. Bersifat nullable karena fungsi mengunggah video dan transkrip berbeda.
- comments : Komentar anotator untuk penyelarasan (kolom E di Spreadsheets)
- created_at = Auto add waktu membuat objek video.

### Model Edited Video
- original_video : Foreign Key yang merujuk ke video asli. Video asli masih tersimpan.
- file : File dari Edited Video
- start_time : Waktu dimulainya pemotongan video
- end_time : Waktu berakhirnya pemotongan video
- transcript : Transkrip yang dimasukan oleh anotator
- comments : Komentar anotator untuk penyelarasan (kolom E di Spreadsheets)
- created_at : Auto add waktu membuat objek edited video

### How to Test it out?
Untuk melakukan testing, saya menggunakan Postman. 