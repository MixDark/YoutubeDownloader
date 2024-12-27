import os
import subprocess
from flask import Flask, request, jsonify
import yt_dlp
import logging
from datetime import timedelta

# Configuración de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Inicialización de la aplicación Flask
app = Flask(__name__, static_folder='static', static_url_path='/static')

# Ruta principal para servir el archivo HTML
@app.route('/')
def home():
    try:
        return app.send_static_file('index.html')  # Sirve el archivo index.html
    except Exception as e:
        logger.error(f"Error al servir index.html: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# Ruta para obtener información del video
@app.route('/get_video_info')
def get_video_info():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL no proporcionada'}), 400

    try:
        ydl_opts = {'quiet': True, 'no_warnings': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_info = {
                'title': info.get('title', 'Título desconocido'),
                'thumbnail': info.get('thumbnail'),
                'duration': str(timedelta(seconds=info.get('duration', 0))),
                'channel': info.get('channel', 'Canal desconocido'),
            }
            return jsonify(video_info)
    except Exception as e:
        logger.error(f"Error al obtener información del video: {str(e)}")
        return jsonify({'error': f'Error al obtener información del video: {str(e)}'}), 500

# Ruta para manejar las descargas
@app.route('/descargar')
def descargar():
    try:
        url = request.args.get('url')
        format = request.args.get('format')
        quality = request.args.get('quality', 'highest')

        if not url:
            return jsonify({'success': False, 'error': 'URL no proporcionada'})

        base_dir = os.path.dirname(__file__)
        audio_dir = os.path.join(base_dir, 'descargas', 'audio')
        video_dir = os.path.join(base_dir, 'descargas', 'video')

        os.makedirs(audio_dir, exist_ok=True)
        os.makedirs(video_dir, exist_ok=True)

        descargas_dir = audio_dir if format == 'mp3' else video_dir

        current_dir = os.path.dirname(os.path.abspath(__file__))
        ffmpeg_location = os.path.join(current_dir, 'ffmpeg.exe')

        if format == 'mp3':
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(descargas_dir, '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'prefer_ffmpeg': True,
                'ffmpeg_location': ffmpeg_location,
                'keepvideo': False
            }
        else:
            format_string = {
                'highest': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                '720p': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best',
                '480p': 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]/best',
                '360p': 'bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360][ext=mp4]/best'
            }.get(quality, 'best')

            ydl_opts = {
                'format': format_string,
                'outtmpl': os.path.join(descargas_dir, '%(title)s.%(ext)s'),
                'prefer_ffmpeg': True,
                'ffmpeg_location': ffmpeg_location
            }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info['title']

                if format == 'mp3':
                    filename = os.path.join(descargas_dir, f"{title}.mp3")
                else:
                    filename = os.path.join(descargas_dir, f"{title}.mp4")

                if os.path.exists(filename):
                    return jsonify({
                        'success': True,
                        'message': f'{"Audio" if format == "mp3" else "Video"} descargado exitosamente',
                        'file': filename
                    })
                else:
                    files = os.listdir(descargas_dir)
                    for file in files:
                        if title in file:
                            actual_file = os.path.join(descargas_dir, file)
                            if format == 'mp3':
                                new_file = os.path.join(descargas_dir, f"{title}.mp3")
                                os.rename(actual_file, new_file)
                                filename = new_file
                            else:
                                filename = actual_file
                            break

                    return jsonify({
                        'success': True,
                        'message': f'{"Audio" if format == "mp3" else "Video"} descargado exitosamente',
                        'file': filename
                    })

        except Exception as e:
            logger.error(f"Error en la descarga: {str(e)}")
            return jsonify({'success': False, 'error': f'Error en la descarga: {str(e)}'})

    except Exception as e:
        logger.error(f"Error general: {str(e)}")
        return jsonify({'success': False, 'error': f'Error general: {str(e)}'})

# Ruta para abrir la ubicación del archivo descargado
@app.route('/abrir_ubicacion')
def abrir_ubicacion():
    ruta = request.args.get('ruta')
    if not ruta:
        return jsonify({'success': False, 'error': 'Ruta no proporcionada'})

    try:
        if os.name == 'nt':  # Windows
            os.startfile(os.path.dirname(ruta))
        elif os.name == 'posix':  # macOS o Linux
            subprocess.run(['open', os.path.dirname(ruta)])  # macOS
            subprocess.run(['xdg-open', os.path.dirname(ruta)])  # Linux
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error al abrir la ubicación: {str(e)}")
        return jsonify({'success': False, 'error': f'Error al abrir la ubicación: {str(e)}'})

# Ruta para obtener la ruta del archivo descargado
@app.route('/obtener_ruta_descarga')
def obtener_ruta_descarga():
    url = request.args.get('url')
    format = request.args.get('format')
    quality = request.args.get('quality', 'highest')

    if not url:
        return jsonify({'success': False, 'error': 'URL no proporcionada'})

    base_dir = os.path.dirname(__file__)
    audio_dir = os.path.join(base_dir, 'descargas', 'audio')
    video_dir = os.path.join(base_dir, 'descargas', 'video')

    descargas_dir = audio_dir if format == 'mp3' else video_dir

    try:
        with yt_dlp.YoutubeDL() as ydl:
            info = ydl.extract_info(url, download=False)
            title = info['title']

            if format == 'mp3':
                filename = os.path.join(descargas_dir, f"{title}.mp3")
            else:
                filename = os.path.join(descargas_dir, f"{title}.mp4")

            if os.path.exists(filename):
                return jsonify({'success': True, 'file': filename})
            else:
                files = os.listdir(descargas_dir)
                for file in files:
                    if title in file:
                        actual_file = os.path.join(descargas_dir, file)
                        if format == 'mp3':
                            new_file = os.path.join(descargas_dir, f"{title}.mp3")
                            os.rename(actual_file, new_file)
                            filename = new_file
                        else:
                            filename = actual_file
                        break

                return jsonify({'success': True, 'file': filename})

    except Exception as e:
        logger.error(f"Error al obtener la ruta del archivo: {str(e)}")
        return jsonify({'success': False, 'error': f'Error al obtener la ruta del archivo: {str(e)}'})

# Iniciar la aplicación
if __name__ == '__main__':
    app.run(debug=True, port=7000)