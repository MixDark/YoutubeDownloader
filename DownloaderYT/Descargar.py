from pytube import YouTube
from tkinter import filedialog

class Descargas():

    def on_progress_do(self,stream, chunk, bytes_remaining):
        size = stream.filesize
        progress = (size - bytes_remaining) / size
        self.barra_progreso['value'] = progress * 100
        self.ventana.update_idletasks()

    def descargar_video(self,url, ruta_guardado, solo_audio):
        try:
            video = YouTube(url, on_progress_callback=self.on_progress_do)
            
            if solo_audio:
                stream = video.streams.filter(only_audio=True).first()
                ext = ".mp3"
            else:
                stream = video.streams.filter(progressive=True).first()
                ext = ".mp4"

            archivo = f"{video.title}{ext}"
            archivo = archivo.replace('/', '').replace('\\', '').replace(':', '').replace('*', '').replace('?', '').replace('"', '').replace('<', '').replace('>', '').replace('|', '')
            stream.download(ruta_guardado, filename=archivo)
            self.mensaje.set("Descarga completada.")
        except Exception as e:
            self.mensaje.set(f"Error al descargar el video: {e}")

    def seleccionar_ruta(self):
        ruta = filedialog.askdirectory()
        self.ruta_guardado.set(ruta)

    def iniciar_descarga(self):
        url_video = self.url.get()
        ruta = self.ruta_guardado.get()
        solo_audio = self.var_solo_audio.get()
        self.descargar_video(url_video, ruta, solo_audio)