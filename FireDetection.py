import cv2
import numpy as np
import pygame
import time
import threading
import requests

#Función encargada de reproducir el sonido de alarma
def play_sound():
    global fuego_detectado, alarma_sonando
    pygame.mixer.init()
    pygame.mixer.music.load("siren.mp3")
    while True:
        if fuego_detectado and not alarma_sonando:
            pygame.mixer.music.play(-1)
            alarma_sonando = True
        elif not fuego_detectado and alarma_sonando:
            pygame.mixer.music.stop()
            alarma_sonando = False
        time.sleep(0.1) 

#Función encargada del envío de la notificación
def send_telegram_notification():
        global fire_message
        while True:
            time.sleep(0.01)
            if fire_message == 30:
                fire_message = 99
                url = f"https://api.telegram.org/bot7787004136:AAHprAxq4B-Qq_wN3qiDrAYZkh-ZZIphiqE/sendMessage"
                payload = {
                    'chat_id': '-0000000000',
                    'text': "ESTE ES UN SIMULACRO:\nSE DETECTA FUEGO 🔥\nEVACUAR EDIFICO 🦺"
                }
                #response = requests.post(url, json=payload)
                print("MENSAJE ENVIADO")

#Función encargada de detectar el fuego en un video
def detect_fire():
    global fire_message, fuego_detectado, alarma_sonando
    # Definir rangos de color para el fuego en el espacio YCbCr
    lower_fire = np.array([0, 135, 85], dtype=np.uint8)
    upper_fire = np.array([255, 180, 135], dtype=np.uint8)

    while video.isOpened():
        time.sleep(0.01)
        ret, frame = video.read()
        if not ret:
            break

        alto_original, ancho_original = frame.shape[:2]

        nuevo_ancho = 720
        nuevo_alto = int((nuevo_ancho / ancho_original) * alto_original)
        frame = cv2.resize(frame, (nuevo_ancho, nuevo_alto))

        #Aplicar Filtro Gaussiano para suavizar la imagen
        frame = cv2.GaussianBlur(frame, (3,3),0)

        #Convertir la imagen al espacio YCbCr
        ycbcr_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)

        #Segmentación de color para detectar el fuego
        fire_mask = cv2.inRange(ycbcr_frame, lower_fire, upper_fire)

        #Aplicar un filtro de detección de bordes (Sobel)
        sobelx = cv2.Sobel(fire_mask, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(fire_mask, cv2.CV_64F, 0, 1, ksize=3)
        edge_detection = cv2.magnitude(sobelx, sobely)
        edge_detection = np.uint8(np.clip(edge_detection, 0, 255))

        #Superponer la máscara de color y los bordes detectados
        combined_output = cv2.bitwise_and(fire_mask, edge_detection)

        # Contar los píxeles en la máscara combinada para determinar si hay fuego
        fire_pixel_count = cv2.countNonZero(combined_output)
        if fire_pixel_count > fire_threshold:
            #print("Fuego detectado en el cuadro")
            fuego_detectado = True
            if fire_message != 99:
                fire_message += 1
        else:
            fuego_detectado = False

        #Aplicar la máscara combinada a la imagen original para mostrar las áreas detectadas como fuego con bordes
        fire_detected = cv2.bitwise_and(frame, frame, mask=combined_output)
        
        #Mostrar el resultado
        combined_frame = cv2.hconcat([frame, fire_detected])
        cv2.imshow("Video Original y Detección de Fuego", combined_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    video.release()

#Casos de prueba
fire_threshold = 4700
video = cv2.VideoCapture("nosotros.mp4")

#fire_threshold = 1300
#video = cv2.VideoCapture("new_video.mp4")

fire_message = 0
fuego_detectado = False
alarma_sonando = False

sound_thread = threading.Thread(target=play_sound, daemon=True)
sound_thread.start()

message_thread = threading.Thread(target=send_telegram_notification, daemon=True)
message_thread.start()
detect_fire()
