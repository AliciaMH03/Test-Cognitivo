# -*- coding: utf-8 -*-
"""
Created on Fri Sep 12 09:37:57 2025

@author: alimo
"""
import pandas as pd
import numpy as np
import streamlit as st
import time
from datetime import datetime
import requests
from streamlit_drawable_canvas import st_canvas
import cv2  # para detectar bordes
import os



# para importar archivos
ruta_base = os.path.dirname(__file__)
ruta_imagenes = os.path.join(ruta_base, "imagenes")     #importar imagenes
ruta_csv = os.path.join(ruta_base, "palabrasF.csv")     #importar excel


# Leer CSV con codificación correcta
df_palabras = pd.read_csv(ruta_csv, encoding="latin-1", header=None)  # Sin encabezado
palabras_validas = set(df_palabras[0].str.lower()) 


palabras_memoria = ["cara", "seda", "iglesia", "carro", "rosa"]

# Inicializar en pagina inicial
if "page" not in st.session_state:
    st.session_state.page = 1
    
    
# Inicializar puntuaciones
if "visuoespacial" not in st.session_state:
    st.session_state.visuoespacial = 0  
if "nombrado" not in st.session_state:
    st.session_state.nombrado = 0 
if "atencion" not in st.session_state:
    st.session_state.atencion = 0
if "memoria" not in st.session_state:
    st.session_state.memoria = 0
if "lenguaje" not in st.session_state:
    st.session_state.lenguaje = 0
if "start_time_lenguaje" not in st.session_state:
    st.session_state.start_time_lenguaje = None
if "abstraccion" not in st.session_state:   
    st.session_state.abstraccion = 0
if "orientacion" not in st.session_state:
    st.session_state.orientacion = 0



# Función para avanzar de página
def siguiente(pagina=None):
    if pagina:
        st.session_state.page = pagina
    else:
        st.session_state.page += 1

    st.rerun()



# Página 1: inicio
if st.session_state.page == 1: 
    st.title("Hola! Bienvenido al :rainbow[Test Cognitivo]🧠")
    st.markdown(
    """
    El **MoCA (Montreal Cognitive Assessment)** es una prueba breve diseñada para detectar el 
    **deterioro cognitivo leve** en adultos. Evalúa varias funciones cognitivas, incluyendo:
    
    - **Habilidades visuoespaciales**  
    - **Memoria**  
    - **Atención y concentración**  
    - **Lenguaje**  
    - **Razonamiento abstracto**  
    - **Orientación en tiempo y espacio**  
    
    Esta prueba es una **adaptación basada en el MoCA** y sirve como orientación sobre tu rendimiento cognitivo, 
    pero **no sustituye un diagnóstico profesional**.
    """
    )

    st.write("Cuando estés listo, pulsa el botón para comenzar el test.")
    if st.button("Empezar!"):
        siguiente(2)


# Página 2: visoespacial - cuadrado
elif st.session_state.page == 2:
    st.title("Dominio de visuoespacial🧩: cuadrado⬜")
    st.write("Dibuja un cuadrado 🎨⬜")

    # Canvas para dibujar
    canvas_result = st_canvas(
        fill_color="rgba(0,0,0,0)",
        stroke_width=5,
        stroke_color="#000000",
        background_color="#FFFFFF",
        height=300,
        width=300,
        drawing_mode="freedraw",
        key="canvas",
    )

    if st.button("Evaluar dibujo"):
        puntos_viso = 0

        if canvas_result.image_data is not None:
            # Convertir a escala de grises
            img = cv2.cvtColor(np.array(canvas_result.image_data, dtype=np.uint8), cv2.COLOR_RGBA2GRAY)
        
            # Umbral para binarizar
            _, thresh = cv2.threshold(img, 50, 255, cv2.THRESH_BINARY_INV)

            # Verificar si hay suficientes píxeles dibujados
            if cv2.countNonZero(thresh) >= 500:  
                # Buscar contornos
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
                for cnt in contours:
                    area = cv2.contourArea(cnt)
                    if area < 1500:  # ignorar trazos pequeños
                        continue

                    approx = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)
                    if len(approx) == 4:
                        pts = approx.reshape(4, 2)
                        lados = [np.linalg.norm(pts[i] - pts[(i+1) % 4]) for i in range(4)]
                        min_lado, max_lado = min(lados), max(lados)
                        if max_lado / min_lado > 1.5:
                            continue

                        angulos = []
                        for i in range(4):
                            p1 = pts[i]
                            p2 = pts[(i+1) % 4]
                            p3 = pts[(i+2) % 4]
                            v1 = p1 - p2
                            v2 = p3 - p2
                            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
                            angle = np.arccos(np.clip(cos_angle, -1.0, 1.0)) * 180 / np.pi
                            angulos.append(angle)

                        if all(75 <= a <= 105 for a in angulos):
                            puntos_viso = 1
                            break

        st.session_state.visuoespacial = puntos_viso
        siguiente(3)


# Página 3: visoespacial - reloj
elif st.session_state.page == 3:
    st.title("Dominio visuoespacial🧩: reloj🕰️")
    st.write("Ejercicio 2: En un reloj, ¿qué número ocupa las siguientes posiciones?")

    puntos_viso = st.session_state.visuoespacial

    # Diapositiva 1
    ruta_img1 = os.path.join(ruta_imagenes, "Diapositiva1.png")
    st.image(ruta_img1, width=300)
    hora1_usuario = st.text_input("Número 1: ", value="", key="num_reloj1")
    hora1_correcta = "4"

    # Diapositiva 2
    ruta_img2 = os.path.join(ruta_imagenes, "Diapositiva2.png")
    st.image(ruta_img2, width=300)
    hora2_usuario = st.text_input("Número 2: ", value="", key="num_reloj2")
    hora2_correcta = "9"

    # Diapositiva 3
    ruta_img3 = os.path.join(ruta_imagenes, "Diapositiva3.png")
    st.image(ruta_img3, width=300)
    hora3_usuario = st.text_input("Número 3: ", value="", key="num_reloj3")
    hora3_correcta = "1"

    # Diapositiva 4: indicar hora completa
    ruta_img4 = os.path.join(ruta_imagenes, "Diapositiva4.png")
    st.image(ruta_img4, width=300)
    hora4_usuario = st.text_input("Escribe la hora que marca el reloj (HH:MM) ", value="", key="hora")
    hora_correcta1 = "02:55"
    hora_correcta2 = "14:55"

    # Evaluar respuestas
    if st.button("Evaluar hora"):
        if hora1_usuario.strip() == hora1_correcta:
            puntos_viso += 1
        if hora2_usuario.strip() == hora2_correcta:
            puntos_viso += 1
        if hora3_usuario.strip() == hora3_correcta:
            puntos_viso += 1
        if hora4_usuario.strip() in [hora_correcta1, hora_correcta2]:
            puntos_viso += 1

        st.session_state.visuoespacial = puntos_viso
        siguiente(4)
        
 # Página 4: nombrado
elif st.session_state.page == 4:
    st.title("Dominio del nombrado🗣️")
    st.write("Identifica los animales que aparecen en las imágenes🐾")
    puntos_nom = 0
    
    # Imagen 1
    ruta_img5 = os.path.join(ruta_imagenes, "perro.png")
    st.image(ruta_img5, width=300)
    animal1_usuario = st.text_input("Animal 1:", value="", key="animal1").strip().lower()
    animal1_correcto = "perro"
    
    # Imagen 2
    ruta_img6 = os.path.join(ruta_imagenes, "caballo.png")
    st.image(ruta_img6, width=300)
    animal2_usuario = st.text_input("Animal 2:", value="", key="animal2").strip().lower()
    animal2_correcto = "caballo"
    
    # Imagen 3
    ruta_img7 = os.path.join(ruta_imagenes, "zebra.png")
    st.image(ruta_img7, width=300)
    animal3_usuario = st.text_input("Animal 3:", value="", key="animal3").strip().lower()
    animal3_correcto = "zebra"
    
    if st.button("Evaluar animales"):
        if animal1_usuario == animal1_correcto:
            puntos_nom += 1
        if animal2_usuario == animal2_correcto:
            puntos_nom += 1        
        if animal3_usuario == animal3_correcto:
            puntos_nom += 1  
    
        st.session_state.nombrado = puntos_nom
        siguiente(5)

# Página 5: memoria
elif st.session_state.page == 5:
    st.title("Dominio de la memoria📝")
    st.write("Recuerda estas 5 palabras:")
    st.write(", ".join(palabras_memoria))
    if st.button("Siguiente"):
        siguiente(6)
        
        
#Página 6: Atención 
elif st.session_state.page == 6:
    st.title("Dominio de la atención🎯")

    num1 = st.number_input("Introduce el siguiente número: 37529", value=0, key="num1")
    num2 = st.number_input("Introduce el siguiente número al revés: 5289", value=0, key="num2")

    st.write("Resta 7 a 100 cinco veces")
    res1 = st.number_input("100 - 7 =", value=0, key="res1")
    res2 = st.number_input("100 - 7*2 =", value=0, key="res2")
    res3 = st.number_input("100 - 7*3 =", value=0, key="res3")
    res4 = st.number_input("100 - 7*4 =", value=0, key="res4")
    res5 = st.number_input("100 - 7*5 =", value=0, key="res5")

    numletras = st.number_input(
        "¿Cuántas letras A hay en la siguiente frase?: La demencia es la séptima causa de muerte a nivel mundial", 
        value=0, key="numletras"
    )


    if st.button("Evaluar atencion"):
        puntos = 0
        if num1 == 37529:
            puntos += 1
        if num2 == 9825:
            puntos += 1

        respuestas_correctas = [93, 86, 79, 72, 65]
        aciertos = 0
        if res1 == respuestas_correctas[0]:
            aciertos += 1
        if res2 == respuestas_correctas[1]:
            aciertos += 1
        if res3 == respuestas_correctas[2]:
            aciertos += 1
        if res4 == respuestas_correctas[3]:
            aciertos += 1
        if res5 == respuestas_correctas[4]:
            aciertos += 1

        if aciertos == 2:
            puntos += 1
        elif aciertos == 3:
            puntos += 2
        elif aciertos >= 4:
            puntos += 3
        if numletras == 8:
            puntos += 1

        st.session_state.atencion = puntos #para que al dar a siguiente no se pierda el valor
        siguiente(7)
        
# Página 5.1: memoria recordatorio
elif st.session_state.page == 7:
    st.title("Dominio de la memoria📝")
    st.write("Te acuerdas de las palabras que te dije antes?")


    # Creo inputs para cada palabra, que empiece sin valor, key para diferenciar los widget iguales
    pal1 = st.text_input("Palabra 1:", value="", key="pal1")
    pal2 = st.text_input("Palabra 2:", value="", key="pal2")
    pal3 = st.text_input("Palabra 3:", value="", key="pal3")
    pal4 = st.text_input("Palabra 4:", value="", key="pal4")
    pal5 = st.text_input("Palabra 5:", value="", key="pal5")

    if st.button("Evaluar memoria"):
        memoria = 0 
        # Contar aciertos, lower es para no distinguir entre mayúsculas y minúsculas
        if pal1.lower() == palabras_memoria[0]:
            memoria += 1
        if pal2.lower() == palabras_memoria[1]:
            memoria += 1
        if pal3.lower() == palabras_memoria[2]:
            memoria += 1
        if pal4.lower() == palabras_memoria[3]:
            memoria += 1
        if pal5.lower() == palabras_memoria[4]:
            memoria += 1

        st.session_state.memoria = memoria #para que al dar a siguiente no se pierda el valor
        siguiente(8)
        
# Página 7: Lenguaje
elif st.session_state.page == 8:
    st.title("Dominio del lenguaje🗨️")
    
    # Frases a repetir
    st.write("Escribe las siguientes frases exactamente:")
    
    frase1_correcta = "El ejercicio y la buena dieta protegen la mente"
    st.write(frase1_correcta)
    frase1_usuario = st.text_input("Frase 1:", key="frase1")
    
    frase2_correcta = "El Alzheimer aparece mucho antes de los síntomas"
    st.write(frase2_correcta)
    frase2_usuario = st.text_input("Frase 2:", key="frase2")
    
    # Evaluar frases
    puntuacion_frases = 0
    if frase1_usuario == frase1_correcta:
        puntuacion_frases += 1
    if frase2_usuario == frase2_correcta:
        puntuacion_frases += 1

    # Palabras por F
    st.write("Pulsa el botón para mostrar una letra. Tendrás 1 minuto para escribir 12 palabras que empiecen con esa letra.")
    if st.button("Mostrar letra") and st.session_state.start_time_lenguaje is None:
        st.session_state.letra_lenguaje = "F"
        st.session_state.start_time_lenguaje = time.time()

    if st.session_state.start_time_lenguaje:
        st.write(f"Letra: {st.session_state.letra_lenguaje}")
        palabras = []
        for i in range(1, 13):
            palabra = st.text_input(f"Palabra {i}:", value="", key=f"pal{i}")
            palabras.append(palabra.lower())

        # Eliminar duplicados
        palabras_unicas = set(palabras)

        # Cronómetro
        elapsed = time.time() - st.session_state.start_time_lenguaje
        tiempo_restante = int(60 - elapsed)

        if elapsed < 60:
            st.write(f"Tiempo restante⏰: {tiempo_restante} segundos")
        else:
            st.write("Se acabó el tiempo⏰")

        # Evaluar palabras correctas
        puntuacion_palabras = sum(
            1/12 for palabra in palabras_unicas
            if palabra in palabras_validas and palabra.startswith(st.session_state.letra_lenguaje.lower())
        )

        st.session_state.lenguaje = puntuacion_frases + puntuacion_palabras

        # Botón para avanzar manualmente ANTES de que acabe el tiempo
        if st.button("Evaluar y continuar"):
            siguiente(9)


        
# Página 8: Abstraccion
elif st.session_state.page == 9:
    st.title("Dominio de la abstracción💡")
    
    comun1_sol= "blanco".lower()
    comun1=st.text_input("¿Qué color tienen en común la nieve y la leche?", value="")
    
    comun2_sol=["redonda", "circular"]
    comun2=st.text_input("¿Qué forma tienen en común una moneda y una rueda de coche?")
        
    if st.button("Siguiente"): #meto los puntos aquí pq sino el usurario acumula puntos cada vez que refresca
        puntos_abs = 0
        if comun1.lower() == comun1_sol:
            puntos_abs += 1
        if comun2.lower() in comun2_sol:
            puntos_abs += 1
        st.session_state.abstraccion += puntos_abs
        siguiente(10)
        
        
# Página 9: Orientacion
elif st.session_state.page == 10:
    st.title("Dominio de la orientación📅🧭")
    hoy = datetime.now() 
    
    #lo defino en español porque solo entiende el inglés
    meses = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
    5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
    9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
    }
    
    dias = {0: "lunes", 1: "martes", 2: "miércoles", 3: "jueves",
        4: "viernes", 5: "sábado", 6: "domingo"}

    mes_actual = meses[hoy.month]
    dia_actual = dias[hoy.weekday()] 

    # Inputs del usuario
    dianum = st.number_input("¿Qué día (número) es hoy?", value=0, key="dia_hoy")
    mes = st.text_input("¿En qué mes estamos (en letras)?", value="", key="mes_hoy")
    año = st.number_input("¿En qué año estamos?", value=0, key="año_hoy")
    diasemana = st.text_input("¿Qué día de la semana es hoy?", value="", key="semana_hoy")
    ciudad_usuario = st.text_input("¿En qué ciudad estamos?", value="", key="ciudad_hoy")
    
    
    res = requests.get("https://ipinfo.io/json")
    geo = res.json()
    ciudad_detectada = (geo.get("city") or "").lower()

    
    if st.button("Siguiente"):
            puntos_or = 0
            if dianum == hoy.day:
                puntos_or += 1
            if mes.strip().lower() == mes_actual:
                puntos_or += 1
            if año == hoy.year:
                puntos_or += 1
            if diasemana.strip().lower() == dia_actual:
                puntos_or += 1
            if ciudad_usuario.strip().lower() in (ciudad_detectada or "").lower():
                puntos_or += 2

            
            st.session_state.orientacion += puntos_or
            siguiente(11)
            
# Página final: resultados
elif st.session_state.page == 11:
    import matplotlib.pyplot as plt

    st.title("📊 Resultados finales")

    raw_scores = {
    "Visuoespacial": st.session_state.visuoespacial,
    "Nombrado": st.session_state.nombrado,
    "Atencion": st.session_state.atencion,
    "Memoria": st.session_state.memoria,
    "Lenguaje": st.session_state.lenguaje,
    "Abstraccion": st.session_state.abstraccion,
    "Orientacion": st.session_state.orientacion
    }

    #  Máximo de puntos por dominio (ajusta según tu test)
    max_scores = {
        "Visuoespacial": 5,
        "Nombrado": 3,
        "Atencion": 6,
        "Memoria": 5,
        "Lenguaje": 3,
        "Abstraccion": 2,
        "Orientacion": 6
        }

    # 1) Limitar las puntuaciones a su máximo
    scores = {k: max(0, min(int(v), max_scores[k])) for k, v in raw_scores.items()}

    # 2) Crear DataFrame para mostrar sobre 10
    df_resultados = pd.DataFrame([
        {"Dominio": k, "Puntuación": v, "Máximo": max_scores[k]}
        for k, v in scores.items()
        ])
    df_resultados["Sobre 10"] = (df_resultados["Puntuación"] / df_resultados["Máximo"]) * 10
    df_resultados["Sobre 10"] = df_resultados["Sobre 10"].round(1)
    
    # 3) Mostrar tabla
    st.write("### Tabla de puntuaciones")
    st.dataframe(df_resultados.set_index("Dominio"))
    
    # 4) Gráfico de barras
    fig, ax = plt.subplots(figsize=(10, 6))
    colores = []
    for v in df_resultados["Sobre 10"]:
        if v >= 8:
            colores.append("green")
        elif v >= 4:
            colores.append("orange")
        else:
            colores.append("red")

    ax.bar(df_resultados["Dominio"], df_resultados["Sobre 10"], color=colores)
    ax.set_ylim(0, 10)
    ax.set_ylabel("Puntuación sobre 10")
    plt.xticks(rotation=45, ha="right")

    # Valores encima de las barras
    for i, v in enumerate(df_resultados["Sobre 10"]):
        ax.text(i, v + 0.2, str(v), ha="center", va="bottom", fontweight="bold")

    st.pyplot(fig)

    # 5) Interpretación usando la puntuación total real
    total_real = sum(scores.values()) 
    
    st.write("### Interpretación del resultado")
    if total_real >= 26:
        st.success(f"{total_real} / 30 puntos → Normal.")
    elif total_real >= 18:
        st.warning(f"{total_real} / 30 puntos → Deterioro cognitivo leve o moderado.")
    else:
        st.error(f"{total_real} / 30 puntos → Deterioro grave.")
