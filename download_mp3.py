import yt_dlp
import os

# Hapus penentuan lokasi FFmpeg di sini. 
# Kita akan mengandalkan FFmpeg yang sudah ada di PATH di lingkungan Railway/Linux.

def download_youtube_as_mp3(youtube_url, output_dir="temp_downloads"):
    """
    Mengunduh audio dari URL YouTube dan mengkonversinya menjadi format MP3.
    """
    
    # 1. Pastikan direktori output ada
    # Gunakan path relatif, Railway akan menyediakannya
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 2. Definisikan opsi yt-dlp
    ydl_opts = {
        'format': 'bestaudio/best',  
        'postprocessors': [{         
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3', 
            'preferredquality': '192',
        }],
        # JANGAN sertakan 'ffmpeg_location', karena kita mengandalkan PATH sistem.
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'extract_audio': True,       
        'verbose': False,            
    }

    print(f"Memulai pengunduhan dari: {youtube_url}...")
    
    try:
        # 3. Jalankan pengunduhan menggunakan YoutubeDL
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Karena yt-dlp sering gagal tanpa nama file yang unik, 
            # kita bisa mengekstrak info dulu
            info_dict = ydl.extract_info(youtube_url, download=False)
            title_slug = ydl.prepare_filename(info_dict)

            # Modifikasi outtmpl agar nama file unik
            ydl_opts['outtmpl'] = os.path.join(output_dir, title_slug + '.%(ext)s')
            
            # Jalankan download
            ydl_run = yt_dlp.YoutubeDL(ydl_opts)
            ydl_run.download([youtube_url])

            title = info_dict.get('title', 'video')
            print(f"✅ Berhasil mengunduh dan mengkonversi: {title}.mp3")
            
            # Cari nama file yang dihasilkan
            # Karena output format adalah mp3, kita cari file mp3 di output_dir
            potential_file = os.path.join(output_dir, title_slug.split(os.sep)[-1] + ".mp3")
            
            return potential_file
            
    except Exception as e:
        print(f"❌ Terjadi kesalahan saat memproses URL: {e}")
        return None
