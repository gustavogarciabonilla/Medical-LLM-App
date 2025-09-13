# backend_local.py
from flask import Flask, request, jsonify, send_from_directory
import whisper
import json
import os
import io
import base64
import time
import tempfile
import traceback
from pydub import AudioSegment
from flask_cors import CORS

# -----------------------------
# Configuración de FFmpeg para Pydub en Windows
# -----------------------------
AudioSegment.converter = r"C:\Users\MKS-5482\Medical\ffmpeg-8.0-full_build\bin\ffmpeg.exe"

# -----------------------------
# Intentar importar GPT4All (modelo local)
# -----------------------------
MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
MODEL_NAME = "mistral-7b-instruct-v0.1.Q4_0.gguf"
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_NAME)

GPT_AVAILABLE = False
gpt_model = None

try:
    from gpt4all import GPT4All
    if os.path.isfile(MODEL_PATH):
        try:
            gpt_model = GPT4All(model_name=MODEL_NAME, model_path=MODEL_DIR)
            GPT_AVAILABLE = True
            size_mb = os.path.getsize(MODEL_PATH) / (1024 * 1024)
            print(f"✅ Modelo GPT4All cargado correctamente: {MODEL_PATH} ({size_mb:.1f} MB)")
        except Exception as e:
            print(f"⚠️ Error cargando GPT4All desde {MODEL_PATH}: {e}")
            traceback.print_exc()
            GPT_AVAILABLE = False
    else:
        print(f"⚠️ No se encontró el archivo del modelo en: {MODEL_PATH}")
except Exception as e:
    print(f"GPT4All no disponible, se usarán respuestas simuladas. Error import: {e}")
    traceback.print_exc()
    GPT_AVAILABLE = False

# -----------------------------
# Inicializar Flask y CORS
# -----------------------------
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB

# -----------------------------
# Cargar modelo Whisper
# -----------------------------
print("⏳ Cargando modelo Whisper (base)... Esto puede tardar unos segundos.")
whisper_model = whisper.load_model("base")
print("✅ Whisper cargado.")

# Carpeta base del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# -----------------------------
# Funciones de procesamiento
# -----------------------------
def transcribir_audio_en_memoria(audio_bytes, formato=None):
    temp_file = None
    try:
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format=formato)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            temp_file = tmp.name
        audio.export(temp_file, format="wav")

        t0 = time.time()
        result = whisper_model.transcribe(temp_file, language="es")
        t1 = time.time()
        print(f"⏱️ Whisper transcripción en {t1 - t0:.2f}s")
        texto = result.get("text", "")
        return texto

    except Exception as e:
        traceback.print_exc()
        raise RuntimeError(f"Error transcribiendo audio: {e}")

    finally:
        try:
            if temp_file and os.path.exists(temp_file):
                os.remove(temp_file)
        except Exception:
            pass

def procesar_texto_llm(texto):
    """
    Procesa texto usando GPT4All (si disponible) o fallback simulado.
    Todo el contenido generado estará en español.
    """
    if GPT_AVAILABLE and gpt_model:
        try:
            t0 = time.time()
            prompt_extraccion = f"""
Extrae la información médica del siguiente texto en JSON con esta estructura y responde completamente en español:
{{
  "sintomas": [], 
  "paciente": {{"nombre": "", "edad": 0, "id": ""}},
  "motivoConsulta": ""
}}
Texto: "{texto}"
"""
            with gpt_model.chat_session():
                info_json_str = gpt_model.generate(prompt_extraccion, max_tokens=300, temp=0.2)

                prompt_diagnostico = f"""
Usando la información: {info_json_str}, genera diagnóstico, tratamiento y recomendaciones.
Responde todo en español y devuelve en JSON:
{{
  "diagnostico": "",
  "tratamiento": "",
  "recomendaciones": ""
}}
"""
                diag_json_str = gpt_model.generate(prompt_diagnostico, max_tokens=300, temp=0.2)
            t1 = time.time()
            print(f"⏱️ GPT4All procesamiento LLM en {t1 - t0:.2f}s")

            try:
                info_json = json.loads(info_json_str)
            except Exception:
                info_json = {"raw": info_json_str}

            try:
                diag_json = json.loads(diag_json_str)
            except Exception:
                diag_json = {"raw": diag_json_str}

        except Exception as e:
            print(f"⚠️ Error procesando texto con LLM: {e}")
            traceback.print_exc()
            info_json = {"error": "Error en extracción con modelo"}
            diag_json = {"error": "Error en diagnóstico con modelo"}

    else:
        # Fallback simulado
        info_json = {
            "sintomas": ["fiebre", "tos"],
            "paciente": {"nombre": "Juan Perez", "edad": 35, "id": "12345"},
            "motivoConsulta": "Dolor de garganta"
        }
        diag_json = {
            "diagnostico": "Infección respiratoria leve",
            "tratamiento": "Descanso y líquidos",
            "recomendaciones": "Evitar cambios bruscos de temperatura"
        }

    resultado = {"infoMedica": info_json, **diag_json}
    return resultado

# -----------------------------
# Endpoints de la API
# -----------------------------
@app.route("/procesar_audio", methods=["POST"])
def procesar_audio():
    try:
        data = request.json
        print("📥 Petición /procesar_audio recibida")
        if not data:
            return jsonify({"error": "No se recibió JSON en la petición"}), 400

        audio_b64 = data.get("audio")
        formato = data.get("formato")
        if not audio_b64:
            return jsonify({"error": "Falta campo 'audio'"}), 400

        audio_bytes = base64.b64decode(audio_b64)
        texto = transcribir_audio_en_memoria(audio_bytes, formato=formato)
        resultado = procesar_texto_llm(texto)
        resultado["textoOriginal"] = texto
        return jsonify(resultado)

    except Exception as e:
        print("❌ Exception en /procesar_audio:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/procesar_texto", methods=["POST"])
def procesar_texto():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No se recibió JSON en la petición"}), 400

        texto = data.get("texto")
        if not texto:
            return jsonify({"error": "Falta campo 'texto'"}), 400

        print(f"📥 /procesar_texto recibido. Texto (len={len(texto)})")
        resultado = procesar_texto_llm(texto)
        resultado["textoOriginal"] = texto
        return jsonify(resultado)

    except Exception as e:
        print("❌ Exception en /procesar_texto:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# -----------------------------
# Servir HTML desde Flask
# -----------------------------
@app.route("/")
def home():
    html_path = os.path.join(BASE_DIR, "index.html")
    if not os.path.isfile(html_path):
        return "<h1>index.html no encontrado</h1>", 404
    return send_from_directory(BASE_DIR, "index.html")

# -----------------------------
# Ejecutar servidor
# -----------------------------
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5005, threaded=True)
