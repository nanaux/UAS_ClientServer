Proyek Tugas Akhir Semester (UAS) — Mata Kuliah **Client Server Programming**

## 1. Deskripsi Proyek

Proyek ini merupakan implementasi sederhana dari arsitektur **client-server**
yang terinspirasi dari prinsip kerja aplikasi perpesanan **Telegram**.
Program ini tidak bertujuan menandingi kompleksitas Telegram yang sesungguhnya,
melainkan untuk mendemonstrasikan konsep-konsep inti yang menjadi fondasi
aplikasi semacam itu, yaitu:

- Komunikasi **TCP Socket** antara banyak client dan satu server
- **Konkurensi** menggunakan `threading`, di mana setiap client ditangani
  oleh satu thread terpisah agar server dapat melayani banyak pengguna
  secara bersamaan
- **Broadcast pesan**, yaitu pesan yang dikirim satu client akan diteruskan
  ke seluruh client lain yang sedang terhubung (mirip konsep grup chat)
- Manajemen **status pengguna** (bergabung, daftar online, keluar)
- Penanganan **disconnect** yang aman agar server tidak mengalami crash
  ketika salah satu client terputus secara tiba-tiba

---

## 2. Struktur Folder

```
UAS/
│
├── chat_server.py      # Program server (menerima & meneruskan pesan)
├── chat_client.py      # Program client (mengirim & menerima pesan)
├── README.md           # Dokumentasi proyek (file ini)
└── requirements.txt     # Daftar dependency (tidak ada, hanya pustaka standar)
```

## 4. Fitur yang Diimplementasikan

| No | Fitur | Keterangan |
|----|-------|------------|
| 1 | Multi-client | Banyak client dapat terhubung ke satu server secara bersamaan |
| 2 | Broadcast pesan | Pesan dari satu client diteruskan ke seluruh client lain |
| 3 | Notifikasi join/leave | Server memberi tahu saat ada user baru bergabung/keluar |
| 4 | Daftar user online | Perintah `/list` menampilkan siapa saja yang sedang online |
| 5 | Keluar dengan aman | Perintah `/quit` menutup koneksi tanpa membuat server crash |
| 6 | Logging server | Setiap aktivitas dicatat dengan timestamp di terminal server |
| 7 | Penanganan error | `try-except` mengantisipasi koneksi yang putus paksa |

---

## 5. Persyaratan Sistem

- Python **3.8** atau lebih baru
- Tidak memerlukan instalasi pustaka tambahan (lihat `requirements.txt`)
- Dapat dijalankan pada Windows, macOS, maupun Linux

---

## 6. Cara Menjalankan Program

### Langkah 1 — Jalankan Server

Buka terminal pertama, arahkan ke folder proyek, lalu jalankan:

```bash
python chat_server.py
```

Server akan menampilkan log berikut jika berhasil:

```
[09:30:45] Server chat berjalan di 0.0.0.0:5050 ...
[09:30:45] Menunggu koneksi client (tekan CTRL+C untuk menghentikan server)
```

### Langkah 2 — Jalankan Client (bisa lebih dari satu)

Buka terminal baru (terpisah dari server) untuk **setiap** client,
lalu jalankan:

```bash
python chat_client.py
```

Program akan meminta nama pengguna:

```
Masukkan username Anda: Hanna
```

Ulangi langkah ini di terminal lain untuk menambahkan client kedua,
ketiga, dan seterusnya — semuanya akan terhubung ke server yang sama.

### Langkah 3 — Mulai Chat

Ketik pesan apa saja lalu tekan **ENTER** untuk mengirim. Pesan akan
langsung muncul di terminal seluruh client yang sedang online.

### Perintah Khusus

| Perintah | Fungsi |
|----------|--------|
| `/list` | Menampilkan daftar user yang sedang online |
| `/quit` | Keluar dari chat room dengan aman |

### Menghentikan Server

Tekan `CTRL + C` pada terminal server untuk menghentikan server.

---

## 7. Contoh Sesi Penggunaan

```
PS D:\...\UAS> python chat_server.py
[09:30:45] Server chat berjalan di 0.0.0.0:5050 ...
[09:30:45] Menunggu koneksi client (tekan CTRL+C untuk menghentikan server)
[09:31:21] Thread baru dibuat untuk ('127.0.0.1', 62298). (Perkiraan total thread aktif: 1)
[09:31:25] Client baru terhubung: Hanna dari ('127.0.0.1', 62298)
[09:31:43] Thread baru dibuat untuk ('127.0.0.1', 62299). (Perkiraan total thread aktif: 2)
[09:31:52] Client baru terhubung: Fadilah dari ('127.0.0.1', 62299)
[09:32:22] Pesan diterima dari Hanna: Halo fadilah, Selamat pagi
[09:32:36] Pesan diterima dari Fadilah: Pagi juga hanna
[09:33:13] Fadilah meminta keluar (/quit)
[09:33:13] Client Fadilah terputus dan dibersihkan dari server.
```

---

## 8. Konfigurasi

Parameter koneksi didefinisikan di bagian atas masing-masing berkas
dan dapat disesuaikan sesuai kebutuhan:

```python
# Pada chat_server.py
HOST = "0.0.0.0"   # menerima koneksi dari semua interface jaringan
PORT = 5050

# Pada chat_client.py
SERVER_HOST = "127.0.0.1"   # ganti dengan IP server jika berbeda mesin
SERVER_PORT = 5050
```

Untuk pengujian pada jaringan LAN (bukan hanya localhost), ubah
`SERVER_HOST` pada `chat_client.py` menjadi alamat IP lokal komputer
yang menjalankan server (misalnya `192.168.1.10`), dan pastikan
firewall mengizinkan koneksi masuk pada port `5050`.

---

## 9. Keterbatasan (Limitations)

Sebagai implementasi sederhana untuk tujuan pembelajaran, proyek ini
memiliki keterbatasan dibandingkan Telegram yang sesungguhnya:

- Pesan dikirim dalam bentuk **plain text**, belum dienkripsi (Telegram
  menggunakan protokol MTProto dengan enkripsi end-to-end/end-to-server)
- Tidak ada **persistensi data** — riwayat chat hilang saat server dimatikan
  (Telegram menyimpan riwayat di cloud)
- Belum ada **autentikasi** (username dapat diisi bebas tanpa verifikasi)
- Hanya mendukung **chat room tunggal**, belum ada konsep grup/channel terpisah
- Belum mendukung pengiriman **media** (gambar, video, dokumen)
- Skalabilitas terbatas pada model single-process multi-threaded, berbeda
  dengan Telegram yang menggunakan server terdistribusi dan load balancing

Pembahasan lebih lanjut mengenai keterbatasan ini serta arah pengembangan
tersedia pada slide 11 (Pembahasan) dan slide 12 (Kesimpulan dan Saran)
pada berkas presentasi.
