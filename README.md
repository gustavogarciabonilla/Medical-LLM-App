# Medical LLM App

Aplicación web para procesar texto o audio y generar información médica estructurada usando modelos de lenguaje.

## Descripción técnica

- **Backend:** Flask + GPT4All + Whisper
- **Frontend:** HTML/JavaScript
- **Funcionalidad:** 
  - Transcripción de audio a texto
  - Extracción de síntomas, paciente y motivo de consulta
  - Generación de diagnóstico, tratamiento y recomendaciones
- **Estructura de carpetas:**
  - `backend_local.py`
  - `index.html`
  - `functions/`
  - `requirements.txt`
  - `.gitignore`
  - `models/` (no incluido en el repositorio, debe descargarse manualmente) Descarga el modelo Mistral `mistral-7b-instruct-v0.1.Q4_0.gguf` desde: https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/blob/main/mistral-7b-instruct-v0.1.Q4_0.gguf  
Colócalo en la carpeta `models/` antes de ejecutar el backend `backend_local.py`

## Cómo ejecutar localmente

1. Clonar el repositorio:
```bash
git clone https://github.com/gustavogarciabonilla/Medical-LLM-App.git
```

2. Entrar a la carpeta:
```bash
cd Medical-LLM-App
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Ejecutar el backend:
```bash
python backend_local.py
```

5. Abrir `index.html` directamente en el navegador (Chrome, Edge, Firefox).

## Uso de la aplicación

### Procesar texto
- Escribir los síntomas o consulta en el área de texto.
- Hacer clic en **Procesar Texto**.
- Ver el resultado con información médica y diagnóstico.

### Procesar audio
- Subir un archivo `.wav` o `.mp3`. Se puede usar el archivo `audio1.wav` ó `audio1.mp3`.
- Hacer clic en **Procesar Audio**.
- Obtener la transcripción, extracción de información médica y diagnóstico.

## Decisiones de diseño relevantes

- Se usa Whisper para transcripción por su precisión en español.
- Se utiliza GPT4All local para evitar depender de APIs externas y controlar costos.
- Respuestas estructuradas en JSON para asegurar compatibilidad entre frontend y backend.
- Uso de Flask para desarrollo local rápido y pruebas.
- Interfaz web simple y minimalista, fácil de usar.

## Archivos de configuración importantes

- `.gitignore` → Ignora archivos temporales y de entorno (ej. `mi_entorno/`, `__pycache__/`).
- `requirements.txt` → Contiene todas las dependencias Python necesarias.
- `functions/` → Contiene funciones simuladas de Firebase con middleware de validación.

## Notas adicionales

- Todos los textos y resultados generados por el LLM están en español.
- La aplicación puede extenderse a producción integrando APIs externas como OpenAI o Google Speech-to-Text.
- Se puede desplegar en Firebase o cualquier servidor que soporte Python y Flask.
