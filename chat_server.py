"""
chat_server.py
================================================================
Implementasi Sederhana Server Chat Room (Studi Kasus: Telegram)
Mata Kuliah  : Client Server Programming (INF2.62.6003)
Mahasiswa    : Hanna Fadilah (23343068)
Prodi        : Informatika - Universitas Negeri Padang
----------------------------------------------------------------
Deskripsi:
Server ini mereplikasi fitur inti aplikasi chat (seperti Telegram)
dalam skala sederhana menggunakan TCP Socket dan Threading bawaan
Python (tanpa framework/library pihak ketiga). Setiap client yang
terhubung ditangani oleh satu thread terpisah (concurrent server),
sehingga server dapat melayani banyak client secara bersamaan.

Fitur yang diimplementasikan:
1. Multi-client chat room (banyak client terhubung ke 1 server)
2. Broadcast pesan ke seluruh client yang sedang online
3. Notifikasi user bergabung / keluar (status online-offline)
4. Daftar user online (perintah khusus: /list)
5. Penanganan disconnect yang aman (graceful handling)

Cara menjalankan:
    python chat_server.py
Server akan listen pada HOST:PORT yang didefinisikan di bawah.
================================================================
"""

import socket
import threading
import datetime

HOST = "0.0.0.0"      # Menerima koneksi dari semua interface jaringan
PORT = 5050            # Port yang digunakan server (analogi port aplikasi)
BUFFER_SIZE = 1024     # Ukuran buffer penerimaan data (bytes)
FORMAT = "utf-8"       # Encoding pesan teks

# ----------------------------------------------------------------
# Struktur data global untuk menyimpan client yang sedang terhubung
# clients: dict -> { socket_object: username }
# Lock digunakan agar akses dictionary 'clients' aman dari race
# condition ketika diakses oleh banyak thread secara bersamaan.
# ----------------------------------------------------------------
clients = {}
clients_lock = threading.Lock()


def log(message: str) -> None:
    """Mencetak log dengan timestamp ke konsol server."""
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")


def broadcast(message: str, sender_socket=None) -> None:
    """
    FUNGSI UTAMA 1: Broadcast pesan ke semua client yang terhubung.

    Mengirimkan 'message' ke seluruh socket client yang tersimpan
    pada dictionary 'clients', kecuali sender_socket itu sendiri
    (opsional, agar pengirim tidak menerima pesannya sendiri dua kali
    jika diperlukan). Jika pengiriman ke salah satu client gagal
    (misalnya koneksi sudah putus), client tersebut akan dibersihkan
    dari daftar agar server tidak crash.
    """
    disconnected_clients = []

    with clients_lock:
        for client_socket in list(clients.keys()):
            try:
                client_socket.sendall(message.encode(FORMAT))
            except (ConnectionResetError, BrokenPipeError, OSError):
                # Tandai client yang gagal menerima pesan (sudah putus)
                disconnected_clients.append(client_socket)

        # Bersihkan client yang terdeteksi putus koneksi
        for dead_socket in disconnected_clients:
            username = clients.pop(dead_socket, "Unknown")
            log(f"Membersihkan koneksi mati: {username}")
            try:
                dead_socket.close()
            except OSError:
                pass


def handle_client(client_socket: socket.socket, address: tuple) -> None:
    """
    FUNGSI UTAMA 2: Menerima dan menangani koneksi dari satu client.

    Fungsi ini dijalankan di dalam thread terpisah untuk SETIAP client
    yang berhasil terhubung ke server (concurrent handling). Tugasnya:
    1. Menerima username dari client saat pertama kali konek
    2. Mengumumkan bahwa user baru telah bergabung (broadcast)
    3. Mendengarkan pesan dari client secara terus-menerus (loop)
    4. Meneruskan (broadcast) setiap pesan yang masuk ke client lain
    5. Menangani perintah khusus seperti /list dan /quit
    6. Membersihkan resource saat client memutus koneksi
    """
    username = None
    try:
        # Langkah 1: Terima username sebagai pesan pertama dari client
        username = client_socket.recv(BUFFER_SIZE).decode(FORMAT).strip()
        if not username:
            username = f"Guest-{address[1]}"

        with clients_lock:
            clients[client_socket] = username

        log(f"Client baru terhubung: {username} dari {address}")

        # Langkah 2: Beri tahu semua client bahwa user baru bergabung
        join_message = f"[SERVER] {username} telah bergabung ke chat room.\n"
        broadcast(join_message)

        welcome = (
            f"[SERVER] Selamat datang, {username}! "
            f"Gunakan /list untuk melihat user online, /quit untuk keluar.\n"
        )
        client_socket.sendall(welcome.encode(FORMAT))

        # Langkah 3: Loop utama menerima pesan dari client ini
        while True:
            data = client_socket.recv(BUFFER_SIZE)
            if not data:
                break  # Client menutup koneksi tanpa kirim /quit

            text = data.decode(FORMAT).strip()
            if not text:
                continue

            # Penanganan perintah khusus
            if text == "/quit":
                log(f"{username} meminta keluar (/quit)")
                break

            elif text == "/list":
                with clients_lock:
                    online_users = ", ".join(clients.values())
                reply = f"[SERVER] User online: {online_users}\n"
                client_socket.sendall(reply.encode(FORMAT))
                continue

            # Pesan biasa -> broadcast ke seluruh client
            timestamp = datetime.datetime.now().strftime("%H:%M")
            formatted_message = f"[{timestamp}] {username}: {text}\n"
            log(f"Pesan diterima dari {username}: {text}")
            broadcast(formatted_message)

    except (ConnectionResetError, BrokenPipeError):
        log(f"Koneksi {username or address} terputus secara paksa.")
    except Exception as exc:  # Penanganan error tak terduga (robustness)
        log(f"Terjadi error pada client {username or address}: {exc}")
    finally:
        # Langkah 6: Bersihkan client dari daftar dan tutup socket
        with clients_lock:
            clients.pop(client_socket, None)
        try:
            client_socket.close()
        except OSError:
            pass

        if username:
            leave_message = f"[SERVER] {username} telah keluar dari chat room.\n"
            broadcast(leave_message)
            log(f"Client {username} terputus dan dibersihkan dari server.")


def start_server() -> None:
    """Inisialisasi socket server, listen, dan terima koneksi client baru."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    log(f"Server chat berjalan di {HOST}:{PORT} ...")
    log("Menunggu koneksi client (tekan CTRL+C untuk menghentikan server)")

    try:
        while True:
            # accept() bersifat blocking sampai ada client yang konek
            client_socket, address = server_socket.accept()

            # Setiap client baru ditangani oleh thread terpisah
            # -> inilah inti dari konkurensi pada server ini
            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, address),
                daemon=True
            )
            client_thread.start()

            with clients_lock:
                active_count = len(clients) + 1  # +1 karena belum terdaftar
            log(f"Thread baru dibuat untuk {address}. "
                f"(Perkiraan total thread aktif: {threading.active_count() - 1})")

    except KeyboardInterrupt:
        log("Server dihentikan oleh administrator (CTRL+C).")
    finally:
        server_socket.close()


if __name__ == "__main__":
    start_server()
