from flask import Flask, request, send_file, jsonify
from download_mp3 import download_youtube_as_mp3 # Impor fungsi dari file sebelumnya
import os, subprocess, stat
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

APP_ENV = os.environ.get('FLASK_ENV', 'production')
IS_LOCAL_DEV = (APP_ENV == 'development' or APP_ENV == 'local')

# Deteksi apakah berjalan di Vercel
is_vercel = os.environ.get("VERCEL", "0") == "1" or "vercel" in os.environ.get("PATH", "").lower()

# Tambahkan path ke folder bin
os.environ["PATH"] += os.pathsep + os.path.abspath("bin")

if not is_vercel:
    for file in ["bin/ffmpeg", "bin/ffprobe"]:
        if os.path.exists(file):
            try:
                st = os.stat(file)
                os.chmod(file, st.st_mode | stat.S_IEXEC)
            except Exception as e:
                print(f"[WARN] Gagal chmod {file}: {e}")
                print(subprocess.getoutput("ffmpeg -version"))
else:
    print("[INFO] Jalankan di Vercel — skip chmod binary ffmpeg/ffprobe")

# --- ENDPOINTS HEALTH CHECK DAN ROOT UTAMA ---
@app.route('/', methods=['GET'])
def root_status():
    """Endpoint root utama untuk memberikan status API dan petunjuk."""
    return jsonify({
        "status": "ok",
        "service": "YouTube MP3 Downloader API",
        "environment": APP_ENV,
        "instructions": "Use /download-mp3?url=<youtube_url> to get the MP3 file."
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint health check sederhana untuk layanan monitoring."""
    return jsonify({"status": "ok"}), 200

@app.route('/list-files', methods=['GET'])
def list_files():
    """Endpoint untuk menampilkan isi folder temp_downloads (hanya untuk debugging)."""
    target_dir = "temp_downloads"
    try:
        # Periksa apakah direktori ada
        if not os.path.exists(target_dir):
            return jsonify({
                "directory": target_dir,
                "exists": False,
                "files": []
            }), 200

        # Ambil daftar file
        files = os.listdir(target_dir)
        
        # Filter untuk menghapus file tersembunyi seperti .gitkeep
        files = [f for f in files if not f.startswith('.')]

        return jsonify({
            "directory": target_dir,
            "exists": True,
            "file_count": len(files),
            "files": files
        }), 200

    except Exception as e:
        return jsonify({
            "error": "Failed to list directory contents",
            "message": str(e)
        }), 500

@app.route('/clear-downloads', methods=['POST'])
def clear_downloads():
    """Endpoint untuk menghapus semua isi file di dalam folder temp_downloads secara manual."""
    target_dir = "temp_downloads"
    deleted_count = 0
    errors = []

    if not os.path.exists(target_dir):
        return jsonify({
            "status": "warning",
            "message": f"Direktori '{target_dir}' tidak ditemukan. Tidak ada yang dihapus."
        }), 200

    # Iterasi melalui semua item di dalam folder
    for item_name in os.listdir(target_dir):
        item_path = os.path.join(target_dir, item_name)
        
        # Hanya hapus file biasa (bukan sub-folder)
        if os.path.isfile(item_path):
            try:
                os.remove(item_path)
                deleted_count += 1
            except Exception as e:
                # Log error spesifik jika gagal hapus
                error_type = type(e).__name__
                errors.append(f"Gagal menghapus {item_name}. Penyebab: {error_type}: {str(e)}")
        # Jika ada sub-folder, kita abaikan saja.
    
    status = "ok" if not errors else "warning"

    return jsonify({
        "status": status,
        "message": f"Operasi pembersihan selesai. {deleted_count} file berhasil dihapus.",
        "errors": errors
    }), 200

@app.route('/download-mp3', methods=['GET'])
def api_download_mp3():
    # Ambil URL dari parameter query (e.g., /download-mp3?url=...)
    youtube_url = request.args.get('url')

    if not youtube_url:
        return jsonify({"error": "Parameter 'url' wajib diisi."}), 400

    # Panggil fungsi pengunduhan
    downloaded_path = download_youtube_as_mp3(youtube_url)
    
    if downloaded_path:
        try:
            # Kirim file MP3 sebagai respons (API Service)
            response = send_file(downloaded_path, as_attachment=True, download_name=os.path.basename(downloaded_path))
            
            # Bersihkan file setelah dikirim (CRITICAL di lingkungan cloud)
            @response.call_on_close
            def cleanup():
                # Cek ulang, dan hapus dengan log error yang lebih detail
                if os.path.exists(downloaded_path):
                    try:
                        os.remove(downloaded_path)
                        print(f"Cleanup: File {downloaded_path} BERHASIL dihapus.")
                    except Exception as e:
                        # Log jenis error yang spesifik (misalnya PermissionError atau OSError)
                        error_type = type(e).__name__
                        print(f"Cleanup Error: Gagal menghapus file {downloaded_path}. Penyebab: {error_type}: {e}")
                else:
                    print(f"Cleanup: File {downloaded_path} sudah TIDAK ADA saat cleanup dipanggil.")
            
            return response
        except Exception as e:
            return jsonify({"error": f"Gagal mengirim file: {e}"}), 500
    else:
        return jsonify({"error": "Gagal mengunduh atau mengkonversi video."}), 500

if __name__ == '__main__':
    # Pastikan 'temp_downloads' ada, atau akan dibuat oleh fungsi
    if not os.path.exists('temp_downloads'):
        os.makedirs('temp_downloads')
        
    # Di lokal, jalankan dengan Flask development server
    # Debug mode diaktifkan HANYA jika APP_ENV adalah 'development' atau 'local'.
    print(f"Running in Environment: {APP_ENV}. Debug Mode: {IS_LOCAL_DEV}")
    app.run(
        host='0.0.0.0', 
        port=os.environ.get('PORT', 5000), 
        debug=IS_LOCAL_DEV
    )