import tkinter as tk
from tkinter import messagebox
from gtts import gTTS
from pydub import AudioSegment
import requests
from bs4 import BeautifulSoup
import os

# Con esta función cambiamos la velocidad del audio
def cambiar_velocidad(audio, velocidad):
    try:
        if velocidad == 1.0:
            return audio

        if velocidad < 1.0:  # Si es menor a 1, reducimos la velocidad
            nuevo_frame_rate = int(audio.frame_rate * velocidad)
            audio = audio._spawn(audio.raw_data, overrides={"frame_rate": nuevo_frame_rate})
            return audio.set_frame_rate(audio.frame_rate)
        else:  # Aumentamos velocidad
            return audio.speedup(playback_speed=velocidad, crossfade=50)
    except Exception as e:
        print(f"Error al ajustar la velocidad: {e}")
        return audio


# Con esta funcion extraemos el texto de la url
def url_a_voz(url):
    try:
        url_solicitada = requests.get(url)
        if url_solicitada.status_code == 200:
            documento_html = BeautifulSoup(url_solicitada.text, 'html5lib')
            
            # Extraemos el texto de los elementos <p>
            contenido = ' '.join([p.text.strip() for p in documento_html.find_all('p') if p.text.strip()])
            contenido = contenido.replace('\n', ' ').replace('\r', ' ').strip()
            contenido = ' '.join(contenido.split())  # Con esto eliminamos los espacios

            print("Texto extraído de la URL:", contenido)  # Mostramos una pequeña parte del texto extraido

            # Controlamos que el texto no sea demasiado largo
            if len(contenido) > 5000:
                contenido = contenido[:5000]
                print("Texto truncado porque excede el límite de caracteres permitidos.")

            if len(contenido) < 10:  # Controlamos que el texto no sea demasiado corto
                print("Advertencia: El texto extraído es muy corto.")
                return None

            return contenido
        else:
            print(f"Error al obtener la URL: {url_solicitada.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error durante la solicitud: {e}")
        return None

def texto_a_voz():
    try:
        # Comprobamos si el usuario a elegido texto o url
        if modo_var.get() == "texto":
            texto = cuadroTexto.get("1.0", tk.END).strip()
        elif modo_var.get() == "url":
            url = cuadroURL.get().strip()
            if not url:
                messagebox.showerror("Error", "Por favor, ingresa una URL válida.")
                return
            texto = url_a_voz(url)
            if not texto:
                messagebox.showerror("Error", "El texto extraído de la URL es insuficiente para generar un audio.")
                return

        if not texto or len(texto) < 3:
            messagebox.showerror("Error", "El texto es demasiado corto para generar un audio.")
            return

        # Aquí vemos que velocidad,idioma y salida que ha elegido el usuario
        velocidad = velocidad_var.get()
        idioma = idiomas[idioma_var.get()]  # Traduce el nombre legible a la abreviatura
        salida = archivo_salida_var.get().strip()
        # Si el usuario no añade la extensión mp3, se la damos nosotros
        if not salida.endswith(".mp3"):
            salida += ".mp3"

        # Creamos el audio
        print("Generando audio...")
        audio_gtts = gTTS(text=texto, lang=idioma)
        audio_gtts.save("audio_temporal.mp3")

        # Ajustamos la velocidad del audio
        audio_pydub = AudioSegment.from_file("audio_temporal.mp3")
        audio_modificado = cambiar_velocidad(audio_pydub, velocidad)

        # Exportar el archivo
        audio_modificado.export(salida, format="mp3")
        messagebox.showinfo("Éxito", f"Audio generado con éxito: {salida}")
        print(f"Audio generado con éxito: {salida}")

    except Exception as e:
        messagebox.showerror("Error", f"Error al procesar el audio: {e}")
    finally:
        if os.path.exists("audio_temporal.mp3"):
            os.remove("audio_temporal.mp3")


# Con esta funcion cambiamos el cuadro del texto y url dependiendo de lo que elija el usuario
def cambiar_modo():
    if modo_var.get() == "texto":
        miLabelTexto.place(relx=0.1, rely=0.2, relwidth=0.2, relheight=0.05)  # Etiqueta para texto
        cuadroTexto.place(relx=0.3, rely=0.2, relwidth=0.6, relheight=0.3)   # Cuadro grande para texto
        cuadroURL.place_forget()
        miLabelURL.place_forget()
    elif modo_var.get() == "url":
        miLabelURL.place(relx=0.1, rely=0.2, relwidth=0.2, relheight=0.05)
        cuadroURL.place(relx=0.3, rely=0.2, relwidth=0.6, relheight=0.05)
        cuadroTexto.place_forget()
        miLabelTexto.place_forget()

def salir():
    if messagebox.askyesno("Salir", "¿Estás seguro de que deseas salir?"):
        raiz.destroy()

# Creamos ventana principal
raiz = tk.Tk()
raiz.geometry("800x600")
raiz.title("Generador de Audios")
idiomas = {
    "Español": "es",
    "Inglés": "en",
    "Francés": "fr",
    "Alemán": "de"
}

# Le damos al idioma,velocidad,archivo de salida y el modo unos parametros predefinidos
idioma_var = tk.StringVar(value="Español") 
velocidad_var = tk.DoubleVar(value=1.0) 
archivo_salida_var = tk.StringVar(value="audio_generado.mp3")  
modo_var = tk.StringVar(value="texto")  

# Creamos frame principal
miFrame = tk.Frame(raiz, bg="#90c9c9", bd=20, relief="ridge")
miFrame.pack(fill="both", expand=True)

# Damos la bienvenida al usuario
miLabel = tk.Label(miFrame, text="Bienvenid@ al Generador de Audios", font=("Arial", 16), bg="#90c9c9",)
miLabel.place(relx=0.5, rely=0.05, anchor="center",relheight=0.10,relwidth=0.5)

# Opciones para seleccionar modo
miLabelModo = tk.Label(miFrame, text="Selecciona el modo:", font=("Arial", 12), bg="#90c9c9", anchor="w")
miLabelModo.place(relx=0.1, rely=0.1, relwidth=0.4, relheight=0.05)

modo_texto = tk.Radiobutton(miFrame, text="Texto", variable=modo_var, value="texto", command=cambiar_modo, bg="#90c9c9", anchor="w",)
modo_texto.place(relx=0.30, rely=0.1, relwidth=0.08, relheight=0.05)

modo_url = tk.Radiobutton(miFrame, text="URL", variable=modo_var, value="url", command=cambiar_modo, bg="#90c9c9", anchor="w")
modo_url.place(relx=0.378, rely=0.1, relwidth=0.08, relheight=0.05)

# Creamos el cuadro de texto para ingresar el contenido
cuadroTexto = tk.Text(miFrame, bg="#d8d8d8", bd=3, wrap="word", font=("Arial", 12),insertofftime=300,insertontime=300,insertbackground="blue",highlightthickness=4, 
highlightbackground="red",highlightcolor="green")
cuadroTexto.place(relx=0.1, rely=0.2, relwidth=0.8, relheight=0.3)

# Cuadro de entrada para la URL
# Etiqueta para el modo Texto
miLabelTexto = tk.Label(miFrame, text="Introduce el texto:", font=("Arial", 12), bg="#90c9c9", anchor="w")
miLabelURL = tk.Label(miFrame, text="Introduce la URL:", font=("Arial", 12), bg="#90c9c9", anchor="w")
cuadroURL = tk.Entry(miFrame, font=("Arial", 12), bg="#d8d8d8",insertofftime=300,insertontime=300,insertbackground="blue",highlightthickness=4, 
highlightbackground="red",highlightcolor="green")

# Etiqueta y entrada para el nombre del archivo
miLabelArchivo = tk.Label(miFrame, text="Nombre del archivo de salida:", font=("Arial", 12), bg="#90c9c9", anchor="w")
miLabelArchivo.place(relx=0.1, rely=0.55, relwidth=0.4, relheight=0.05)
entrada_salida = tk.Entry(miFrame, textvariable=archivo_salida_var, font=("Arial", 12),insertofftime=300,insertontime=300,insertbackground="blue",highlightthickness=4, 
highlightbackground="red",highlightcolor="green")
entrada_salida.place(relx=0.39, rely=0.55, relwidth=0.4, relheight=0.05)

# Opciones disponibles para el idioma
miLabelIdioma = tk.Label(miFrame, text="Idioma:", font=("Arial", 12), bg="#90c9c9", anchor="w")
miLabelIdioma.place(relx=0.1, rely=0.65, relwidth=0.2, relheight=0.05)
opciones_idioma = tk.OptionMenu(miFrame, idioma_var, *idiomas.keys())
opciones_idioma.place(relx=0.3, rely=0.65, relwidth=0.2, relheight=0.05)

# Opciones disponibles para la velocidad del audio
miLabelVelocidad = tk.Label(miFrame, text="Velocidad:", font=("Arial", 12), bg="#90c9c9", anchor="w")
miLabelVelocidad.place(relx=0.1, rely=0.75, relwidth=0.2, relheight=0.05)
slider_velocidad = tk.Scale(miFrame, from_=0.5, to=2.0, resolution=0.1, orient="horizontal", variable=velocidad_var, bg="#90c9c9")
slider_velocidad.place(relx=0.3, rely=0.75, relwidth=0.4, relheight=0.1)

# Botón para generar el audio
botonEnvio = tk.Button(miFrame, text="Convertir", font=("Arial", 14), command=texto_a_voz)
botonEnvio.place(relx=0.1, rely=0.9, relwidth=0.12, relheight=0.08)
botonSalir = tk.Button(miFrame, text="Salir", font=("Arial", 14),command=salir)
botonSalir.place(relx=0.8, rely=0.9, relwidth=0.12, relheight=0.08)

cambiar_modo()

raiz.mainloop()
