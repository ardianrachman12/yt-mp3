import yt_dlp
import os
import glob

def download_youtube_as_mp3(youtube_url, output_dir="temp_downloads"):
    """
    Mengunduh audio dari URL YouTube dan mengkonversinya menjadi format MP3.
    Mengembalikan path file yang dikonversi.
    """
    
    # 1. Pastikan direktori output ada
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 2. Ambil metadata (ID dan Judul) untuk digunakan sebagai nama file unik
    try:
        # Gunakan instance terpisah, 'quiet' untuk mendapatkan info tanpa log download
        with yt_dlp.YoutubeDL({'quiet': True, 'simulate': True}) as ydl_info:
            info_dict = ydl_info.extract_info(youtube_url, download=False)
            video_id = info_dict.get('id')
            raw_title = info_dict.get('title', 'unknown_video')
            
            # Buat nama file final yang diharapkan berdasarkan ID (paling aman)
            # yt-dlp secara otomatis menangani sanitasi karakter
            expected_filename_template = os.path.join(output_dir, f"{video_id}-%(title)s.%(ext)s")
            
    except Exception as e:
        print(f"❌ Gagal mengambil info video: {e}")
        return None

    # 3. Definisikan opsi yt-dlp untuk DOWNLOAD
    ydl_opts = {
        'format': 'bestaudio/best',  
        'postprocessors': [{ 
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3', 
            'preferredquality': '192',
        }],
        # Gunakan ID di template, yt-dlp akan mengganti %(title)s dengan judul yang disanitasi
        'outtmpl': expected_filename_template, 
        'extract_audio': True,
        'verbose': False, 
        'noplaylist': True, # Pastikan hanya 1 video yang diunduh
        # Tambahkan hook untuk mendapatkan nama file akhir yang benar
        'progress_hooks': [lambda d: print(f"Processing: {d['status']}")] 
    }

    print(f"Memulai pengunduhan dari: {youtube_url}...")
    
    try:
        # 4. Jalankan pengunduhan
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])

        # 5. Cari file MP3 yang baru dibuat
        # Kita perlu mencari file yang diawali dengan ID video dan berakhiran .mp3
        search_pattern = os.path.join(output_dir, f"{video_id}-*.mp3")
        found_files = glob.glob(search_pattern)
        
        if found_files:
            final_downloaded_path = found_files[0]
            print(f"✅ Berhasil mengunduh dan mengkonversi: {os.path.basename(final_downloaded_path)}")
            return final_downloaded_path
        else:
            print("❌ File MP3 akhir tidak ditemukan setelah konversi.")
            return None
            
    except Exception as e:
        print(f"❌ Terjadi kesalahan saat memproses URL: {e}")
        return None
