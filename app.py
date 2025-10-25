from flask import Flask, request, send_file, jsonify
from download_mp3 import download_youtube_as_mp3 # Impor fungsi dari file sebelumnya
import os, subprocess, stat

app = Flask(__name__)

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

@app.route('/download-mp3', methods=['GET'])
def api_download_mp3():
    # Ambil URL dari parameter query (e.g., /download-mp3?url=...)
    youtube_url = request.args.get('url')

    if not youtube_url:
        return jsonify({"error": "Parameter 'url' wajib diisi."}), 400

    # Panggil fungsi pengunduhan
    downloaded_path = download_youtube_as_mp3(youtube_url, output_dir="temp_downloads")
    
    if downloaded_path:
        try:
            # Kirim file MP3 sebagai respons (API Service)
            response = send_file(downloaded_path, as_attachment=True, download_name=os.path.basename(downloaded_path))
            
            # Bersihkan file setelah dikirim (penting untuk API)
            @response.call_on_close
            def cleanup():
                os.remove(downloaded_path)
            
            return response
        except Exception as e:
            return jsonify({"error": f"Gagal mengirim file: {e}"}), 500
    else:
        return jsonify({"error": "Gagal mengunduh atau mengkonversi video."}), 500

if __name__ == '__main__':
    # Pastikan 'temp_downloads' ada, atau akan dibuat oleh fungsi
    if not os.path.exists('temp_downloads'):
        os.makedirs('temp_downloads')
        
    app.run(debug=True)