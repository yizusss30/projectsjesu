from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import requests
import uvicorn
import os

app = FastAPI()

# Para evitar problemas de conexión en la nube
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# En la nube, es mejor usar variables de entorno, pero por ahora pongámoslas aquí
META_TOKEN = "IGAAO5Ql0bFblBZAGJFYmtrMVpMWG9FNUNHVU81ZAVZADWUZA0OHNIMktTN1pmUFBqVFNBT2dVQmpOVV94TDJvd0FLcUhhazFFcUc2THlCQU1uaGRtRlNLdGVKRGU1UzdmVTdoVFJSSDh0czlGbzVTdjBRaE85Vl9FOEFuMWFLVllVawZDZD"
VERIFY_TOKEN = "usm_bot_token_2026"


def procesar_mensaje(texto):
    texto = texto.lower()
    if "precio" in texto or "costo" in texto or texto == "1":
        return "Los costos de matrícula varían según la carrera. Mira la lista aquí: [Linktree/Precios] 💸"
    elif "papel" in texto or "requisito" in texto or texto == "2":
        return "Para formalizar necesitas: Notas, Título, etc. Todo detallado aquí: [Linktree/Requisitos] 📁"
    elif "inscripcion" in texto or "pagina" in texto or texto == "3":
        return "El proceso es en usm.edu.ve. Guía paso a paso: [Linktree/Inscripciones] 🌐"
    elif "carrera" in texto or "ofrecen" in texto or texto == "4":
        return "Ofrecemos Ingeniería, Derecho, Farmacia, Odontología. Conoce más: [Linktree/Carreras] 🏛️"
    elif "pensum" in texto or "materia" in texto or texto == "5":
        return "Descarga el pensum completo en PDF aquí: [Linktree/Pensum] 📖"
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
    # ESTAS SON LAS LÍNEAS NUEVAS PARA DETECTAR EL ERROR:
    respuesta = requests.post(url, headers=headers, json=data)
    print(
        f"INTENTO DE RESPUESTA A META: {respuesta.status_code} - {respuesta.text}")
# Endpoint de Salud (Para que Render sepa que la app está viva)


@app.get("/")
def home():
    return {"status": "USM Bot Activo"}


@app.get("/webhook")
async def verificar_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return Response(content=challenge, media_type="text/plain")
    return Response(content="Error de verificación", status_code=403)


@app.post("/webhook")
async def recibir_mensajes(request: Request):
    body = await request.json()
    try:
        if body.get("object") == "instagram":
            for entry in body["entry"]:
                for evento in entry.get("messaging", []):
                    if "message" in evento and "text" in evento["message"]:
                        id_estudiante = evento["sender"]["id"]
                        texto_recibido = evento["message"]["text"]

                        respuesta = procesar_mensaje(texto_recibido)
                        enviar_mensaje_instagram(id_estudiante, respuesta)
    except Exception as e:
        print(f"Error procesando mensaje: {e}")
    return {"status": "ok"}

# Esta parte es vital para que corra en Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
