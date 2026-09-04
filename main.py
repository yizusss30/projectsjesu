from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import requests
import uvicorn
import os

app = FastAPI()

# Configuración de CORS para evitar bloqueos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------
# PEGA AQUÍ TU TOKEN CORRECTO (Empieza por EAA...)
# -------------------------------------------------------------
META_TOKEN = "EAAPBRPZACvFkBSYSQuz9YXAHHekWUpYnGXssOpg6cS7M0d5M3tvZC8Esas78LceXVPZBpIcssUZBfZBRHqXZB0lygZCGvDhkj3RwSkvMTiMH2P2Nwt4W9yuOgAmaQLgxOEZC1uLKFCCFNrbg5QWQeQE0Q0XsyFVrej5tIasmsJfSQZB0UnzXqvXNXfRTpVOldxnMpqevt6OcKRQZDZD"
VERIFY_TOKEN = "usm_bot_token_2026"


def procesar_mensaje(texto):
    texto = texto.lower()
    if "precio" in texto or "costo" in texto or texto == "1":
        return "Los costos de matrícula varían según la carrera. Puedes preguntar por tu carrera a este numero: 0426-9723515 o visitar la pagina web: usm.terna.net 💸"
    elif "papel" in texto or "requisito" in texto or texto == "2":
        return "Para formalizar tu incscripción necesitas: Notas certificadas, Título de bachiller,Certificado de la OPSU, Partida de nacimiento. Para más información aqui esta el numero de planeamiento y admisión: 0414-5757609📁"
    elif "inscripcion" in texto or "pagina" in texto or texto == "3":
        return "El proceso es en usm.terna.net . Guía paso a paso en publicaciones destacadas en nuestro perfil 🌐"
    elif "carrera" in texto or "ofrecen" in texto or texto == "4":
        return "Ofrecemos Ingeniería (de Sistemas, Civil, Industrial), Derecho y Comunicación Social,Conoce más del pensum de nuestras carreras en: https://linktr.ee/USMBarinas?utm_source=linktree_profile_share&ltsid=3fcd4c2b-b38d-4ecb-9674-7cd5d652441f 🏛️"
    elif "pensum" in texto or "materia" in texto or texto == "5":
        return "Descarga el pensum completo en PDF aquí en nuestro link: https://linktr.ee/USMBarinas?utm_source=linktree_profile_share&ltsid=3fcd4c2b-b38d-4ecb-9674-7cd5d652441f 📖"
    else:
        return ("¡Hola! 👋 Bienvenido a la cuenta oficial de la USM Barinas.\n\n"
                "¿En qué te puedo ayudar hoy? Escribe un número:\n"
                "1. 💰 Precios y aranceles\n"
                "2. 📝 Requisitos (Papeles)\n"
                "3. 💻 Inscripciones y Página\n"
                "4. 🎓 Carreras\n"
                "5. 📚 Pensum")


def enviar_mensaje_instagram(id_usuario, texto_respuesta):
    url = "https://graph.facebook.com/v19.0/me/messages"
    headers = {
        "Authorization": f"Bearer {META_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "recipient": {"id": id_usuario},
        "message": {"text": texto_respuesta}
    }
    respuesta = requests.post(url, headers=headers, json=data)
    print(
        f"INTENTO DE RESPUESTA A META: {respuesta.status_code} - {respuesta.text}")

# Endpoint de Salud para Render


@app.get("/")
def home():
    return {"status": "USM Bot Activo"}

# Endpoint de Verificación del Webhook (GET)


@app.get("/webhook")
async def verificar_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return Response(content=challenge, media_type="text/plain")
    return Response(content="Error de verificación", status_code=403)

# Endpoint para recibir los mensajes de Instagram (POST) con filtro de ecos


@app.post("/webhook")
async def recibir_mensajes(request: Request):
    body = await request.json()

    try:
        if body.get("object") == "instagram":
            for entry in body["entry"]:
                for evento in entry.get("messaging", []):
                    if "message" in evento and "text" in evento["message"]:

                        # Filtro para ignorar mensajes salientes de la propia cuenta
                        if evento["message"].get("is_echo"):
                            continue

                        id_estudiante = evento["sender"]["id"]
                        texto_recibido = evento["message"]["text"]

                        respuesta = procesar_mensaje(texto_recibido)
                        enviar_mensaje_instagram(id_estudiante, respuesta)
    except Exception as e:
        print(f"Error procesando mensaje: {e}")

    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
