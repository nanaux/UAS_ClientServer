"""
chat_client.py
================================================================
Implementasi Sederhana Client Chat Room (Studi Kasus: Telegram)
Mata Kuliah  : Client Server Programming (INF2.62.6003)
Mahasiswa    : Hanna Fadilah (23343068)
Prodi        : Informatika - Universitas Negeri Padang
----------------------------------------------------------------
Deskripsi:
Client ini terhubung ke chat_server.py melalui TCP Socket.
Client menggunakan DUA thread:
1. Thread utama  -> menangani input pengguna (mengetik & kirim pesan)
2. Thread receiver -> mendengarkan pesan masuk dari server secara
                       terus-menerus, agar client tetap bisa menerima
                       pesan broadcast walau sedang tidak mengetik
                       (mirip notifikasi real-time pada Telegram).

Perintah khusus yang didukung:
    /list   -> menampilkan daftar user yang sedang online
    /quit   -> keluar dari chat room dengan aman

Cara menjalankan:
    python chat_client.py
    (pastikan chat_server.py sudah berjalan lebih dahulu)
================================================================
"""

import socket
import threading
import sys

SERVER_HOST = "127.0.0.1"  # Alamat server (localhost untuk pengujian)
SERVER_PORT = 5050
BUFFER_SIZE = 1024
FORMAT = "utf-8"


def receive_messages(client_socket: socket.socket) -> None:
    """
    FUNGSI UTAMA: Mendengarkan pesan masuk dari server secara terus-menerus.

    Berjalan pada thread terpisah (non-blocking terhadap input pengguna)
    sehingga client dapat menerima pesan broadcast kapan saja, persis
    seperti notifikasi pesan real-time pada aplikasi Telegram.
    """
    while True:
        try:
            data = client_socket.recv(BUFFER_SIZE)
            if not data:
                print("\n[INFO] Koneksi ke server telah ditutup oleh server.")
                break

            message = data.decode(FORMAT)
            # \r dan flush memastikan tampilan terminal tetap rapi
            # walau pengguna sedang mengetik pesan.
            print(f"\r{message}\n> ", end="")

        except (ConnectionResetError, OSError):
            print("\n[INFO] Koneksi ke server terputus.")
            break

    client_socket.close()
    sys.exit(0)


def start_client() -> None:
    """Membuat koneksi ke server, mengirim username, dan membuka sesi chat."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((SERVER_HOST, SERVER_PORT))
    except ConnectionRefusedError:
        print(f"[ERROR] Tidak dapat terhubung ke server {SERVER_HOST}:{SERVER_PORT}.")
        print("        Pastikan chat_server.py sudah dijalankan terlebih dahulu.")
        return

    username = input("Masukkan username Anda: ").strip()
    if not username:
        username = "Anonymous"
    client_socket.sendall(username.encode(FORMAT))

    print(f"\n[INFO] Terhubung ke server sebagai '{username}'.")
    print("[INFO] Ketik pesan dan tekan ENTER untuk mengirim.")
    print("[INFO] Gunakan /list untuk lihat user online, /quit untuk keluar.\n")

    # Thread penerima pesan berjalan paralel dengan loop input di bawah
    receiver_thread = threading.Thread(
        target=receive_messages, args=(client_socket,), daemon=True
    )
    receiver_thread.start()

    try:
        while True:
            message = input("> ")
            if not message:
                continue

            client_socket.sendall(message.encode(FORMAT))

            if message == "/quit":
                print("[INFO] Keluar dari chat room...")
                break

    except (KeyboardInterrupt, EOFError):
        print("\n[INFO] Sesi dihentikan oleh pengguna.")
        try:
            client_socket.sendall("/quit".encode(FORMAT))
        except OSError:
            pass
    finally:
        client_socket.close()


if __name__ == "__main__":
    start_client()
