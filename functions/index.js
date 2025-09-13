const functions = require("firebase-functions");

// Middleware simple
function validatePOST(req, res, next) {
  try {
    if (req.method !== "POST") return res.status(400).json({ error: "Solo POST permitido" });
    next();
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
}

// 1️⃣ Función: transcribeAudio (simulada)
exports.transcribeAudio = functions.https.onRequest((req, res) => {
  validatePOST(req, res, () => {
    const audioLink = req.body.audio || "No hay audio";
    const textoTranscrito = "Transcripción simulada del audio: " + audioLink;
    res.json({ texto: textoTranscrito });
  });
});

// 2️⃣ Función: extractMedicalInfo (simulada)
exports.extractMedicalInfo = functions.https.onRequest((req, res) => {
  validatePOST(req, res, () => {
    const texto = req.body.texto || "No hay texto";
    const infoMedica = {
      sintomas: ["dolor de cabeza", "fiebre"],
      paciente: { nombre: "Juan Pérez", edad: 30, id: "12345" },
      motivoConsulta: "Consulta general",
      textoOriginal: texto
    };
    res.json(infoMedica);
  });
});

// 3️⃣ Función: generateDiagnosis (simulada)
exports.generateDiagnosis = functions.https.onRequest((req, res) => {
  validatePOST(req, res, () => {
    const info = req.body;
    const resultado = {
      diagnostico: `Diagnóstico simulado para: ${info.textoOriginal || "sin texto"}`,
      tratamiento: "Tratamiento simulado",
      recomendaciones: "Seguir reposo y medicación",
      infoMedica: info
    };
    res.json(resultado);
  });
});
