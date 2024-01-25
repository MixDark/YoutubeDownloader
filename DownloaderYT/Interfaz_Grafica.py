import tkinter as tk
from tkinter import ttk
from Descargar import *

class Interfaz(Descargas):
    
    def __init__(self,ventana):
        self.ventana = ventana
        self.ventana.title("YouTube Downloader")
        self.ventana.resizable(0,0)
        self.ventana.geometry("540x260")
    
        self.url = tk.StringVar()
        self.ruta_guardado = tk.StringVar()
        self.var_solo_audio = tk.BooleanVar()
        self.mensaje = tk.StringVar()

        tk.Label(self.ventana, text="URL del video:").grid(row=0, column=0, padx=10, pady=10, sticky="e")

        tk.Entry(self.ventana, textvariable=self.url, width=50).grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self.ventana, text="Ruta de guardado:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        tk.Entry(self.ventana, textvariable=self.ruta_guardado, width=50,state="readonly").grid(row=1, column=1, padx=10, pady=10)
        tk.Button(self.ventana, text="Seleccionar", command=self.seleccionar_ruta).grid(row=1, column=2, padx=10, pady=10)

        tk.Checkbutton(self.ventana, text="Descargar solo audio", variable=self.var_solo_audio).grid(row=3, column=1, padx=10, pady=10, sticky="w")

        tk.Button(self.ventana, text="Descargar", command=self.iniciar_descarga).grid(row=4, column=1, padx=10, pady=10)

        self.barra_progreso = ttk.Progressbar(ventana, orient="horizontal", length=300, mode="determinate")
        self.barra_progreso.grid(row=5, column=1, padx=10, pady=10)

        tk.Label(ventana, textvariable=self.mensaje).grid(row=6, column=1, padx=10, pady=10)

ventana = tk.Tk()
aplicacion = Interfaz(ventana)
ventana.mainloop()        