import yt_dlp
import os

def download_youtube_as_mp3(youtube_url, output_dir="downloads"):
    """
    Mengunduh audio dari URL YouTube dan mengkonversinya menjadi format MP3.

    Args:
        youtube_url (str): URL video YouTube.
        output_dir (str): Direktori untuk menyimpan file MP3.
    """
    
    # 1. Pastikan direktori output ada
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 2. Definisikan opsi yt-dlp
    # Opsi-opsi ini sama fungsinya dengan argumen baris perintah Anda:
    ydl_opts = {
        'format': 'bestaudio/best',  # Pilih kualitas audio terbaik
        'postprocessors': [{         # Pasca-pemrosesan untuk ekstraksi audio dan konversi
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3', # Tentukan format output: mp3
            'preferredquality': '192', # Kualitas MP3 (Kbps)
        }],
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'extract_audio': True,       # Ekstraksi audio (-x)
        'verbose': False,            # Agar output dari yt-dlp tidak terlalu banyak
    }

    print(f"Memulai pengunduhan dari: {youtube_url}...")
    
    try:
        # 3. Jalankan pengunduhan menggunakan YoutubeDL
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=True)
            title = info_dict.get('title', 'video')
            print(f"✅ Berhasil mengunduh dan mengkonversi: {title}.mp3")
            
            # Mengembalikan nama file yang diunduh (berguna untuk API)
            final_filename = os.path.join(output_dir, f"{title}.mp3") 
            return final_filename
            
    except Exception as e:
        print(f"❌ Terjadi kesalahan: {e}")
        return None